#!/usr/bin/env python3
"""Hardware and package source-only 4x4 controls: no privileged probes."""
import copy
import json
import unittest
from pathlib import Path
from tools import hardwareVendorMinimum as vm

class VendorMinimumTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads(vm.CONTRACT.read_text(encoding="utf-8"))

    def testFourByFourAndSafeBoundaries(self):
        receipt=vm.validate(self.data)
        self.assertEqual(receipt["matrixCells"],16)
        self.assertEqual(receipt["status"],"AMBER_SOURCE_ONLY")
        self.assertEqual(receipt["declaredAptPackages"],34)
        self.assertFalse(receipt["actualPackageInstall"])
        self.assertFalse(receipt["firmwareWritten"])
        self.assertFalse(receipt["physicalDeviceVerified"])

    def testProfilesGetSmallerWhenContextShrinks(self):
        selected={name:vm.package_projection(self.data,name) for name in
                  ("samsungCockpit","linuxHeadless","linuxWebBuild","linuxStudio","existingCodespace")}
        self.assertEqual(selected["samsungCockpit"]["selectedCount"],0)
        self.assertEqual(selected["linuxHeadless"]["selectedCount"],4)
        self.assertGreater(selected["linuxWebBuild"]["selectedCount"],4)
        self.assertGreater(selected["linuxStudio"]["selectedCount"],selected["linuxWebBuild"]["selectedCount"])
        self.assertEqual(selected["existingCodespace"]["selectedCount"],34)
        self.assertNotIn("nginx",selected["linuxStudio"]["selectedPackages"])

    def testNeverModifyHost(self):
        with self.assertRaisesRegex(vm.ProfileError,"UNKNOWN_PROFILE"):
            vm.package_projection(self.data,"force-flash-everything")
        self.assertIsNone(vm.package_projection(self.data,"linuxStudio")["installCommand"])

    def testNoAndroidApt(self):
        bad=copy.deepcopy(self.data)
        bad["debian"]["profiles"]["samsungCockpit"]["packages"]=["blender"]
        with self.assertRaisesRegex(vm.ProfileError,"SAMSUNG_APT_FORBIDDEN|ANDROID_APT"):
            vm.validate(bad)

    def testNoNewUnknownPackages(self):
        bad=copy.deepcopy(self.data)
        bad["debian"]["profiles"]["linuxStudio"]["packages"].append("mystery-driver")
        with self.assertRaisesRegex(vm.ProfileError,"PROFILE_PACKAGE_NOT_DECLARED"):
            vm.validate(bad)

    def testNoServicePollutionInStudio(self):
        bad=copy.deepcopy(self.data)
        bad["debian"]["profiles"]["linuxStudio"]["packages"].append("mariadb-server")
        with self.assertRaisesRegex(vm.ProfileError,"STUDIO_UNNEEDED_SERVERS"):
            vm.validate(bad)

    def testNoBiosWrites(self):
        for field in ("firmwareFlashing","uefiOrBiosWrites","kernelModuleLoads",
                      "driverBindingChanges","packageInstalls","networkListenerStarts",
                      "releaseSigning","agentStarts","paidApiCalls"):
            with self.subTest(field=field):
                bad=copy.deepcopy(self.data)
                bad["safety"][field]=True
                with self.assertRaisesRegex(vm.ProfileError,"UNAUTHORIZED_OPERATION"):
                    vm.validate(bad)

    def testNoInventedNorthbridgeInAndroid(self):
        bad=copy.deepcopy(self.data)
        bad["rows"][2]["id"]="legacyPc"
        with self.assertRaisesRegex(vm.ProfileError,"MATRIX_AXES"):
            vm.validate(bad)

    def testNoFalsePhysicalProof(self):
        bad=copy.deepcopy(self.data)
        bad["claimPhysicalChipset"]=True
        with self.assertRaisesRegex(vm.ProfileError,"NO_HARDWARE_PROOF"):
            vm.validate(bad)

    def testDeclaringDoesNotInstall(self):
        declaration=Path(vm.ROOT/".devcontainer/Dockerfile").read_text()
        pkgs=vm.parse_declared_apt(declaration)
        self.assertEqual(len(pkgs),34)
        self.assertEqual(len(set(pkgs)),34)

    def testRejectDuplicateAptAndShellInjection(self):
        for text in ("apt-get install -y --no-install-recommends python3 python3;",
            "apt-get install -y --no-install-recommends python3 $(id);",
            "apt-get install -y --no-install-recommends python3; apt-get install -y --no-install-recommends curl;"):
            with self.subTest(text=text), self.assertRaises(vm.ProfileError):
                vm.parse_declared_apt(text)

    def testNoAliasPretendsToBeFirmwareAddress(self):
        bad=copy.deepcopy(self.data)
        bad["matrix"][0]["address"]="0xF000"
        with self.assertRaisesRegex(vm.ProfileError,"CELL_MISMATCH"):
            vm.validate(bad)

    def testVendorLicensesNotRelabeled(self):
        bad=copy.deepcopy(self.data)
        bad["vendorBoundaries"]["blenderHasGPLLicense"]=False
        with self.assertRaisesRegex(vm.ProfileError,"LICENSING_OR_VENDOR_SAFETY"):
            vm.validate(bad)

    def testDoNotEnablePackageInstallAuthority(self):
        bad=copy.deepcopy(self.data)
        bad["debian"]["packageInstallAuthorized"]=True
        with self.assertRaisesRegex(vm.ProfileError,"DEBIAN_AUTHORITY"):
            vm.validate(bad)

if __name__=="__main__":
    unittest.main()
