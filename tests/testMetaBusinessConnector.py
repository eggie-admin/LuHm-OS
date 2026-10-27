"""Existing-account Meta integration policy: no user secrets, changes or false payouts."""
import unittest
from copy import deepcopy
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/"doctrine/metaBusinessConnectorV1.yaml"

def errors(policy, text):
    faults=[]
    def need(ok,name):
        if not ok:faults.append(name)
    need(policy.get("schema")=="luhmOs.metaBusinessConnector.v1","schema")
    need(policy.get("status")=="SOURCE_CANDIDATE_OWNER_OAUTH_REQUIRED","status")
    need(policy.get("sourceOfTruth",{}).get("accountIdsAndTokensNeverStoredInGitHub") is True,"privacy")
    routes={x["id"]:x for x in policy.get("availableIntegrationRoutes",[])}
    need({"pluginConnector","metaInstagramLogin","metaFacebookLogin","facebookPagesOrMetaAds"}.issubset(routes),"routes")
    if "metaInstagramLogin" in routes:
        ig=routes["metaInstagramLogin"]
        need(ig.get("exactInitialScope")==["instagram_business_basic"],"igMinScopes")
        need(ig.get("scopesUseOfficial2025NamesOnly") is True,"igNewScopes")
        need(set(ig.get("staleScopesForbidden",[]))=={
            "business_basic","business_content_publish","business_manage_comments","business_manage_messages"},"igDeprecatedScopes")
        need(ig.get("redirectAllowlistAndPkceOrStateRequired") is True
             and ig.get("serverSideTokenExchangeAndRefreshOnly") is True,"oauthBound")
        need(ig.get("appIdOrSecretPresentInRepository") is False,"igSecrets")
        need(ig.get("currentLiveConnection")=="NOT_CONFIRMED","igUnconnected")
    if "metaFacebookLogin" in routes:
        fb=routes["metaFacebookLogin"]
        need(fb.get("pageRequiredForThisPath") is True and fb.get("linkedPageKnown") is False,"fbPage")
        need(fb.get("currentLiveConnection")=="NOT_CONFIRMED","fbUnconnected")
    auth=policy.get("oauthBoundaries",{})
    for key in ("accountConnectionRequiresOwnerAction","neverAskForPasswordsCodesCookiesOrRawTokensInChat",
                "permissionScopesStartReadOnly","noSilentReauthOrProfileConversion",
                "encryptedServerSideTokenStorageIfBuildingCustomAdapter",
                "allowPublishingOnlyWithExactApprovedAssetCaptionAccountTimingAndLicenseProof",
                "allowBudgetOrCampaignChangesOnlyWithExactUserConfirmation"):
        need(auth.get(key) is True, "auth_"+key)
    mon=policy.get("monetization",{})
    need(mon.get("inferredFromVerificationBadge") is False,"badgeVsRevenue")
    need(mon.get("currentAccountEligibility")=="NOT_READ","eligibility")
    need(mon.get("autoPublishingOrEditingProfile") is False and
         mon.get("automaticallyApplyingForMonetization") is False,"noAutoPublishing")
    need(mon.get("commercialMusicRightsNeedSeparateReview") is True,"musicRights")
    stage=policy.get("stageSequence",[])
    need(len(stage)>=8 and stage[0].get("status")=="USER_CONNECTION_REQUIRED","nextUserStep")
    runtime=policy.get("execution",{})
    for k in ("credentialsRead","userAccountsMutated","oauthStartedByCandidate",
              "publicationPerformed","messagesReadOrSent","adsSpend","payoutsReadOrChanged",
              "productionWebhookCreated","publicLaunchAuthorized"):
        need(runtime.get(k) is False,"noAction_"+k)
    need(runtime.get("crownStatus")=="STOP","crown")
    need("@" not in text,"publicHandle")
    need("access_token:" not in text and "client_secret:" not in text,"rawSecret")
    return faults

class MetaBusinessConnectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text=DOC.read_text(encoding="utf8")
        cls.conf=yaml.safe_load(cls.text)

    def test_current_staged_contract(self):
        self.assertEqual(errors(self.conf,self.text),[])

    def test_initial_scopes_must_not_publish(self):
        p=deepcopy(self.conf)
        next(x for x in p["availableIntegrationRoutes"] if x["id"]=="metaInstagramLogin")["exactInitialScope"]=["instagram_business_basic","instagram_business_content_publish"]
        self.assertIn("igMinScopes",errors(p,self.text))

    def test_instagram_login_no_facebook_page_assumption(self):
        p=deepcopy(self.conf)
        next(x for x in p["availableIntegrationRoutes"] if x["id"]=="metaFacebookLogin")["linkedPageKnown"]=True
        self.assertIn("fbPage",errors(p,self.text))

    def test_owner_must_consent(self):
        p=deepcopy(self.conf)
        p["oauthBoundaries"]["accountConnectionRequiresOwnerAction"]=False
        self.assertIn("auth_accountConnectionRequiresOwnerAction",errors(p,self.text))

    def test_no_automated_spend(self):
        p=deepcopy(self.conf)
        p["execution"]["adsSpend"]=True
        self.assertIn("noAction_adsSpend",errors(p,self.text))

    def test_business_badge_not_monetization_proof(self):
        p=deepcopy(self.conf)
        p["monetization"]["inferredFromVerificationBadge"]=True
        self.assertIn("badgeVsRevenue",errors(p,self.text))

    def test_no_disclosure_of_business_handle(self):
        self.assertIn("publicHandle",errors(self.conf,self.text+"\nhandle: somebody@example.test"))

    def test_no_publishing_without_asset_rights(self):
        p=deepcopy(self.conf)
        p["oauthBoundaries"]["allowPublishingOnlyWithExactApprovedAssetCaptionAccountTimingAndLicenseProof"]=False
        self.assertIn("auth_allowPublishingOnlyWithExactApprovedAssetCaptionAccountTimingAndLicenseProof",errors(p,self.text))

    def test_no_implicit_account_creation(self):
        p=deepcopy(self.conf)
        p["oauthBoundaries"]["noSilentReauthOrProfileConversion"]=False
        self.assertIn("auth_noSilentReauthOrProfileConversion",errors(p,self.text))

if __name__=="__main__":
    unittest.main()
