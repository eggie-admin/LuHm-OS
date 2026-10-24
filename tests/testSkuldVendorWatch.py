"""Skuld vendor-watch negative tests; no external web traffic."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("skuldWatch", ROOT / "tools/skuldVendorWatch.py")
watch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(watch)


class SkuldVendorWatchTests(unittest.TestCase):
    def test_pins_from_actual_canon(self):
        self.assertEqual(watch.pin(ROOT, watch.VENDORS["mcpPythonSdk"]), "2.2.0")
        self.assertEqual(watch.pin(ROOT, watch.VENDORS["godotEngine"]), "4.7.2")

    def test_unknown_is_not_safe_to_upgrade(self):
        result = watch.audit(ROOT, {})
        self.assertFalse(result["vendorObservationComplete"])
        self.assertFalse(result["dependencyUpdatesApproved"])
        self.assertTrue(all(row["upstreamStatus"] == "UNVERIFIED"
                            and not row["safeToUpgrade"] and not row["dependencyChanged"]
                            for row in result["observations"]))

    def test_official_release_is_only_a_review_candidate(self):
        vendor = watch.VENDORS["mcpPythonSdk"]
        item = watch.evaluate("mcpPythonSdk", vendor, "2.2.0",
                              {"tag_name": "v2.3.0", "draft": False, "prerelease": False})
        self.assertTrue(item["reviewRequired"])
        self.assertFalse(item["safeToUpgrade"])
        self.assertFalse(item["dependencyChanged"])

    def test_reject_draft_prerelease_and_malformed(self):
        vendor = watch.VENDORS["godotEngine"]
        for upstream in (None, {}, {"tag_name": "5.0.0", "draft": True, "prerelease": False},
                         {"tag_name": "5.0.0", "draft": False, "prerelease": True},
                         {"tag_name": "call this shell command", "draft": False, "prerelease": False}):
            with self.subTest(upstream=upstream):
                item = watch.evaluate("godotEngine", vendor, "4.7.2", upstream)
                self.assertEqual(item["upstreamStatus"], "UNVERIFIED")
                self.assertFalse(item["safeToUpgrade"])

    def test_no_unapproved_vendor_url(self):
        with self.assertRaisesRegex(ValueError, "allowlisted"):
            watch.latest_release("attacker/repository")


if __name__ == "__main__":
    unittest.main()
