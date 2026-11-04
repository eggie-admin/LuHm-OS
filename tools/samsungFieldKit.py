#!/usr/bin/env python3
"""Samsung Termux field console: no root, installs, external APIs, or state mutation."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "doctrine/currentSourceTruthV3.json"
EDGE = "doctrine/apiSpineV1.json"
AUDIT = "tools/hardSystemAudit200.py"
HELP = "tools/luhm.py"


def run_command(args: list[str], *, timeout: float = 8) -> tuple[int, str]:
    try:
        p = subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                           timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return 127, ""
    return p.returncode, p.stdout.strip()


def git_identity() -> dict:
    code, head = run_command(["git", "rev-parse", "--verify", "HEAD"])
    branch_code, branch = run_command(["git", "branch", "--show-current"])
    status_code, status = run_command(["git", "status", "--porcelain", "--untracked-files=no"])
    return {
        "sourceRef": head if code == 0 and re.fullmatch(r"[0-9a-f]{40}", head) else "UNVERIFIED",
        "branch": branch if branch_code == 0 and branch else "UNVERIFIED",
        "trackedChangesPresent": bool(status) if status_code == 0 else None,
        "trackedChangesProof": "OBSERVED" if status_code == 0 else "UNKNOWN",
    }


def safe_pull_instruction(identity: dict) -> str:
    if identity["sourceRef"] == "UNVERIFIED":
        return "STOP_NOT_A_GIT_CHECKOUT"
    if identity["trackedChangesPresent"] is not False:
        return "STOP_LOCAL_CHANGES_OR_STATUS_UNKNOWN"
    if identity["branch"] != "main":
        return "STOP_NOT_ON_MAIN"
    return "git pull --ff-only origin main"


def device_hints() -> dict:
    out = {}
    for key, prop in (("model", "ro.product.model"),
                      ("android", "ro.build.version.release"),
                      ("abi", "ro.product.cpu.abi")):
        code, value = run_command(["getprop", prop], timeout=2)
        out[key] = value[:80] if code == 0 and value else "UNVERIFIED"
    return out


def source_profile() -> dict:
    doc = json.loads((ROOT / SOURCE).read_text(encoding="utf-8"))
    return {
        "schema": doc.get("schema"),
        "status": doc.get("status"),
        "crownStatus": doc.get("crownStatus"),
        "sourceAuthority": doc.get("canonicalRepository"),
    }


def edge_profile() -> dict:
    doc = json.loads((ROOT / EDGE).read_text(encoding="utf-8"))
    edge = doc["providers"]["edgeGallery"]
    return {
        "providerId": "edgeGallery",
        "sourceReadiness": edge["readiness"],
        "modelIdentityState": edge["modelIdentityState"],
        "appInstalled": "UNVERIFIED",
        "modelDownloaded": "UNVERIFIED",
        "luHmBridgeOperational": "UNVERIFIED",
        "networkCalls": 0,
    }


def ollama_probe(*, fetch=urlopen) -> dict:
    """GET loopback only, by explicit invocation; does not generate/download models."""
    result = {"target": "http://127.0.0.1:11434", "transport": "loopbackOnly",
              "modelInference": False, "modelDownloaded": False}
    # Only fixed literal endpoints; do not accept user URLs or proxy credentials.
    for name, path in (("version", "/api/version"), ("models", "/api/tags")):
        try:
            with fetch(result["target"] + path, timeout=2) as response:
                raw = response.read(65537)
            if len(raw) > 65536:
                result[name] = "UNVERIFIED_RESPONSE_TOO_LARGE"
                continue
            obj = json.loads(raw)
            if name == "version":
                result[name] = str(obj.get("version", "UNKNOWN"))[:80]
            else:
                models = obj.get("models")
                result["modelCount"] = len(models) if isinstance(models, list) else "UNKNOWN"
                result["modelNames"] = [x["name"][:120] for x in models[:16]
                                        if isinstance(x, dict) and isinstance(x.get("name"), str)] if isinstance(models, list) else []
        except (OSError, ValueError, TypeError, KeyError, HTTPError, URLError):
            result[name] = "NOT_REACHABLE_OR_UNVERIFIED"
    result["localServiceProven"] = isinstance(result.get("version"), str) and result["version"] not in (
        "NOT_REACHABLE_OR_UNVERIFIED", "UNVERIFIED_RESPONSE_TOO_LARGE", "UNKNOWN")
    result["luHmBridgeOperational"] = "UNVERIFIED"
    return result


def doctor(*, passes: int) -> tuple[int, dict]:
    if not (1 <= passes <= 4):
        return 2, {"verdict": "RED_INVALID_PASS_BUDGET"}
    identity = git_identity()
    sha = identity["sourceRef"]
    if sha == "UNVERIFIED" or not (ROOT / AUDIT).is_file():
        return 2, {"verdict": "RED_SOURCE_NOT_BOUND", "sourceRef": sha}
    receipts = []
    for i in range(passes):
        try:
            run = subprocess.run(
                [sys.executable, str(ROOT / AUDIT)], cwd=ROOT,
                capture_output=True, text=True, timeout=45,
                env={**os.environ, "LUHM_SOURCE_REF": sha},
                check=False,
            )
            lines = run.stdout.splitlines()
            count = next((s.partition("=")[2] for s in lines if s.startswith("passes=")), "UNKNOWN")
            state = next((s.partition("=")[2] for s in lines if s.startswith("HARD_SYSTEM_AUDIT=")), "UNKNOWN")
            matching = "sourceRef=" + sha in lines
            ok = run.returncode == 0 and count == "200/200" and state == "GREEN" and matching
            receipts.append({"pass": i + 1, "status": "PASS_SOURCE_ONLY" if ok else "RED_AUDIT",
                             "checks": count, "exitCode": run.returncode, "exactSource": matching})
        except (OSError, subprocess.TimeoutExpired):
            receipts.append({"pass": i + 1, "status": "RED_EXECUTION", "checks": "UNKNOWN"})
        if receipts[-1]["status"] != "PASS_SOURCE_ONLY":
            break
    success = len(receipts) == passes and all(x["status"] == "PASS_SOURCE_ONLY" for x in receipts)
    return (0 if success else 1), {
        "schema": "luhmOs.samsungFieldDoctorReceipt.v1",
        "sourceRef": sha,
        "requestedPasses": passes,
        "completedPasses": len(receipts),
        "totalSourceChecksPassed": sum(200 for x in receipts if x["status"] == "PASS_SOURCE_ONLY"),
        "verdict": "GREEN_SOURCE_ONLY" if success else "RED_OR_UNVERIFIED_SOURCE",
        "runs": receipts,
        "samsungRuntimeProven": False,
        "productionAuthority": False,
        "crownStatus": "STOP",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="LuHmOS Samsung field kit: read-only Git, Edge Gallery, Ollama and 200-check Doctor.",
        epilog="No root, APK install, model download, production merge or remote execution.")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("help", help="Show existing LuHm Canon naming and command help")
    sub.add_parser("status", help="Read Git checkout, device hints and exact source contract")
    sub.add_parser("git", help="Print safe git pull instruction without executing it")
    sub.add_parser("edge", help="Show Canon Edge Gallery readiness (not app integration proof)")
    sub.add_parser("ollama", help="Explicitly probe only local 127.0.0.1:11434, read-only")
    doc = sub.add_parser("doctor", help="Run actual 200-check source audit, bounded")
    doc.add_argument("--passes", type=int, default=1, choices=range(1, 5), metavar="1..4")
    args = parser.parse_args(argv)
    if args.command in (None, "help"):
        parser.print_help()
        if (ROOT / HELP).is_file():
            subprocess.run([sys.executable, str(ROOT / HELP), "--help"],
                           cwd=ROOT, check=False, timeout=10)
        return 0
    try:
        if args.command == "status":
            result = {"schema": "luhmOs.samsungFieldStatus.v1", "git": git_identity(),
                      "device": device_hints(), "canon": source_profile(),
                      "deviceIntegrationProven": False, "crownStatus": "STOP"}
        elif args.command == "git":
            identity = git_identity()
            result = {"git": identity, "suggestedCommand": safe_pull_instruction(identity),
                      "pullExecuted": False, "crownStatus": "STOP"}
        elif args.command == "edge":
            result = edge_profile()
        elif args.command == "ollama":
            result = ollama_probe()
        elif args.command == "doctor":
            code, result = doctor(passes=args.passes)
            print(json.dumps(result, indent=2, sort_keys=True))
            return code
        else:
            parser.error("unknown operation")
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        print('{"verdict":"RED_SOURCE_CONTRACT_UNAVAILABLE","crownStatus":"STOP"}')
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
