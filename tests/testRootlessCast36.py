"""Doctrine negative controls. Green source audit does not claim a Samsung APK."""
import copy
import json
import unittest
from tools.rootlessCast36Audit import POLICY, verify


class TestCast36(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads(POLICY.read_text(encoding='utf8'))
    def drift(self,section,field,value,code):
        doc=copy.deepcopy(self.doc)
        doc[section][field]=value
        self.assertIn(code,verify(doc))
    def test_valid_source(self):self.assertEqual(verify(self.doc),[])
    def test_exact_six_by_six(self):
        doc=copy.deepcopy(self.doc)
        doc['expansion']['gates'].pop()
        self.assertIn('GATE_SET',verify(doc))
    def test_exact_four_by_four(self):
        doc=copy.deepcopy(self.doc)
        doc['foundation']['cells'].pop()
        self.assertIn('FOUNDATION_COVERAGE',verify(doc))
    def test_no_claim_apk(self):self.drift('rootless','nativeApkBuilt',True,'ROOTLESS_FALSE_PROOF_nativeApkBuilt')
    def test_no_root(self):self.drift('rootless','requiresRoot',True,'ROOTLESS_FALSE_PROOF_requiresRoot')
    def test_no_cloud(self):self.drift('rootless','cloudApisCalled',True,'ROOTLESS_FALSE_PROOF_cloudApisCalled')
    def test_no_device_proof(self):self.drift('expansion','hardwareProven',1,'FAKE_RUNTIME_GREEN')
    def test_no_firmware(self):self.drift('storage','firmwareWrite',True,'SQLITE_FIRMWARE_OR_FALSE_MIGRATION')
    def test_no_model_score_fabrication(self):self.drift('aiBenchmarkLaw','crossVendorScoreClaims',True,'AI_BENCHMARK_TRUTH')
    def test_no_deprecated_openai_evals(self):self.drift('aiBenchmarkLaw','relianceOnOpenAiEvalsApiDeprecated',True,'AI_BENCHMARK_TRUTH')
    def test_no_unreal_claim(self):self.drift('engineChain','unreal','SHIPPED','ENGINE_BOUNDARY')
    def test_no_auto_publish(self):self.drift('release','publish',True,'RELEASE_BOUNDARY_publish')
    def test_no_unsupervised_signing(self):self.drift('release','signAutomatically',True,'RELEASE_BOUNDARY_signAutomatically')
    def test_no_fake_avatar(self):self.drift('persona','realAvatarRigProven',True,'AVATAR_REALITY')
    def test_minimal_deps(self):self.drift('rootless','pythonDependencies',['opencv-python'],'NONSTANDARD_PYTHON_DEPS')


if __name__ == '__main__':unittest.main()
