import json
import tempfile
import unittest
from pathlib import Path
from tools.k9000PublicReadiness import inspect, ROOT

class PublicReadinessTests(unittest.TestCase):
    def test_preflight_not_release(self):
        receipt=inspect(ROOT)
        self.assertEqual(20,receipt["sourceChecks"])
        self.assertEqual([],receipt["sourceFailures"])
        self.assertFalse(receipt["publishReady"])
        self.assertTrue(receipt["publicationBlockers"])
        self.assertFalse(receipt["apkBuiltOrUploaded"])
    def test_corrupt_license_fails_closed(self):
        files=[
          "LICENSE", "frontEnd/k9000.html", "frontEnd/brand/k9000-cathedral-mark.svg",
          "androidWeb3Plugin/plugin/src/main/java/art/eggiebagelface/luhmos/web3/AndroidWeb3CockpitPlugin.kt",
          "export_presets.cfg","doctrine/k9000CrownCathedralReleaseV1.json",
          "fastlane/metadata/android/en-US/short_description.txt",
          "project.godot","frontEnd/brand/k9000-main-192.png",
          "frontEnd/brand/k9000-adaptive-432.png",
          "fastlane/metadata/android/en-US/images/icon.png",
          "fastlane/metadata/android/en-US/full_description.txt"
        ]
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)
            for f in files:
                t=target/f
                t.parent.mkdir(parents=True,exist_ok=True)
                t.write_bytes((ROOT/f).read_bytes())
            (target/"LICENSE").write_text("No license",encoding="utf-8")
            result=inspect(target)
            self.assertIn("gpl3License",result["sourceFailures"])
            self.assertFalse(result["publishReady"])
if __name__=="__main__":
    unittest.main()
