#!/usr/bin/env python3
from pathlib import Path
import json
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "doctrine/enterpriseSecurity-20260926.json"
SECURITY = ROOT / "SECURITY.md"

results = []

def gate(name, ok, detail):
    state = "GREEN" if ok else "RED"
    results.append((name, state, detail))
    print(f"{state:5} {name}: {detail}")

policy = json.loads(POLICY.read_text()) if POLICY.is_file() else {}
security_text = SECURITY.read_text() if SECURITY.is_file() else ""

runtime_paths = [
    ROOT / "cockpit",
    ROOT / "native/kaiwebview",
    ROOT / "scripts",
    ROOT / "tools",
    ROOT / ".github/workflows",
]

text_files = []
for base in runtime_paths:
    if not base.exists():
        continue
    for path in base.rglob("*"):
        if path.is_file() and not any(part in {"node_modules", "build", ".gradle", "vendor"} for part in path.parts):
            if path.suffix.lower() in {".kt", ".kts", ".java", ".gd", ".js", ".json", ".py", ".sh", ".yml", ".yaml", ".xml", ".cfg", ".md"}:
                text_files.append(path)

secret_patterns = {
    "private_key_pem": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "google_access_token": re.compile(r"\bya29\.[A-Za-z0-9._-]{16,}"),
    "google_refresh_token": re.compile(r"\b1//[A-Za-z0-9._-]{20,}"),
    "google_api_key": re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    "github_classic_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "github_fine_token": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    "openai_api_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "slack_token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{16,}\b"),
}
secret_hits = []
for path in text_files:
    text = path.read_text(errors="ignore")
    for label, pattern in secret_patterns.items():
        if pattern.search(text):
            secret_hits.append(f"{label}:{path.relative_to(ROOT)}")

gate("01_source_authority", POLICY.is_file() and SECURITY.is_file() and policy.get("authority", {}).get("human_final_authority") is True, "enterprise policy and SECURITY.md present with human authority")
gate("02_secret_material_scan", not secret_hits, "no runtime/workflow secret-shaped material" if not secret_hits else ", ".join(secret_hits))

workflow_files = [
    ROOT / ".github/workflows/final-install-route.yml",
    ROOT / ".github/workflows/s24fe-canary-admin-harness.yml",
]
workflow_ok = True
for wf in workflow_files:
    text = wf.read_text() if wf.is_file() else ""
    workflow_ok &= "permissions:\n  contents: read" in text and "persist-credentials: false" in text
gate("03_github_ci_token_boundary", workflow_ok, "workflows use contents:read and discard checkout credentials")

identity = policy.get("identity", {}).get("google_live_session", {})
identity_ok = (
    identity.get("connector_tokens_are_opaque") is True
    and identity.get("export_connector_access_token_to_apk") is False
    and identity.get("read_browser_cookies_or_google_session_db") is False
    and identity.get("client_secret_in_apk") is False
    and identity.get("nonce_state_pkce_required") is True
)
gate("04_google_identity_oauth", identity_ok, "live connector credentials stay opaque; native app uses explicit modern OAuth/identity flow")

tls = policy.get("tls", {})
forbidden_tls = re.compile(r"HostnameVerifier\s*\{[^}]*true|TrustAll|trustAll|ALLOW_ALL_HOSTNAME|MIXED_CONTENT_ALWAYS_ALLOW|proceed\(\)\s*;?\s*//\s*ssl", re.S)
tls_hits = []
for path in text_files:
    text = path.read_text(errors="ignore")
    if forbidden_tls.search(text):
        tls_hits.append(str(path.relative_to(ROOT)))
tls_ok = tls.get("hostname_verification") is True and tls.get("trust_all_certificates") is False and tls.get("cleartext_http_non_loopback") is False and not tls_hits
gate("05_tls_certificate_validation", tls_ok, "platform validation retained; no trust-all/hostname bypass in runtime sources")

keys = policy.get("keys", {})
key_ok = (
    "never" in keys.get("android_release_signing", "").lower()
    and keys.get("oauth_client_secret", "").startswith("not applicable")
    and "never repository" in keys.get("vpn_private_key", "")
    and policy.get("google_drive", {}).get("public_share") is False
)
gate("06_private_public_key_lifecycle", key_ok, "private material remains external; public certs/fingerprints are recordable receipts")

vpn = policy.get("vpn", {}).get("openvpn", {})
vpn_ok = vpn.get("status") == "OPTIONAL_NOT_ACTIVATED" and vpn.get("profile_in_repo") is False and vpn.get("embedded_client_private_key") is False and vpn.get("embedded_password") is False
gate("07_vpn_overlay_boundary", vpn_ok, "OpenVPN is optional remote overlay; no profile/private key/password embedded")

build_gradle = (ROOT / "native/kaiwebview/kaiwebview/build.gradle.kts").read_text()
shizuku_src = (ROOT / "native/kaiwebview/kaiwebview/src/main/java/art/eggiebagelface/luhmos/kaiwebview/ShizukuCapability.kt").read_text()
webview_src = (ROOT / "native/kaiwebview/kaiwebview/src/main/java/art/eggiebagelface/luhmos/kaiwebview/KAIWebView.kt").read_text()
shizuku_ok = (
    'dev.rikka.shizuku:api:$shizukuVersion' in build_gradle
    and 'dev.rikka.shizuku:provider:$shizukuVersion' in build_gradle
    and 'val shizukuVersion = "13.1.5"' in build_gradle
    and "Shizuku.newProcess" not in shizuku_src
    and "UserService" not in shizuku_src
    and "Runtime.getRuntime().exec" not in shizuku_src
    and "ProcessBuilder" not in shizuku_src
    and '"status.request"' in webview_src
    and '"shizuku.permission.request"' not in webview_src
)
gate("08_shizuku_privilege_boundary", shizuku_ok, "pinned Shizuku capability probe; permission is native-explicit and WebView cannot request privilege")

drive = policy.get("google_drive", {})
drive_ok = drive.get("public_share") is False and "OAuth_access_tokens" in drive.get("forbidden", []) and "private_signing_keys" in drive.get("forbidden", [])
gate("09_drive_artifact_policy", drive_ok, "Drive build lane accepts artifacts/receipts, not tokens or private keys")

openssl = shutil.which("openssl")
openssl_version = "missing"
if openssl:
    proc = subprocess.run([openssl, "version"], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    openssl_version = proc.stdout.strip()
recovery = policy.get("keys", {}).get("rotation", "")
gate("10_crypto_receipts_rotation", bool(openssl) and bool(recovery), f"{openssl_version}; rotation/revocation/recovery contract present")

failed = [name for name, state, _ in results if state != "GREEN"]
summary = {
    "schema": "luhm.enterprise-security.audit.v1",
    "source_result": "GREEN" if not failed else "RED",
    "enterprise_result": "AMBER_EXTERNAL_PROOF_PENDING" if not failed else "RED",
    "external_pending": [
        "GitHub branch ruleset/protection",
        "persistent Android signing custody",
        "Google OAuth client registration and consent verification if APK auth is activated",
        "live TLS/mTLS endpoint evidence if remote HTTPS is activated",
        "live VPN endpoint evidence if OpenVPN is activated",
        "physical Samsung Shizuku permission/runtime receipt",
        "physical APK install/runtime smoke"
    ],
    "passes": results,
    "failed": failed,
}
print(json.dumps(summary, indent=2))
sys.exit(1 if failed else 0)
