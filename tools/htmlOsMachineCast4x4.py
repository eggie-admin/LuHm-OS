#!/usr/bin/env python3
"""Machine-only HTML OS CAST 4x4 audit, no autonomous promotion."""
import json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "build" / "html-os-cast" / "receipt.json"
CHECKS = (
    ("canon", [sys.executable, "-m", "json.tool", "doctrine/currentSourceTruthV3.json"]),
    ("escalation", [sys.executable, "tools/escalationKernelAudit.py"]),
    ("html-negative-tests", [sys.executable, "-m", "unittest", "tests/testInChatHtmlCheck.py", "-v"]),
    ("html-runtime-static", [sys.executable, "tools/inChatHtmlCheck.py", "frontEnd/index.html"]),
)
def execute():
    results = []
    for name, command in CHECKS:
        try:
            p = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=180)
            passed = p.returncode == 0
            result = {"check": name, "passed": passed, "returnCode": p.returncode,
                      "outputTail": (p.stdout + "\n" + p.stderr)[-2000:]}
        except (OSError, subprocess.TimeoutExpired) as exc:
            passed = False
            result = {"check": name, "passed": False, "error": str(exc)}
        results.append(result)
        print(f"{name}: {'PASS' if passed else 'FAIL'}", flush=True)
    ok = all(row["passed"] for row in results)
    receipt = {"schema": "luhm.htmlOs.machineCast4x4.v1", "sourceRef": os.environ.get("GITHUB_SHA", "LOCAL_UNVERIFIED"),
               "status": "SOURCE_CHECKS_PASS" if ok else "BLOCKED", "checks": results,
               "realDeviceProof": False, "liveHtmlOsRuntimeProof": False,
               "ownerCastAuthorized": False, "productionPromoted": False,
               "nextAction": "review exact-source evidence; prove runtime and device before CAST"}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return 0 if ok else 1
if __name__ == "__main__":
    raise SystemExit(execute())
