"""Zero-mutation LuHm install wizard design and failure-mode checks."""
import unittest
from copy import deepcopy
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/"doctrine/minimalInstallerWizardV1.yaml"
HTML=ROOT/"frontEnd/installWizard/preview.html"


def audit(config, html):
    failures=[]
    def check(cond,reason):
        if not cond:failures.append(reason)
    check(config.get("schema")=="luhmOs.minimalInstallerWizard.v1","schema")
    check(config.get("status")=="SOURCE_CANDIDATE_NO_INSTALL_ENGINE","status")
    base=config.get("productionBase",{})
    check(base.get("preferred")=="Debian13TrixieStable","debianBase")
    check(base.get("noManualHexFirmwareEdits") is True and base.get("noBIOSRewrite") is True,"noBiosHex")
    check(base.get("noInstallOnSamsungPhoneOrTablet") is True,"samsungSafety")
    check(base.get("directBareMetalInstallPermitted") is False,"bareMetal")
    boot=config.get("bootStack",{})
    check(boot.get("bootloader")=="grub2" and boot.get("preserveExistingEfiEntries") is True,"grub")
    check(boot.get("secureBoot")=="preserveWhenAvailable","secureBoot")
    firmware=config.get("firmwareAndDriverSupport",{})
    check(firmware.get("packageFirmwareNotSameAsFlashingBios") is True,"fwVsPkg")
    check(firmware.get("updateAssistant",{}).get("firmwareUpdatesNeverPartOfInstallAutomatically") is True,"noFlash")
    check(config.get("serviceReduction",{}).get("neverDisableSecurityUpdatesForPerformance") is True,"securityUpdates")
    wizard=config.get("wizard",{})
    check(wizard.get("backendMode")=="NONE_PREVIEW_ONLY" and
          wizard.get("previewFinalAction")=="BLOCKED_SIMULATION_ONLY","noEngine")
    check(wizard.get("noPrivilegedCallsFromBrowser") is True,"noPrivilegedJs")
    check(wizard.get("noDiskPartitioningPerformed") is True and
          wizard.get("noAutoinstallGeneratedOrApplied") is True,"noDiskWipe")
    check(len(wizard.get("order",[]))>=10,"wizardStages")
    g=wizard.get("diskGates",{})
    check(g.get("noDiskPreselected") is True and
          g.get("destructiveActionRequiresTypedExactTargetAndFreshOwnerApproval") is True,"diskConsent")
    check(g.get("neverExecuteBasedOnNarrativeRoleplay") is True,"noRoleplayExec")
    check(config.get("vendorAndCrown",{}).get("crownStatus")=="STOP" and
          config.get("vendorAndCrown",{}).get("noOSInstalled") is True,"crown")
    for phrase in ('<!doctype html>', 'CROWN STOP',
                   'installerEngine: NOT_CONNECTED',
                   'approvedForDiskWrites: false', 'diskSelection: ',
                   'No disk selected (default)', 'Start preview again'):
        check(phrase in html,"html_"+phrase)
    for forbidden in ('fetch(', 'XMLHttpRequest', 'WebSocket(', 'localStorage',
                      'navigator.usb', 'navigator.serial', 'eval(', 'document.write('):
        check(forbidden not in html,"forbiddenPrimitive_"+forbidden)
    return failures


class MinimalInstallerWizardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
        cls.html=HTML.read_text(encoding="utf-8")

    def test_current_candidate(self):
        self.assertEqual(audit(self.doc,self.html),[])

    def test_no_disk_preselection(self):
        p=deepcopy(self.doc)
        p["wizard"]["diskGates"]["noDiskPreselected"]=False
        self.assertIn("diskConsent",audit(p,self.html))

    def test_no_public_samsung_repartition(self):
        p=deepcopy(self.doc)
        p["productionBase"]["noInstallOnSamsungPhoneOrTablet"]=False
        self.assertIn("samsungSafety",audit(p,self.html))

    def test_no_firmware_flash_through_wizard(self):
        p=deepcopy(self.doc)
        p["firmwareAndDriverSupport"]["updateAssistant"]["firmwareUpdatesNeverPartOfInstallAutomatically"]=False
        self.assertIn("noFlash",audit(p,self.html))

    def test_no_os_installed_claim(self):
        p=deepcopy(self.doc)
        p["vendorAndCrown"]["noOSInstalled"]=False
        self.assertIn("crown",audit(p,self.html))

    def test_no_roleplay_as_disk_authority(self):
        p=deepcopy(self.doc)
        p["wizard"]["diskGates"]["neverExecuteBasedOnNarrativeRoleplay"]=False
        self.assertIn("noRoleplayExec",audit(p,self.html))

    def test_no_dom_network_or_script_exec(self):
        self.assertNotIn('fetch(', self.html)
        bad=self.html.replace('installerEngine: NOT_CONNECTED','installerEngine: PRIVILEGED')
        self.assertIn('html_installerEngine: NOT_CONNECTED',audit(self.doc,bad))

    def test_never_disable_security_updates_for_small_size(self):
        p=deepcopy(self.doc)
        p["serviceReduction"]["neverDisableSecurityUpdatesForPerformance"]=False
        self.assertIn("securityUpdates",audit(p,self.html))

if __name__=="__main__":
    unittest.main()
