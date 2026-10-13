#!/usr/bin/env python3
"""Deterministic fast-path router for the LuHm agent mesh.

This chooses workers. It does not grant authority, mutate source, or claim GREEN.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROUTES = {
    "direct": ["lum"],
    "read": ["lum", "kiri"],
    "records": ["lum", "belldandySecretary", "fumi"],
    "proof": ["lum", "urdDoctorGoddess"],
    "patch": ["lum", "kugi", "urdDoctorGoddess"],
    "build": ["lum", "kugi", "tetsu", "kaji", "urdDoctorGoddess"],
    "external": ["lum", "skuldResearch"],
    "diagnose": ["lum", "urdDoctorGoddess"],
    "research": ["lum", "skuldResearch"],
    "monitor": ["lum", "urdDoctorGoddess", "belldandySecretary", "skuldResearch"],
    "release": ["lum", "urdDoctorGoddess", "ProfessorCrown"],
    "art": ["lum", "yume"],
    "media": ["lum", "yume", "sumi"],
    "mediaFactory": ["lum", "yume", "mediaAssetFactory"],
    "dictation": ["lum", "belldandySecretary", "koe"],
    "asset": ["lum", "sumi"],
}

SUPPORT = {"kiri", "momo", "shiori", "fumi", "yume", "koe", "sumi", "urdDoctorGoddess", "belldandySecretary", "skuldResearch"}
RESIDENT_CABINET = ["urdDoctorGoddess", "belldandySecretary", "skuldResearch"]
LAZY_ONI = ["kiri", "momo", "shiori", "kugi", "tetsu", "kaji", "fumi", "sumi", "koe", "yume", "mediaAssetFactory"]

QUARANTINE_PATH = Path(__file__).resolve().parents[1] / "doctrine/belldandyOperationalQuarantineV1.json"
COMPANY_QUARANTINE_PATH = Path(__file__).resolve().parents[1] / "doctrine/companyWideOperationalQuarantineV1.json"


def read_company_quarantine() -> dict:
    try:
        policy = json.loads(COMPANY_QUARANTINE_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SystemExit("RED_COMPANY_QUARANTINE_POLICY_UNAVAILABLE") from exc
    if (policy.get("schema") != "luhmOs.companyWideOperationalQuarantine.v1" or
            policy.get("state") not in ("QUARANTINED", "CLEARED") or
            policy.get("registeredCount") != 15 or
            policy.get("crownStatus") != "STOP"):
        raise SystemExit("RED_COMPANY_QUARANTINE_CONTRACT_INVALID")
    if policy["state"] == "CLEARED":
        evidence = policy.get("supervisedProbe", {})
        if not all(evidence.get(key) for key in
                   ("hostInvocationReceipt", "urdEvaluationReceipt", "professorResumeReceipt")):
            raise SystemExit("RED_COMPANY_RELEASE_PROOF_MISSING")
    return policy


def read_quarantine() -> dict:
    try:
        policy = json.loads(QUARANTINE_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SystemExit("RED_QUARANTINE_POLICY_MISSING_OR_MALFORMED") from exc
    if (policy.get("schema") != "luhmOs.belldandyOperationalQuarantine.v1" or
            policy.get("subject") != "belldandySecretary" or
            policy.get("state") not in ("QUARANTINED", "CLEARED")):
        raise SystemExit("RED_QUARANTINE_POLICY_INVALID")
    if policy["state"] == "CLEARED":
        release = policy.get("release", {})
        if not (release.get("urdEvidenceReceipt") and release.get("professorApprovalReceipt")):
            raise SystemExit("RED_QUARANTINE_RELEASE_WITHOUT_URD_AND_PROFESSOR")
    return policy


def unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=sorted(ROUTES))
    parser.add_argument("--truth-sensitive", action="store_true")
    parser.add_argument("--contested", action="store_true")
    parser.add_argument("--external-fact", action="store_true")
    parser.add_argument("--asset-review", action="store_true")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    workers = list(ROUTES[args.kind])
    reasons = [f"base:{args.kind}"]

    if args.truth_sensitive and "urdDoctorGoddess" not in workers:
        workers.append("urdDoctorGoddess")
        reasons.append("truth-sensitive")
    if args.contested:
        workers.append("shiori")
        if "urdDoctorGoddess" not in workers:
            workers.append("urdDoctorGoddess")
        reasons.append("contested")
    if args.external_fact and "momo" not in workers:
        workers.append("momo")
        reasons.append("external-fact")
    if args.asset_review and "sumi" not in workers:
        workers.append("sumi")
        reasons.append("asset-review")

    workers = unique(workers)
    policy = read_quarantine()
    quarantined = policy["state"] == "QUARANTINED"
    if quarantined:
        workers = [worker for worker in workers if worker != policy["subject"]]
        reasons.append("professor-quarantine:belldandySecretary")
    company_quarantine = read_company_quarantine()
    all_held = company_quarantine["state"] == "QUARANTINED"
    if all_held:
        workers = []
        reasons.append("professor-companywide-operational-hold")
    support = [w for w in workers if w in SUPPORT]
    if len(support) > 3:
        raise SystemExit("RED_ROUTER_SUPPORT_PARALLELISM_EXCEEDED")

    active_oni = [w for w in workers if w in LAZY_ONI]
    standby_oni = [w for w in LAZY_ONI if w not in active_oni]

    report = {
        "schema": "luhm-os.task-route.v2",
        "kind": args.kind,
        "workers": workers,
        "residentCabinet": RESIDENT_CABINET,
        "residentCabinetState": "registeredRosterNotProofOfActiveExecution",
        "activeResidentCabinet": [] if all_held else [name for name in RESIDENT_CABINET if not (quarantined and name == policy["subject"])],
        "companyQuarantine": {
            "state": company_quarantine["state"],
            "registeredAgents": company_quarantine["registeredCount"],
            "activeWorkers": len(workers),
            "supervisedProbeTool": company_quarantine["supervisedProbe"]["tool"],
            "hostInvocationProven": False,
            "releaseRequiresProfessor": True,
        },
        "operationalQuarantine": {
            "subject": policy["subject"],
            "state": policy["state"],
            "urdReviewRequired": True,
            "professorReleaseRequired": True,
            "noCulpabilityInferred": True,
        },
        "residentCabinetHiddenAsync": False,
        "activeOni": active_oni,
        "standbyOni": standby_oni,
        "standbyMeansRegisteredNotExecuting": True,
        "reasons": reasons,
        "supportWorkers": support,
        "sourceMutationLanes": 1 if "kugi" in workers else 0,
        "parallelBuilds": 2 if {"tetsu", "kaji"}.issubset(workers) else 0,
        "requiresDeterministicAdjudicator": "urdDoctorGoddess" in workers,
        "usesDoctorGoddess": "urdDoctorGoddess" in workers,
        "usesSecretaryGoddess": "belldandySecretary" in workers,
        "usesResearchGoddess": "skuldResearch" in workers,
        "requiresProfessorCrown": args.kind == "release" or "ProfessorCrown" in workers,
        "dictationExecutesDirectly": False,
        "greenAuthority": False,
    }
    output = json.dumps(report, indent=2) + "\n"
    print(output, end="")
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(output, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
