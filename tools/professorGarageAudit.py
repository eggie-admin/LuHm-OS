#!/usr/bin/env python3
import argparse
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCTRINE = ROOT / "doctrine" / "professorGarageWorkspaceV1.json"
REPAIR = ROOT / "doctrine" / "ffmpegAiRepairBayV1.json"
DEVCONTAINER = ROOT / ".devcontainer" / "devcontainer.json"

def need(condition, message, errors):
    if not condition:
        errors.append(message)

def command_version(name, args):
    path = shutil.which(name)
    if not path:
        return {"found": False, "path": None, "version": None}
    try:
        proc = subprocess.run([name, *args], capture_output=True, text=True, timeout=10)
        text = (proc.stdout or proc.stderr).strip().splitlines()
        version = text[0] if text else "UNKNOWN"
    except Exception as exc:
        version = f"ERROR:{type(exc).__name__}"
    return {"found": True, "path": path, "version": version}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", action="store_true")
    args = parser.parse_args()

    errors = []
    doctrine = json.loads(DOCTRINE.read_text(encoding="utf-8"))
    repair = json.loads(REPAIR.read_text(encoding="utf-8"))
    dev = json.loads(DEVCONTAINER.read_text(encoding="utf-8"))

    need(doctrine.get("schema") == "luhmOs.professorGarageWorkspace.v1", "garage schema drift", errors)
    need(doctrine.get("authority") == "Professor", "garage authority drift", errors)
    need(doctrine.get("boss") == "lum", "garage boss drift", errors)
    need(doctrine.get("crownStatus") == "STOP", "garage Crown must STOP", errors)
    need(doctrine.get("promotion") is False, "garage may not self-promote", errors)
    need(doctrine.get("workspace", {}).get("publicSshPortRequired") is False, "public SSH port must not be required", errors)
    need(doctrine.get("mediaLaw", {}).get("sourceClipImmutable") is True, "source clip immutability missing", errors)
    need(doctrine.get("mediaLaw", {}).get("frameExactRepairPreferred") is True, "frame repair preference missing", errors)
    need(repair.get("schema") == "luhmOs.ffmpegAiRepairBay.v1", "repair schema drift", errors)
    need(repair.get("frameLaw", {}).get("sourceIsReadOnly") is True, "repair source must be read-only", errors)
    need(repair.get("frameLaw", {}).get("untouchedFramesCopiedForward") is True, "untouched frame law missing", errors)
    need(repair.get("crownStatus") == "STOP", "repair Crown must STOP", errors)
    need(dev.get("containerEnv", {}).get("LUHM_WORKBENCH") == "professor-garage", "devcontainer workbench drift", errors)
    need(dev.get("containerEnv", {}).get("LUHM_CROWN_STATUS") == "STOP", "devcontainer Crown drift", errors)
    need("tools/professorGarageBootstrap.sh" in dev.get("postCreateCommand", ""), "garage bootstrap not wired", errors)

    print("PROFESSOR_GARAGE_SOURCE_AUDIT=" + ("PASS" if not errors else "FAIL"))
    if errors:
        for error in errors:
            print("ERROR=" + error)
        return 2

    if args.runtime:
        checks = {
            "git": ["--version"],
            "gh": ["--version"],
            "python3": ["--version"],
            "node": ["--version"],
            "ffmpeg": ["-version"],
            "ffprobe": ["-version"],
            "jq": ["--version"],
            "sqlite3": ["--version"],
            "cmake": ["--version"],
            "ninja": ["--version"],
            "clang": ["--version"],
            "gdb": ["--version"],
            "shellcheck": ["--version"],
            "rclone": ["version"],
            "ssh": ["-V"],
            "git-lfs": ["version"],
            "blender": ["--version"],
            "gimp": ["--version"],
            "godot": ["--version"]
        }
        for name, argv in checks.items():
            status = command_version(name, argv)
            print(f"TOOL={name} FOUND={str(status['found']).upper()} VERSION={status['version']}")
        print("RUNTIME_NOTE=Missing optional creative tools remain UNKNOWN/PENDING; do not infer installation or entitlement.")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
