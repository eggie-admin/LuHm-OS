#!/usr/bin/env python3
"""Audit source-only LuHm APK update DNS identity without reopening Cloudflare onboarding."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))
def need(ok, why):
    if not ok:
        raise SystemExit("RED_FDROID_CLOUDFLARE_IDENTITY_" + why)

identity = read("doctrine/publicApkUpdateIdentityV1.json")
spine = read("doctrine/networkSpineV1.json")
cloudflare = read("doctrine/cloudflareAirTrafficControllerV1.json")
mapdoc = read("doctrine/artRepositoryNameMapV1.json")
android = read("doctrine/androidDeliveryLanesV1.json")
truth = read("doctrine/currentSourceTruthV3.json")
need(identity["schema"] == "luhmOs.publicApkUpdateIdentity.v1", "SCHEMA")
need(identity["status"] == "SOURCE_RECONCILED_NOT_NETWORK_OR_RELEASE_PROVEN", "PROOF_SCOPE")
need(identity["publicRepo"]["candidateFqdn"] == "art.eggiebagelface.art", "PUBLIC_HOST")
need(identity["publicRepo"]["candidateUrl"] == "https://art.eggiebagelface.art/fdroid/repo/", "PUBLIC_URL")
need(identity["publicRepo"]["published"] is False, "FALSE_PUBLICATION")
need(identity["publicRepo"]["legacyVoiceAlias"] == "art.egguebagelface.*" and identity["publicRepo"]["aliasSpellingUnconfirmed"] is True, "VOICE_ALIAS_NOT_VERIFIED")
dns = identity["dns"]
need(dns["intendedAuthority"] == "cloudflare" and dns["operatorEstablishedAuthority"] is True, "CLOUDFLARE_BASELINE")
need(dns["actualRegistrarDelegation"] == "EXISTING_CLOUDFLARE_AUTHORITY_ACCEPTED_FROM_OPERATOR_AND_PREVIOUS_PROOFS", "HISTORICAL_AUTHORITY")
need(dns["authoritativeNsSoa"] == "CLOUDFLARE_MANAGED_DO_NOT_REPLACE_OR_SELF_HOST", "NS_HOSTING_OUT_OF_SCOPE")
for key in ("doNotRequireReOnboardingOrNewNameservers","providerControlsAuthoritativeNameserverFleet","registrarMigrationOutOfScope","selfHostedNameserversOutOfScope","delegateChildZoneOutOfScope","reverseDnsHostingOutOfScope"):
    need(dns[key] is True, "NO_NEW_REGISTRAR_NS_OR_PTR_WORK_"+key)
h = dns["historicalVerifiedFqdn"]
need(h["hostname"] == "ai.eggiebagelface.art" and h["httpsRoot"] == "HTTP_200_PREVIOUSLY_RECORDED" and h["healthResponse"] == "HTTP_200_PREVIOUSLY_RECORDED", "RETAIN_PRIOR_HTTP_200")
need(h["currentHealth"] == "NOT_RETESTED_THIS_TURN" and "HISTORICAL_HOST_HTTP" in h["proofScope"], "NO_FABRICATED_FRESH_PROOF")
need(dns["historicalApex"]["resolved"] == "NOT_PROVED_FROM_AVAILABLE_HISTORICAL_RECEIPT", "NO_APEX_GREEN_FROM_AI_HOST")
need(dns["historicalRenderSiteIsConfirmedFdroidRepoServer"] is False, "REPO_HOST_UNPROVEN")
need(identity["publicRepo"]["officialFdroidCatalogAcceptanceProven"] is False, "OFFICIAL_CATALOG_NOT_PROVED")
rev = identity["reverseDomainIdentity"]
need(rev["reversedZoneBase"] == "art.eggiebagelface", "REVERSE_PACKAGE_NAMESPACE")
need(rev["canonicalStableApplicationId"] == "PENDING_OWNER_APPROVED_STABLE_PACKAGE_AND_SIGNER", "NO_UNAPPROVED_STABLE_APP_ID")
need(rev["existingTestingPackage"] == "art.eggiebagelface.luhmos.testing" and rev["existingBetaPackage"] == "art.eggiebagelface.luhmos.beta", "PRESERVE_EXISTING_APPS")
apk = identity["androidUpdateInvariant"]
for key in ("sameInstalledApplicationId","sameOrAndroidVerifiedCompatibleAppSigningCertificateLineage","higherMonotonicVersionCode","neverClearUserAppData","installAndUpgradeWithoutUninstall"):
    need(apk[key] is True, "UPDATE_LINEAGE_"+key)
need(identity["fdroid"]["signingIdentity"] == "separate from APK app release signer", "INDEPENDENT_FDROID_SIGNER")
need(identity["fdroid"]["noAutomaticPublication"] is True, "OWNER_PUBLICATION")
tls = identity["tls"]
need(tls["noTLSVerify"] is False and tls["httpToHttps"]["noFlexibleMode"] is True and tls["httpToHttps"]["hstsPreloadRequiresSeparateHumanApproval"] is True, "TLS_POLICY")
need("FullStrict" in tls["edgeProxyMode"], "FULL_STRICT")
need(identity["reversePtr"]["notRequiredForDomainControlValidationOrAndroidApkUpdate"] is True, "PTR_NOT_APP_ID")
need(spine["identityChain"]["authoritativeNameservers"]["delegationState"] == "CLOUDFLARE_EXISTING_AUTHORITY_OPERATOR_AND_HISTORICAL_PROOF", "SPINE_NS_BASELINE")
need(spine["publicDnsProviderBaseline"] == "CLOUDFLARE_EXISTING_AUTHORITY_PREVIOUSLY_PROVED", "SPINE_PROVIDER")
need(cloudflare["lanes"]["publicApkUpdates"]["existingCloudflareZoneReused"] is True, "REUSE_EXISTING_ZONE")
need(cloudflare["dnsLaw"]["noNameserverFleetHostingOrRegistrarWork"] is True, "TRAFFIC_LAW")
need(mapdoc["publicAndroidUpdateLane"]["existingCloudflareDnsHostAuthority"] == "PRESERVE_ESTABLISHED_PROVIDER", "ART_REPO_PROVIDER")
need(android["releaseUpdateIdentity"]["contract"] == "doctrine/publicApkUpdateIdentityV1.json", "ANDROID_BINDING")
need(truth["networkLayer"]["publicApkUpdateIdentity"] == "doctrine/publicApkUpdateIdentityV1.json", "SOURCE_TRUTH")
need(truth["networkLayer"]["reonboardingOrOwnNameserverFleetRequired"] is False, "SOURCE_TRUTH_REGISTRAR")
need(truth["packageDelivery"]["publicFdroidUpdateLane"]["publicationAuthority"] is False, "NO_PUBLICATION_BY_CI")
for key in ("branchMergeAuthority","dnsMutationAuthority","certificateMutationAuthority","signingAuthority","releasePublicationAuthority","canCallPublicFinalFormGreen"):
    need(identity["releaseAndRuntimeProof"][key] is False, "AUTHORITY_BOUNDARY_"+key)
print("GREEN_PUBLIC_APK_IDENTITY_SOURCE_ONLY_EXISTING_CLOUDFLARE_BASELINE")
