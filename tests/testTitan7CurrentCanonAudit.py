import copy
import unittest
from tools.titan7CurrentCanonAudit import load, validate, proposal_fields

class Titan7CurrentCanonTruthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.truth=load("doctrine/currentSourceTruthV3.json")
        cls.ledger=load("doctrine/titan7CurrentCanonReconciliationV1.json")
        cls.plugin=load("plugins/luhm-os/plugin.json")
        cls.mcp=load("plugins/luhm-os/mcp.json")
        cls.titan=load("doctrine/operationTitan7FinalFormV1.json")
        cls.agent=load("doctrine/agentSystemDeploymentV1.json")
    def audit(self,**overrides):
        x={k:copy.deepcopy(getattr(self,k)) for k in ("truth","ledger","plugin","mcp","titan","agent")}
        x.update(overrides)
        return validate(**x)
    def test_currentScopedCanon(self): self.assertEqual(self.audit(),[])
    def test_globalOverclaim(self):
        x=copy.deepcopy(self.truth);x["status"]="GREEN_FULL_SYSTEM"
        self.assertIn("sourceTruthStillAmber",self.audit(truth=x))
    def test_crownOverclaim(self):
        x=copy.deepcopy(self.ledger);x["crownStatus"]="GREEN"
        self.assertIn("crownStop",self.audit(ledger=x))
    def test_hostOverclaim(self):
        x=copy.deepcopy(self.ledger);x["runtimeEvidence"]["chatGptHostMount"]="GREEN"
        self.assertIn("externalHostProofGuard:chatGptHostMount",self.audit(ledger=x))
    def test_sourceDrift(self):
        x=copy.deepcopy(self.ledger);x["auditBasis"]["observedMain"]="0"*40
        self.assertIn("observedMainDrift",self.audit(ledger=x))
    def test_bulkProposalPromotion(self):
        x=copy.deepcopy(self.truth);x["titan7CurrentCanonReconciliation"]["allProposedChangesPromoted"]=True
        self.assertIn("noBulkPromotion",self.audit(truth=x))
    def test_missingOpenPr(self):
        x=copy.deepcopy(self.ledger);x["openPullRequests"]["items"].pop()
        self.assertIn("openPrCount",self.audit(ledger=x))
    def test_noSelfMerge(self):
        x=copy.deepcopy(self.ledger);x["openPullRequests"]["items"][0]["mergeAuthority"]=True
        self.assertTrue(any("noAutoMerge" in err for err in self.audit(ledger=x)))
    def test_agentWorkersNotLive(self):
        x=copy.deepcopy(self.ledger);x["canonBoundaries"]["liveProviderWorkerClaim"]=True
        self.assertIn("noImaginaryAgents",self.audit(ledger=x))
    def test_scanDetectsNestedProposals(self):
        self.assertEqual(proposal_fields({"outer":{"status":"PROPOSED_ONLY"}})[0]["key"],"outer.status")

if __name__=="__main__": unittest.main()
