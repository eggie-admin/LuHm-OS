#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
MANIFEST = ROOT / "manifest.json"
BIN = ROOT / "bin"

errors: list[str] = []
checks: list[dict[str, str]] = []

def check(name: str, ok: bool, note: str) -> None:
    checks.append({"name": name, "status": "GREEN" if ok else "RED", "note": note})
    if not ok:
        errors.append(f"{name}: {note}")

try:
    manifest = json.loads(MANIFEST.read_text())
except Exception as exc:
    print(f"manifest parse failed: {exc}", file=sys.stderr)
    raise SystemExit(2)

check("source_authority", manifest.get("authority", {}).get("crown") == "Professor", "Professor remains Crown")
check("project_scope", manifest.get("project_boundary", {}).get("target_project") == "KAI 9000", "target is KAI 9000")
check("runtime_separation", manifest.get("project_boundary", {}).get("termux_execution_bridge_in_android_runtime") is False, "no Termux bridge in native Android runtime")
check("quarantine", manifest.get("project_boundary", {}).get("merge_into_luhm_os") is False, "branch is explicitly non-merge quarantine")
check("ollama_loopback_contract", manifest.get("runtime", {}).get("ollama_bind") == "127.0.0.1:11434", "Ollama contract is loopback")
check("vnc_loopback_contract", manifest.get("runtime", {}).get("vnc_bind") == "127.0.0.1:5901", "VNC contract is loopback")
check("root_boundary", manifest.get("runtime", {}).get("root_login") is False, "root login disabled by contract")
check("selinux_boundary", manifest.get("runtime", {}).get("selinux_disable") is False, "SELinux disable forbidden")

scripts = sorted(BIN.glob("*.sh")) + [ROOT / "forge.sh"]
check("scripts_present", len(scripts) >= 6, f"{len(scripts)} forge scripts present")
for script in scripts:
    proc = subprocess.run(["bash", "-n", str(script)], capture_output=True, text=True)
    check(f"bash_n:{script.name}", proc.returncode == 0, proc.stderr.strip() or "syntax clean")

text = "\n".join(p.read_text() for p in scripts)
forbidden = {
    "public_bind": r"(?:0\.0\.0\.0|\[::\]|::):(?:11434|5901|6080)",
    "root_escalation": r"(^|\n)\s*(?:sudo|su|tsu)\b",
    "selinux_disable": r"setenforce\s+0|SELINUX=disabled",
    "blind_upgrade": r"(^|\n)\s*(?:pkg|apt)\s+(?:upgrade|full-upgrade)\b",
    "remote_shell": r"\b(?:sshd|dropbear)\b.*(?:start|serve|listen)",
}
for name, pattern in forbidden.items():
    check(f"forbidden:{name}", re.search(pattern, text, re.I | re.M) is None, f"pattern absent: {name}")

required_tokens = [
    "127.0.0.1:11434",
    "-localhost yes",
    "termux-info",
    "dpkg-query",
    "ollama-models.json",
    "KAI_HEALTH_URL",
    "snapshot",
    "human_promotion_required=true",
]
for token in required_tokens:
    check(f"required:{token}", token in text, f"required evidence/control token {token!r}")

hashes = {}
for path in [MANIFEST, ROOT / "forge.sh", *sorted(BIN.glob("*.sh"))]:
    hashes[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()

receipt = {
    "schema": "kai9000.witching-hour.static-audit.v1",
    "status": "GREEN" if not errors else "RED",
    "checks": checks,
    "hashes": hashes,
    "runtime_proof": "REQUIRED_ON_TERMUX_DEVICE",
    "human_promotion_required": True,
}
out = ROOT / "witching-hour-static-receipt.json"
out.write_text(json.dumps(receipt, indent=2) + "\n")

for row in checks:
    print(f"{row['status']:5} {row['name']}: {row['note']}")
print(f"STATIC RESULT: {receipt['status']}")
if errors:
    raise SystemExit(1)
