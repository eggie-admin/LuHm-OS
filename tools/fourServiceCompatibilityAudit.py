#!/usr/bin/env python3
"""Fail-closed LuHm four-service authority, namespace and sync contract audit."""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine/fourServiceCompatibilityCanonV1.json"
READ = lambda p: json.loads((ROOT / p).read_text(encoding="utf-8"))
IDENTITY = re.compile(r"^[a-z][A-Za-z0-9]*$")
SHA = re.compile(r"^[0-9a-f]{40}$")
PROVIDERS = ("openAi", "github", "googleAi", "cloudflare")
FORWARD = {
    "publicMcp": "mcp.eggiebagelface.art",
    "privateSystem": "system.eggiebagelface.art",
    "staticAssets": "assets.eggiebagelface.art",
    "signedArt": "art.eggiebagelface.art",
    "legacyAi": "ai.eggiebagelface.art",
}


def audit(data, source, network, cloudflare, quarantine) -> list[str]:
    errors = []
    def check(ok, issue):
        if not ok:
            errors.append(issue)
    check(data.get("schema") == "luhmOs.fourServiceCompatibilityCanon.v1", "SCHEMA_DRIFT")
    check(data.get("status") == "SOURCE_CANDIDATE_ONLY", "FALSE_PRODUCTION_GREEN")
    check(data.get("authority") == "Professor", "OWNER_DRIFT")
    check(data.get("sourceLaw") == "AI proposes. Policy authorizes. CI proves. Human promotes.", "SOURCE_LAW_DRIFT")
    check(data.get("canonicalRepository") == "eggie-admin/LuHm-OS", "GITHUB_CANON_DRIFT")
    check(bool(SHA.fullmatch(data.get("sourceRefAtProposal", ""))), "SOURCE_REF_MUST_BE_EXACT_SHA")
    check(data.get("inherits") == [
        "doctrine/currentSourceTruthV3.json",
        "doctrine/cloudflareLumOrchestrationV1.json",
        "doctrine/networkSpineV1.json",
        "doctrine/cloudflareAirTrafficControllerV1.json",
        "doctrine/stablePluginUpdateSpineV1.json",
        "doctrine/aiTaskManifestV2.template.json",
        "doctrine/companyWideOperationalQuarantineV1.json",
        "doctrine/storageTopologyV1.json",
    ], "SOURCE_LINKS_DRIFT")
    providers = data.get("providerLanes", [])
    check(isinstance(providers, list) and [p.get("id") for p in providers] == list(PROVIDERS), "FOUR_PROVIDERS_CHANGED")
    if isinstance(providers, list):
        check(all(IDENTITY.fullmatch(p.get("id", "")) for p in providers), "NON_CAMELHUMP_PROVIDER_ID")
        lanes = {p["id"]: p for p in providers if p.get("id") in PROVIDERS}
        if len(lanes) == 4:
            check(lanes["openAi"]["role"] == "frontEndAndConversation"
                  and lanes["github"]["role"] == "sourceCompatibilityCiAndReleaseReceipts"
                  and lanes["googleAi"]["role"] == "optionalWorkhorseForScopedTasks"
                  and lanes["cloudflare"]["role"] == "managedDnsAndTrafficController", "PROVIDER_ROLE_DRIFT")
            check(lanes["googleAi"]["runtime"] == "NOT_PROVEN_CONNECTED_OR_EXECUTED", "GOOGLE_AI_FALSE_LIVE")
            check(lanes["cloudflare"]["runtime"] == "ZONE_API_NOT_CONNECTED", "CLOUDFLARE_FALSE_LIVE")
    storage = data.get("storage", {})
    check(storage.get("syncCandidatePr") == 530 and storage.get("defaultArmed") is False,
          "RCLONE_PENDING_SOURCE_LAW")
    check(storage.get("chatGptLibraryDirectRsyncSupported") is False
          and storage.get("chatGptLibraryBulkFilesystemApiProven") is False,
          "CHATGPT_LIBRARY_RSYNC_FABRICATION")
    check(storage.get("privateAssetRefsInPublicGithub") is False
          and storage.get("github") == "PUBLIC_SOURCE_SCHEMAS_AND_SANITIZED_HASH_RECEIPTS_ONLY",
          "PRIVATE_ASSET_LEAK")
    check(all(x in storage.get("rsyncRequires", []) for x in (
          "restrictedOAuth", "approvedFolder", "dryRun", "checksum", "restoreDrill")), "UNSAFE_RSYNC_PLAN")
    plugin = data.get("plugin", {})
    check(plugin.get("shape") == "skillsPlusMcpServerPlusOptionalMcpAppsUi"
          and plugin.get("privateSiteBinding") == "PRESERVE_ORIGINAL", "PLUGIN_REPLACEMENT")
    check(plugin.get("skillLocation") == "plugins/luhm-os/skills/luhm-four-service-compatibility/SKILL.md",
          "SKILL_PATH_DRIFT")
    check(plugin.get("reasoningBoundary", {}).get("persistPrivateChainOfThought") is False
          and plugin.get("reasoningBoundary", {}).get("providerOutputUntrusted") is True,
          "HIDDEN_REASONING_EXPOSURE")
    check(plugin.get("noIndependentWorkersInCurrentQuarantine") is True
          and plugin.get("neverTreatSkillsAsExecutor") is True
          and quarantine.get("state") == "QUARANTINED"
          and quarantine.get("activeTaskWorkersAllowed") is False, "WORKER_QUARANTINE_BYPASS")
    fqdn = data.get("fqdn", {})
    forward = fqdn.get("forward", [])
    check(fqdn.get("zone") == "eggiebagelface.art"
          and fqdn.get("expectedAuthoritativeProvider") == "cloudflare"
          and fqdn.get("publicMcpOrigin") == "luhm-os-harness-green.onrender.com", "FQDN_ZONE_DRIFT")
    check(isinstance(forward, list) and len(forward) == 5
          and {r.get("id"): r.get("fqdn") for r in forward} == FORWARD, "FQDN_IDENTITY_DRIFT")
    check(all(IDENTITY.fullmatch(r.get("id", "")) for r in forward), "NON_CAMELHUMP_FQDN_LANE")
    check(all(r.get("allowProxyBeforeStreamProof") is False for r in forward), "UNAPPROVED_PROXY_SWITCH")
    reversed_labels = fqdn.get("reversedLabelNamespace", {})
    check(reversed_labels.get("forward") == network["identityChain"]["reverseFqdnNamespace"]["forwardExample"]
          and reversed_labels.get("reverse") == network["identityChain"]["reverseFqdnNamespace"]["reverseExample"]
          and all(reversed_labels.get(k) is False for k in ("isDnsRecord", "isPtrRecord", "mayGrantAuthority")),
          "REVERSE_NAMESPACE_NOT_PTR")
    ptr = fqdn.get("ptr", {})
    check(ptr.get("sharedRenderCloudflareIpsOwnedByLuHm") is False
          and ptr.get("queryByDefault") is False
          and ptr.get("mutationAllowed") is False, "SHARED_IP_PTR_WRONG")
    check(fqdn.get("actualNs") == "PENDING_FRESH_DNS_PROBE"
          and fqdn.get("actualDns") == "PENDING_FRESH_DNS_PROBE", "DNS_SOURCE_ASSERTS_LIVE")
    check(fqdn.get("directMcpUntilProven") == cloudflare["trafficLanes"]["publicMcp"]["origin"] + "/mcp",
          "MCP_ORIGIN_REPLACEMENT")
    check(source.get("crownStatus") == "STOP" and source.get("status") == "AMBER_PROPOSED_SEAL_OF_TRUTH",
          "SOURCE_TRUTH_FALSE_GREEN")
    validation = data.get("validation", {})
    drift = validation.get("runtimeSourceDrift", {})
    check(drift.get("status") == "SOURCE_DEPLOYMENT_DRIFT_OBSERVED_20261107"
          and bool(SHA.fullmatch(drift.get("renderMcpDeployedSha", ""))), "DEPLOYMENT_DRIFT_HIDDEN")
    changes = data.get("safeMutations", {})
    check(all(changes.get(k) is False for k in (
        "privateSiteEditorUsed", "productionDeployment", "dnsChanges",
        "signingChanges", "newAgentActivation", "liveProviderSpend"))
        and changes.get("crownStatus") == "STOP", "UNAUTHORIZED_PRODUCTION_MUTATION")
    return errors


def main() -> int:
    data = READ("doctrine/fourServiceCompatibilityCanonV1.json")
    problems = audit(data, READ("doctrine/currentSourceTruthV3.json"),
                     READ("doctrine/networkSpineV1.json"),
                     READ("doctrine/cloudflareLumOrchestrationV1.json"),
                     READ("doctrine/companyWideOperationalQuarantineV1.json"))
    result = {
        "schema": "luhmOs.fourServiceCompatibilityAudit.v1",
        "status": "GREEN_SOURCE_ONLY" if not problems else "RED_SOURCE",
        "errors": problems,
        "liveGoogleWorkers": "UNVERIFIED", "liveCloudflareDns": "UNVERIFIED",
        "chatGptLibraryRsync": "NOT_SUPPORTED_AS_FILESYSTEM",
        "siteBackendChanged": False, "crownStatus": "STOP",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return int(bool(problems))


if __name__ == "__main__":
    raise SystemExit(main())
