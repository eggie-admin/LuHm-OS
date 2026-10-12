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

