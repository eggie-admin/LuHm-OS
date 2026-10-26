"""Canonical/Ubuntu official kiosk/kernel/VM research stays proposal-only."""
import unittest
from copy import deepcopy
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "doctrine/ubuntuKioskKernelVmStudyV1.yaml"
MINIMUM = ROOT / "doctrine/minimumViableKernelAndServicesV1.yaml"


def defects(policy, minimum):
    failures = []
    def check(ok, key):
        if not ok:
            failures.append(key)

    check(policy.get("schema") == "luhmOs.ubuntuKioskKernelVmStudy.v1", "schema")
    check(policy.get("status") == "SOURCE_CANDIDATE_RESEARCH_ONLY", "status")
    check(policy.get("crownStatus") == "STOP", "crown")
    law = policy.get("sourceLaw", {})
    check(law.get("ubuntuAndCanonicalOfficialFirst") is True, "officialFirst")
    check(law.get("sql") == "firstApprovedPrivateOperationalStore" and
          law.get("yaml") == "reviewedPortableConfiguration", "sqlYaml")
    evidence = policy.get("officialSources", {})
    required = ("lts26", "interim2610", "core26", "minimalServer", "frame",
                "coreKioskQuickstart", "frameOSK", "coreImaging",
                "mainlineUnsupported", "stableKernel", "customKernel",
                "lxd", "qemu", "chiseling", "linuxSecurity")
    check(all(x in evidence and evidence[x].get("url","").startswith("https://")
              for x in required), "officialLinks")
    check(evidence.get("minimalServer",{}).get("supportedSourceId") == "ubuntu-server-minimal",
          "minimalSource")
    check(evidence.get("mainlineUnsupported",{}).get("securityUpdates") == "none" and
          evidence.get("mainlineUnsupported",{}).get("productionPermitted") is False,
          "mainlineUnsupported")
    check(evidence.get("customKernel",{}).get("separateVmOnly") is True,
          "customKernelVmOnly")
    comp = {x.get("id"): x for x in policy.get("comparison", [])}
    check(comp.get("ubuntuServer2604Minimal",{}).get("disposition") == "TEST_IN_VM",
          "vmFirst")
    check(comp.get("ubuntuCore26",{}).get("disposition") == "VM_FIRST_WHEN_READY",
          "coreVmFirst")
    check(comp.get("mainlineKernel",{}).get("disposition") == "NO_PRODUCTION",
          "noMainlineProd")
    safe = policy.get("kernelAndServiceSafety", {})
    check(safe.get("disableUnknownServices") is False, "noRandomDisable")
    check(safe.get("noBiosOrRomHexEdit") is True and safe.get("noOdinFlashing") is True,
          "noBios")
    check(safe.get("noLiveChangesWithoutSeparateApproval") is True, "approval")
    selection = policy.get("strategy", {})
    check(selection.get("noBareMetalReplacement") is True and
          selection.get("noDirectUbuntuCoreInstallOnSamsungOEMDevice") is True,
          "deviceIsolation")
    check(selection.get("noMainlineKernelProduction") is True and
          selection.get("noStandaloneExperimentalKernelOnExistingHost") is True,
          "kernelIsolation")
    check(policy.get("noCommandsExecuted") is True and
          policy.get("noVmCreated") is True and
          policy.get("noServiceDisabled") is True and
          policy.get("noAutoinstallRun") is True,
          "noFalseExecution")
    check(minimum.get("status") == "SOURCE_CANDIDATE_NOT_APPLIED" and
          minimum.get("targets",{}).get("samsungAndroid",{}).get("noHexEditorOrBiosDependency") is True,
          "existingLaw")
    return failures


class UbuntuResearchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy=yaml.safe_load(POLICY.read_text(encoding="utf-8"))
        cls.minimum=yaml.safe_load(MINIMUM.read_text(encoding="utf-8"))

    def test_staged_research(self):
        self.assertEqual(defects(self.policy,self.minimum), [])

    def test_mainline_never_becomes_production(self):
        p=deepcopy(self.policy)
        p["officialSources"]["mainlineUnsupported"]["productionPermitted"]=True
        self.assertIn("mainlineUnsupported", defects(p,self.minimum))

    def test_no_removing_unknown_essential_services(self):
        p=deepcopy(self.policy)
        p["kernelAndServiceSafety"]["disableUnknownServices"]=True
        self.assertIn("noRandomDisable", defects(p,self.minimum))

    def test_no_running_autoinstall(self):
        p=deepcopy(self.policy)
        p["noAutoinstallRun"]=False
        self.assertIn("noFalseExecution", defects(p,self.minimum))

    def test_no_installing_core_on_samsung_without_hardware_proof(self):
        p=deepcopy(self.policy)
        p["strategy"]["noDirectUbuntuCoreInstallOnSamsungOEMDevice"]=False
        self.assertIn("deviceIsolation", defects(p,self.minimum))

    def test_no_unreviewed_custom_kernel_on_host(self):
        p=deepcopy(self.policy)
        p["strategy"]["noStandaloneExperimentalKernelOnExistingHost"]=False
        self.assertIn("kernelIsolation", defects(p,self.minimum))

    def test_no_bios_or_odin(self):
        p=deepcopy(self.policy)
        p["kernelAndServiceSafety"]["noBiosOrRomHexEdit"]=False
        self.assertIn("noBios", defects(p,self.minimum))

    def test_need_explicit_promotion(self):
        p=deepcopy(self.policy)
        p["kernelAndServiceSafety"]["noLiveChangesWithoutSeparateApproval"]=False
        self.assertIn("approval", defects(p,self.minimum))

    def test_source_url_baseline(self):
        p=deepcopy(self.policy)
        p["officialSources"]["frame"]["url"]="http://example.test"
        self.assertIn("officialLinks", defects(p,self.minimum))

if __name__ == "__main__":
    unittest.main()
