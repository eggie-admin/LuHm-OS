#!/usr/bin/env python3
"""Four separate release packages: negative gates and actual private DEV archive."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("fourPackageTrain",ROOT/"tools/fourPackageTrain.py")
package=importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)

class FourPackageTrainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy=package.load()
        mapping={"glassPkg":"frontEnd/prototypes/glassWorld/package.json",
           "glassLock":"frontEnd/prototypes/glassWorld/package-lock.json",
           "frontPkg":"frontEnd/package.json","webPkg":"packages/k9000-web/package.json",
           "presets":"export_presets.cfg","gradle":"androidWeb3Plugin/plugin/build.gradle.kts",
           "apkWorkflow":".github/workflows/android-testing-build.yml",
           "trainWorkflow":".github/workflows/four-package-train.yml"}
        cls.files={k:(ROOT/v).read_text(encoding="utf-8") for k,v in mapping.items()}

    def rejected(self,policy=None,files=None):
        return package.inspect(policy or self.policy,files or self.files,ROOT)

    def test_four_distinct_lanes(self):
        self.assertEqual(list(package.LANES),["dev","npm","dmg","apk"])
        self.assertEqual(self.rejected(),[])

    def test_remove_apk_rejected(self):
        policy=copy.deepcopy(self.policy)
        policy["lanes"].pop("apk")
        self.assertIn("EXACTLY_FOUR_LANES",self.rejected(policy=policy))

    def test_no_auto_publish(self):
        policy=copy.deepcopy(self.policy)
        policy["lanes"]["npm"]["publish"]=True
        self.assertIn("NO_PUBLICATION",self.rejected(policy=policy))

    def test_godot_duplicate_android_options_rejected(self):
        files=dict(self.files)
        files["presets"]=files["presets"].replace("[preset.3.options]","[preset.0.options]")
        self.assertIn("ONE_OPTIONS_SECTION_PER_PRESET",self.rejected(files=files))

    def test_unlocked_jquery_rejected(self):
        files=dict(self.files)
        data=json.loads(files["glassPkg"])
        data["dependencies"]["jquery"]="latest"
        files["glassPkg"]=json.dumps(data)
        self.assertIn("GLASS_RUNTIME_DEPS_PINNED",self.rejected(files=files))

    def test_public_json_private_file_excluded(self):
        policy=copy.deepcopy(self.policy)
        policy["sourceAllowlist"].append("private/avatar.glb")
        self.assertIn("PRIVATE_SOURCE_NOT_ALLOWLISTED",self.rejected(policy=policy))

    def test_traversal_and_unapproved_files_rejected(self):
        policy=copy.deepcopy(self.policy)
        policy["sourceAllowlist"].append("../private/secret.txt")
        self.assertIn("DEV_PATH_TRAVERSAL",self.rejected(policy=policy))

    def test_unapproved_apk_shortcut_rejected(self):
        policy=copy.deepcopy(self.policy)
        policy["lanes"]["apk"]["execution"]="PR_CI"
        self.assertIn("APK_NO_DUPLICATE_BYPASS",self.rejected(policy=policy))

    def test_npm_publish_step_rejected(self):
        files=dict(self.files)
        files["trainWorkflow"]+="\n npm publish --access public\n"
        self.assertIn("NO_REGISTRY_OR_GH_PUBLICATION",self.rejected(files=files))

    def test_build_real_dev_archive_reproducible(self):
        with tempfile.TemporaryDirectory() as temp:
            receipt1=package.build_dev(ROOT,Path(temp))
            archive=Path(temp)/self.policy["lanes"]["dev"]["artifact"]
            digest=receipt1["sha256"]
            with zipfile.ZipFile(archive) as z:
                names=z.namelist()
                self.assertEqual(len(names),len(self.policy["sourceAllowlist"]))
                self.assertTrue(all(name.startswith("luhmos-dev/") for name in names))
                self.assertTrue(all("private" not in name.lower() for name in names))
            receipt2=package.build_dev(ROOT,Path(temp))
            self.assertEqual(digest,receipt2["sha256"])
            self.assertEqual("PRIVATE_CI_CANDIDATE_NO_RELEASE",receipt2["status"])

if __name__=="__main__":
    unittest.main()
