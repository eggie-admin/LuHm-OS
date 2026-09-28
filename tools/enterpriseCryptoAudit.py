#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import socket
import ssl
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCTRINE = ROOT / "doctrine" / "ENTERPRISE_CRYPTO_V1.json"
SOURCE_TRUTH = ROOT / "doctrine" / "SOURCE_OF_TRUTH.json"
MCP_DOCTRINE = ROOT / "doctrine" / "MCP_ENTERPRISE_SCOPE_V1.json"
SUPPLY_CHAIN = ROOT / "doctrine" / "releaseSupplyChain-20260927.json"
SERVER = ROOT / "host" / "mcp" / "luhmMcpServer.py"
PLUGIN_MCP = ROOT / "plugins" / "luhm-os" / "mcp.json"
PROOF_VAULT = ROOT / "native" / "kaiwebview" / "kaiwebview" / "src" / "main" / "java" / "art" / "eggiebagelface" / "luhmos" / "kaiwebview" / "ProofVault.kt"
WEBVIEW = ROOT / "native" / "kaiwebview" / "kaiwebview" / "src" / "main" / "java" / "art" / "eggiebagelface" / "luhmos" / "kaiwebview" / "KAIWebView.kt"
SECURITY = ROOT / "SECURITY.md"
RENDER = ROOT / "render.yaml"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load(path: Path) -> dict:
    value = json.loads(read(path))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def flatten_name(name: tuple) -> str:
    return ", ".join(f"{key}={value}" for rdn in name for key, value in rdn)


def issuer_allowed(issuer: str, approved: list[str]) -> bool:
    lower = issuer.lower()
    aliases = {
        "Let's Encrypt": ("let's encrypt", "lets encrypt", "letsencrypt"),
        "Google Trust Services": ("google trust services", "gts ca", "google trust"),
    }
    return any(
        any(token in lower for token in aliases.get(ca, (ca.lower(),)))
        for ca in approved
    )


