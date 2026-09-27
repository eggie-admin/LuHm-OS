#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAW = "AI proposes. Policy authorizes. CI proves. Human promotes."
ROLES = {"Lum", "Kiri", "Tetsu", "Kaji", "Momo", "Shiori", "DrNao", "Kugi", "Fumi", "Sumi", "Koe", "Yume"}
PET_STATES = {"idle", "thinking", "working", "inspect", "waiting", "success", "alert", "sleep"}
PRODUCTION_MCP_FQDN = "mcp.eggiebagelface.art"


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def data(path: str) -> dict:
    value = json.loads(text(path))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def audit() -> None:
    truth = data("doctrine/SOURCE_OF_TRUTH.json")
    control = data("doctrine/ONI_MESH_CONTROL_PLANE_V2.json")
    deploy = data("doctrine/openAiLumOniDeployment-20260927.json")
    plugin = data("plugins/luhm-os/plugin.json")
    plugin_mcp = data("plugins/luhm-os/mcp.json")
    plugin_mcp_local = data("plugins/luhm-os/mcp.local.json")
    marketplace = data(".agents/plugins/marketplace.json")
    pet_manifest = data("assets/pet/oni/manifest.json")

    require(truth.get("source_law") == LAW, "source law drift")
    require(truth.get("unknown_is_not_green") is True, "UNKNOWN must not become GREEN")
    require(truth.get("publication_authority") is False and truth.get("promotion") is False, "source truth gained consequential authority")
    require(truth.get("android", {}).get("internetPermission") is False, "Android runtime network law drift")
    workflow_truth = truth.get("agentWorkflowCandidate", {})
    require(workflow_truth.get("branch") == "feature/oni-pet-activity-dock-v2-20260927", "agent workflow branch drift")
    require(workflow_truth.get("status") == "CANDIDATE_EXACT_HEAD_CI_REQUIRED", "agent workflow source-truth status drift")
    for key in ("publicationAuthority", "promotionAuthority", "mcpMutationAuthority", "proofImportGreenAuthority"):
        require(workflow_truth.get(key) is False, f"agent workflow authority drift: {key}")

    topology = control.get("topology", {})
    require(control.get("sourceLaw") == LAW, "control-plane source law drift")
    require(control.get("boss") == "Lum" and control.get("humanAuthority") == "Professor", "boss/human authority drift")
    require(topology.get("helperRecruitment") is False, "recursive recruitment enabled")
    require(topology.get("maxParallelSupportWorkers") == 3, "support parallelism drift")
    require(topology.get("maxMutableSourceLanesPerCandidate") == 1, "mutable source lane drift")
    require(set(control.get("roles", {})) == ROLES, "canonical role roster drift")

    require(set(pet_manifest.get("spriteSheet", {}).get("states", [])) == PET_STATES, "pet sprite-sheet state contract drift")
    require(pet_manifest.get("runtimeGreenRequiresExactAssetHashImportProof") is True, "pet runtime GREEN evidence law drift")
    require(pet_manifest.get("maxVisibleSupportWorkers") == 3, "pet activity dock support-worker drift")

    architecture = deploy.get("architecture", {})
    require(deploy.get("schema") == "luhm-os.openai-lum-oni-deployment.v2", "OpenAI/Oni doctrine not reconciled")
    require(set(architecture.get("roles", [])) == ROLES, "deployment roster incomplete")
    require(architecture.get("android_provider_secrets") is False, "provider secret entered Android")
    require(architecture.get("android_runtime_network_default") is False, "Android runtime network drift")
    private_mcp = deploy.get("privateMcp", {})
    require(private_mcp.get("mutationAuthority") is False and private_mcp.get("publicBindAllowed") is False, "private MCP authority/bind drift")
    require(private_mcp.get("bind") == "127.0.0.1:8788", "private MCP doctrine bind drift")
    require(private_mcp.get("directCloudTo127001Claim") is False, "direct cloud-to-loopback claim enabled")
    require(deploy.get("androidProofVault", {}).get("importVerdict") == "UNKNOWN_UNTIL_ADJUDICATED", "proof import authority drift")

    skill_paths = [
        "agents/lum/SKILL.md", "agents/kiriContextOni/SKILL.md", "agents/buildOnis/SKILL.md",
        "agents/momoResearchOni/SKILL.md", "agents/shioriCriticOni/SKILL.md", "agents/doctorOni/SKILL.md",
        "agents/kugiToolOni/SKILL.md", "agents/fumiSecretaryOni/SKILL.md", "agents/sumiAssetOni/SKILL.md",
        "agents/koeDictationOni/SKILL.md", "agents/yumeArtOni/SKILL.md", "agents/shared/ONI_PROTOCOL_V2.md",
        "plugins/luhm-os/skills/luhm-agent-workflow/SKILL.md",
    ]
    for path in skill_paths:
        require((ROOT / path).is_file(), f"missing canonical skill: {path}")

    portable_skill = text("plugins/luhm-os/skills/luhm-agent-workflow/SKILL.md")
    for phrase in (LAW, "Lum is the only conversational boss", "UNKNOWN", "Secure MCP Tunnel", "agents/*/SKILL.md"):
        require(phrase in portable_skill, f"portable skill missing doctrine: {phrase}")

    require(plugin.get("$schema") == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", "portable plugin schema drift")
    require(plugin.get("name") == "luhm-os", "plugin identity drift")
    capabilities = plugin.get("extensions", {}).get("com.openai", {}).get("interface", {}).get("capabilities", [])
    require(capabilities == ["Read"], "candidate plugin must remain read-only")

    production_mcp = plugin_mcp.get("mcpServers", {}).get("luhm", {})
    require(production_mcp.get("type") == "streamable-http", "production plugin MCP transport drift")
    require(production_mcp.get("url") == f"https://{PRODUCTION_MCP_FQDN}/mcp", "production plugin MCP FQDN drift")
    local_mcp = plugin_mcp_local.get("mcpServers", {}).get("luhm_local", {})
    require(local_mcp.get("type") == "streamable-http", "local plugin MCP transport drift")
    require(local_mcp.get("url") == "http://127.0.0.1:8788/mcp", "local plugin MCP must remain loopback-local")
    require(marketplace.get("plugins", [{}])[0].get("source", {}).get("path") == "./plugins/luhm-os", "repo marketplace path drift")

    runtime = text("scripts/agentMeshRuntime.py")
    router = text("tools/lumTaskRouter.py")
    for token in ('FUMI = Agent("Fumi"', "RECORDS_ONI", "MAX_PARALLEL = 3", "MAX_PARALLEL_BUILDS = 2"):
        require(token in runtime, f"agent mesh runtime missing: {token}")
    for token in ('"records": ["Lum", "Fumi"]', '"proof": ["Lum", "Sumi", "DrNao"]', '"schema": "luhm-os.task-route.v2"'):
        require(token in router, f"task router missing: {token}")

    mcp_server = text("host/mcp/luhmMcpServer.py")
    for token in (
        'LOCAL_HOST = "127.0.0.1"', "LOCAL_PORT = 8788", 'DEFAULT_PUBLIC_FQDN = "mcp.eggiebagelface.art"',
        'host="0.0.0.0"', "port=port", "stateless_http=True", "json_response=True",
        "TransportSecuritySettings", "enable_dns_rebinding_protection=True", "allowed_hosts=[fqdn, f\"{fqdn}:*\"]",
        "readOnlyHint=True", "destructiveHint=False", "openWorldHint=False",
        "luhm_status", "luhm_agent_roster", "luhm_route_task", "luhm_proof_contract",
        '"records", "proof"', "greenAuthority", '"/healthz"', '"/.well-known/openai-apps-challenge"',
    ):
        require(token in mcp_server, f"MCP source missing contract token: {token}")
    require('if profile == "production"' in mcp_server, "MCP public bind not production-gated")
    require("merge_pull_request" not in mcp_server and "production_sign" not in mcp_server, "MCP gained consequential executor")
    require(text("host/mcp/requirements.txt").strip() == "mcp==2.2.0", "MCP SDK pin drift")

    native = text("native/kaiwebview/kaiwebview/src/main/java/art/eggiebagelface/luhmos/kaiwebview/KAIWebView.kt")
    vault = text("native/kaiwebview/kaiwebview/src/main/java/art/eggiebagelface/luhmos/kaiwebview/ProofVault.kt")
    for token in ("Intent.ACTION_OPEN_DOCUMENT", "Intent.CATEGORY_OPENABLE", "FLAG_GRANT_PERSISTABLE_URI_PERMISSION", "takePersistableUriPermission", "ProofVault.WEB_PATH", "InternalStoragePathHandler", "blockNetworkLoads = true", '"proof.pick"', '"proof.list"', '"proof.pin"'):
        require(token in native, f"Android proof bridge missing: {token}")
    for token in ('MessageDigest.getInstance("SHA-256")', "MAX_PROOF_BYTES", "MAX_INLINE_TEXT_BYTES", '"UNKNOWN"', '"android-saf-local-copy"', "extractDocxBlocks", "DocumentBuilderFactory", "disallow-doctype-decl", "external-general-entities", "rawHtmlTrusted"):
        require(token in vault, f"proof vault missing structural control: {token}")
    require("OPENAI_API_KEY" not in native + vault, "provider credential reference entered APK source")
    require("127.0.0.1" not in native + vault and "localhost" not in native + vault, "Python/loopback control plane entered Android source")
    require("uri.toString()" not in vault, "raw SAF URI must not be serialized into proof metadata")
    require("innerHTML" not in vault and ".html(" not in vault, "proof vault must not generate raw HTML")

    host = text("host/openai/lumHost.py")
    for name in ROLES:
        require(name in host, f"OpenAI host instructions missing role: {name}")
    require(LAW in host, "OpenAI host instructions missing source law")

    secret_pattern = re.compile(r"(sk-proj-[A-Za-z0-9_-]{8,}|BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY|AIza[A-Za-z0-9_-]{20,})")
    guarded = [
        "host/mcp/luhmMcpServer.py", "plugins/luhm-os/plugin.json", "plugins/luhm-os/mcp.json",
        "plugins/luhm-os/mcp.local.json", "plugins/luhm-os/skills/luhm-agent-workflow/SKILL.md",
        "doctrine/openAiLumOniDeployment-20260927.json",
        "native/kaiwebview/kaiwebview/src/main/java/art/eggiebagelface/luhmos/kaiwebview/KAIWebView.kt",
        "native/kaiwebview/kaiwebview/src/main/java/art/eggiebagelface/luhmos/kaiwebview/ProofVault.kt",
        "render.yaml",
    ]
    for path in guarded:
        require(secret_pattern.search(text(path)) is None, f"secret-like material detected in {path}")

    print("LUHM_AGENT_WORKFLOW_GREEN")


if __name__ == "__main__":
    audit()
