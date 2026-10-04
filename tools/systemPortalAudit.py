#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORTAL = ROOT / "systemPortal"

errors = []

def require(condition, message):
    if not condition:
        errors.append(message)

required = [
    PORTAL / "README.md",
    PORTAL / "index.html",
    PORTAL / "services.json",
    PORTAL / "dns.example.yaml",
    PORTAL / "portalPolicy.json",
]
for path in required:
    require(path.is_file(), f"missing required portal file: {path.relative_to(ROOT)}")

if not errors:
    services = json.loads((PORTAL / "services.json").read_text(encoding="utf-8"))
    policy = json.loads((PORTAL / "portalPolicy.json").read_text(encoding="utf-8"))
    html = (PORTAL / "index.html").read_text(encoding="utf-8")
    dns = (PORTAL / "dns.example.yaml").read_text(encoding="utf-8")
    all_text = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in required)

    require(services.get("portal", {}).get("crown") == "STOP", "portal registry must keep CROWN=STOP")
    require(services.get("portal", {}).get("authority") == "READ_ONLY", "portal registry must be READ_ONLY")
    for service in services.get("services", []):
        require(service.get("writeAuthority") is False, f"service grants writeAuthority: {service.get('id')}")

    auth = policy.get("authority", {})
    require(policy.get("crown") == "STOP", "portal policy must keep CROWN=STOP")
    for key in ("execution", "merge", "sign", "publish", "deploy", "crown"):
        require(auth.get(key) is False, f"portal authority escalation: {key}")

    require("<script" not in html.lower(), "portal HTML must remain script-free in v1")
    require("fetch(" not in html.lower(), "portal HTML must not fetch remote state in v1")
    require("websocket" not in html.lower(), "portal HTML must not open WebSockets in v1")
    require("EXAMPLE_ONLY" in dns, "DNS proposal must remain EXAMPLE_ONLY")
    require("<cloudflare-tunnel-uuid>" in dns, "DNS proposal must not embed a claimed live tunnel target")

    secret_patterns = [
        r"sk-[A-Za-z0-9_-]{16,}",
        r"gh[pousr]_[A-Za-z0-9]{20,}",
        r"AIza[0-9A-Za-z_-]{20,}",
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
        r"(?i)(api[_-]?token|access[_-]?token|refresh[_-]?token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-/.]{12,}",
    ]
    for pattern in secret_patterns:
        require(re.search(pattern, all_text) is None, f"secret-like material matched: {pattern}")

if errors:
    print("SYSTEM_PORTAL_AUDIT=RED")
    for error in errors:
        print(f"ERROR: {error}")
    raise SystemExit(1)

print("SYSTEM_PORTAL_AUDIT=GREEN")
print("scope=static-candidate-only")
print("runtimeDnsCertificateTunnelProof=UNPROVEN")
print("crown=STOP")