def static_audit() -> dict:
    for path in (
        DOCTRINE, SOURCE_TRUTH, MCP_DOCTRINE, SUPPLY_CHAIN, SERVER,
        PLUGIN_MCP, PROOF_VAULT, WEBVIEW, SECURITY, RENDER,
    ):
        require(path.is_file(), f"missing crypto audit input: {path.relative_to(ROOT)}")

    doctrine = load(DOCTRINE)
    require(doctrine.get("schema") == "luhm-os.enterprise-crypto.v1", "crypto doctrine schema drift")
    require(doctrine.get("sourceLaw") == "AI proposes. Policy authorizes. CI proves. Human promotes.", "source law drift")

    ingress = doctrine.get("publicIngress", {})
    require(ingress.get("fqdn") == "mcp.eggiebagelface.art", "public FQDN drift")
    require(ingress.get("provider") == "Render managed TLS", "TLS provider drift")
    require(str(ingress.get("minimumTls")) == "1.2", "minimum TLS must remain 1.2 or higher")
    require(ingress.get("httpRedirectToHttps") is True, "HTTP to HTTPS redirect contract missing")
    approved = ingress.get("approvedCertificateAuthorities", [])
    require(approved == ["Let's Encrypt", "Google Trust Services"], "Render managed CA allowlist drift")
    require(ingress.get("preferredCertificateAuthority") == "Let's Encrypt", "Let's Encrypt preference drift")
    require(ingress.get("strictLetsEncryptOnly") is False, "strict Let's Encrypt-only claim is invalid for Render managed TLS")
    require(ingress.get("customDomainRequired") is True, "custom domain gate missing")
    require(ingress.get("liveCertificateEvidenceRequired") is True, "live certificate evidence gate missing")
    require(ingress.get("certificatePinning") is False, "managed certificate pinning must remain disabled")
    caa = ingress.get("caaPolicy", {})
    require(caa.get("requiredWhenCaaExists") == ["letsencrypt.org", "pki.goog"], "CAA must permit both Render CAs")
    require(caa.get("letsEncryptOnlyCaaAllowed") is False, "Let's Encrypt-only CAA can break Render renewal")

    render_boundary = doctrine.get("renderBoundary", {})
    require(render_boundary.get("publicTlsTermination") == "Render load balancer", "Render TLS termination model drift")
    require(render_boundary.get("edgeToAppProtocol") == "http", "Render edge-to-app model must be represented truthfully")
    require(render_boundary.get("edgeToAppPubliclyReachable") is False, "Render app port must not be represented as public")

    local = doctrine.get("localDevelopment", {})
    require(local.get("loopbackHttpAllowed") is True, "loopback development rule missing")
    require(local.get("publicCleartextForbidden") is True, "public cleartext must fail closed")
    require(local.get("developmentCaForbiddenInProduction") is True, "development CA production ban missing")

    secrets = doctrine.get("secrets", {})
    for key in ("git", "androidApk", "pluginPackage"):
        require(secrets.get(key) is False, f"secret boundary drift: {key}")
    require(secrets.get("renderRuntimeEnvironment") is True, "Render secret environment boundary missing")
    require(secrets.get("secretLoggingForbidden") is True, "secret logging prohibition missing")

    vault_policy = doctrine.get("androidProofVault", {})
    require(vault_policy.get("sha256Integrity") is True, "ProofVault SHA-256 integrity contract missing")
    require(vault_policy.get("appPrivateStorage") is True, "ProofVault app-private storage contract missing")
    require(vault_policy.get("appLayerEncryptionSourceImplemented") is True, "ProofVault encryption source implementation missing")
    require(vault_policy.get("appLayerEncryptionRuntimeProven") is False, "ProofVault runtime encryption must not be claimed before device proof")
    require(vault_policy.get("algorithm") == "AES-256-GCM", "ProofVault AEAD algorithm drift")
    require(vault_policy.get("keyStore") == "AndroidKeyStore", "ProofVault key storage drift")
    require(vault_policy.get("strongBoxPreferredWhenSupported") is True, "StrongBox preference missing")
    require(vault_policy.get("plaintextCopyAtRestByDesign") is False, "plaintext proof copies at rest are forbidden")
    require(vault_policy.get("metadataEncryptedAtRestByDesign") is True, "proof metadata must be encrypted at rest")
    require(vault_policy.get("sensitiveProofsAllowedForEnterprise") is False, "sensitive proofs must remain blocked pending runtime proof")
    require(vault_policy.get("webViewVirtualHttpsOriginIsNetworkTls") is False, "WebView virtual HTTPS must not be called network TLS")

    proof = read(PROOF_VAULT)
    for phrase in (
        'MessageDigest.getInstance("SHA-256")',
        'Cipher.getInstance("AES/GCM/NoPadding")',
        'KeyStore.getInstance("AndroidKeyStore")',
        'KeyProperties.KEY_ALGORITHM_AES',
        '.setKeySize(AES_KEY_BITS)',
        '.setIsStrongBoxBacked(true)',
        'CipherOutputStream',
        'CipherInputStream',
        'File(context.filesDir, "luhm-proof-vault")',
        'ORIGIN = "https://appassets.androidplatform.net"',
        'plaintextAtRest", false',
    ):
        require(phrase in proof, f"ProofVault crypto source missing: {phrase}")
    require('val publicDir = File(rootDir, "public")' not in proof, "plaintext public ProofVault directory must be removed")

    webview = read(WEBVIEW)
    require("proofVault.openWebResource(path)" in webview, "WebView must stream decrypted proof resources from encrypted vault")
    require("InternalStoragePathHandler(host, proofVault.publicDir)" not in webview, "WebView must not serve plaintext proof directory")
    require('blockNetworkLoads = true' in webview, "WebGlass network block drift")
    require('mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW' in webview, "WebGlass mixed-content block drift")

    integrity = doctrine.get("integrityVsEncryption", {})
    require(integrity.get("sha256") == "integrity-not-encryption", "SHA-256 must not be classified as encryption")
    require(integrity.get("apkSignature") == "authenticity-and-integrity-not-encryption", "APK signature classification drift")

    auth = doctrine.get("authentication", {})
    require(auth.get("currentMcpTools") == "anonymous-read-only", "current MCP auth posture drift")
    require(auth.get("oauthImplemented") is False, "OAuth must not be claimed implemented")
    require(auth.get("privateOrWriteToolsBlockedUntilOAuth21") is True, "private/write OAuth gate missing")

    mcp_doctrine = load(MCP_DOCTRINE)
    require(mcp_doctrine.get("cryptographyDoctrine") == "doctrine/ENTERPRISE_CRYPTO_V1.json", "MCP crypto-doctrine binding missing")
    require(mcp_doctrine.get("transport", {}).get("publicTlsPreferredCa") == "Let's Encrypt", "MCP Let's Encrypt preference drift")

    plugin = load(PLUGIN_MCP)
    remote = plugin.get("mcpServers", {}).get("luhm", {})
    require(remote.get("url") == "https://mcp.eggiebagelface.art/mcp", "remote MCP must use canonical HTTPS FQDN")
    require("http://mcp.eggiebagelface.art" not in read(PLUGIN_MCP), "public cleartext MCP URL forbidden")

    render = read(RENDER)
    for phrase in (
        "mcp.eggiebagelface.art",
        "healthCheckPath: /healthz",
        "OPENAI_APPS_CHALLENGE",
        "sync: false",
        "python tools/enterpriseCryptoAudit.py",
    ):
        require(phrase in render, f"Render crypto hardening missing: {phrase}")

    server = read(SERVER)
    for phrase in (
        'host="0.0.0.0"',
        'streamable_http_path="/mcp"',
        "stateless_http=True",
        "enable_dns_rebinding_protection=True",
        "LOCAL_HOST = \"127.0.0.1\"",
    ):
        require(phrase in server, f"MCP transport hardening missing: {phrase}")

    security = read(SECURITY).lower()
    for phrase in (
        "private keys",
        "oauth tokens",
        "keystores",
        "do not log secrets",
        "render-managed tls",
        "let's encrypt",
        "google trust services",
        "aes-256-gcm",
        "android keystore",
    ):
        require(phrase in security, f"SECURITY.md crypto boundary missing: {phrase}")

    truth = load(SOURCE_TRUTH)
    require(truth.get("unknown_is_not_green") is True, "UNKNOWN != GREEN source law drift")
    require(truth.get("android", {}).get("internetPermission") is False, "game APK network boundary drift")
    require(truth.get("android", {}).get("production_signer") is False, "production signer must not be claimed before evidence")

    supply = load(SUPPLY_CHAIN)
    require(supply.get("provenance", {}).get("bind_apk_sha256") is True, "APK hash provenance missing")
    require(supply.get("security", {}).get("signing_secret_recorded") is False, "signing secret must never enter provenance")

    result = {
        "status": "GREEN_STATIC_SOURCE",
        "schema": doctrine["schema"],
        "fqdn": ingress["fqdn"],
        "preferredCA": ingress["preferredCertificateAuthority"],
        "approvedCAs": approved,
        "strictLetsEncryptOnly": False,
        "liveCertificateEvidence": "PENDING_EXTERNAL",
        "proofVaultConfidentiality": "SOURCE_IMPLEMENTED_DEVICE_RUNTIME_PENDING",
        "oauthPrivateWrite": "BLOCKED_NOT_IMPLEMENTED",
    }
    print("LUHM_ENTERPRISE_CRYPTO_STATIC_GREEN", json.dumps(result, sort_keys=True))
    return result


