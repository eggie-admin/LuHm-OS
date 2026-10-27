"""Premonition source-only seller/monetization gate, no owner identifiers."""
import copy
import unittest
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
SPEC=ROOT/"doctrine/premonitionBusinessLaunchV1.yaml"


def validate(conf, source):
    errors=[]
    def check(ok,name):
        if not ok:
            errors.append(name)
    check(conf.get("schema")=="luhmOs.premonitionBusinessLaunch.v1","schema")
    check(conf.get("status")=="SOURCE_CANDIDATE_NO_ACCOUNT_ACTIONS","status")
    check(conf.get("project",{}).get("publicReleaseAuthorized") is False,"public")
    private=conf.get("publicSourcePrivacy",{})
    for key in ("personalAccountVerificationMustRemainPrivate",
                "noSocialAccountHandlesInThisFile",
                "noDbaLegalNamesAddressesOrRegistrationNumbersInThisFile",
                "noTaxOrPayoutDocumentsInGitHub",
                "noIdDocumentsOrPrivateMetaScreenshotsInGitHub",
                "noSignerPrivateKeysOrCredentialsInRepoAppOrBrowser"):
        check(private.get(key) is True,"privacy_"+key)
    check(conf.get("businessIdentity",{}).get("dbaIsTradeNameNotAutomaticallySeparateLegalEntity") is True,"tradeName")
    check(conf.get("instagram",{}).get("badgeDoesNotConferMonetizationEligibility") is True,"badgeRevenue")
    check(conf.get("instagram",{}).get("badgeDoesNotConferMetaBusinessPortfolioVerification") is True,"businessBadge")
    check(conf.get("instagram",{}).get("badgeDoesNotConferFacebookVerification") is True,"facebookBadge")
    check(conf.get("facebook",{}).get("contentMonetization2026")=="INVITE_ONLY","metaInvite")
    check(conf.get("facebook",{}).get("monetizationDashboard")=="NOT_READ","metaDashboard")
    ss=conf.get("samsungGalaxyStore",{})
    check(ss.get("currentCommercialSellerStatus")=="NOT_READ","sellerUnknown")
    check(ss.get("existingPersistentReleaseSigner")=="NOT_PROVEN","signerUnknown")
    check(ss.get("noSilentPackageIdSwitch", True) is True,"packageId")
    check(ss.get("sellerApi",{}).get("enabled") is False,"sellerApiOff")
    check(ss.get("sellerApi",{}).get("appMustFirstBeRegisteredInSellerPortal") is True,"sellerApiPrereq")
    revenue=conf.get("revenueSafety",{})
    check(revenue.get("noGuaranteedMonetizationOrPaidAccountBenefits") is True,"noGuarantee")
    check(revenue.get("noPrivateReferenceAnimeOrGameDonorsInPublicRelease") is True,"assetRights")
    check(revenue.get("noAutoPostingAdvertisingAudienceScrapingOrMassMessaging") is True,"noSpamming")
    check(revenue.get("noCredentialSharingOrAccountDelegationWithoutExplicitOwnerConsent") is True,"noAccountDelegation")
    monet=conf.get("monetizationOptions",[])
    check(len(monet)>=5 and all(x.get("status")!="APPROVED" for x in monet),"proposedOnly")
    gates=conf.get("launchGates",[])
    check(len(gates)>=7 and any(x.get("id")=="lockSigningAndAndroidUpdates" for x in gates),"launchGates")
    runtime=conf.get("runtime",{})
    for key in ("accountsConnectedByThisCandidate","userPrivacySettingsChanged",
                "signingKeysReadOrCreated","verificationAppliedFor","storeSellerStatusAppliedFor",
                "productsPricedOrListed","socialPostsPublished","paidCampaignStarted",
                "payoutsOrFinancialAccountsRead","mergePerformed"):
        check(runtime.get(key) is False,"noAction_"+key)
    check(runtime.get("crownStatus")=="STOP","crown")
    check("@" not in source,"noHandleOrEmail")
    check("sk-" not in source and "token:" not in source,"noSecret")
    return errors

class BusinessLaunchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text=SPEC.read_text(encoding="utf-8")
        cls.conf=yaml.safe_load(cls.text)

    def test_complete_staged_draft(self):
        self.assertEqual(validate(self.conf,self.text),[])

    def test_instagram_badge_not_payout(self):
        conf=copy.deepcopy(self.conf)
        conf["instagram"]["badgeDoesNotConferMonetizationEligibility"]=False
        self.assertIn("badgeRevenue",validate(conf,self.text))

    def test_samsung_commercial_status_must_not_be_faked(self):
        conf=copy.deepcopy(self.conf)
        conf["samsungGalaxyStore"]["currentCommercialSellerStatus"]="APPROVED"
        self.assertIn("sellerUnknown",validate(conf,self.text))

    def test_no_public_personal_handles(self):
        self.assertIn("noHandleOrEmail",validate(self.conf,self.text+"\nemail: somebody@example.test"))

    def test_no_unapproved_business_api(self):
        conf=copy.deepcopy(self.conf)
        conf["samsungGalaxyStore"]["sellerApi"]["enabled"]=True
        self.assertIn("sellerApiOff",validate(conf,self.text))

    def test_no_automatic_social_campaigns(self):
        conf=copy.deepcopy(self.conf)
        conf["runtime"]["socialPostsPublished"]=True
        self.assertIn("noAction_socialPostsPublished",validate(conf,self.text))

    def test_no_fake_signing_receipt(self):
        conf=copy.deepcopy(self.conf)
        conf["samsungGalaxyStore"]["existingPersistentReleaseSigner"]="PROVEN"
        self.assertIn("signerUnknown",validate(conf,self.text))

    def test_no_blind_release(self):
        conf=copy.deepcopy(self.conf)
        conf["project"]["publicReleaseAuthorized"]=True
        self.assertIn("public",validate(conf,self.text))

if __name__=="__main__":
    unittest.main()
