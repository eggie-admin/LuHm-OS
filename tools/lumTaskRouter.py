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
    "dictation": ["lum", "belldandySecretary", "koe"],
    "asset": ["lum", "sumi"],
}

SUPPORT = {"kiri", "momo", "shiori", "fumi", "yume", "koe", "sumi", "urdDoctorGoddess", "belldandySecretary", "skuldResearch"}
RESIDENT_CABINET = ["urdDoctorGoddess", "belldandySecretary", "skuldResearch"]
LAZY_ONI = ["kiri", "momo", "shiori", "kugi", "tetsu", "kaji", "fumi", "sumi", "koe", "yume", "mediaAssetFactory"]


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
        "residentCabinetState": "resident",
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
        "requiresProfessorCrown": "ProfessorCrown" in workers,
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
