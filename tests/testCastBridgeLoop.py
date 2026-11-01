import unittest
from tools.castBridgeLoop import tick

SHA = 'a' * 40
class CastBridgeLoopTests(unittest.TestCase):
    def run_tick(self, previous=None, runner=None, source=None):
        return tick(SHA, previous or {}, runner or (lambda _: {'status': 'GREEN'}), source or (lambda: SHA))

    def test_green_is_not_release_authority(self):
        r = self.run_tick()
        self.assertEqual(r['testingSourceStatus'], 'GREEN')
        self.assertFalse(r['releaseAuthorized'])
        self.assertEqual(r['castStatus'], 'WAIT_FOR_PROFESSOR')
        self.assertIn('playInternalInstall', r['requiredExternalProof'])

    def test_failure_continues_independent_ladders(self):
        calls = []
        def run(script):
            calls.append(script)
            return {'status': 'RED' if len(calls) == 1 else 'GREEN'}
        r = self.run_tick(runner=run)
        self.assertEqual(len(calls), 4)
        self.assertEqual(r['testingSourceStatus'], 'AMBER')
        self.assertEqual(r['checks'][0]['tier'], 1)

    def test_three_failures_stop_repeated_execution(self):
        r = {}
        for _ in range(3):
            r = self.run_tick(r, lambda _: {'status': 'RED'})
        r = self.run_tick(r, lambda _: self.fail('budget exhausted'))
        self.assertTrue(all(x['status'] == 'BLOCKED' for x in r['checks']))

    def test_changed_source_resets_retry_budget(self):
        r = {'sourceRef': 'b' * 40, 'checks': [{'ladder': 'machine', 'failures': 3, 'tier': 3}]}
        self.assertEqual(self.run_tick(r)['checks'][0]['failures'], 0)

    def test_previous_green_is_retested(self):
        r = self.run_tick()
        self.assertEqual(self.run_tick(r, lambda _: {'status': 'RED'})['testingSourceStatus'], 'AMBER')

    def test_mid_tick_source_change_holds(self):
        count = [0]
        def source():
            count[0] += 1
            return SHA if count[0] == 1 else 'b' * 40
        r = self.run_tick(source=source)
        self.assertFalse(r['sourceStable'])
        self.assertEqual(r['testingSourceStatus'], 'AMBER')

    def test_invalid_retry_state_rejected(self):
        with self.assertRaises(ValueError):
            self.run_tick({'sourceRef': SHA, 'checks': [{'ladder': 'machine', 'tier': -1}]})

if __name__ == '__main__':
    unittest.main()
