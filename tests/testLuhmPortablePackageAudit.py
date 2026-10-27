"""Negative and positive controls for the LuHm cross-platform packaging contract."""
import importlib.util
import json
import copy
from pathlib import Path
from unittest import TestCase, main
import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("luhmPortablePackageAudit", ROOT / "tools/luhmPortablePackageAudit.py")
tool = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tool)
POLICY = yaml.safe_load((ROOT/"doctrine/universalPackageMatrixV1.yaml").read_text(encoding="utf-8"))


class PortablePackageTests(TestCase):
    def test_one_shared_payload_eight_independent_packaging_adapters(self):
        result = tool.audit(POLICY)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["status"], "GREEN_SOURCE_INVENTORY_ONLY")
        self.assertEqual(len(result["candidateFormats"]), 8)
        self.assertGreaterEqual(len(result["sharedAssets"]), 6)
        self.assertGreater(result["sharedAssetBytes"], 1000)
        for e in result["sharedAssets"]:
            self.assertEqual(len(e["sha256"]), 64)
            self.assertTrue(e["path"].startswith("frontEnd/"))
        self.assertFalse(result["releaseArtifactGenerated"])
        self.assertFalse(result["androidSignedOrInstalled"])

    def test_android_vs_ubuntu_native_abi_must_not_be_conflated(self):
        candidate=copy.deepcopy(POLICY)
        candidate["abis"]["linuxGlibcIsAndroidBionic"]=True
        self.assertIn("RED_NATIVE_ABI",tool.audit(candidate)["errors"])

    def test_npm_is_not_a_published_driver_or_android_package(self):
        candidate=copy.deepcopy(POLICY)
        candidate["outputs"]["npm"]["currentPackagePrivate"]=False
        self.assertIn("RED_NPM_PRIVATE",tool.audit(candidate)["errors"])

    def test_no_false_samsung_install(self):
        candidate=copy.deepcopy(POLICY)
        candidate["outputs"]["android"]["signingProven"]=True
        self.assertIn("RED_ANDROID_SIGNER",tool.audit(candidate)["errors"])

    def test_no_fake_chatgpt_gui_proof(self):
        candidate=copy.deepcopy(POLICY)
        candidate["outputs"]["chatGpt"]["nativeHostMount"]="GREEN"
        self.assertIn("RED_CHAT_MOUNT",tool.audit(candidate)["errors"])

    def test_no_server_api_keys_inside_webview(self):
        candidate=copy.deepcopy(POLICY)
        candidate["architecture"]["proprietaryApiAdaptersOnlyServerSideAndOptIn"]=False
        self.assertIn("RED_VENDOR",tool.audit(candidate)["errors"])

    def test_path_traversal_rejected(self):
        candidate=copy.deepcopy(POLICY)
        candidate["architecture"]["immutablePayloadComponents"][0]="../secrets.txt"
        self.assertIn("RED_PATH_ESCAPE",tool.audit(candidate)["errors"])

    def test_missing_asset_not_silently_elided(self):
        candidate=copy.deepcopy(POLICY)
        candidate["architecture"]["immutablePayloadComponents"][0]="frontEnd/file-does-not-exist.js"
        self.assertTrue(any(x.startswith("RED_SHARED_FILE_MISSING_") for x in tool.audit(candidate)["errors"]))

    def test_claimed_output_build_rejected(self):
        candidate=copy.deepcopy(POLICY)
        candidate["outputs"]["oci"]["generated"]=True
        self.assertIn("RED_FALSE_BUILD_oci",tool.audit(candidate)["errors"])

    def test_never_downloads_or_executes_toolchains(self):
        source=(ROOT/"tools/luhmPortablePackageAudit.py").read_text()
        self.assertNotIn("subprocess",source)
        self.assertNotIn("urllib",source)
        self.assertNotIn("requests",source)
        self.assertNotIn("os.system",source)
        self.assertNotIn("os.environ",source)
        self.assertNotIn("shutil",source)

if __name__ == "__main__":
    main()
