#!/usr/bin/env python3
"""Check shared source contracts only; never probe or mutate infrastructure."""
import argparse
import json
from pathlib import Path


def audit(rootPath):
    errorList = []

    def need(conditionValue, messageValue):
        if not conditionValue:
            errorList.append(messageValue)

    def readDoc(pathValue):
        value = json.loads((rootPath / pathValue).read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("contract must be an object")
        return value

    try:
        spineDoc = readDoc("doctrine/networkSpineV1.json")
        cloudDoc = readDoc("doctrine/cloudflareAirTrafficControllerV1.json")
        pkiDoc = readDoc("doctrine/belldandyPkiCorporateSecretaryV1.json")
        truthDoc = readDoc("doctrine/currentSourceTruthV3.json")
        repoDoc = readDoc("doctrine/activeRepositorySetV1.json")
        need(spineDoc["canonicalRepository"] == repoDoc["canonicalPrimary"] == "eggie-admin/LuHm-OS", "canonical source drift")
        need(spineDoc["dnsRole"] == "nameResolution" and spineDoc["proxyRole"] == "requestForwarding", "DNS and proxy responsibilities conflated")
        need(spineDoc["repositoryAlignment"]["strategy"] == "selectiveReviewedTransplant", "repository alignment drift")
        need(spineDoc["repositoryAlignment"]["symlinksProveAlignment"] is False, "symlink treated as source alignment proof")
        need(spineDoc["repositoryAlignment"]["unrelatedHistoryMerge"] is False, "unrelated histories silently merged")
        for nameValue in ("snapshotsBeforeStructuralChanges", "exactDonorCommitRequired", "lockfilesRequiredForNpm"):
            need(spineDoc["repositoryAlignment"][nameValue] is True, "alignment requirement missing: " + nameValue)
        need(spineDoc["runtimeState"] == "UNVERIFIED" and spineDoc["runtimeProofFromStaticCi"] is False, "static CI promoted to live infrastructure proof")
        need(spineDoc["hostIdentity"]["runtimeReceiptRequired"] is True, "host identity inferred from workspace label")
        need(spineDoc["tls"]["edgeMode"] == "FullStrict", "strict edge TLS drift")
        need(spineDoc["tls"]["tunnelOriginValidation"] == "independentCloudflaredVerification", "tunnel origin TLS conflated with edge mode")
        need(spineDoc["tls"]["noTlsVerify"] is False, "tunnel certificate verification disabled")
        chainDoc = spineDoc["identityChain"]
        need(chainDoc["sequence"] == ["forwardFqdn", "reverseFqdnNamespace", "authoritativeNameservers", "reverseDnsPtrWhenApplicable", "proxyLane", "canonicalRepository"], "identity chain order drift")
        forwardDoc = chainDoc["forwardFqdn"]
        need(forwardDoc["publicMcp"] == "mcp.eggiebagelface.art" and forwardDoc["systemPortal"] == "system.eggiebagelface.art" and forwardDoc["staticAssets"] == "assets.eggiebagelface.art", "forward FQDN identity drift")
        need(forwardDoc["status"] == "UNVERIFIED" and forwardDoc["recordsAreNotProofOfLiveTraffic"] is True, "forward DNS promoted without runtime proof")
        revDoc = chainDoc["reverseFqdnNamespace"]
        need(revDoc["forwardExample"] == "mcp.eggiebagelface.art" and revDoc["reverseExample"] == "art.eggiebagelface.mcp", "reverse namespace identity drift")
        for keyValue in ("isDnsRecord", "isPtrRecord", "wildcardTldIsPublicDns", "mayGrantNetworkOrExecutionAuthority"):
            need(revDoc[keyValue] is False, "reverse namespace treated as DNS or authority: " + keyValue)
        nsDoc = chainDoc["authoritativeNameservers"]
        need(nsDoc["expectedProvider"] == "cloudflare" and nsDoc["delegationState"] == "CLOUDFLARE_EXISTING_AUTHORITY_OPERATOR_AND_HISTORICAL_PROOF", "established Cloudflare DNS authority was erased or replaced")
        need(nsDoc.get("proofScope") == "EXISTING_PROVIDER_CONFIRMED; CURRENT_ASSIGNED_NS_HOSTS_NOT_REMEASURED", "historical provider evidence overstated as current NS query")
        need(nsDoc.get("noRegistrarOrAuthoritativeNameserverServiceImplementation") is True and nsDoc.get("noDelegationChangePlanned") is True and nsDoc.get("confirmOnlyOnRelevantIncidentOrApprovedDnsChange") is True, "new registrar or nameserver project invented")
        need(all(nsDoc.get(k) is False for k in ("confirmParentZoneDelegation", "confirmAuthoritativeNsAndSoa", "checkDnssecChainWhenEnabled")), "established Cloudflare DNS re-onboarding wrongly required")
        for keyValue in ("nameserverNamesMustBeObservedNotGuessed", "sourceExampleMayNotClaimLiveAuthority"):
            need(nsDoc[keyValue] is True, "nameserver proof boundary missing: " + keyValue)
        need(nsDoc["mayChangeRegistrarDelegation"] is False, "source grants registrar mutation")
        ptrDoc = chainDoc["reverseDnsPtrWhenApplicable"]
        need(ptrDoc["ptrState"] == "UNVERIFIED" and ptrDoc["requiresIpPrefixAuthority"] is True, "PTR authority proof drift")
        need(ptrDoc["isReverseFqdnNamespace"] is False and ptrDoc["renderSharedIpIsOwnedByProject"] is False, "reverse DNS confused with namespace or borrowed IP")
        need(ptrDoc["optionalForPublicMcpTlsReadiness"] is True and ptrDoc["mayMutatePtr"] is False, "PTR overreach or unsafe mutation")
        routeDoc = chainDoc["proxyLane"]
        need(routeDoc["mcp"] == "dnsOnlyDirectRenderManagedTlsUntilStreamingProof", "direct MCP rerouted without streaming proof")
        need(routeDoc["systemPortal"] == "optionalCloudflareTunnelWithBoundedOrigin" and routeDoc["staticAssets"] == "sameOriginUntilApprovedCdnProof", "proxy lane collision")
        need(routeDoc["trustUnverifiedForwardedHeaders"] is False and routeDoc["mayActivateFromSourceOnly"] is False, "proxy source grants live traffic control")
        canonDoc = chainDoc["canonicalRepository"]
        need(canonDoc["source"] == repoDoc["canonicalPrimary"] and canonDoc["registryRef"] == "doctrine/activeRepositorySetV1.json", "repo identity drift")
        need(canonDoc["migration"] == "selectiveReviewedTransplant" and canonDoc["artMappingDraftPr"] == 216, "repo mapping lineage drift")
        remoteIdentityDoc = canonDoc["remoteSourceIdentity"]
        need(remoteIdentityDoc["identity"] == "art.eggiebagelface.mcp.LuHm-OS" and remoteIdentityDoc["reverseNamespace"] == "art.eggiebagelface.mcp" and remoteIdentityDoc["repository"] == "eggie-admin/LuHm-OS", "remote repository identity drift")
        need(remoteIdentityDoc["forwardHttpsFqdn"] == forwardDoc["publicMcp"] and remoteIdentityDoc["publicHttpsUsesForwardFqdn"] is True, "public HTTPS route conflated with reverse identity")
        need(remoteIdentityDoc["wildcardSortingPattern"] == "art.eggiebagelface.*" and remoteIdentityDoc["wildcardSortingPatternIsLiteralDns"] is False, "sorting pattern presented as live wildcard DNS")
        need(remoteIdentityDoc["isDnsRecord"] is False and remoteIdentityDoc["isPtrRecord"] is False, "remote source identity treated as DNS or PTR")
        need(remoteIdentityDoc["route"] == "CloudflareManagedDns -> RenderManagedTls -> LuHmMcp" and remoteIdentityDoc["cloudflareProxy"] == "disabledUntilSeparateStreamingProof", "MCP proxy route changed without proof")
        pullDoc = remoteIdentityDoc["directoryPullLocator"]
        need(pullDoc["provider"] == "github" and pullDoc["repository"] == repoDoc["canonicalPrimary"], "remote pull provider or repository drift")
        need(pullDoc["components"] == ["repository", "ref", "path", "commitSha"] and pullDoc["requiresExactRepositoryRefPathAndCommitSha"] is True, "precise GitHub pull locator is incomplete")
        need(pullDoc["reverseNamespaceIsLookupSortingKeyOnly"] is True and pullDoc["maySubstituteForGitHubRefPathOrCommit"] is False, "reverse namespace substituted for a GitHub pull locator")
        dnsDoc = remoteIdentityDoc["forwardDns"]
        need(dnsDoc["fqdn"] == forwardDoc["publicMcp"] and dnsDoc["httpsPath"] == "/mcp", "forward HTTPS host/path drift")
        need(dnsDoc["recordType"] == "CNAME" and dnsDoc["recordName"] == "mcp" and dnsDoc["targetCandidate"] == "luhm-os-harness-green.onrender.com", "Render custom-host CNAME candidate drift")
        need(dnsDoc["proxy"] == "DNS_ONLY" and dnsDoc["aRecord"] == "notUsedForThisRenderSubdomain" and dnsDoc["aaaaRecord"] == "mustBeAbsent", "Render DNS record contract drift")
        need(dnsDoc["runtimeState"] == "UNVERIFIED_UNTIL_RENDER_DOMAIN_DNS_TLS_AND_MCP_PROBES_PASS" and dnsDoc["currentPublishedEndpoint"] == "https://luhm-os-harness-green.onrender.com/mcp", "candidate FQDN promoted or endpoint pointer drift")
        need(canonDoc["donorHistoryAutoMerge"] is False and canonDoc["githubRepositoryIsDnsNameserver"] is False and canonDoc["dnsDoesNotServeRepositorySource"] is True, "GitHub/repo authority confused with DNS")
        need(chainDoc["runtimeState"] == "UNVERIFIED" and chainDoc["liveMutation"] is False, "identity spine claimed live authority")
        policyDoc = spineDoc["reverseProxy"]
        for nameValue in ("allowForwardProxy", "trustClientForwardedHeaders", "serveRepositoryRoot", "exposeShellOrSqlAdmin", "symlinksGrantAccess"):
            need(policyDoc[nameValue] is False, "unsafe proxy policy: " + nameValue)
        need(policyDoc["unknownHostAction"] == "reject", "unknown hostname allowed")
        need(policyDoc["backendBinding"] == "loopbackOrUnixSocket", "unbounded backend binding")
        need(policyDoc["rewriteBackendRedirects"] is True, "backend redirect policy missing")
        need(policyDoc["cacheAuthenticatedOrMcpTraffic"] is False, "authenticated or MCP traffic caching allowed")
        need(policyDoc["symlinkResolution"] == "resolveWithinApprovedServiceRoot", "service symlink boundary missing")
        need(spineDoc["hostIdentity"]["persistentOriginDistinctFromEphemeralWorkspace"] is True, "ephemeral workspace treated as persistent origin")
        need(spineDoc["tls"]["privateKeyCustody"] == "persistentOriginOrApprovedSecretStore", "TLS private-key custody drift")
        need(spineDoc["tls"]["filesystemProofDoesNotProveCertificateOrRenewal"] is True, "filesystem proof expanded to TLS readiness")
        need(set(spineDoc["liveMutation"]) == {"dns", "tunnel", "proxy", "certificate", "identityPolicy"} and all(value is False for value in spineDoc["liveMutation"].values()), "source contract grants live mutation")
        need(spineDoc["cabinet"] == {"recordsOwner": "belldandySecretary", "evidenceOwner": "urdDoctorGoddess", "reconciliationOwner": "lum"}, "cabinet role drift")
        refValue = "doctrine/networkSpineV1.json"
        need(cloudDoc["networkSpineContract"] == pkiDoc["networkSpineContract"] == truthDoc["networkLayer"]["spineContract"] == refValue, "shared spine pointer mismatch")
        need(cloudDoc["recordsDesk"]["owner"] == pkiDoc["owner"] == "belldandySecretary", "records owner mismatch")
        need(cloudDoc["perimeterModel"]["evidenceDiagnosis"] == "urdDoctorGoddess", "Urd evidence role mismatch")
        for laneId, hostnameValue, hostKey in (("systemPortal", "system.eggiebagelface.art", "publicHostnameCandidate"), ("publicChatPluginMcp", "mcp.eggiebagelface.art", "customFqdnCandidate"), ("staticAssets", "assets.eggiebagelface.art", "assetFqdnCandidate")):
            laneDoc = spineDoc["lanes"][laneId]
            need(laneDoc["fqdn"] == hostnameValue == cloudDoc["lanes"][laneId][hostKey], "FQDN drift: " + laneId)
            need(laneDoc["activationState"] == "UNVERIFIED", "candidate hostname presented as active: " + laneId)
        portalDoc = spineDoc["lanes"]["systemPortal"]
        need(portalDoc["requestPath"] == ["client", "cloudflareEdge", "cloudflared", "hostReverseProxy", "boundedService"], "portal request direction drift")
        need(portalDoc["connectorDirection"] == "originInitiatesOutbound", "tunnel connection direction drift")
        need(cloudDoc["lanes"]["systemPortal"]["mode"] == "optionalCloudflareTunnel", "portal mode drift")
        mcpDoc = cloudDoc["lanes"]["publicChatPluginMcp"]
        need(mcpDoc["tunnelForThisLane"] is False and mcpDoc["bootstrapRecord"]["proxied"] is False, "direct Render bootstrap changed to proxy/tunnel")
        need(mcpDoc["tlsTermination"] == "RenderManagedTls", "Render certificate responsibility drift")
        need(spineDoc["lanes"]["publicChatPluginMcp"]["requestPath"] == ["client", "renderManagedTls", "luhmMcp"], "MCP direct request path drift")
        need(cloudDoc["tlsLaw"]["preferredProxyEncryptionMode"] == "FullStrict", "Cloudflare TLS mismatch")
        need(pkiDoc["githubForgeBoundary"]["repoStoresPrivatePem"] is False, "private-key custody drift")
        expectedChecks = {"hostIdentity", "dnsTarget", "tlsHostnameAndChain", "originTlsValidation", "proxyConfigSyntax", "unknownHostRejected", "forwardedHeaderSpoofRejected", "backendRedirects", "authBoundary", "httpsHealth", "mcpInitializationWhenApplicable", "certificateRenewalWhenApplicable", "rollbackRef"}
        need(set(spineDoc["runtimeEvidenceRequired"]) == expectedChecks, "runtime proof requirements drift")
        for pathValue in ("agents/belldandyQualityOni/SKILL.md", "agents/urdMutationOni/SKILL.md"):
            skillValue = (rootPath / pathValue).read_text(encoding="utf-8")
            need(refValue in skillValue and "networkSpineAudit.py" in skillValue, "agent not bound to spine gate: " + pathValue)
    except (OSError, ValueError, KeyError, TypeError) as errorValue:
        errorList.append("contractReadOrShapeError:" + type(errorValue).__name__)
    return {"schema": "luhmOs.networkSpineAudit.v1", "status": "RED_NETWORK_SPINE_SOURCE" if errorList else "GREEN_NETWORK_SPINE_SOURCE_ONLY", "errors": errorList, "runtimeProven": False, "liveMutation": False, "secretValuesRead": False, "milestoneCompletion": False}


def main():
    parserValue = argparse.ArgumentParser(description=__doc__)
    parserValue.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    argsValue = parserValue.parse_args()
    resultValue = audit(argsValue.root)
    print(json.dumps(resultValue, indent=2))
    return 1 if resultValue["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

