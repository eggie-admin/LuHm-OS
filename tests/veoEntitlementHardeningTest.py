import importlib.util
import pathlib
import unittest
from unittest.mock import patch

root = pathlib.Path(__file__).resolve().parents[1]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, root / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

queue = load('queue', 'tools/yumeVertexVeoQueue.py')
preflight = load('preflight', 'host/api/luhmCloudVideoPreflight.py')

class EntitlementBoundaryTests(unittest.TestCase):
    def testLegacyDirectSubmitCannotAccessCredentialsOrNetwork(self):
        with patch('subprocess.run', side_effect=AssertionError('credentials accessed')), patch('urllib.request.urlopen', side_effect=AssertionError('network accessed')):
            with self.assertRaisesRegex(PermissionError, 'LEGACY_SUBMIT_DISABLED'):
                queue.submit_one('project-test', 'lum', {})

    def testLegacyCliRejectsEvenApprovedSpend(self):
        with self.assertRaisesRegex(SystemExit, 'LEGACY_SUBMIT_DISABLED'):
            queue.main(['--manifest', '/missing', '--submit', '--approve-spend', '--cost-ceiling-usd', 'nan'])

    def testApiEvidenceMustMatchProject(self):
        for providerProject in ('project-test', 'other-project', '123456789'):
            def response(url):
                if 'cloudbilling' in url:
                    return {'projectId': 'project-test', 'billingEnabled': True}
                return {'name': 'projects/' + providerProject + '/services/aiplatform.googleapis.com', 'state': 'ENABLED'}
            result = preflight.probe('project-test', response)
            self.assertEqual(result['vertexApi'], 'ENABLED' if providerProject == 'project-test' else 'INVALID_PROVIDER_RESPONSE')
            self.assertFalse(result['readyToSpend'])
            self.assertEqual(result['veoModelEntitlement'], 'UNVERIFIED')

if __name__ == '__main__':
    unittest.main()
