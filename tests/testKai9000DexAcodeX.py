"""KAI 9000 source-only device layout and historic AcodeX boundary checks."""
import unittest
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "doctrine/kai9000SamsungDexAcodeXV1.yaml"
CSS = ROOT / "frontEnd/styles.css"
HTML = ROOT / "frontEnd/index.html"
WEBVIEW = ROOT / "androidWeb3Plugin/plugin/src/main/java/art/eggiebagelface/luhmos/web3/AndroidWeb3CockpitPlugin.kt"


def validate(config: dict, css: str, html: str, webview: str) -> list[str]:
    faults = []
    def require(cond, key):
        if not cond:
            faults.append(key)

    require(config.get("schema") == "luhmOs.kai9000SamsungDexAcodeX.v1", "schema")
    require(config.get("status") == "SOURCE_CANDIDATE_NOT_RELEASED", "candidate")
    require(config.get("crownStatus") == "STOP" and
            config.get("buildProof", {}).get("publicRelease") is False, "crown")
    require(config.get("operationalHierarchy", {}).get("liveState") == "existingApprovedPrivateSql", "sqlFirst")
    require(config.get("operationalHierarchy", {}).get("portableConfiguration") == "reviewedYaml", "yamlSecond")
    devices = config.get("deviceProfiles", {})
    tablet = devices.get("samsungTablet", {})
    phone = devices.get("samsungPhone", {})
    require(tablet.get("actualDexSupport") == "NOT_VERIFIED_ON_DEVICE", "dexTruth")
    require(tablet.get("noTermuxOrAcodeDependency") is True, "optionalTools")
    require(phone.get("secureFolderDataSeparate") is True and
            phone.get("localAppDataCopiedAcrossProfiles") is False, "secureFolderIsolation")
    require(phone.get("actualInstallVerified") is False, "installTruth")
    bridge = config.get("acodeXHistorical", {})
    require(bridge.get("sameDeviceLoopbackOnly") is True and
            bridge.get("differentDevicesCannotShareLocalhost") is True, "sameDeviceOnly")
    require(bridge.get("latestRevalidation") == "PENDING" and
            bridge.get("rebootPersistence") == "NOT_VERIFIED", "bridgeEvidence")
    require(bridge.get("noAXSPublicBind") is True and
            bridge.get("noCurlPipeShellAutoInstall") is True, "bridgeSecurity")
    antenna = config.get("antenna", {})
    require(antenna.get("tabletToPhoneTransport") == "NOT_IMPLEMENTED" and
            antenna.get("doNotProxyLocalhostAcrossDevices") is True, "noCrossDeviceLocalhost")
    require(antenna.get("edge") == "outboundAuthenticatedWssTlsOnlyAfterAuthorization"
            and antenna.get("publicInboundTermuxVncOllama") == "FORBIDDEN"
            and antenna.get("noNewWebhooksOrPorts") is True, "outboundOnly")
    require(config.get("appIdentity", {}).get("noSilentPackageIdSwitch") is True, "appId")
    require(config.get("appIdentity", {}).get("historicalCathedralVersionIsNotUniversalUpgradeProof") is True, "oldApkNotUpgradeProof")
    require(config.get("buildProof", {}).get("currentSourceApkBuiltByThisPr") is False and
            config.get("buildProof", {}).get("sourceCIIsNotDeviceProof") is True, "sourceCannotProveApk")
    require("@media (min-width: 980px) and (min-height: 600px)" in css and
            ".scene { right: 34%; bottom: 0; }" in css and
            "width: 34%;" in css, "desktopLayout")
    require("@media (max-height: 539px)" in css and
            ".cockpit { min-height: 0; }" in css, "smallWindow")
    require(":focus-visible" in css and "min-height: 44px;" in css, "inputAccessibility")
    require('data-luhm-cockpit' in html and
            'data-luhm-chat' in html and 'data-luhm-lum-viewport' in html, "originalSlots")
    require('LOCAL_ORIGIN = "https://appassets.androidplatform.net"' in webview
            and "WebViewAssetLoader.Builder()" in webview, "webViewOrigin")
    require("allowFileAccess = false" in webview and
            "allowContentAccess = false" in webview and
            "WebSettings.MIXED_CONTENT_NEVER_ALLOW" in webview, "assetSandbox")
    require("setOf(LOCAL_ORIGIN)" in webview and
            "WebViewCompat.addWebMessageListener" in webview
            and "if (!isMainFrame || sourceOrigin.toString() != LOCAL_ORIGIN)" in webview, "nativeBridge")
    require("Runtime.getRuntime().exec(" not in webview and "addJavascriptInterface(" not in webview, "noShellApi")
    return faults


class KAI9000Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
        cls.css = CSS.read_text(encoding="utf-8")
        cls.html = HTML.read_text(encoding="utf-8")
        cls.kotlin = WEBVIEW.read_text(encoding="utf-8")

    def test_actual_candidate(self):
        self.assertEqual(validate(self.policy,self.css,self.html,self.kotlin), [])

    def test_reject_fake_dex_proof(self):
        conf=yaml.safe_load(POLICY.read_text())
        conf["deviceProfiles"]["samsungTablet"]["actualDexSupport"]="GREEN"
        self.assertIn("dexTruth",validate(conf,self.css,self.html,self.kotlin))

    def test_reject_cross_device_localhost(self):
        conf=yaml.safe_load(POLICY.read_text())
        conf["acodeXHistorical"]["differentDevicesCannotShareLocalhost"]=False
        self.assertIn("sameDeviceOnly",validate(conf,self.css,self.html,self.kotlin))

    def test_reject_public_termux_inbound(self):
        conf=yaml.safe_load(POLICY.read_text())
        conf["antenna"]["publicInboundTermuxVncOllama"]="ALLOWED"
        self.assertIn("outboundOnly",validate(conf,self.css,self.html,self.kotlin))

    def test_reject_historical_apk_promoted_without_proof(self):
        conf=yaml.safe_load(POLICY.read_text())
        conf["buildProof"]["currentSourceApkBuiltByThisPr"]=True
        self.assertIn("sourceCannotProveApk",validate(conf,self.css,self.html,self.kotlin))

    def test_fail_if_bridge_origin_unbounded(self):
        kotlin=self.kotlin.replace("setOf(LOCAL_ORIGIN)",'setOf("*")')
        self.assertIn("nativeBridge",validate(self.policy,self.css,self.html,kotlin))

    def test_fail_if_minimal_window_support_removed(self):
        css=self.css.replace(".cockpit { min-height: 0; }","")
        self.assertIn("smallWindow",validate(self.policy,css,self.html,self.kotlin))

if __name__ == "__main__":
    unittest.main()
