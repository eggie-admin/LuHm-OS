"""Promotion gate hostile-fixture controls; no GitHub release is created."""
import hashlib
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

spec = importlib.util.spec_from_file_location("gate", Path(__file__).resolve().parents[1] / "tools/pluginReleasePromotionGate.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

SOURCE = "a" * 40
VERSION = "1.2.3"


class PromotionGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.filename = f"LuHm-OS-plugin-{VERSION}-{SOURCE[:8]}.zip"
        self.package = self.root / self.filename
        with zipfile.ZipFile(self.package, "w") as archive:
            archive.writestr("plugin.json", json.dumps({"name": "luhm-os", "version": VERSION}))
            archive.writestr("BUILD_RECEIPT.json", json.dumps({
                "sourceRef": SOURCE, "status": "PACKAGE_READY_ONLY",
                "hostInstalled": False, "inChatToolInvoked": False}))
        self.digest = hashlib.sha256(self.package.read_bytes()).hexdigest()
        self.receipt = {
            "schema": "luhmOs.publicPluginPackageBuildReceipt.v2",
            "status": "BUILT_BY_CAST_SCOPE", "sourceRef": SOURCE,
            "buildScope": "publicPluginPackage",
            "artifact": {"filename": self.filename, "sha256": self.digest, "bytes": self.package.stat().st_size},
            "publicationAuthority": False, "releaseAuthority": False, "crownAuthority": False,
        }
        self.save()

    def save(self):
        (self.root / "publicPluginPackageBuildReceipt.json").write_text(json.dumps(self.receipt), encoding="utf-8")

    def inspect(self, channel="proposed", digest=None, acceptance=None):
        return gate.inspect(self.root, channel, SOURCE, digest or self.digest, acceptance)

    def test_valid_proposed_package_only(self):
        result = self.inspect()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["crownStatus"], "STOP")
        self.assertFalse(result["hostAndDeviceVerifiedByThisScript"])

    def test_beta_and_stable_need_independent_proof(self):
        for channel in ("beta", "stable"):
            with self.subTest(channel=channel):
                self.assertEqual(self.inspect(channel)["status"], "RED")

    def test_reject_wrong_digest(self):
        self.assertEqual(self.inspect(digest="0" * 64)["status"], "RED")

    def test_reject_source_mismatch(self):
        self.receipt["sourceRef"] = "b" * 40
        self.save()
        self.assertEqual(self.inspect()["status"], "RED")

    def test_reject_embedded_false_host_proof(self):
        with zipfile.ZipFile(self.package, "w") as archive:
            archive.writestr("plugin.json", json.dumps({"name": "luhm-os", "version": VERSION}))
            archive.writestr("BUILD_RECEIPT.json", json.dumps({
                "sourceRef": SOURCE, "status": "PACKAGE_READY_ONLY",
                "hostInstalled": True, "inChatToolInvoked": False}))
        self.digest = hashlib.sha256(self.package.read_bytes()).hexdigest()
        self.receipt["artifact"]["sha256"] = self.digest
        self.receipt["artifact"]["bytes"] = self.package.stat().st_size
        self.save()
        self.assertEqual(self.inspect()["status"], "RED")

    def test_reject_publication_authority_smuggling(self):
        self.receipt["publicationAuthority"] = True
        self.save()
        self.assertEqual(self.inspect()["status"], "RED")

    def test_reject_fake_short_acceptance(self):
        document = self.root / "acceptance.json"
        document.write_text(json.dumps({"status": "PROVED", "sourceRef": SOURCE, "channel": "beta", "sha256": self.digest,
                                        "externalChatGptHostInstallReceipt": "OK"}), encoding="utf-8")
        self.assertEqual(self.inspect("beta", acceptance=document)["status"], "RED")


if __name__ == "__main__":
    unittest.main()
