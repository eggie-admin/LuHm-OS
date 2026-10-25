#!/usr/bin/env python3
"""Fail-closed structural tests: sign-in must not become AI/Forge/admin authority."""
import copy
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = ROOT / "doctrine/premonitionIdentityGatewayV1.json"

def assess(doc):
    problems = []
    def expect(ok, name):
        if not ok:
            problems.append(name)
    expect(doc.get("schema") == "luhmOs.premonitionIdentityGateway.v1", "schema")
    expect(doc.get("status") == "SOURCE_CANDIDATE_AUTH_IMPLEMENTATION_NOT_PRESENT", "runtimeNotClaimed")
    providers = doc.get("providers", {})
    expect(all(providers.get(k, {}).get("signInCandidate") is True for k in ("google","github","apple","gitlab")), "fourActualLoginProviders")
    expect(providers.get("google", {}).get("kind") == "oidcLogin", "googleOIDC")
    expect(providers.get("github", {}).get("kind") == "oauthLogin", "githubOAuth")
    expect(providers.get("apple", {}).get("kind") == "oidcLogin", "appleOIDC")
    expect(providers.get("gitlab", {}).get("kind") == "oidcLogin", "gitlabOIDC")
    expect(all(providers.get(k, {}).get("signInCandidate") is False for k in ("fdroid","izzyOnDroid")), "distributorsNotLogin")
    expect(all(providers.get(k, {}).get("requiresAccountToInstall") is False for k in ("fdroid","izzyOnDroid")), "freeAnonymousInstall")
    guest = doc.get("anonymousAndLocal", {})
    expect(guest.get("guestModeAllowed") is True and guest.get("localGameAndRehearsalWithoutAccount") is True, "guestPlayWorks")
    expect(guest.get("offlineGuestNeverInheritsCloudPermissions") is True, "guestNoCloudPrivileges")
    flow = doc.get("identityProtocol", {})
    for field in ("antiCsrfStateRequired","oidcNonceRequired","oidcValidateIssuerAudienceSignatureAndExpiry",
                  "linkingRequiresFreshFirstPartySession","linkingRequiresProofOfNewProviderAccount",
                  "linkingRequiresExplicitUserConfirmation","unlinkRequiresRemainingRecoveryPath",
                  "noEmailAsPrimarySubject","noUntrustedEmailAutolink",
                  "noProviderAccessTokenInBrowserJsGodotJsonOrScreenRecording",
                  "neverAssumeChatGptHostProvidesDelegatedSignIn","noRedirectToPrivateLanFromPublicOAuth"):
        expect(flow.get(field) is True, field)
    expect("PKCE" in flow.get("flow","") and "authorization-code" in flow.get("flow",""), "PKCE")
    expect(flow.get("noProviderPasswordCollection") is True and flow.get("noSecretsInRepositoryOrLogs") is True, "noSecretCollection")
    bound = doc.get("authorizationBoundary", {})
    expect(bound.get("systemPortal", "").startswith("independent Cloudflare Zero Trust"), "ownerPortalSeparate")
    expect(bound.get("renderMcpCurrent","").startswith("preserve anonymous read-only"), "mcpPublicStreamUnaffected")
    expect(bound.get("forgeWrite", "").startswith("deny by default"), "forgeWriteDefaultDeny")
    expect("quarantine" in bound.get("agents", "") and "no private worker activation" in bound.get("agents", ""), "noWorkerActivation")
    expect(bound.get("noAutomaticAccessEscalation") is True, "noAutomaticEscalation")
    expect(bound.get("crownStatus") == "STOP", "crownStop")
    budget = doc.get("freeProviderBudget", {})
    expect(budget.get("unknownQuotaMeansNoPaidOrAssumedFreeCalls") is True, "budgetUnknownStop")
    expect(doc.get("acceptance",{}).get("loginSessionEndToEnd") is False, "noUnprovenLiveSignIn")
    return problems

class IdentityGatewayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(IDENTITY.read_text(encoding="utf-8"))

    def test_source_contract(self):
        self.assertEqual(assess(self.doc), [])

    def test_cannot_pretend_app_store_is_identity_provider(self):
        bad = copy.deepcopy(self.doc)
        bad["providers"]["fdroid"]["signInCandidate"] = True
        self.assertIn("distributorsNotLogin", assess(bad))

    def test_guest_access_not_forced_to_sign_in(self):
        bad = copy.deepcopy(self.doc)
        bad["anonymousAndLocal"]["guestModeAllowed"] = False
        self.assertIn("guestPlayWorks", assess(bad))

    def test_no_email_auto_merge(self):
        bad = copy.deepcopy(self.doc)
        bad["identityProtocol"]["noUntrustedEmailAutolink"] = False
        self.assertIn("noUntrustedEmailAutolink", assess(bad))

    def test_provider_token_not_sent_to_game(self):
        bad = copy.deepcopy(self.doc)
        bad["identityProtocol"]["noProviderAccessTokenInBrowserJsGodotJsonOrScreenRecording"] = False
        self.assertIn("noProviderAccessTokenInBrowserJsGodotJsonOrScreenRecording", assess(bad))

    def test_game_login_never_opens_private_system_portal(self):
        bad = copy.deepcopy(self.doc)
        bad["authorizationBoundary"]["systemPortal"] = "LuHm login automatically opens admin"
        self.assertIn("ownerPortalSeparate", assess(bad))

    def test_no_unproved_auth_runtime(self):
        bad = copy.deepcopy(self.doc)
        bad["acceptance"]["loginSessionEndToEnd"] = True
        self.assertIn("noUnprovenLiveSignIn", assess(bad))

if __name__ == "__main__":
    unittest.main()
