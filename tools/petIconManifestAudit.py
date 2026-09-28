#!/usr/bin/env python3
"""Validate the Oni pet activity contract without pretending concept art is runtime proof."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "assets/pet/oni/manifest.json"
EXPECTED_ROLES = {
    "lum", "fumi", "drNao", "tetsu", "kaji", "kiri", "momo",
    "shiori", "kugi", "yume", "koe", "sumi",
}
EXPECTED_STATES = {
    "idle", "thinking", "working", "inspect", "waiting", "success", "alert", "sleep",
}
ALLOWED_STATES = {"CONCEPT", "AMBER_REVIEW", "APPROVED_ART", "BETA_ACTIVITY_DOCK"}


def nonempty(value: object) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value) and all(nonempty(x) for x in value)
    return value is not None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "build/pet-icons/manifest-audit.json")
    args = parser.parse_args()

    errors: list[str] = []
    unknowns: list[str] = []
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    if manifest.get("logicalCanvas") != [128, 128]:
        errors.append("logical canvas must be exactly 128x128")

    sheet = manifest.get("spriteSheet", {})
    states = sheet.get("states") if isinstance(sheet, dict) else None
    if not isinstance(states, list) or set(states) != EXPECTED_STATES or len(states) != len(EXPECTED_STATES):
        errors.append("spriteSheet.states must be exactly the eight canonical activity states")

    roles = manifest.get("roles")
    if not isinstance(roles, list):
        errors.append("roles must be a list")
        roles = []
    ids = [r.get("id") for r in roles if isinstance(r, dict)]
    if set(ids) != EXPECTED_ROLES or len(ids) != len(EXPECTED_ROLES):
        errors.append("pet role roster drift")

    for role in roles:
        if not isinstance(role, dict):
            errors.append("role entry is not an object")
            continue
        rid = role.get("id", "UNKNOWN")
        for field in ("id", "displayName", "role", "accent", "motif"):
            if not nonempty(role.get(field)):
                errors.append(f"{rid}: missing_or_empty:{field}")

    if manifest.get("provenanceRequired") is not True:
        errors.append("provenanceRequired must be true")
    if manifest.get("runtimeGreenRequiresExactAssetHashImportProof") is not True:
        errors.append("runtime GREEN must require exact asset hash import proof")
    if manifest.get("status") not in ALLOWED_STATES:
        errors.append("manifest status escaped the concept/beta lane")
    if manifest.get("maxVisibleSupportWorkers") != 3:
        errors.append("pet dock support-worker visibility drift")

    expected_idle = [ROOT / f"assets/pet/oni/{rid}/{rid}_idle_v1.png" for rid in sorted(EXPECTED_ROLES)]
    missing_idle = [str(p.relative_to(ROOT)) for p in expected_idle if not p.is_file()]
    if missing_idle:
        unknowns.append("shipping idle masters not yet present")

    report = {
        "schema": "luhm-os.pet-icon-manifest-audit.v2",
        "status": "GREEN_PET_ICON_CONTRACT" if not errors else "RED_PET_ICON_CONTRACT",
        "assetRuntimeState": "UNKNOWN_ASSETS_NOT_GENERATED" if missing_idle else "AMBER_ASSET_FILES_PRESENT_IMPORT_PROOF_REQUIRED",
        "errors": errors,
        "unknowns": unknowns,
        "roleCount": len(roles),
        "requiredStateCount": len(states) if isinstance(states, list) else 0,
        "missingIdleMasters": missing_idle,
        "promotionAuthority": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
