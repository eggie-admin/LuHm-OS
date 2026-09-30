#!/usr/bin/env python3
"""Deterministic LuHm OS pet-runtime contract audit.

This proves repository contract consistency only. It does not prove Android device,
Ollama, Termux:X11, bubble, background-service, or physical runtime behavior.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "doctrine" / "petRuntimeHardening-20260926.json"
SOURCE = ROOT / "doctrine" / "SOURCE_OF_TRUTH.json"
RELEASE = ROOT / "doctrine" / "RELEASE_BOUNDARY.json"
CONTROLLER = ROOT / "scripts" / "game" / "petWindowController.gd"

EXPECTED_MODES = {
    "FULLSCREEN",
    "MINI_PLAYER",
    "PET_INSPECT",
    "CHAT_HEAD",
    "BACKGROUND",
    "EXIT",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def audit() -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    manifest = load_json(MANIFEST)
    source = load_json(SOURCE)
    release = load_json(RELEASE)
    controller = CONTROLLER.read_text(encoding="utf-8")

    if manifest.get("authority") != "Professor":
        errors.append("pet manifest must keep Professor as authority")
    if manifest.get("seal", {}).get("promotion") is not False:
        errors.append("candidate checkpoint must not self-promote")
    if manifest.get("seal", {}).get("release_authority") is not False:
        errors.append("candidate checkpoint must not grant release authority")

    modes = {item.get("id") for item in manifest.get("ux_modes", [])}
    if modes != EXPECTED_MODES:
        errors.append(f"ux mode set mismatch: {sorted(modes)}")

    passes = manifest.get("ten_pass_audit", [])
    pass_numbers = [item.get("pass") for item in passes]
    if pass_numbers != list(range(1, 11)):
        errors.append("ten-pass audit must contain exactly passes 1..10 in order")

    evidence = manifest.get("evidence_state", {})
    for key in (
        "deterministic_ci",
        "godot_import",
        "android_debug_build",
        "physical_device",
        "ollama_runtime",
        "termux_x11_runtime",
        "android_system_bubble",
    ):
        if key not in evidence:
            errors.append(f"missing evidence field: {key}")
    if evidence.get("physical_device") == "GREEN":
        errors.append("physical device may not be predeclared GREEN in doctrine candidate")

    if source.get("canonical_repository") != "eggie-admin/LuHm-OS":
        errors.append("canonical repository drift")
    excluded = set(source.get("excluded", []))
    if "Termux execution bridge" not in excluded:
        errors.append("clean Android runtime must continue excluding Termux execution bridge")

    denied = set(release.get("deny", []))
    for required in (
        "production signing",
        "publishing",
        "stable promotion",
        "remote shell execution",
        "loopback control plane in Android runtime",
        "embedded provider secrets",
    ):
        if required not in denied:
            errors.append(f"release boundary lost deny: {required}")

    required_controller_tokens = (
        "OS.has_feature(\"android\")",
        "android_bubble_requested",
        "android_background_requested",
        "WINDOW_FLAG_BORDERLESS",
        "WINDOW_FLAG_ALWAYS_ON_TOP",
        "get_tree().quit()",
    )
    for token in required_controller_tokens:
        if token not in controller:
            errors.append(f"petWindowController missing contract token: {token}")

    forbidden_controller_tokens = (
        "OS.execute(",
        "setenforce",
        "sudo ",
        "su ",
        "127.0.0.1:11434",
        "0.0.0.0:11434",
    )
    for token in forbidden_controller_tokens:
        if token in controller:
            errors.append(f"petWindowController contains forbidden integration token: {token}")

    if "CROWN_AMBER_CANDIDATE" != manifest.get("status"):
        warnings.append("candidate status changed; inspect before promotion")

    status = "GREEN_REPOSITORY_CONTRACT" if not errors else "RED_REPOSITORY_CONTRACT"
    return {
        "schema": "luhm-os.pet-runtime-audit-report.v1",
        "status": status,
        "scope": "repository_contract_only",
        "errors": errors,
        "warnings": warnings,
        "runtimeProof": False,
        "deviceProof": False,
        "releaseAuthority": False,
        "promotionAuthority": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = audit()
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    print(payload, end="")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    return 0 if not report["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
