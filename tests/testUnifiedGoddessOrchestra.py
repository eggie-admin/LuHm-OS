"""Contract and SQLite negative checks without external services."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from unifiedGoddessOrchestraAudit import inspect, matrix, sql_smoke

POLICY=json.loads((ROOT/"doctrine/unifiedGoddessOrchestraV1.json").read_text())


class UnifiedGoddessOrchestraTests(unittest.TestCase):
    def test_real_contract_green(self):
        report=inspect()
        self.assertEqual(report["failures"],[])
        self.assertEqual(report["state"],"SOURCE_PROFILE_GREEN_RUNTIME_UNVERIFIED")
        self.assertEqual(report["activeAgents"],0)

    def test_64_cells(self):
        report=matrix()
        self.assertEqual(report["count"],64)
        self.assertTrue(all(c["authority"]=="NONE" and not c["liveCapabilityVerified"] for c in report["cells"]))

    def test_in_memory_sql_and_four_rejections(self):
        report=sql_smoke()
        self.assertEqual(report["negativeCasesRejected"],4)
        self.assertFalse(report["productionDatabaseTouched"])

    def assert_bad(self, change):
        policy=copy.deepcopy(POLICY)
        change(policy)
        self.assertTrue(inspect(policy_override=policy)["failures"])

    def test_reject_company_auto_publishing(self):
        self.assert_bad(lambda p: p["safety"].update(noAutomaticDeploy=False))

    def test_reject_unquarantined_kaji(self):
        self.assert_bad(lambda p: p["agentSong"].update(actAuthority="CAN_EXECUTE"))

    def test_reject_browser_runtime_node(self):
        self.assert_bad(lambda p: p["toolchain"]["npm"].update(runtimeOnAndroid=True))

    def test_reject_arbitrary_vendor_pulls(self):
        self.assert_bad(lambda p: p["toolchain"]["vendorSelection"].update(neverAutoPullThirdPartyCode=False))

    def test_reject_duplicate_browser_renderer(self):
        self.assert_bad(lambda p: p["toolchain"]["vendorSelection"].update(noDuplicateRendererInstall=False))

    def test_reject_fifth_unapproved_quarter(self):
        self.assert_bad(lambda p: p["quarters"].append("specialAdmin"))

    def test_reject_missing_artifact_contract(self):
        self.assert_bad(lambda p: p["moduleRegistry"][1].update(ref="does-not-exist.sql"))

    def test_reject_public_sql_route(self):
        self.assert_bad(lambda p: p["toolchain"]["sql"].update(publicPort=True))

    def test_reject_incomplete_manifest(self):
        self.assert_bad(lambda p: p["tasks"]["manifestFields"].remove("consent"))


if __name__=="__main__":
    unittest.main()
