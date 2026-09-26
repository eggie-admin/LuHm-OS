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
ANDROID = ROOT / "doctrine" / "androidCandidate.json"
COMMUNITY = ROOT / "assets" / "community" / "community-assets.json"
NOTICES = ROOT / "assets" / "community" / "THIRD_PARTY_NOTICES.md"
CONTROLLER = ROOT / "scripts" / "game" / "petWindowController.gd"
OVERLAY = ROOT / "scripts" / "game" / "petHudOverlay.gd"
SITTER = ROOT / "scripts" / "game" / "pixelSitter.gd"
MAIN = ROOT / "scripts" / "main.gd"
PRESET = ROOT / "export_presets.cfg"

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
    android = load_json(ANDROID)
    community = load_json(COMMUNITY)
    controller = CONTROLLER.read_text(encoding="utf-8")
    overlay = OVERLAY.read_text(encoding="utf-8")
    sitter = SITTER.read_text(encoding="utf-8")
    main = MAIN.read_text(encoding="utf-8")
    preset = PRESET.read_text(encoding="utf-8")

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

    forbidden_runtime_tokens = (
        "OS.execute(",
        "setenforce",
        "sudo ",
        "su ",
        "127.0.0.1:11434",
        "0.0.0.0:11434",
        "OPENAI_API_KEY",
        "sk-proj-",
    )
    runtime_text = "\n".join((controller, overlay, sitter, main))
    for token in forbidden_runtime_tokens:
        if token in runtime_text:
            errors.append(f"pet runtime contains forbidden integration token: {token}")

    for token in ("FULL", "MINI", "PET", "CHAT", "BG", "X", "PixelSitterScript"):
        if token not in overlay:
            errors.append(f"pet HUD missing mode/control token: {token}")
    for token in ("horn", "hair", "skin", "eye", "suit", "accent"):
        if token not in sitter:
            errors.append(f"pixel sitter contract missing visual token: {token}")
    for token in ("PetWindowControllerScript", "PetHudOverlayScript", "pet_hud_overlay.configure"):
        if token not in main:
            errors.append(f"main runtime missing pet shell wiring: {token}")

    expected_package = android.get("package")
    expected_version_code = android.get("versionCode")
    expected_version_name = android.get("versionName")
    for token in (
        f'package/unique_name="{expected_package}"',
        f'version/code={expected_version_code}',
        f'version/name="{expected_version_name}"',
        'permissions/internet=false',
    ):
        if preset.splitlines().count(token) != 1:
            errors.append(f"Android export drift: {token}")

    vendored = community.get("vendored", [])
    if len(vendored) < 2:
        errors.append("expected at least two provenance-audited community donor sources")
    for donor in vendored:
        if donor.get("license") != "MIT":
            errors.append(f"vendored donor is not approved MIT text lane: {donor.get('id')}")
        for rel in donor.get("files", []):
            path = ROOT / "assets" / "community" / rel
            if not path.is_file():
                errors.append(f"missing vendored community file: {rel}")
    if not NOTICES.is_file() or "MIT" not in NOTICES.read_text(encoding="utf-8"):
        errors.append("community third-party notices missing or incomplete")

    external = {item.get("id"): item for item in community.get("vetted_external_packs", [])}
    for required in (
        "kenney-pixel-ui-pack",
        "kenney-game-icons",
        "polyhaven",
        "quaternius-cyberpunk-game-kit",
    ):
        if required not in external:
            errors.append(f"missing vetted external asset registry entry: {required}")
    for item in external.values():
        if str(item.get("status", "")).startswith("VENDORED"):
            errors.append(f"external binary pack incorrectly claimed vendored: {item.get('id')}")
    for item_id, item in external.items():
        if item_id.startswith("quaternius-") and not str(item.get("repo_mirror", "")).startswith("DO_NOT_REDISTRIBUTE"):
            errors.append(f"Quaternius current-license mirror restriction lost: {item_id}")

    if "CROWN_AMBER_CANDIDATE" != manifest.get("status"):
        warnings.append("candidate status changed; inspect before promotion")

    status = "GREEN_REPOSITORY_CONTRACT" if not errors else "RED_REPOSITORY_CONTRACT"
    return {
        "schema": "luhm-os.pet-runtime-audit-report.v1",
        "status": status,
        "scope": "repository_contract_only",
        "passes": 10,
        "vendoredCommunitySources": len(vendored),
        "vettedExternalPacks": len(external),
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
