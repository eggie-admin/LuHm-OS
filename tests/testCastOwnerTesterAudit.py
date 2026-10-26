"""Guard the separation between owner plugin, host GUI, and one outside tester."""
import json
import copy
import unittest
from pathlib import Path
from tools.castOwnerTesterAudit import ROOT,check

D=json.loads((ROOT/"doctrine/castOwnerTesterActivationV1.json").read_text(encoding="utf-8"))
class CastOwnerTesterAuditTest(unittest.TestCase):
    def test_source_contract(self): self.assertEqual(check(D),[])
    def mutation(self,loc,val,expect):
        p=copy.deepcopy(D)
        x=p
        for k in loc[:-1]: x=x[k]
        x[loc[-1]]=val
        self.assertIn(expect,check(p))
    def test_cannot_fake_owner_gui(self):
        self.mutation(["cast","ownerChatGptAndroidInlineMount"],"GREEN","OWNER_DISPLAY")
    def test_cannot_share_owner_user_plugin(self):
        self.mutation(["access","firstTester","privateUserPluginShareableByLink"],True,"PRIVATE_NOT_SHAREABLE")
    def test_cannot_claim_tester_ready(self):
        self.mutation(["access","firstTester","status"],"READY","TESTER_READY_FALSE")
    def test_cannot_drop_automatic_safe_work(self):
        self.mutation(["operatorMode","noRoutineApprovalLoops"],False,"AUTOMATION")
    def test_no_unapproved_invites(self):
        self.mutation(["access","firstTester","sendInviteAutomatically"],True,"NO_UNAPPROVED_INVITE")
    def test_no_hiding_red_host_mount(self):
        self.mutation(["cast","failedHostMountOverridesCiSuccess"],False,"NO_FALSE_GREEN")
    def test_no_private_asset_share(self):
        self.mutation(["assets","doNotExposePrivateDrive"],False,"PRIVATE_ASSETS")

if __name__=="__main__": unittest.main()
