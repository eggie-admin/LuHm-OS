#!/usr/bin/env python3
"""R sidecar source safety, bounded grid and synthetic cross-language receipt tests."""
from __future__ import annotations
import copy
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

P=Path(__file__).resolve().parents[1]/"tools/rSyntheticTuningGate.py"
s=importlib.util.spec_from_file_location("rSyntheticTuningGate",P)
assert s and s.loader
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)


class TestRSyntheticTune(unittest.TestCase):
    def test_four_lanes_four_phase_R_source_and_zero_live_runtime(self):
        a=m.source_audit()
        self.assertEqual(a["state"],"SOURCE_ONLY",a["issues"])
        self.assertEqual(a["matrixCells"],16)
        self.assertEqual(a["maxTrials"],16)
        self.assertEqual(len(a["scriptSha256"]),64)
        self.assertFalse(a["agentActivated"])
        self.assertFalse(a["realKernelBenchmark"])

    def test_bounded_objective_and_reproducible_order(self):
        a=m.plan(target=2,candidates=[0,1,2,3,4])
        self.assertEqual((a["best"],a["trials"]),(2,5))
        self.assertFalse(a["kernelVariablesChanged"])
        self.assertFalse(a["rExecutedByPython"])
        self.assertFalse(a["credentialsTested"])
        b=m.plan(target=2,candidates=[4,3,2,1,0])
        self.assertEqual(a["best"],b["best"])
        self.assertEqual(m.plan(target=0,candidates=[0,1,2])["best"],0)

    def test_limits_deny_credential_search_unbounded_and_type_confusion(self):
        for target,candidates in [
           (True,[0]),(-1,[0]),(11,[0]),(0,[]),(0,[0]*2),
           (0,list(range(17))),(0,[-1]),(0,[100]),(0,[True]),
           (0,["1"]),(0,None),(0,"0"),
        ]:
            with self.subTest(target=target,candidates=str(candidates)[:30]),self.assertRaises(ValueError):
                m.plan(target=target,candidates=candidates)

    def test_real_base_r_fixture_accepts_exact_small_response_only(self):
        result=m.verify_r_fixture("\n".join(k+"="+v for k,v in m.SAFE_OUT.items())+"\n")
        self.assertTrue(result["rOracleCompared"])
        self.assertEqual(result["candidateTrials"],5)
        self.assertFalse(result["agentAuthorized"])
        for text in (
            "best=9\n",
            "schema=luhmOs.syntheticRTune.v1\nbest=9\ntrials=5\nstate=SYNTHETIC_ONLY_NOT_REAL_KERNEL_OR_AGENT_TUNING\nruntimeRights=HOLD\n",
            "\n".join(k+"="+v for k,v in m.SAFE_OUT.items())+"\nfoo=bar",
            "schema=luhmOs.syntheticRTune.v1\n"*5,
            "",
        ):
            with self.assertRaises(ValueError):
                m.verify_r_fixture(text)

    def test_forged_agent_permission_is_source_red(self):
        orig=m._source
        def forged():
            p=orig()
            p=copy.deepcopy(p)
            p["math"]["noRealKernelTuning"]=False
            return p
        with patch.object(m,"_source",side_effect=forged):
            a=m.source_audit()
        self.assertIn("RED_R_SECURITY_POLICY",a["issues"])
        with patch.object(m,"_source",side_effect=forged):
            self.assertEqual(m.plan(target=2,candidates=[0,1,2])["state"],
                             "STOP_SOURCE_DRIFT")


if __name__=="__main__":
    unittest.main()
