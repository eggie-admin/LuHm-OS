"""The GPL license must travel with the public LuHm developer ZIP.

Source inspection only: does not build or publish a package and does not
claim that third-party media rights are conveyed by GPL alone.
"""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "pluginPackage", ROOT / "tools/buildPublicPluginPackage.py"
)
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


class PublicPackageLicenseTests(unittest.TestCase):
    def test_real_collector_includes_exact_license(self):
        payload, version = package.collect("a" * 40)
        self.assertEqual(package.REPO_MEMBERS, ("LICENSE",))
        self.assertEqual(payload["LICENSE"], (ROOT / "LICENSE").read_bytes())
        self.assertIn(b"GNU GENERAL PUBLIC LICENSE", payload["LICENSE"])
        self.assertIn("SOURCE_MAP.json", payload)
        self.assertIn("BUILD_RECEIPT.json", payload)
        self.assertEqual(len(payload), len(package.MEMBERS) + 3)
        self.assertTrue(version)

    def test_license_is_in_integrity_source_map(self):
        import json
        import hashlib
        payload, _ = package.collect("b" * 40)
        source_map = json.loads(payload["SOURCE_MAP.json"])
        self.assertEqual(
            source_map["members"]["LICENSE"],
            hashlib.sha256((ROOT / "LICENSE").read_bytes()).hexdigest()
        )

    def test_collector_rejects_wrong_source_ref(self):
        with self.assertRaisesRegex(ValueError, "sourceRef"):
            package.collect("main")


if __name__ == "__main__":
    unittest.main()