def live_audit() -> dict:
    doctrine = load(DOCTRINE)
    ingress = doctrine["publicIngress"]
    host = ingress["fqdn"]
    approved = ingress["approvedCertificateAuthorities"]
    hard_fail_days = int(ingress["certificateExpiryHardFailDays"])

    context = ssl.create_default_context()
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    with socket.create_connection((host, 443), timeout=10) as raw:
        with context.wrap_socket(raw, server_hostname=host) as tls:
            cert = tls.getpeercert()
            protocol = tls.version() or "UNKNOWN"

    require(protocol in {"TLSv1.2", "TLSv1.3"}, f"unexpected TLS protocol: {protocol}")
    issuer = flatten_name(cert.get("issuer", ()))
    subject = flatten_name(cert.get("subject", ()))
    require(issuer_allowed(issuer, approved), f"unapproved certificate issuer: {issuer}")

    sans = [value for kind, value in cert.get("subjectAltName", ()) if kind == "DNS"]
    require(host in sans, f"certificate SAN does not contain {host}")

    not_after_text = cert.get("notAfter")
    require(bool(not_after_text), "certificate missing notAfter")
    not_after = datetime.strptime(not_after_text, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
    days_remaining = (not_after - datetime.now(timezone.utc)).total_seconds() / 86400
    require(days_remaining >= hard_fail_days, f"certificate expires too soon: {days_remaining:.1f} days")

    request = urllib.request.Request(f"https://{host}/healthz", headers={"User-Agent": "LuHmEnterpriseCryptoAudit/1"})
    with urllib.request.urlopen(request, timeout=10, context=context) as response:
        status = response.status
        body = response.read(65536).decode("utf-8", errors="replace")
        hsts = response.headers.get("Strict-Transport-Security", "")
    require(status == 200, f"healthz returned HTTP {status}")
    require('"status":"ok"' in body.replace(" ", "") or '"status": "ok"' in body, "healthz body not healthy")

    receipt = {
        "schema": "luhm-os.enterprise-crypto.live-receipt.v1",
        "status": "GREEN_LIVE_TLS",
        "fqdn": host,
        "tlsProtocol": protocol,
        "issuer": issuer,
        "subject": subject,
        "sans": sans,
        "notAfter": not_after.isoformat(),
        "daysRemaining": round(days_remaining, 2),
        "healthHttpStatus": status,
        "hstsPresent": bool(hsts),
        "hsts": hsts or "MISSING",
        "preferredCA": ingress["preferredCertificateAuthority"],
        "issuerApproved": True,
        "issuerIsPreferredLetsEncrypt": "let" in issuer.lower() and "encrypt" in issuer.lower(),
    }
    print("LUHM_ENTERPRISE_CRYPTO_LIVE", json.dumps(receipt, sort_keys=True))
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Verify the live public certificate and HTTPS health endpoint")
    args = parser.parse_args()
    static_audit()
    if args.live:
        live_audit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
