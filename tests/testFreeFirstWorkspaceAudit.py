"""Fail-closed negative controls for public-source free-first workspace protocol."""
import copy
import json
import unittest
from tools.freeFirstWorkspaceAudit import POLICY,assess,check

class FreeFirstWorkspaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=json.loads(POLICY.read_text(encoding="utf8"))

    def mutate(self,path,value):
        p=copy.deepcopy(self.p)
        node=p
        for item in path[:-1]: node=node[item]
        node[path[-1]]=value
        return check(p)

    def test_4x4x6(self):
        receipt=assess(self.p)
        self.assertEqual(receipt["total"],96)
        self.assertEqual(receipt["policyErrors"],[])
        self.assertEqual(receipt["counts"]["BLOCKED"],16)
        self.assertGreater(receipt["counts"]["UNVERIFIED"],0)
        self.assertFalse(receipt["spendApproved"])
        self.assertFalse(receipt["driveAclOwnerOnly"])

    def test_drive_public_writer_must_not_be_hidden(self):
        self.assertIn("PRIVATE_ACL_GAP_HIDDEN",
             self.mutate(["drive","securityFinding"],"PRIVATE_CONTROL_PLANE_SAFE"))

    def test_drive_transfer_stays_disabled(self):
        self.assertIn("DRIVE_LANE_UNSAFE_protectedWriteEnabled",
             self.mutate(["drive","protectedWriteEnabled"],True))

    def test_no_auto_billing(self):
        self.assertIn("BILLING_ELEVATION_autoUpgradeToPaid",
             self.mutate(["freeFirst","autoUpgradeToPaid"],True))

    def test_no_auto_ai_calls(self):
        self.assertIn("GOOGLE_AUTO_CALL",self.mutate(["freeFirst","googleAiStudioGemini","autoCall"],True))

    def test_no_new_proxy_port(self):
        self.assertIn("REMOTE_EXPOSURE",self.mutate(["proxies","remote","exposeNewPublicPort"],True))

    def test_no_lan_open_proxy(self):
        self.assertIn("LOCAL_EXPOSURE",self.mutate(["proxies","local","allowLanPublicBind"],True))

    def test_no_silent_release(self):
        self.assertIn("UNSAFE_allowAutoDeploy",self.mutate(["safety","allowAutoDeploy"],True))

    def test_no_drive_ci_sync(self):
        self.assertIn("DAILY_SIDE_EFFECT_noDriveSync",self.mutate(["dailyBuild","noDriveSync"],False))

    def test_no_false_device_green(self):
        self.assertIn("FAKE_DEVICE_PROOF",self.mutate(["studio","godotDeviceLaunch"],"GREEN"))

if __name__=="__main__":unittest.main()
