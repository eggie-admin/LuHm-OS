"""R1 honest-source, hex escalation and no-root host boundary negative tests."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from tools.r1UnifiedFlow import POLICY,ROOT,DEPTHS,assess,depth_value,inspect_host,sample_256,validate_policy,source_truth_identity,source_truth_crown_stop

class R1FlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads(POLICY.read_text(encoding="utf-8"))
        cls.sha="a"*40
    def mutate(self,section,key,value,expected):
        d=copy.deepcopy(self.doc);d[section][key]=value
        self.assertIn(expected,validate_policy(d))
        return d
    def test_policy_shape(self):
        self.assertEqual(validate_policy(self.doc),[])
        self.assertEqual(len(self.doc["coverage"]["axes"]),4)
    def test_hex_depth_equivalence(self):
        for value in DEPTHS:
            self.assertEqual(depth_value(str(value)),value)
            self.assertEqual(depth_value(hex(value)),value)
        self.assertEqual(len(DEPTHS),9)
    def test_invalid_depth(self):
        for raw in ("-1","1","7","0x03","0x200","999","0x-1","garbage","0x10;sh"):
            with self.assertRaises(ValueError):depth_value(raw)
    def test_exact_sha_required(self):
        with self.assertRaisesRegex(ValueError,"EXACT_SHA_REQUIRED"):assess(self.doc,"main")
    def test_2048_total_is_plan_not_runtime(self):
        r=assess(self.doc,self.sha,16)
        self.assertEqual(r["matrixConceptualCells"],2048)
        self.assertEqual(r["matrixCasesExecuted"],0)
        self.assertEqual(r["matrixSourceAddressesPlanned"],256)
        self.assertEqual(r["crownEvidenceSlotsAssessed"],336)
        self.assertEqual(r["sourceChecksExecuted"],16)
        self.assertEqual(r["sourceChecksPassed"],16)
        self.assertEqual(r["status"],"AMBER_SOURCE_ONLY")
        self.assertFalse(r["sourceRefIndependentlyChecked"])
        self.assertFalse(r["releaseAuthorized"])
    def test_source_truth_identity_fail_closed(self):
        truth=json.loads((ROOT/"doctrine/currentSourceTruthV3.json").read_text(encoding="utf-8"))
        self.assertTrue(source_truth_identity(truth))
        for key,value in (
            ("schema","luhmOs.currentSourceTruth.v2"),
            ("canonicalRepository","other/repository"),
            ("authority","bot"),
            ("sourceLaw","AI promotes itself")):
            changed=copy.deepcopy(truth);changed[key]=value
            self.assertFalse(source_truth_identity(changed),key)

    def test_source_truth_release_flags_are_independent(self):
        truth=json.loads((ROOT/"doctrine/currentSourceTruthV3.json").read_text(encoding="utf-8"))
        self.assertTrue(source_truth_crown_stop(truth))
        for key,value in (
            ("crownStatus","GREEN"),
            ("promotion",True),
            ("publicationAuthority",True),
            ("releaseAuthority",True),
            ("productionSigningAuthority",True)):
            changed=copy.deepcopy(truth);changed[key]=value
            self.assertFalse(source_truth_crown_stop(changed),key)
        for key,value in (
            ("status","RELEASED"),
            ("crownStatus","GREEN"),
            ("currentMutationPromotion",True),
            ("professorPromotionRequired",False)):
            changed=copy.deepcopy(truth);changed["workingDoctrineLane"][key]=value
            self.assertFalse(source_truth_crown_stop(changed),key)
        changed=copy.deepcopy(truth);changed.pop("workingDoctrineLane")
        self.assertFalse(source_truth_crown_stop(changed))

    def test_256_sample_unique_axes(self):
        points=sample_256(self.doc)
        self.assertEqual(len(points),256)
        self.assertEqual(len(set(points)),256)
        for i,count in enumerate((4,4,8,16)):
            self.assertEqual({point[i] for point in points},set(range(count)))
    def test_0x100_only_planned(self):
        r=assess(self.doc,self.sha,256)
        self.assertEqual(r["auditDepthHex"],"0x100")
        self.assertEqual(r["expandedDepthsStatus"],"PLANNED_NOT_EXECUTED")
        self.assertEqual(r["matrixCasesExecuted"],0)
        self.assertEqual(r["escalation"]["nextTier"],0)
    def test_no_auto_grub_edit(self):self.mutate("guardrails","autoEditGrub",True,"R1_UNSAFE_autoEditGrub")
    def test_no_firmware_mutation(self):self.mutate("guardrails","autoModifyFirmware",True,"R1_UNSAFE_autoModifyFirmware")
    def test_no_kernel_changes(self):self.mutate("guardrails","autoModifyKernel",True,"R1_UNSAFE_autoModifyKernel")
    def test_no_root(self):self.mutate("guardrails","autoRoot",True,"R1_UNSAFE_autoRoot")
    def test_no_auto_agent(self):self.mutate("guardrails","autoInvokeAgent",True,"R1_UNSAFE_autoInvokeAgent")
    def test_no_spend(self):self.mutate("guardrails","autoSpendUsd",1,"R1_CROWN_HOLD")
    def test_no_autonomous_permissions(self):
        d=self.mutate("flow","unattendedProtectedMutations",True,"R1_ONE_UNIT")
        r=assess(d,self.sha)
        self.assertEqual(r["status"],"RED_SOURCE")
        self.assertEqual(r["escalation"],"ESCALATE")
    def test_no_new_vendor_packages(self):self.mutate("reduction","newPackageDependenciesAllowed",True,"R1_VENDOR_newPackageDependenciesAllowed")
    def test_no_competing_crown(self):self.mutate("reduction","duplicateAuthoritiesAllowed",True,"R1_VENDOR_duplicateAuthoritiesAllowed")
    def test_preserve_existing_kernel(self):self.mutate("existingCanon","resolver","tools/evil.py","R1_CANON_REUSE")
    def test_android_has_no_grub(self):
        d=inspect_host(system="Linux",termux=True)
        self.assertEqual(d["hostClass"],"ANDROID_TERMUX_USERSPACE")
        self.assertFalse(d["grubApplicable"])
        self.assertFalse(d["grubConfigFilePresent"])
        self.assertFalse(d["privilegedMutationPerformed"])
        self.assertFalse(d["hardwareProven"])
    def test_linux_grub_is_inspection_only(self):
        class FakePath:
            def __init__(self,path):self.path=path
            def is_file(self):return self.path=="/etc/default/grub"
            def is_dir(self):return self.path in ("/boot/grub","/sys/firmware/efi")
        d=inspect_host(system="Linux",termux=False,filesystem=FakePath)
        self.assertTrue(d["grubApplicable"])
        self.assertTrue(d["grubConfigFilePresent"])
        self.assertTrue(d["efiDirectoryPresent"])
        self.assertFalse(d["privilegedMutationPerformed"])
    def test_other_os_never_fakes_grub(self):
        d=inspect_host(system="Windows",termux=False)
        self.assertFalse(d["grubApplicable"])
        self.assertEqual(d["hostClass"],"OTHER_USERSPACE")
    def test_runtime_source_includes_prior_art_and_media(self):
        r=assess(self.doc,self.sha)
        self.assertTrue(r["sourceCheckStatuses"]["evidence/staticWeb"])
        self.assertTrue(r["sourceCheckStatuses"]["evidence/godotCandidate"])
        self.assertTrue(r["sourceCheckStatuses"]["policy/mediaVendor"])
        self.assertFalse(r["ownerApproval"])
    def test_dont_shrink_depths(self):
        d=copy.deepcopy(self.doc);d["coverage"]["depths"].pop()
        self.assertIn("R1_HEX_LADDER",validate_policy(d))
    def test_failure_keeps_crown_stop(self):
        d=copy.deepcopy(self.doc);d["guardrails"]["autoCallProvider"]=True
        r=assess(d,self.sha)
        self.assertEqual(r["crown"],"STOP")
        self.assertEqual(r["status"],"RED_SOURCE")
        self.assertEqual(r["matrixCasesExecuted"],0)
if __name__=="__main__":unittest.main()
