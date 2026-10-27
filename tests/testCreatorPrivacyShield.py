"""Creator business privacy firewall. Does not connect, inspect, publish or alter Meta."""
from copy import deepcopy
from pathlib import Path
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"doctrine/creatorPrivacyShieldV1.yaml"

def check_policy(conf, raw):
    issues=[]
    def needs(flag,name):
        if not flag:issues.append(name)
    needs(conf.get("schema")=="luhmOs.creatorPrivacyShield.v1","schema")
    needs(conf.get("status")=="SOURCE_CANDIDATE_NOT_APPLIED","sourceOnly")
    links=conf.get("linkage",{})
    needs(links.get("legalIdentityToPublicBrandMapping")=="OWNER_PRIVATE_ACCOUNT_ONLY","noPublicIdentityLink")
    needs(links.get("personalSocialHandlesInPublicRepo")=="FORBIDDEN","handlesStayPrivate")
    needs(links.get("doNotAssertAnOldAliasEqualsANewDisplayNameWithoutOwnerCheck") is True,"noAliasDrift")
    people=conf.get("identities",{})
    needs(set(people)=={"primaryCreatorBrand","filmProductionBrand","ownerPersonal"},"threeLanes")
    needs(people.get("ownerPersonal",{}).get("neverAddToPublicAboutBioOrBrandAssets") is True,"legalName")
    needs(people.get("filmProductionBrand",{}).get("publicCrossLinkingRequiresOwnerConsent") is True,"crossLinkConsent")
    truth=conf.get("truthAndLimits",{})
    needs(truth.get("instagramBusinessIsPublicFacing") is True and
          truth.get("cannotMakeBusinessAccountFullyPrivateWithoutChangingAccountType") is True,"professionalPublic")
    needs(truth.get("verifiedAccountDisplayNameOrHandleChangeRequiresPreflightReview") is True,"verifiedName")
    needs(truth.get("verifiedBadgeMethodUnknown") is True and
          truth.get("noVerifiedBadgeRetentionGuaranteeAfterProfileChange") is True,"badgeRisk")
    needs(truth.get("completeAnonymityPromise") is False,"noAnonymityOverclaim")
    needs(truth.get("publicDbaRegistrationsOrAdsDisclosuresMayRevealLegalBusinessLinks") is True,"legalDisclosure")
    priorities=conf.get("priority",[])
    ids=[x.get("id") for x in priorities]
    needs(len(priorities)>=9 and len(ids)==len(set(ids)),"auditCoverage")
    needs(all(x.get("status") not in ("DONE","LIVE","VERIFIED") for x in priorities),"notPretendApplied")
    controls=conf.get("automationRules",{})
    for field in ("readOnlyInventoryFirst","eachAccountMustBeIdentifiedThroughOwnerAuthorizedConnector",
                  "doNotEditVerifiedNameUsernameProfilePictureWithoutSeparateOwnerApproval",
                  "doNotDestroyPostsMessagesFollowersOrLinkedPagesWithoutSeparateOwnerApproval",
                  "doNotRemoveAccountRecoveryMethodsAutomatically",
                  "noAutomaticUnlinkOrPageTransfer","noPasswordCookieOtpOrAccessTokenInChat",
                  "noPublishingFollowingDmsLikesOrAdSpend","noBusinessDocumentsUploadedToPublicGithub",
                  "noSecretScreenshotsInIssuesPrsOrBuildLogs",
                  "doNotChangeAccountTypeToMakeProfessionalProfilePrivate",
                  "rollbackEachApprovedSettingChange"):
        needs(controls.get(field) is True,"control_"+field)
    src=conf.get("sourceOnly",{})
    for field in ("noLiveMetaConnection","noProfileSettingsRead","noProfileEdited",
                  "noBrandRenamed","noBusinessLegalIdentityPublished",
                  "noContentDeleted","noAdsOrSponsoredPosts","noCredentialsOrPayoutDataRead"):
        needs(src.get(field) is True,"truth_"+field)
    needs(src.get("publicLaunchAuthorized") is False and src.get("crownStatus")=="STOP","crown")
    needs("@" not in raw and "sk-" not in raw,"noLiteralHandleOrSecret")
    return issues


class CreatorPrivacyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=SOURCE.read_text(encoding="utf-8")
        cls.conf=yaml.safe_load(cls.raw)

    def test_source_policy_with_no_real_account_access(self):
        self.assertEqual(check_policy(self.conf,self.raw),[])

    def test_verified_name_cannot_change_silently(self):
        p=deepcopy(self.conf)
        p["automationRules"]["doNotEditVerifiedNameUsernameProfilePictureWithoutSeparateOwnerApproval"]=False
        self.assertIn("control_doNotEditVerifiedNameUsernameProfilePictureWithoutSeparateOwnerApproval",check_policy(p,self.raw))

    def test_brand_to_private_profile_link_requires_review(self):
        p=deepcopy(self.conf)
        p["identities"]["filmProductionBrand"]["publicCrossLinkingRequiresOwnerConsent"]=False
        self.assertIn("crossLinkConsent",check_policy(p,self.raw))

    def test_facebook_page_admin_must_not_be_removed_silently(self):
        p=deepcopy(self.conf)
        p["automationRules"]["noAutomaticUnlinkOrPageTransfer"]=False
        self.assertIn("control_noAutomaticUnlinkOrPageTransfer",check_policy(p,self.raw))

    def test_business_profile_cannot_claim_full_private_status(self):
        p=deepcopy(self.conf)
        p["truthAndLimits"]["completeAnonymityPromise"]=True
        self.assertIn("noAnonymityOverclaim",check_policy(p,self.raw))

    def test_existing_photos_must_not_be_bulk_deleted(self):
        p=deepcopy(self.conf)
        p["automationRules"]["doNotDestroyPostsMessagesFollowersOrLinkedPagesWithoutSeparateOwnerApproval"]=False
        self.assertIn("control_doNotDestroyPostsMessagesFollowersOrLinkedPagesWithoutSeparateOwnerApproval",check_policy(p,self.raw))

    def test_legal_identifiers_never_in_public_bio(self):
        p=deepcopy(self.conf)
        p["identities"]["ownerPersonal"]["neverAddToPublicAboutBioOrBrandAssets"]=False
        self.assertIn("legalName",check_policy(p,self.raw))

    def test_must_show_oauth_missing(self):
        p=deepcopy(self.conf)
        p["sourceOnly"]["noLiveMetaConnection"]=False
        self.assertIn("truth_noLiveMetaConnection",check_policy(p,self.raw))

    def test_no_new_account_handles_or_email_in_source(self):
        self.assertIn("noLiteralHandleOrSecret",check_policy(self.conf,self.raw+"\nprivateEmail: test@example.invalid"))

    def test_never_disable_recovery_methods_unilaterally(self):
        p=deepcopy(self.conf)
        p["automationRules"]["doNotRemoveAccountRecoveryMethodsAutomatically"]=False
        self.assertIn("control_doNotRemoveAccountRecoveryMethodsAutomatically",check_policy(p,self.raw))

    def test_older_alias_is_not_auto_updated(self):
        p=deepcopy(self.conf)
        p["linkage"]["doNotAssertAnOldAliasEqualsANewDisplayNameWithoutOwnerCheck"]=False
        self.assertIn("noAliasDrift",check_policy(p,self.raw))

if __name__=="__main__":
    unittest.main()
