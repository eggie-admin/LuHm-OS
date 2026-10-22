#!/usr/bin/env python3
"""Offline LuHm entitlement-policy safety gate. No network, secrets, billing or API calls."""
import copy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "doctrine" / "openAiDeveloperEntitlementsV1.json"

def check(data):
    errors = []
    def require(ok, name):
        if not ok:
            errors.append(name)
    require(data.get("schema") == "luhmOs.openAiDeveloperEntitlements.v1", "schema")
    require(data.get("status") == "SOURCE_CONFIGURED_CANDIDATE", "candidateState")
    require(data.get("canonicalRepository") == "eggie-admin/LuHm-OS", "canonicalRepo")
    account = data.get("accountScope", {})
    require(account.get("kind") == "independentPrivateArtStudio", "soloStudio")
    require(account.get("enterpriseSeatRequired") is False, "noEnterprise")
    require(account.get("accountEntitlementReadAvailable") is False, "noFakeAccountRead")
    axes = data.get("entitlementAxes", {})
    chat = axes.get("chatGptPersonal", {})
    work = axes.get("workSessions", {})
    signin = axes.get("signInWithChatGpt", {})
    api = axes.get("apiPlatform", {})
    community = axes.get("developerCommunity", {})
    startup = axes.get("startupPartnerBenefits", {})
    verify = axes.get("accountVerification", {})
    require(chat.get("apiCreditsIncluded") is False, "chatIsNotApi")
    require(work.get("requiresCodex") is False, "codexNotRequired")
    require(work.get("codexExecutionRequested") is False, "noCodex")
    require(work.get("usesSharedWorkCodexAllowance") is True, "sharedAllowance")
    require(work.get("accountAvailability") == "UNKNOWN_UNTIL_ACCOUNT_UI", "hostProof")
    require(work.get("cannotProgrammaticallySwitchMode") is True, "noModeEscalation")
    require(signin.get("explicitConsentRequired") is True, "signinConsent")
    require(signin.get("notApiBilling") is True and signin.get("usesSharedWorkCodexAllowance") is True, "signinSeparateFromApi")
    require(signin.get("doesNotShareChatOrMemoryByDefault") is True, "signinPrivate")
    require(signin.get("allowAppCreditUseWithoutOptIn") is False, "appCreditsConsent")
    require(signin.get("automaticallyPurchasesCredits") is False, "noCreditAutoBuy")
    require(api.get("independentBilling") is True and api.get("separateFromChatGptSubscription") is True, "apiBilling")
    require(api.get("allowPaidCalls") is False and api.get("allowBillingActivation") is False, "noPaidCall")
    require(api.get("allowKeyCreation") is False, "noImplicitApiKey")
    require(community.get("automaticallyAddsApiCredits") is False, "communityNoAutoCredits")
    require(community.get("automaticallyAddsWorkAllowance") is False, "communityNoAutoWork")
    require(startup.get("creditsGranted") == "UNVERIFIED", "startupUnknown")
    require(startup.get("automaticallyAddsWorkAllowance") is False, "startupNoAutoWork")
    require(verify.get("approvalForOneScopeMayUnlockAnother") is False, "scopeIsolation")
    receipt = data.get("receiptContract", {})
    require("PRIVATE_PROVIDER_SIDE_ONLY" == api.get("organizationAndProjectIdentity"), "privateOrg")
    require(set(("PROVIDER_OBSERVED","HOST_INVOKED","UNKNOWN")).issubset(set(receipt.get("allowedEvidenceStates", []))), "proofStates")
    deny = data.get("failClosedGates", {})
    require(all(deny.get(k) is True for k in [
        "unknownNeverGreen", "noEnterpriseImpersonation", "noEntitlementEscalationBySchema",
        "noApiCreditClaimsWithoutGrantReceipt", "noPaidApiCallsWithoutSeparateApproval",
        "noUnattendedWorkAfterSessionWithoutScheduledTask", "noPluginInstallOrPermissionMutationWithoutUserAction",
        "noAgentQuarantineRelease", "noAutomaticMergeDeployPublishSignOrCrown"
    ]), "failClosed")
    require(data.get("promotion") is False and data.get("crownStatus") == "STOP", "crownStop")
    return errors

def selftest(data):
    assert not check(data), check(data)
    cases = [
        ("paidApi", ("entitlementAxes", "apiPlatform", "allowPaidCalls"), True),
        ("fakeCredit", ("entitlementAxes", "startupPartnerBenefits", "creditsGranted"), "APPROVED"),
        ("enterprise", ("accountScope", "enterpriseSeatRequired"), True),
        ("codexForced", ("entitlementAxes", "workSessions", "requiresCodex"), True),
        ("modeEscalation", ("entitlementAxes", "workSessions", "cannotProgrammaticallySwitchMode"), False),
        ("communityCredits", ("entitlementAxes", "developerCommunity", "automaticallyAddsApiCredits"), True),
        ("quarantine", ("failClosedGates", "noAgentQuarantineRelease"), False),
        ("crown", ("crownStatus",), "GREEN"),
    ]
    for name, path, new_value in cases:
        bad = copy.deepcopy(data)
        node = bad
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = new_value
        assert check(bad), "Negative control escaped: " + name
    return len(cases)

if __name__ == "__main__":
    path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = check(data)
    if errors:
        print("OPENAI_ENTITLEMENT_AUDIT=RED", ",".join(errors))
        raise SystemExit(1)
    print("OPENAI_ENTITLEMENT_AUDIT=GREEN_STATIC_ONLY", "negativeControls=" + str(selftest(data)))
    print("ACCOUNT_ENTITLEMENTS=NOT_VERIFIED; WORK_ACTIVATION=NOT_CHANGED; API_BILLING=UNTOUCHED; CROWN=STOP")
