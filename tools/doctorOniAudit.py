#!/usr/bin/env python3
"""Read-only dual-build adjudicator for LuHm OS.

GREEN is derived only when two independent build evidence bundles agree on the
same immutable source and all required evidence is present. Missing/null/error
states fail closed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

BAD_TOKENS = {"", "NULL", "NONE", "UNKNOWN", "ERROR"}
REQUIRED_FILES = (
    "cathedral-atelier-receipt.txt",
    "badging.txt",
    "manifest.txt",
    "signature.txt",
    "zipalign.txt",
    "sha256.txt",
    "source-components-sha256.txt",
    "oni-builder.json",
)


def parse_kv(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        out[key.strip()] = value.strip()
    return out


def parse_hashes(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        parts = raw.strip().split(maxsplit=1)
        if len(parts) != 2:
            continue
        digest, name = parts
        out[name.lstrip("* ")] = digest
    return out


def bad(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().upper() in BAD_TOKENS
    return False


def read_bundle(root: Path, expected_sha: str) -> tuple[dict, list[str], list[str]]:
    errors: list[str] = []
    unknowns: list[str] = []
    for name in REQUIRED_FILES:
        path = root / name
        if not path.is_file() or path.stat().st_size == 0:
            unknowns.append(f"missing_or_empty:{name}")

    if unknowns:
        return {}, errors, unknowns

    try:
        receipt = parse_kv(root / "cathedral-atelier-receipt.txt")
        builder = json.loads((root / "oni-builder.json").read_text(encoding="utf-8"))
        components = parse_hashes(root / "source-components-sha256.txt")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"malformed_bundle:{type(exc).__name__}:{exc}")
        return {}, errors, unknowns

    required_receipt = ("source_sha", "package", "version", "status")
    for key in required_receipt:
        if bad(receipt.get(key)):
            unknowns.append(f"missing_receipt_field:{key}")

    for key in ("name", "role", "runId", "jobId", "sourceSha"):
        if bad(builder.get(key)):
            unknowns.append(f"missing_builder_field:{key}")

    if receipt.get("source_sha") != expected_sha:
        errors.append(f"receipt_source_mismatch:{receipt.get('source_sha')}!={expected_sha}")
    if builder.get("sourceSha") != expected_sha:
        errors.append(f"builder_source_mismatch:{builder.get('sourceSha')}!={expected_sha}")
    if not components:
        unknowns.append("missing_component_hashes")

    return {
        "receipt": receipt,
        "builder": builder,
        "components": components,
    }, errors, unknowns


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--tetsu", type=Path, required=True)
    parser.add_argument("--kaji", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    tetsu, t_errors, t_unknowns = read_bundle(args.tetsu, args.expected_sha)
    kaji, k_errors, k_unknowns = read_bundle(args.kaji, args.expected_sha)
    errors = [*(f"tetsu:{x}" for x in t_errors), *(f"kaji:{x}" for x in k_errors)]
    unknowns = [*(f"tetsu:{x}" for x in t_unknowns), *(f"kaji:{x}" for x in k_unknowns)]
    divergences: list[str] = []

    if tetsu and kaji:
        if tetsu["builder"].get("name") != "Tetsu":
            errors.append("tetsu:wrong_builder_identity")
        if kaji["builder"].get("name") != "Kaji":
            errors.append("kaji:wrong_builder_identity")
        if tetsu["builder"].get("runId") == kaji["builder"].get("runId") and tetsu["builder"].get("jobId") == kaji["builder"].get("jobId"):
            errors.append("builders_not_independent")

        for key in ("source_sha", "package", "version"):
            if tetsu["receipt"].get(key) != kaji["receipt"].get(key):
                divergences.append(f"receipt.{key}")
        if tetsu["components"] != kaji["components"]:
            divergences.append("source_components")

    if errors:
        status = "RED_DOCTOR_ONI_CONTRACT_FAILURE"
    elif unknowns:
        status = "UNKNOWN_DOCTOR_ONI_EVIDENCE_INCOMPLETE"
    elif divergences:
        status = "AMBER_DOCTOR_ONI_BUILD_DIVERGENCE"
    else:
        status = "GREEN_DOCTOR_ONI_DUAL_BUILD_PROVEN"

    report = {
        "schema": "luhm-os.doctor-oni-audit.v1",
        "status": status,
        "expectedSourceSha": args.expected_sha,
        "promotionAuthority": False,
        "sourceMutationAuthority": False,
        "errors": errors,
        "unknowns": unknowns,
        "divergences": divergences,
        "builders": {
            "Tetsu": tetsu.get("builder") if tetsu else None,
            "Kaji": kaji.get("builder") if kaji else None,
        },
        "semanticEvidence": {
            "Tetsu": {
                "receipt": tetsu.get("receipt"),
                "components": tetsu.get("components"),
            } if tetsu else None,
            "Kaji": {
                "receipt": kaji.get("receipt"),
                "components": kaji.get("components"),
            } if kaji else None,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if status.startswith("GREEN_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
