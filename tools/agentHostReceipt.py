#!/usr/bin/env python3
"""Fail-closed physical-host receipt for the LuHm OpenAI agent mesh.

This verifier never reads or records the provider key. A live provider request is
performed only when the human explicitly supplies --live-smoke.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SDK_VERSION = "0.22.3"
DEFAULT_ENV = Path("/home/eggie/.secrets/luhm-agent.env")
DEFAULT_RECEIPT = Path("/mnt/lum/logs/luhm-agent-host-receipt.json")
DEFAULT_UNIT = "luhm-agent-mesh.service"
SMOKE_TOKEN = "LUHM_PROVIDER_SMOKE_OK"


def run(args: list[str], *, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def mode_string(path: Path) -> str:
    return oct(stat.S_IMODE(path.stat().st_mode))


def systemd_state(unit: str) -> dict[str, str]:
    proc = run(
        [
            "systemctl",
            "show",
            unit,
            "--property=LoadState",
            "--property=ActiveState",
            "--property=SubState",
            "--property=Result",
        ]
    )
    values: dict[str, str] = {"queryExit": str(proc.returncode)}
    for line in proc.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    return values


def tracked_tree_clean() -> bool:
    unstaged = run(["git", "diff", "--quiet", "HEAD", "--"]).returncode
    staged = run(["git", "diff", "--cached", "--quiet", "HEAD", "--"]).returncode
    return unstaged == 0 and staged == 0


def live_smoke() -> tuple[bool, str]:
    if not os.getenv("OPENAI_API_KEY"):
        return False, "OPENAI_API_KEY is not present in the process environment"
    proc = run(
        [
            sys.executable,
            str(ROOT / "agents/luhm_mesh.py"),
            "Crown-authorized provider connectivity smoke. Do not call tools. Reply exactly LUHM_PROVIDER_SMOKE_OK.",
        ],
        timeout=120,
    )
    output = proc.stdout.strip()
    ok = proc.returncode == 0 and output == SMOKE_TOKEN
    if ok:
        return True, hashlib.sha256(output.encode("utf-8")).hexdigest()
    return False, f"live smoke failed with exit={proc.returncode}; output intentionally not stored"


def write_receipt(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify physical LuHm agent-host deployment without exposing secrets")
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--unit", default=DEFAULT_UNIT)
    parser.add_argument("--live-smoke", action="store_true", help="Explicitly perform one provider request")
    parser.add_argument("--allow-pending-live", action="store_true", help="Return success for installed-but-not-live-smoked AMBER state")
    args = parser.parse_args()

    errors: list[str] = []
    env_mode = "MISSING"
    parent_mode = "MISSING"
    if not args.env_file.is_file() or args.env_file.is_symlink():
        errors.append("secret environment file missing, non-regular, or symlinked")
    else:
        env_mode = mode_string(args.env_file)
        parent_mode = mode_string(args.env_file.parent)
        if env_mode != "0o600":
            errors.append(f"secret environment file mode must be 0600, observed {env_mode}")
        if parent_mode != "0o700":
            errors.append(f"secret directory mode must be 0700, observed {parent_mode}")

    try:
        sdk_version = importlib.metadata.version("openai-agents")
    except importlib.metadata.PackageNotFoundError:
        sdk_version = "MISSING"
        errors.append("openai-agents package missing")
    if sdk_version != SDK_VERSION:
        errors.append(f"openai-agents version must be {SDK_VERSION}, observed {sdk_version}")

    source = run(["git", "rev-parse", "HEAD"])
    source_sha = source.stdout.strip() if source.returncode == 0 else "UNKNOWN"
    if source.returncode != 0:
        errors.append("cannot resolve source commit")
    if not tracked_tree_clean():
        errors.append("tracked source tree differs from HEAD")

    self_test = run([sys.executable, str(ROOT / "agents/luhm_mesh.py"), "--self-test"], timeout=60)
    if self_test.returncode != 0:
        errors.append("agent mesh self-test failed")

    unit = systemd_state(args.unit)
    if unit.get("LoadState") != "loaded":
        errors.append("systemd unit is not loaded")
    if unit.get("Result") != "success":
        errors.append(f"systemd unit result is not success: {unit.get('Result', 'unknown')}")

    live_ok = False
    live_proof = "NOT_REQUESTED"
    if args.live_smoke:
        live_ok, live_proof = live_smoke()
        if not live_ok:
            errors.append(live_proof)

    base_errors = list(errors)
    if not args.live_smoke:
        errors.append("live provider smoke not yet Crown-authorized/executed")

    if base_errors:
        status = "RED_HOST_RUNTIME_PROOF"
    elif not live_ok:
        status = "AMBER_LIVE_PROVIDER_SMOKE_REQUIRED"
    else:
        status = "GREEN_HOST_RUNTIME"

    receipt = {
        "schema": "luhm-os.agent-host-receipt.v1",
        "status": status,
        "sourceCommit": source_sha,
        "trackedSourceClean": tracked_tree_clean(),
        "openaiAgentsVersion": sdk_version,
        "envFile": str(args.env_file),
        "envFileMode": env_mode,
        "envParentMode": parent_mode,
        "providerKeyRecorded": False,
        "tracingDefault": "disabled",
        "traceSensitiveData": False,
        "unit": unit,
        "liveProviderSmoke": live_ok,
        "liveSmokeProofSha256": live_proof if live_ok else None,
        "errors": errors,
        "canonicalPromotion": False,
    }
    write_receipt(args.receipt, receipt)
    print(json.dumps(receipt, indent=2, sort_keys=True))

    if status == "GREEN_HOST_RUNTIME":
        return 0
    if status == "AMBER_LIVE_PROVIDER_SMOKE_REQUIRED" and args.allow_pending_live:
        return 0
    return 2 if status == "AMBER_LIVE_PROVIDER_SMOKE_REQUIRED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
