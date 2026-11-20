import copy
import unittest
from tools.fourTierDeviceArtPublicAudit import ROOT, SPEC, SURFACE, read, audit
class FourTierProductTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec=read(ROOT,SPEC);cls.public=read(ROOT,SURFACE)
    def check(self,s=None,p=None):
        return audit(s or copy.deepcopy(self.spec),p or copy.deepcopy(self.public),ROOT)
    def test_source_candidate(self): self.assertEqual(self.check(),[])
    def test_not_final_without_owner(self):
        s=copy.deepcopy(self.spec);s["stages"][3]["promotion"]=True
        self.assertIn("final-human",self.check(s=s))
    def test_private_urd_cannot_publish(self):
        s=copy.deepcopy(self.spec);s["artCanon"]["privateUrdPack"]="PUBLIC"
        self.assertIn("urd-public-bypass",self.check(s=s))
    def test_no_fake_trademark(self):
        s=copy.deepcopy(self.spec);s["artCanon"]["trademarkRegistrationStatus"]="REGISTERED"
        self.assertIn("fake-registration",self.check(s=s))
    def test_no_public_pr_runner(self):
        s=copy.deepcopy(self.spec);s["crossDeviceArchitecture"]["publicRepoRunnerPolicy"]="ALLOW"
        self.assertIn("public-runner-exposure",self.check(s=s))
    def test_no_fake_webgl(self):
        s=copy.deepcopy(self.spec);s["godotWeb"]["runtimeWebgl"]="GREEN"
        self.assertIn("fake-webgl-green",self.check(s=s))
    def test_no_fake_public_service_health(self):
        p=copy.deepcopy(self.public);p["render"]["livePublicHttpAndContent"]="GREEN"
        self.assertIn("render-live-overclaim",self.check(p=p))
    def test_19_public_repos_listed(self):
        p=copy.deepcopy(self.public);p["github"]["repositories"].pop()
        self.assertIn("repo-inventory",self.check(p=p))
    def test_no_expanded_production_ports(self):
        s=copy.deepcopy(self.spec);s["crossDeviceArchitecture"]["noPortForwarding"]=False
        self.assertIn("lan-ingress",self.check(s=s))
    def test_no_iphone_build_fabrication(self):
        s=copy.deepcopy(self.spec);s["platforms"]["iphoneIos"]["hostBuild"]="ANY_HOST"
        self.assertIn("no-mac-ios-build-claim",self.check(s=s))
if __name__=="__main__":unittest.main()
