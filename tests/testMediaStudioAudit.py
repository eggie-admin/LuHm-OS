"""Negative-control coverage for 4x4 media / vendor / native VLC boundaries."""
import copy,json,unittest
from tools.mediaStudioAudit import POLICY,audit,inspect_sources
class MediaStudioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=json.loads(POLICY.read_text(encoding="utf-8"))
    def fault(self,section,key,value,expected):
        p=copy.deepcopy(self.p);p[section][key]=value
        self.assertIn(expected,audit(p))
    def test_01_valid_source_and_real_pruning(self):
        self.assertEqual(audit(self.p),[]);self.assertEqual(inspect_sources(),[])
    def test_02_actual_four_by_four(self):
        self.assertEqual(len(self.p["matrix"]["cells"]),16)
        self.assertEqual(len(set((c["row"],c["column"]) for c in self.p["matrix"]["cells"])),16)
    def test_03_no_fake_hardware(self):self.fault("matrix","realHardwareTestsByPolicy",1,"FAKE_TESTS")
    def test_04_no_jquery_vendor(self):self.fault("vendor","isolatedPrototypeJqueryPackageExpected",True,"VENDOR_SCOPE_isolatedPrototypeJqueryPackageExpected")
    def test_05_legacy_still_intact(self):self.fault("vendor","legacyJqueryWorkspaceIntact",False,"LEGACY_OR_PYTHON_VENDOR")
    def test_06_no_extra_python_packages(self):self.fault("vendor","pythonPackagesAdded",7,"LEGACY_OR_PYTHON_VENDOR")
    def test_07_no_new_renderer(self):self.fault("vendor","rendererAdded",True,"VENDOR_SCOPE_rendererAdded")
    def test_08_disable_external_urls(self):self.fault("media","remoteUrlsAllowed",True,"MEDIA_UNSAFE_remoteUrlsAllowed")
    def test_09_no_auto_play(self):self.fault("media","autoplay",True,"MEDIA_UNSAFE_autoplay")
    def test_10_keep_webp_as_derivative(self):self.fault("media","webpEditableMaster",True,"IMAGE_MASTER_BOUNDARY")
    def test_11_reject_fake_samsung_decode(self):self.fault("media","mediaDecodeVerifiedOnSamsung",True,"MEDIA_UNSAFE_mediaDecodeVerifiedOnSamsung")
    def test_12_vlc_browser_plugin_removed(self):self.fault("vlc","browserPluginSupported",True,"VLC_FALSE_PROOF_browserPluginSupported")
    def test_13_native_vlc_not_installed(self):self.fault("vlc","aarInstalled",True,"VLC_FALSE_PROOF_aarInstalled")
    def test_14_no_open_vlc_http(self):self.fault("vlc","serverVlcHttpInterfaceAllowed",True,"VLC_FALSE_PROOF_serverVlcHttpInterfaceAllowed")
    def test_15_no_arbitrary_ping(self):self.fault("pings","remoteHostScanAllowed",True,"PING_ALLOWLIST")
    def test_16_no_provider_ping(self):self.fault("pings","providerApiPingsWithoutAuthorization",True,"PING_ALLOWLIST")
    def test_17_no_fake_3d_engine(self):self.fault("asset3d","glbImportBuilt",True,"FAKE_3D")
if __name__=="__main__":unittest.main()
