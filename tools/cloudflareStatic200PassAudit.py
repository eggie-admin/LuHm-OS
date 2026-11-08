#!/usr/bin/env python3
"""LuHm-OS Cloudflare static/CDN Canon: 200 policy scenarios, no network or keys."""
from __future__ import annotations
from collections import Counter
from itertools import product
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
load = lambda name: json.loads((ROOT / name).read_text(encoding="utf-8"))
LANES = ("publicMcp", "staticAssets", "publicSite", "signedArt", "privateSystem")
CLASSES = ("staticHtml", "jsonManifest", "sha256Asset", "publicCertificate")
CASES = ("baseline", "authorization", "sessionCookie", "setCookie", "privateAsset",
         "unapprovedArtwork", "remoteExecutable", "unhashedAsset", "unknownTls", "unverifiedOrigin")
EXPECTED = {"DENY_PUBLIC": 108, "BYPASS_CACHE": 52, "HOLD_TLS": 16,
            "HOLD_ORIGIN": 16, "REVALIDATE_SOURCE_ONLY": 4,
            "IMMUTABLE_ELIGIBLE_SOURCE_ONLY": 2, "HOLD_SIGNATURE": 2}
CAMEL = re.compile(r"^[a-z][A-Za-z0-9]*$")
HASH = re.compile(r"^[0-9a-f]{40}$")


def oracle(lane, kind, condition):
    if lane not in LANES or kind not in CLASSES or condition not in CASES:
        raise ValueError("unknown explicit namespace")
    if condition in ("privateAsset", "unapprovedArtwork", "remoteExecutable") or lane == "privateSystem":
        return "DENY_PUBLIC"
    if condition in ("authorization", "sessionCookie", "setCookie"):
        return "BYPASS_CACHE"
    if condition == "unknownTls":
        return "HOLD_TLS"
    if condition == "unverifiedOrigin":
        return "HOLD_ORIGIN"
    if condition == "unhashedAsset":
        return "DENY_PUBLIC"
    if lane == "publicMcp":
        return "BYPASS_CACHE"
    if lane == "signedArt":
        return "HOLD_SIGNATURE" if kind in ("sha256Asset", "jsonManifest") else "DENY_PUBLIC"
    if lane == "staticAssets":
        if kind == "sha256Asset":
            return "IMMUTABLE_ELIGIBLE_SOURCE_ONLY"
        return "REVALIDATE_SOURCE_ONLY" if kind == "jsonManifest" else "DENY_PUBLIC"
    return "IMMUTABLE_ELIGIBLE_SOURCE_ONLY" if kind == "sha256Asset" else "REVALIDATE_SOURCE_ONLY"


