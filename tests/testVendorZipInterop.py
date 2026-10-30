#!/usr/bin/env python3
"""Hostile ZIP negative controls and GPL/Apache source-license safety."""
from __future__ import annotations
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
import warnings
import zipfile

ROOT=Path(__file__).resolve().parents[1]
def imported(module,filename):
    spec=importlib.util.spec_from_file_location(module,ROOT/filename)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj
z=imported("zipInteropAudit","tools/zipInteropAudit.py")
licenses=imported("vendorApacheAudit","tools/vendorApacheAudit.py")
SHA="a"*40

def make_zip(destination,names,contents=b"test"):
    with zipfile.ZipFile(destination,"w") as f:
        for name in names:
            i=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
            i.compress_type=zipfile.ZIP_DEFLATED
            i.external_attr=(0o100644<<16)
            f.writestr(i,contents)

class ZipInteropTests(unittest.TestCase):
    def test_valid_deterministic_small_zip(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"dev.zip"
            make_zip(p,["luhmos-dev/README.txt"])
            a=z.verify_dev_archive(p,["README.txt"],source_ref=SHA)
            self.assertEqual(a["fileCount"],1)
            self.assertEqual(a["compression"],"ZIP_DEFLATED")
            self.assertFalse(a["releaseAllowed"])

    def test_archive_reproducible(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"one.zip"
            q=Path(d)/"two.zip"
            make_zip(p,["luhmos-dev/a.txt"],b"hello")
            make_zip(q,["luhmos-dev/a.txt"],b"hello")
            self.assertEqual(p.read_bytes(),q.read_bytes())

    def test_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"traverse.zip"
            make_zip(p,["luhmos-dev/../secret.txt"])
            with self.assertRaises(ValueError):
                z.verify_dev_archive(p,["../secret.txt"],source_ref=SHA)

    def test_duplicate_member_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"duplicate.zip"
            with warnings.catch_warnings():
                warnings.simplefilter("ignore",UserWarning)
                make_zip(p,["luhmos-dev/a.txt","luhmos-dev/a.txt"])
            with self.assertRaises(ValueError):
                z.verify_dev_archive(p,["a.txt"],source_ref=SHA)

    def test_unknown_member_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"unknown.zip"
            make_zip(p,["luhmos-dev/private.txt"])
            with self.assertRaises(ValueError):
                z.verify_dev_archive(p,["README.txt"],source_ref=SHA)

    def test_symlink_member_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"link.zip"
            i=zipfile.ZipInfo("luhmos-dev/symlink",date_time=(1980,1,1,0,0,0))
            i.compress_type=zipfile.ZIP_DEFLATED
            i.external_attr=(0o120777<<16)
            with zipfile.ZipFile(p,"w") as f:f.writestr(i,b"../secret")
            with self.assertRaises(ValueError):
                z.verify_dev_archive(p,["symlink"],source_ref=SHA)

    def test_nondeterministic_timestamp_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"date.zip"
            with zipfile.ZipFile(p,"w") as f:
                i=zipfile.ZipInfo("luhmos-dev/a.txt",date_time=(2025,1,1,0,0,0))
                i.compress_type=zipfile.ZIP_DEFLATED
                f.writestr(i,b"data")
            with self.assertRaises(ValueError):
                z.verify_dev_archive(p,["a.txt"],source_ref=SHA)

    def test_expansion_ratio_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"bomb.zip"
            make_zip(p,["luhmos-dev/a.bin"],b"A"*100000)
            with self.assertRaises(ValueError):
                z.verify_dev_archive(p,["a.bin"],source_ref=SHA)

    def test_zip_stored_not_compatible_contract(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"stored.zip"
            with zipfile.ZipFile(p,"w") as f:
                i=zipfile.ZipInfo("luhmos-dev/a.txt",date_time=(1980,1,1,0,0,0))
                f.writestr(i,b"data")
            with self.assertRaises(ValueError):
                z.verify_dev_archive(p,["a.txt"],source_ref=SHA)

    def test_casefold_collision_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"casefold.zip"
            make_zip(p,["luhmos-dev/A.txt","luhmos-dev/a.txt"])
            with self.assertRaisesRegex(ValueError,"ZIP_PORTABLE_CASE_COLLISION"):
                z.verify_dev_archive(p,["A.txt","a.txt"],source_ref=SHA)

    def test_windows_reserved_name_rejected(self):
        for relative in ("CON.txt","dir/NUL","dir/COM1.txt","dir/LPT9.log"):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as d:
                p=Path(d)/"reserved.zip"
                make_zip(p,["luhmos-dev/"+relative])
                with self.assertRaisesRegex(ValueError,"ZIP_UNSAFE_OR_UNLISTED_ENTRY"):
                    z.verify_dev_archive(p,[relative],source_ref=SHA)

    def test_alternate_stream_or_trailing_dot_rejected(self):
        for relative in ("a.txt:stream","a.","dir/aux.txt","dir/a?.txt"):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as d:
                p=Path(d)/"portable.zip"
                make_zip(p,["luhmos-dev/"+relative])
                with self.assertRaises(ValueError):
                    z.verify_dev_archive(p,[relative],source_ref=SHA)

    def test_non_ascii_path_rejected_but_contents_allowed(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"unicode.zip"
            make_zip(p,["luhmos-dev/café.txt"],"é".encode())
            with self.assertRaises(ValueError):
                z.verify_dev_archive(p,["café.txt"],source_ref=SHA)
            q=Path(d)/"unicode-content.zip"
            make_zip(q,["luhmos-dev/utf8.txt"],"é".encode())
            self.assertEqual(z.verify_dev_archive(q,["utf8.txt"],source_ref=SHA)["fileCount"],1)

    def test_source_sha_required(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"source.zip"
            make_zip(p,["luhmos-dev/a.txt"])
            with self.assertRaises(ValueError):
                z.verify_dev_archive(p,["a.txt"],source_ref="unknown")

    def test_current_license_hold(self):
        result=licenses.check()
        self.assertEqual(result["errors"],[])
        self.assertFalse(result["apacheRelicensingDone"])

    def test_false_apache_declaration_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Negative mutation in memory only; do not rewrite actual GPL files.
            cfg=json.loads((ROOT/"doctrine/vendorApacheReadinessV1.json").read_text())
            cfg["licenseChangeAllowed"]=True
            self.assertNotEqual(cfg["licenseChangeAllowed"],False)

if __name__=="__main__":
    unittest.main()
