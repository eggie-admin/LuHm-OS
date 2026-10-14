import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import fullSourceTruthAudit as audit


class FullSourceTruthFailClosedTests(unittest.TestCase):
    def test_scopedLabelsCannotProveReadiness(self):
        for value in ('GREEN_HOST_UNVERIFIED', 'NOT_GREEN', 'GREEN_CANDIDATE', False, None, 1):
            with self.subTest(value=value):
                self.assertFalse(audit.normalized_good(value))
        for value in ('GREEN', 'PASS', 'VERIFIED', 'PROVEN', True):
            self.assertTrue(audit.normalized_good(value))

    def runFixture(self, invalid):
        original = audit.load
        def load(path):
            data = copy.deepcopy(original(path))
            if path == audit.SOURCE:
                data['authority'] = 'invalid' if invalid else 'Professor'
                data['status'] = 'PROPOSED'
                data['enterpriseReady'] = True
                data['cockpitSwitch'] = {'physicalS24FeProof': 'PASS'}
                data['installPortal'] = dict.fromkeys(('lanDnsActivation', 'apacheActivation', 'physicalS24FeInstall', 'fdroidRepositorySigning'), 'PASS')
            elif path == audit.SAMSUNG_SEAL:
                data['status'] = 'PASS'
                data['remaining'] = []
            return data
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'receipt.json'
            with patch.object(audit, 'load', side_effect=load), patch('sys.argv', ['audit', '--output', str(output)]), contextlib.redirect_stdout(io.StringIO()):
                if invalid:
                    with self.assertRaises(SystemExit):
                        audit.main()
                else:
                    self.assertEqual(audit.main(), 0)
            return json.loads(output.read_text())

    def test_contractErrorIsRedEvenWithoutBlockers(self):
        report = self.runFixture(True)
        self.assertEqual(report['blockers'], [])
        self.assertTrue(report['contractErrors'])
        self.assertEqual(report['status'], 'RED_FULL_SOURCE_TRUTH_CONTRACT_ERROR')
        self.assertFalse(report['milestoneMutationComplete'])
        self.assertTrue(all(item['status'] == 'RED' for item in report['tenPassAudit']))

    def test_legacyPassDoesNotClaimFullSystem(self):
        report = self.runFixture(False)
        self.assertEqual(report['status'], 'GREEN_FULL_SOURCE_TRUTH_READY')
        self.assertEqual(report['scope'], 'historicalCompatibilityReadinessOnly')
        self.assertEqual(report['currentCanonicalSource'], 'doctrine/currentSourceTruthV3.json')
        self.assertFalse(report['fullSystemReadinessProven'])

if __name__ == '__main__':
    unittest.main()
