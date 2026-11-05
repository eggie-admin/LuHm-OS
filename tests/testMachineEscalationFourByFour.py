#!/usr/bin/env python3
"""Negative controls: no audit-depth, Titan7, or four-by-four path may self-Crown."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("machineEscalation",ROOT/"tools/machineEscalationFourByFour.py")
machine=importlib.util.module_from_spec(spec)
spec.loader.exec_module(machine)
SHA="b"*40

def pass_audit(name, sha):
    return {"status":"PASS","exitCode":0,"outputSha256":"c"*64}

class MachineReleaseFourByFourTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy,cls.docs=machine.load_current()

    def test_current_canon_and_existing_machine_contracts(self):
        machine.validate_policy(self.policy,self.docs)
        self.assertEqual(self.policy["releaseMatrix"]["cells"],16)
        self.assertEqual(self.policy["existingMachineAudit"]["cells"],16)
        self.assertEqual(self.policy["existingMachineAudit"]["originalLanes"],["machine","service","studio","interface"])

    def test_five_checks_quick_source_only(self):
        result=machine.audit(SHA,"five",0,self.policy,pass_audit,lambda:SHA)
        self.assertEqual((result["countExecuted"],result["countPassed"]),(5,5))
        self.assertEqual(result["status"],"GREEN_SOURCE_ONLY_EXTERNAL_HOLD")
        self.assertEqual(len(result["matrix"]),4)
        self.assertTrue(all(len(x["cells"])==4 for x in result["matrix"]))
        self.assertFalse(result["runtimeDeployed"])
        self.assertFalse(result["mergedToMain"])
        self.assertEqual(result["crownStatus"],"STOP")

    def test_twelve_checks_not_a_model_or_a_deploy(self):
        result=machine.audit(SHA,"twelve",3,self.policy,pass_audit,lambda:SHA)
        self.assertEqual((result["countExecuted"],result["countPassed"]),(12,12))
        self.assertEqual(result["titanMode"],"finalForm")
        self.assertTrue(result["titanEscalationDoesNotAuthorizeAction"])
        self.assertFalse(result["aiFineTuned"])
        self.assertFalse(result["agentQuarantineReleased"])
        self.assertTrue(all(x["state"]!="PASS_SOURCE_ONLY"
                            for row in result["matrix"] for x in row["cells"]
                            if x["evidenceScope"]=="EXTERNAL_REQUIRED"))

    def test_failing_check_stops_source_green_but_keeps_evidence(self):
        def failure(name,sha):
            if name=="tools/networkSpineAudit.py":
                return {"status":"FAIL","exitCode":1}
            return pass_audit(name,sha)
        result=machine.audit(SHA,"five",1,self.policy,failure,lambda:SHA)
        self.assertEqual(result["countPassed"],4)
        self.assertEqual(result["status"],"RED_OR_UNKNOWN_SOURCE_STOP")
        self.assertEqual(result["reaperStop"],"HOLD_FOCUSSED_CANDIDATE_PRESERVE_EVIDENCE")
        self.assertEqual(result["crownStatus"],"STOP")

    def test_source_drift_refused(self):
        with self.assertRaisesRegex(ValueError,"exact checkout drift"):
            machine.audit(SHA,"five",0,self.policy,pass_audit,lambda:"a"*40)

    def test_no_fabricated_crown_authority(self):
        p=copy.deepcopy(self.policy)
        p["approval"]["productionDeploy"]=True
        with self.assertRaisesRegex(ValueError,"authority acquired"):
            machine.validate_policy(p,self.docs)

    def test_no_unsafe_reaper_process_kill(self):
        p=copy.deepcopy(self.policy)
        p["reaperStop"]["noKillProcess"]=False
        with self.assertRaisesRegex(ValueError,"reaper phrase"):
            machine.validate_policy(p,self.docs)

    def test_merge_and_cast_cannot_be_downgraded_to_source(self):
        p=copy.deepcopy(self.policy)
        p["releaseMatrix"]["rows"][2]["cells"][3]["kind"]="SOURCE"
        with self.assertRaisesRegex(ValueError,"release gate bypass"):
            machine.validate_policy(p,self.docs)

    def test_no_unknown_audit_depth_or_tier(self):
        with self.assertRaises(ValueError):
            machine.audit(SHA,"sixty",3,self.policy,pass_audit,lambda:SHA)
        with self.assertRaises(ValueError):
            machine.audit(SHA,"five",5,self.policy,pass_audit,lambda:SHA)

    def test_cannot_claim_global_green(self):
        p=copy.deepcopy(self.policy)
        p["externalStatus"]="LIVE_GREEN"
        with self.assertRaisesRegex(ValueError,"false external proof"):
            machine.validate_policy(p,self.docs)

if __name__=="__main__":
    unittest.main()