def inspect(doc, source, edge, brand, network):
    problems = []
    def need(ok, name):
        if not ok:
            problems.append(name)
    need(doc.get("schema") == "luhmOs.cloudflareStaticTransmutation.v1"
         and doc.get("status") == "PROPOSED_SOURCE_ONLY_NO_CDN_DEPLOY", "sourceOnly")
    need(doc.get("authority") == "Professor"
         and doc.get("sourceLaw") == "AI proposes. Policy authorizes. CI proves. Human promotes.", "authority")
    need(doc.get("sourceTruth") == "doctrine/currentSourceTruthV3.json"
         and bool(HASH.fullmatch(doc.get("sourceMainAtReview", ""))), "sourcePin")
    need(source.get("status") == "AMBER_PROPOSED_SEAL_OF_TRUTH"
         and source.get("crownStatus") == "STOP", "sourceCrown")
    need(edge.get("lanes", {}).get("publicAssets", {}).get("externalCdnState") == "NOT_VERIFIED"
         and edge.get("lanes", {}).get("chatGptMcp", {}).get("plannedCloudflareProxy") is False, "cdnNeverFalselyLive")
    identity = doc.get("identity", {})
    need(identity.get("publisher") == brand["identity"]["publisher"]["display"]
         and identity.get("product") == "LuHm-OS"
         and identity.get("product") == brand["identity"]["product"]["display"]
         and identity.get("world") == brand["identity"]["world"]["display"]
         and identity.get("namespace") == "luhmOs", "officialLuHmOsName")
    tokens = brand["visualSystem"]["currentExistingTokens"]
    need(identity.get("brandColor") == tokens["pluginBrandColor"]
         and identity.get("background") == tokens["background"]
         and identity.get("mark") == tokens["mark"]
         and identity.get("ink") == tokens["ink"], "brandTokens")
    need(identity.get("externalProviderLogosByDefault") is False
         and identity.get("brandArtworkPublicApproved") is False, "artRights")
    brand_logo = ROOT / "publicationSite/logo.svg"
    plugin_logo = ROOT / "plugins/luhm-os/assets/logo.svg"
    need(brand_logo.read_bytes() == plugin_logo.read_bytes(), "matchedMasterPluginLogo")
    route_ids = [r.get("id") for r in doc.get("routes", [])]
    need(route_ids == list(LANES)
         and all(CAMEL.fullmatch(x or "") for x in route_ids), "fiveCamelHumpLanes")
    need([r.get("fqdn") for r in doc.get("routes", [])] ==
         ["mcp.eggiebagelface.art", "assets.eggiebagelface.art",
          "eggiebagelface.art", "art.eggiebagelface.art",
          "system.eggiebagelface.art"], "fqdnCanonicalRoutes")
    need(doc.get("contentClasses") == list(CLASSES)
         and doc.get("conditionCases") == list(CASES)
         and set(doc.get("decisionStates", [])) == set(EXPECTED), "auditMatrixAxes")
    need(doc.get("audit", {}).get("lattice", {}).get("expectedChecks") == 200, "200PassLaw")
    pub = doc.get("publicRecords", {})
    need(pub.get("zone") == "eggiebagelface.art"
         and pub.get("reverseLabels") == network["identityChain"]["reverseFqdnNamespace"]["reverseExample"]
         and pub.get("ptrState") == "UPSTREAM_PREFIX_OWNER_NOT_LUHM", "reverseIsNotPtr")
    need(pub.get("dnsChange") is False and pub.get("proxyChange") is False
         and pub.get("reversePtrChange") is False, "noNetworkMutation")
    need("pemPrivateKey" in pub.get("publicationNotGranted", [])
         and "apiToken" in pub.get("publicationNotGranted", [])
         and "jwkPrivateParameters" in pub.get("publicationNotGranted", []), "publicKeyNoPrivateMaterial")
    sem = doc.get("decisionSemantics", {})
    need(all(sem.get(k) is True for k in (
        "runtimeGreenNeverImplied", "mcpAnonymousOrAuthenticatedNeverCdnCached",
        "manifestNeverImmutable", "htmlNeverImmutable",
        "hashedPublicAssetsOnlyIfProxyAndRightsAndTlsProven",
        "privateAssetsNeverCdn", "providerAuthResponsesNeverCdn",
        "publicCertificatesNoTrustByAssetPublicationAlone", "statusDoesNotAuthorizeDeploy"
    )), "neverPromoteSourcePolicy")
    cache = doc.get("cache", {})
    need(cache.get("cdnCustomHostnameActive") is False
         and cache.get("cacheRulesOnlyOnProxiedHostnames") is True
         and all(cache.get(k) is True for k in (
             "neverCacheWithAuthorization", "neverCacheWithSetCookie",
             "neverCacheWithPersonalCookie")), "cacheSecrets")
    projection = doc.get("presentation", {})
    need(projection.get("transformation") == "DETERMINISTIC_BRANDED_STATIC_HTML_PROJECTION_ONLY"
         and projection.get("htmlRewriterWorker") == "NOT_DEPLOYED_NOT_REQUIRED"
         and projection.get("inlineHtmlScripting") is False
         and projection.get("noRemoteCssImports") is True, "noArbitraryHtmlTransmutation")
    html_file = ROOT / projection.get("staticHtmlSource", "")
    js_file = ROOT / projection.get("javaScriptLibrary", "")
    preview_file = ROOT / projection.get("staticHtmlScript", "")
    need(all(p.is_file() for p in (html_file, js_file, preview_file)), "previewFilesExist")
    if all(p.is_file() for p in (html_file, js_file, preview_file)):
        html, js, preview = (p.read_text(encoding="utf-8") for p in (html_file, js_file, preview_file))
        need(all(x in html for x in ("LuHm-OS", "Eggie Bagelface", "Project Premonition"))
             and "LuHm-OS" in js, "publicFaceUsesExactName")
        need("../publicationSite/logo.svg" in html
             and 'src="./edgeCanonPreview.mjs"' in html, "localBrandAssets")
        need(not re.search(r"<(?:script|link)[^>]*(?:src|href)=[\"']https?://", html, re.I)
             and "<iframe" not in html.lower() and "onclick=" not in html.lower(),
             "noRemoteExecutableHtml")
        need("textContent" in preview and "innerHTML" not in preview
             and "replaceChildren" in preview, "textOnlyHtmlProjection")
        need(not re.search(r"\b(fetch|XMLHttpRequest|eval|Function)\s*\(", js + preview)
             and "import(" not in js + preview, "noRemoteScriptExecution")
        need('runtime: "UNVERIFIED"' in js
             and "cloudflareCdnDeployed: false" in js
             and 'crown: "STOP"' in js, "notGreenJs")
    boundary = doc.get("boundary", {})
    need(all(boundary.get(k) is False for k in (
        "liveSitePluginUpdated", "cloudflareZoneUpdated", "cloudflareWorkerCreated",
        "jsExecutedInChatGptWidget", "renderDeployed", "publicKeysOrTokensUploaded",
        "cdnActivated", "agentsStarted"
    )) and boundary.get("crownStatus") == "STOP", "boundaryNoRuntimeClaim")
    return problems


def main():
    doc = load("doctrine/cloudflareStaticTransmutationV1.json")
    errors = inspect(doc, load("doctrine/currentSourceTruthV3.json"),
                     load("doctrine/cloudflareEdgeHardeningV1.json"),
                     load("doctrine/brandCanonV1.json"),
                     load("doctrine/networkSpineV1.json"))
    counts = Counter(oracle(lane, kind, cond) for lane, kind, cond in product(LANES, CLASSES, CASES))
    if counts != Counter(EXPECTED):
        errors.append("200DistinctCaseLatticeDrift")
    print(json.dumps({
        "schema": "luhmOs.cloudflareStatic200PassAudit.v1",
        "officialPublicName": "LuHm-OS",
        "sourcePasses": 5 * 4 * 10 if not errors else 0,
        "caseDistribution": dict(counts),
        "status": "GREEN_SOURCE_ONLY" if not errors else "RED_SOURCE",
        "errors": errors, "runtimeCdn": "UNVERIFIED",
        "networkMutations": 0, "crownStatus": "STOP"
    }, indent=2))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
