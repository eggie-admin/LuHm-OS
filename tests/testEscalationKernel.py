"""Exact-source escalation kernel negative tests; tier never grants authority."""
import copy
import unittest
from unittest.mock import patch

from tools.escalationKernel import PROFILE_PATHS,load,plan

class EscalationKernelTests(unittest.TestCase):
    def replace_doc(self,path,change):
        altered=copy.deepcopy(load(path))
        change(altered)
        return patch("tools.escalationKernel.load",
                     side_effect=lambda p: altered if p==path else load(p))

    def test_all_domains_and_tiers(self):
        for domain in PROFILE_PATHS:
            for tier in range(4):
                for outcome in ("working","green","blocked","unknown","conflict"):
                    with self.subTest(domain=domain,tier=tier,outcome=outcome):
                        result=plan(domain,tier,outcome)
                        self.assertEqual(result["currentTier"],tier)
                        self.assertEqual(result["authorityBoundary"],
                            {"tierChangesAuthority":False,
                             "providerMayGrantGreen":False,
                             "professorRetainsCrown":True,
                             "mutationAuthority":False})
                        if outcome=="blocked":
                            self.assertEqual(result["nextTier"],min(3,tier+1))
                        elif outcome=="green":
                            self.assertEqual(result["nextTier"],max(0,tier-1))
                        else:
                            self.assertEqual(result["nextTier"],tier)

    def test_outcomes_and_tier_types_fail_closed(self):
        for bad in ("gren","success",None,True,0):
            with self.assertRaises(ValueError):
                plan("technology",0,bad)
        for bad in (True,False,1.0,"1",-1,4):
            with self.assertRaises(ValueError):
                plan("technology",bad,"working")

    def test_kernel_crown_must_remain_stop(self):
        with self.replace_doc("doctrine/escalationKernelV1.json",
                              lambda d:d.update(crownStatus="GREEN")):
            with self.assertRaisesRegex(RuntimeError,"RED_ESCALATION_KERNEL_CONTRACT"):
                plan("technology",0,"green")

    def test_four_beats_must_match(self):
        def drift(d):d["fourByFourModel"]["horizontalBeats"]=["hear","act","verify","publish"]
        with self.replace_doc("doctrine/escalationKernelV1.json",drift):
            with self.assertRaisesRegex(RuntimeError,"RED_ESCALATION_KERNEL_CONTRACT"):
                plan("default",0,"working")

    def test_profile_crown_drift_rejected_for_all_domains(self):
        for domain,path in PROFILE_PATHS.items():
            with self.subTest(domain=domain):
                with self.replace_doc(path,lambda d:d.update(crownStatus="GREEN")):
                    with self.assertRaisesRegex(RuntimeError,"RED_.*_AUTHORITY"):
                        plan(domain,0,"green")

    def test_profile_kernel_pointer_rejected(self):
        with self.replace_doc(PROFILE_PATHS["corporate"],
                              lambda d:d.update(kernel="doctrine/fakeKernel.json")):
            with self.assertRaisesRegex(RuntimeError,"RED_CORPORATE_AUTHORITY"):
                plan("corporate",1,"working")

    def test_titan_cannot_promote(self):
        with self.replace_doc(PROFILE_PATHS["technology"],
                              lambda d:d.update(promotion=True)):
            with self.assertRaisesRegex(RuntimeError,"RED_TECHNOLOGY_PROMOTION_OR_TIERS"):
                plan("technology",3,"green")

    def test_titan_tier_map_drift_rejected(self):
        def drift(d):d["escalationTierMap"]["finalForm"]=0
        with self.replace_doc(PROFILE_PATHS["technology"],drift):
            with self.assertRaisesRegex(RuntimeError,"RED_TECHNOLOGY_PROMOTION_OR_TIERS"):
                plan("technology",3,"working")

    def test_titan_fast_path_room_drift_rejected(self):
        def drift(d):d["defaultFastPathRoom"]["tier"]=3
        with self.replace_doc("doctrine/escalationWorkflowRoomsV1.json",drift):
            with self.assertRaisesRegex(RuntimeError,"RED_TECHNOLOGY_ROOM_CONTRACT"):
                plan("technology",0,"working")

if __name__=="__main__":
    unittest.main()
