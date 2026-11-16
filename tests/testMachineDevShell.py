import json, pathlib, subprocess, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class MachineDevShellTests(unittest.TestCase):
    def test_bash_syntax(self):
        r=subprocess.run(['bash','-n',str(ROOT/'machine-harness/luhm-dev-shell.sh')],capture_output=True)
        self.assertEqual(r.returncode,0,r.stderr.decode())
    def test_locked_commands_and_sql_reuse(self):
        s=(ROOT/'machine-harness/luhm-dev-shell.sh').read_text()
        for good in ('tools/canonHexLedger.py','--all-scales','RED_SOURCE_REF_MISMATCH','RED_ROOT_FORBIDDEN','RED_UNSUPPORTED_COMMAND'):
            self.assertIn(good,s)
        for bad in ('sudo ','fastboot ','mkfs.','gparted','eval '):
            self.assertNotIn(bad,s)
    def test_policy_no_signing_or_release(self):
        p=json.loads((ROOT/'doctrine/machineDevShellV1.json').read_text())
        self.assertFalse(any(p['authority'].values()))
        self.assertEqual(p['sql']['importer'],'tools/canonHexLedger.py')
        self.assertEqual(p['crownStatus'],'STOP')
    def test_workflow_attestation_is_main_only(self):
        w=(ROOT/'.github/workflows/machine-signed-shell.yml').read_text()
        self.assertIn("github.event_name == 'push' && github.ref == 'refs/heads/main'",w)
        self.assertIn('actions/attest@1e69f48acb82d1966a394da916b4c1698aa569d6',w)
        self.assertIn('gh attestation verify',w)
        self.assertIn('id-token: write',w)
        self.assertIn('persist-credentials: false',w)
if __name__=='__main__':unittest.main()
