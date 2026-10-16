#!/usr/bin/env python3
"""Fail-closed source audit of Professor continuity and free-beta doctrine."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
def loadDoc(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def violations(doc, truth):
    issues = []
    def need(test, why):
        if not test:
            issues.append(why)

    need(doc.get("schema") == "luhmOs.continuityReleaseLifecycle.v1", "SCHEMA")
    need(doc.get("authority") == "Professor", "CROWN_AUTHORITY")
    need(doc.get("motto") == "PROVE → SEAL → PRESERVE → RESUME → ADVANCE", "CONTINUITY_MOTTO")
    phases = doc.get("phases") or []
    need([p.get("id") for p in phases] == ["PROVE","SEAL","PRESERVE","RESUME","ADVANCE"], "PHASE_ORDER")
    need([p.get("step") for p in phases] == [100,200,300,400,500], "MILESTONE_NUMBERING")
    need(all(p.get("rule") and p.get("requires") for p in phases), "NO_UNPROVEN_PHASE")
    c = doc.get("continuityRules") or {}
    for flag in ("evidenceNotAutomaticallyTransitive","priorProofMustNotBeErasedWhenSuperseded",
                 "historicalProofCanBeStaleForCurrentRoute","noRestatingProvenFoundationAsUnverifiedWithoutReason",
                 "contradictionMayReopenSpecificClaimOnly","greenAuditDoesNotProvePublicRelease",
                 "existingInfrastructurePreferred","noNewRegistrarOrNameserverOperations"):
        need(c.get(flag) is True, "PROOF_CONTINUITY_"+flag)
    need(c.get("cloudflareManagedDnsBaseline") == "PRESERVE_EXISTING_PROVEN_PROVIDER", "CLOUDFLARE_BASELINE")
    business = doc.get("releaseBusinessCanon") or {}
    need(business.get("sequence") == ["FREE_OPEN_BETA","COMMUNITY_GROWTH","PUBLIC_VERSION_1_0","OPTIONAL_MONETIZATION"], "COMMERCIAL_LIFECYCLE")
    beta = business.get("openBeta") or {}
    for flag in ("publicSignupFees","automaticCharges"):
        need(beta.get(flag) is False, "NO_BETA_CHARGES_"+flag)
    need(beta.get("costToTesters") == "FREE" and beta.get("requiresSignedUpdatesAndBasicPrivacySecurity") is True, "FREE_BETA_SECURE")
    need(business.get("versionOne",{}).get("existingBetaUsersAutomaticallyCharged") is False, "NO_CONVERSION_CHARGES")
    need(business.get("versionOne",{}).get("priceAndLicensing") == "NOT_SELECTED", "NO_PRICING_PRETENSE")
    need(business.get("noAutomaticPublicBetaPromotion") is True and business.get("productNotYetPubliclyReleased") is True, "NO_PRETEND_PUBLIC_RELEASE")
    need(business.get("noUnreviewedArtworkCommercialization") is True, "ARTIST_RIGHTS")
    seal = doc.get("seal") or {}
    need(seal.get("kind") == "SOURCE_CONTRACT_ONLY_NOT_RELEASE_RECEIPT", "NO_SOURCE_AS_RELEASE")
    need(seal.get("releaseState") == "AMBER" and seal.get("noPublicationOrBillingAuthority") is True, "CROWN_GATED_RELEASE")
    crown = doc.get("crown") or {}
    for flag in ("publicReleaseExplicitApproval","billingExplicitApproval","agentsNeverSelfPromote"):
        need(crown.get(flag) is True, "HUMAN_AUTHORITY_"+flag)
    need(truth.get("continuityLifecycle",{}).get("contract") == "doctrine/continuity-release-lifecycle-v1.json", "SOURCE_TRUTH_POINTER")
    need(truth.get("commercialReleaseModel",{}).get("publicBetaFree") is True, "SOURCE_TRUTH_FREE_BETA")
    need(truth.get("commercialReleaseModel",{}).get("noAutomaticCharges") is True, "SOURCE_TRUTH_NO_BILLING")
    need(truth.get("commercialReleaseModel",{}).get("publicBetaPublishProven") is False, "SOURCE_TRUTH_FALSE_LAUNCH")
    need(truth.get("finalFormRelease",{}).get("status") == "AMBER_RELEASE_HOLD", "RELEASE_NOT_PROVEN")
    need(truth.get("networkLayer",{}).get("publicDnsAuthority","").startswith("CLOUDFLARE_"), "EXISTING_DNS_BASELINE")
    return issues

def main():
    doc = loadDoc("doctrine/continuity-release-lifecycle-v1.json")
    truth = loadDoc("doctrine/currentSourceTruthV3.json")
    errors = violations(doc, truth)
    import copy
    broken = copy.deepcopy(doc)
    broken["releaseBusinessCanon"]["openBeta"]["automaticCharges"] = True
    if not violations(broken, truth): errors.append("NEGATIVE_TEST_BETA_CHARGE")
    broken = copy.deepcopy(doc)
    broken["continuityRules"]["greenAuditDoesNotProvePublicRelease"] = False
    if not violations(broken, truth): errors.append("NEGATIVE_TEST_FALSE_GREEN")
    broken = copy.deepcopy(doc)
    broken["crown"]["agentsNeverSelfPromote"] = False
    if not violations(broken, truth): errors.append("NEGATIVE_TEST_CROWN")
    print(json.dumps({"status":"RED_CONTINUITY_CANON" if errors else "GREEN_CONTINUITY_SOURCE_ONLY",
        "sourceOnly":True,"publicBetaLiveProven":False,"paidBillingAuthorized":False,
        "errors":errors},indent=2))
    return 1 if errors else 0
if __name__ == "__main__":
    raise SystemExit(main())
