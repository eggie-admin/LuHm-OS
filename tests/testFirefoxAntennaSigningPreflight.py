"""Signing-preflight tests: no fake XPI, no TLS key misuse, no remote code."""
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from tools import firefoxAntennaSigningPreflight as signer

ROOT = Path(__file__).resolve().parents[1]


class FirefoxSigningPreflightTests(unittest.TestCase):
    def test_exact_signing_metadata(self):
        manifest, source = signer.inspect_package_source(ROOT)
        self.assertEqual(manifest["browser_specific_settings"]["gecko"]["data_collection_permissions"],
                         {"required": ["none"]})
        self.assertEqual(len(source), 4)

    def test_deterministic_zip_without_signature(self):
        first, r1 = signer.build_source_zip(ROOT, "a" * 40)
        second, r2 = signer.build_source_zip(ROOT, "a" * 40)
        self.assertEqual(first, second)
        self.assertEqual(r1, r2)
        self.assertEqual(r1["packageSha256"], hashlib.sha256(first).hexdigest())
        self.assertLess(r1["uncompressedShellBytes"], 100_000_000)
        self.assertFalse(r1["mozillaSignaturePresent"])
        self.assertFalse(r1["amoSubmissionPerformed"])
        self.assertEqual(r1["verdict"], "PACKAGE_SOURCE_READY_NOT_SIGNED")
        with zipfile.ZipFile(io.BytesIO(first)) as z:
            self.assertEqual(z.namelist(), list(signer.FILES))
            self.assertEqual(z.testzip(), None)
            self.assertTrue(all(info.date_time[:3] == (1980, 1, 1)
                                for info in z.infolist()))
            self.assertFalse(any(name.startswith("META-INF/") for name in z.namelist()))
            self.assertEqual(z.read("manifest.json"), (ROOT / signer.REL / "manifest.json").read_bytes())

    def test_invalid_ref_fails(self):
        with self.assertRaises(ValueError):
            signer.build_source_zip(ROOT, "../stale")

    def test_policy_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp)
            folder = fake / signer.REL
            folder.mkdir(parents=True)
            for name in signer.FILES:
                (folder / name).write_bytes((ROOT / signer.REL / name).read_bytes())
            manifest = json.loads((folder / "manifest.json").read_text())
            manifest["browser_specific_settings"]["gecko"]["data_collection_permissions"] = {
                "required": ["browsingActivity"]
            }
            (folder / "manifest.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "AMO_PACKAGE_POLICY_DRIFT"):
                signer.inspect_package_source(fake)

    def test_unreviewed_script_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp)
            folder = fake / signer.REL
            folder.mkdir(parents=True)
            for name in signer.FILES:
                (folder / name).write_bytes((ROOT / signer.REL / name).read_bytes())
            (folder / "remote.js").write_text("alert('not approved')")
            with self.assertRaisesRegex(ValueError, "UNREVIEWED_EXTENSION_FILE_SET"):
                signer.inspect_package_source(fake)


if __name__ == "__main__":
    unittest.main()
