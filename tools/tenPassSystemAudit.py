#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/system-audit/ten-pass.json"
LAW = "AI proposes. Policy authorizes. CI proves. Human promotes."


def txt(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def js(path: str) -> dict:
    value = json.loads(txt(path))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected object")
    return value


def has(path: str) -> bool:
    return (ROOT / path).is_file()


def result(n: int, name: str, checks: list[tuple[bool, str]], external: list[str] | None = None) -> dict:
    failures = [label for ok, label in checks if not ok]
    ext = external or []
    if failures:
        status = "RED"
    elif ext:
        status = "AMBER_EXTERNAL"
    else:
        status = "GREEN"
    return {"pass": n, "name": name, "status": status, "failures": failures, "externalGates": ext}


def audit() -> dict:
    truth = js("doctrine/SOURCE_OF_TRUTH.json")
    mesh = js("doctrine/ONI_MESH_CONTROL_PLANE_V2.json")
    deploy = js("doctrine/openAiLumOniDeployment-20260927.json")
    cloud = js("doctrine/fastApiCloudBoundary-20260927.json")
    cloud_policy = js("host/cloud/policy.json")
    preset = txt("export_presets.cfg")
    security = txt("SECURITY.md")
    gitignore = txt(".gitignore")
    vault = txt("native/kaiwebview/kaiwebview/src/main/java/art/eggiebagelface/luhmos/kaiwebview/ProofVault.kt")
    native = txt("native/kaiwebview/kaiwebview/src/main/java/art/eggiebagelface/luhmos/kaiwebview/KAIWebView.kt")
    mcp = txt("host/mcp/luhmMcpServer.py")
    host = txt("host/openai/lumHost.py")
    cloud_app = txt("host/cloud/main.py")

    passes: list[dict] = []
    passes.append(result(1, "source-truth-and-doctrine", [
        (truth.get("source_law") == LAW, "source law"),
        (truth.get("unknown_is_not_green") is True, "UNKNOWN is not GREEN"),
        (truth.get("publication_authority") is False and truth.get("promotion") is False, "no source self-promotion"),
        (truth.get("canonical_repository") == "eggie-admin/LuHm-OS", "canonical repository"),
        (truth.get("agentWorkflowCandidate", {}).get("branch") == "feature/oni-pet-activity-dock-v2-20260927", "active workflow branch"),
    ]))

    passes.append(result(2, "github-governance-and-entitlements", [
        ("production credentials" in security and ".env" in security, "security doctrine present"),
        ("*.keystore" in gitignore and ".env" in gitignore and "*.key" in gitignore, "secret files ignored"),
    ], ["server-side branch protection/ruleset must be verified through GitHub admin evidence"]))

    passes.append(result(3, "android-entitlements-and-package-boundary", [
        ('gradle_build/target_sdk="36"' in preset, "target SDK 36"),
        ('architectures/arm64-v8a=true' in preset and 'architectures/x86_64=false' in preset, "ARM64-only"),
        ('permissions/internet=false' in preset, "no Android Internet permission"),
        ('permissions/custom_permissions=PackedStringArray()' in preset, "no custom Android permission"),
        ('exclude_filter="host/**"' in preset, "host code excluded from APK"),
        (truth.get("android", {}).get("internetPermission") is False, "source truth Android offline"),
    ]))

    passes.append(result(4, "webview-proof-vault-and-content-security", [
        ("Intent.ACTION_OPEN_DOCUMENT" in native, "SAF picker"),
        ('MessageDigest.getInstance("SHA-256")' in vault, "SHA-256 vault identity"),
        ("disallow-doctype-decl" in vault and "external-general-entities" in vault, "XXE hardening"),
        ("blockNetworkLoads = true" in native, "WebView network block"),
        ("innerHTML" not in vault and ".html(" not in vault, "no raw HTML generation"),
        ("uri.toString()" not in vault, "no raw SAF URI serialization"),
    ]))

    topo = mesh.get("topology", {})
    passes.append(result(5, "lum-oni-agent-control-plane", [
        (mesh.get("boss") == "Lum", "Lum sole boss"),
        (len(mesh.get("roles", {})) == 12, "12 canonical roles"),
        (topo.get("maxParallelSupportWorkers") == 3, "support parallelism 3"),
        (deploy.get("architecture", {}).get("parallelism_max_builds") == 2, "build parallelism 2"),
        (topo.get("helperRecruitment") is False, "no helper recursion"),
        (topo.get("maxMutableSourceLanesPerCandidate") == 1, "one mutable source lane"),
        (has("agents/kugiToolOni/SKILL.md"), "Kugi skill present"),
    ]))

    passes.append(result(6, "host-openai-mcp-secret-boundary", [
        ('host="127.0.0.1"' in mcp and 'port=8788' in mcp, "MCP loopback"),
        ('host="0.0.0.0"' not in mcp, "no public MCP bind"),
        ("OPENAI_API_KEY" in host and "OPENAI_API_KEY" not in native + vault, "OpenAI credential host-only"),
        (deploy.get("privateMcp", {}).get("mutationAuthority") is False, "MCP read-only authority"),
        (deploy.get("architecture", {}).get("android_provider_secrets") is False, "no Android provider secrets"),
        ("store\":False" in host.replace(" ", "") or '"store":False' in host.replace(" ", ""), "Responses API store disabled"),
    ], ["live OpenAI probe receipt", "private ChatGPT MCP secure-tunnel/approved-HTTPS receipt"]))

    ent = cloud.get("entitlements", {})
    passes.append(result(7, "fastapi-cloud-https-bridge", [
        (cloud.get("status") == "READINESS_ONLY_NOT_DEPLOYED", "cloud readiness not falsely deployed"),
        (set(ent.get("allowed", [])) == {"health:read", "status:read", "capabilities:read"}, "cloud read-only entitlements"),
        (ent.get("mutationAuthority") is False and ent.get("promotionAuthority") is False, "cloud no mutation/promotion"),
        ("secrets.compare_digest" in cloud_app, "constant-time bearer validation"),
        ("@app.post" not in cloud_app and "@app.delete" not in cloud_app and "@app.patch" not in cloud_app and "@app.put" not in cloud_app, "cloud GET-only"),
        ("docs_url=None" in cloud_app and "openapi_url=None" in cloud_app, "cloud docs disabled"),
        (cloud_policy.get("providerSecretsAccepted") is False, "cloud does not accept provider secret payloads"),
    ], ["FastAPI Cloud linked app/auth receipt", "terminal-success deployment receipt", "runtime log/HTTPS auth smoke receipt"]))

    critical_workflows = [
        ".github/workflows/luhm-agent-workflow-audit.yml",
        ".github/workflows/oni-dual-build-audit.yml",
        ".github/workflows/proof-viewer-audit.yml",
        ".github/workflows/oni-pet-activity-audit.yml",
    ]
    existing = [p for p in critical_workflows if has(p)]
    wf_text = "\n".join(txt(p) for p in existing)
    passes.append(result(8, "ci-supply-chain-and-fast-path", [
        (len(existing) == len(critical_workflows), "critical workflows present"),
        ("actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09" in txt(".github/workflows/luhm-agent-workflow-audit.yml"), "agent checkout SHA-pinned"),
        ("cancel-in-progress: true" in txt(".github/workflows/luhm-agent-workflow-audit.yml"), "agent audit cancels superseded work"),
        ("timeout-minutes:" in txt(".github/workflows/luhm-agent-workflow-audit.yml"), "agent audit bounded timeout"),
        ("permissions:\n  contents: read" in txt(".github/workflows/luhm-agent-workflow-audit.yml"), "agent workflow least privilege"),
        ("Lum Mesh Fast Preflight" in txt(".github/workflows/oni-dual-build-audit.yml"), "preflight before dual build"),
    ]))

    candidate_gate = txt("tools/candidateGate.py")
    passes.append(result(9, "artifact-provenance-release-and-recovery", [
        ("apksigner" in candidate_gate, "APK signature receipt"),
        ("zipalign -c -P 16 -v 4" in candidate_gate, "16K zip alignment receipt"),
        ("ELF LOAD alignment below 16KB" in candidate_gate, "16K ELF alignment gate"),
        ("apkSha256" in candidate_gate and "certificateSha256" in candidate_gate, "APK and certificate digests"),
    ], ["persistent Crown-owned signer/recovery", "release SBOM/provenance binding", "backup/restore drill"]))

    fast = js("doctrine/TOTAL_SYSTEM_AUDIT_V1.json").get("fastPath", [])
    passes.append(result(10, "performance-and-operational-readiness", [
        ("run static ten-pass preflight" in fast, "static-first fast path"),
        ("run Tetsu and Kaji only after preflight" in fast, "defer heavy dual build"),
        (cloud.get("runtime", {}).get("stateless") is True and cloud.get("runtime", {}).get("databaseRequired") is False, "stateless cloud bridge/no DB"),
        (deploy.get("architecture", {}).get("parallelism_max_builds") == 2, "two build lanes only"),
    ], ["physical Samsung runtime smoke", "latency/error/cost benchmark receipt"]))

    code_red = [p for p in passes if p["status"] == "RED"]
    external = [p for p in passes if p["status"] == "AMBER_EXTERNAL"]
    overall = "RED" if code_red else ("AMBER_EXTERNAL_GATES" if external else "GREEN")
    report = {
        "schema": "luhm-os.total-system-audit-result.v1",
        "overall": overall,
        "sourceLaw": LAW,
        "passes": passes,
        "codeRedCount": len(code_red),
        "externalGatePassCount": len(external),
        "promotionAuthority": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    report = audit()
    raise SystemExit(1 if report["overall"] == "RED" else 0)
