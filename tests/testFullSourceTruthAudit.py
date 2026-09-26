import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('audit', Path(__file__).resolve().parents[1] / 'tools/fullSourceTruthAudit.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

class ReadinessTests(unittest.TestCase):
    def test_qualified_green_is_not_full_proof(self):
        for value in ('GREEN_PENDING', 'GREEN_CI_DEVICE_PROOF_PENDING', 'NOT_GREEN', None, 1):
            self.assertFalse(audit.normalized_good(value), value)
        for value in ('PASS', 'VERIFIED', 'GREEN', True):
            self.assertTrue(audit.normalized_good(value), value)

    def report(self, corrupt=False):
        original = audit.load
        def load(path):
            data = original(path)
            if corrupt and path == audit.SOURCE:
                data['authority'] = 'NotProfessor'
            return data
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'report.json'
            with patch.object(audit, 'load', load), patch('sys.argv', ['audit', '--output', str(output)]), contextlib.redirect_stdout(io.StringIO()):
                if corrupt:
                    with self.assertRaises(SystemExit):
                        audit.main()
                else:
                    self.assertEqual(audit.main(), 0)
            return json.loads(output.read_text())

    def test_contract_error_forces_red_receipt(self):
        report = self.report(True)
        self.assertEqual(report['status'], 'RED_CONTRACT_ERROR')
        self.assertFalse(report['milestoneMutationComplete'])
        self.assertTrue(report['contractErrors'])

    def test_unchecked_passes_are_not_green(self):
        report = self.report()
        self.assertEqual(len(report['tenPassAudit']), 10)
        self.assertFalse(report['milestoneMutationComplete'])
        for item in report['tenPassAudit']:
            if item['name'] not in ('Evidence', 'Machine Readability'):
                self.assertEqual(item['status'], 'UNKNOWN')
        self.assertIn('ten_pass_evidence', [b['gate'] for b in report['blockers']])

if __name__ == '__main__':
    unittest.main()
