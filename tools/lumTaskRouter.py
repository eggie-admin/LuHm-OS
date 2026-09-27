#!/usr/bin/env python3
"""Deterministic fast-path router for the LuHm agent mesh.

This chooses workers. It does not grant authority, mutate source, or claim GREEN.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROUTES = {
    "direct": ["Lum"],
    "read": ["Lum", "Kiri"],
    "records": ["Lum", "Fumi"],
    "proof": ["Lum", "Sumi", "DrNao"],
    "patch": ["Lum", "Kugi", "DrNao"],
    "build": ["Lum", "Kugi", "Tetsu", "Kaji", "DrNao"],
    "external": ["Lum", "Momo"],
    "monitor": ["Lum", "DrNao"],
    "release": ["Lum", "DrNao", "ProfessorCrown"],
    "art": ["Lum", "Yume"],
    "media": ["Lum", "Yume", "Sumi"],
    "dictation": ["Lum", "Koe"],
    "asset": ["Lum", "Sumi"],
}

SUPPORT = {"Kiri", "Momo", "Shiori", "Fumi", "Yume", "Koe", "Sumi"}


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

    if args.truth_sensitive and "DrNao" not in workers:
        workers.append("DrNao")
        reasons.append("truth-sensitive")
    if args.contested:
        workers.append("Shiori")
        if "DrNao" not in workers:
            workers.append("DrNao")
        reasons.append("contested")
    if args.external_fact and "Momo" not in workers:
        workers.append("Momo")
        reasons.append("external-fact")
    if args.asset_review and "Sumi" not in workers:
        workers.append("Sumi")
        reasons.append("asset-review")

    workers = unique(workers)
    support = [w for w in workers if w in SUPPORT]
    if len(support) > 3:
        raise SystemExit("RED_ROUTER_SUPPORT_PARALLELISM_EXCEEDED")

    report = {
        "schema": "luhm-os.task-route.v2",
        "kind": args.kind,
        "workers": workers,
        "reasons": reasons,
        "supportWorkers": support,
        "sourceMutationLanes": 1 if "Kugi" in workers else 0,
        "parallelBuilds": 2 if {"Tetsu", "Kaji"}.issubset(workers) else 0,
        "requiresDoctorVerdict": "DrNao" in workers,
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
