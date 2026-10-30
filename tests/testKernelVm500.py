#!/usr/bin/env python3
"""Negative controls for the 500-slot kernel, DNS, budget and authority audit."""
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("kernelVm500Audit",ROOT/"tools/kernelVm500Audit.py")
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class KernelVmAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy,cls.files=module.read_policy_files()

    def test_500_distinct_assessments(self):
        rows=module.assess(False)
        self.assertEqual(len(rows),500)
        self.assertEqual(len({x["id"] for x in rows}),500)
        self.assertEqual(sum(map(len,module.LAYERS.values())),100)

    def test_remote_vm_not_falsely_proven(self):
        rows=module.assess(True)
        remote=[x for x in rows if x["target"]!="githubActionsRunner"]
        self.assertEqual(len(remote),400)
        self.assertTrue(all(x["verdict"]=="UNVERIFIED" for x in remote))

    def test_source_policy_passes(self):
        self.assertEqual(module.policy_failures(self.policy,self.files),[])

    def test_open_resolver_rejected(self):
        p=copy.deepcopy(self.policy)
        p["dns"]["bind9"]["recursive"]=True
        failures=module.policy_failures(p,self.files)
        self.assertIn("BIND_MUST_BE_PRIVATE",failures)

    def test_wildcard_dns_bind_rejected(self):
        f=copy.deepcopy(self.files)
        f["options"]=f["options"].replace("127.0.0.1;","0.0.0.0;")
        self.assertIn("BIND_NO_WILDCARD",module.policy_failures(self.policy,f))

    def test_google_public_ipv4_cost_not_erased(self):
        p=copy.deepcopy(self.policy)
        p["provider"]["google"]["publicIpv4Billed"]=False
        self.assertIn("GOOGLE_BILLING_MUST_NOT_BE_CALLED_FREE",
                      module.policy_failures(p,self.files))

    def test_oracle_free_allotment_not_doubled(self):
        p=copy.deepcopy(self.policy)
        p["provider"]["oracle"]["nominalFullMonthOcpu"]=4
        self.assertIn("ORACLE_FREE_TIER_MUST_USE_CURRENT_LIMIT",
                      module.policy_failures(p,self.files))

    def test_android_dnsmasq_forbidden(self):
        p=copy.deepcopy(self.policy)
        p["dns"]["dnsmasq"]["androidAppEmbedded"]=True
        self.assertIn("DNSMASQ_NOT_IN_ANDROID",module.policy_failures(p,self.files))

    def test_agent_resumption_forbidden(self):
        p=copy.deepcopy(self.policy)
        p["security"]["unquarantineAgents"]=True
        self.assertIn("NO_MUTATION_OR_COST",module.policy_failures(p,self.files))

    def test_source_not_equal_live_vm(self):
        result=module.audit(True)
        self.assertEqual(result["sourcePolicy"],"PASS")
        self.assertFalse(result["liveCloudInspection"])
        self.assertEqual(result["verdict"],"AMBER_REMOTE_VM_UNVERIFIED")
        self.assertEqual(result["crownStatus"],"STOP")

if __name__=="__main__":
    unittest.main()
