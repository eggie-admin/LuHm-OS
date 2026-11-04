"""Fail-closed 512/1024/1536/2048 source-only escalation tests."""
import copy
import json
import unittest

from tools import crownCathedral512EscalationAudit as a
from tools import hex64Insanus2048Audit as core

REF="a"*40
DOC=json.loads(a.MANIFEST.read_text())
CASES=list(core.matrix(REF))
ANCHORS=core.source_requirements(a.ROOT)
DIGESTS=a.fingerprints()


def check(target=512,manifest=None,cases=None,actual=REF,anchors=None):
    return a.audit(DOC if manifest is None else manifest,REF,actual,target,
                   CASES if cases is None else cases,
                   ANCHORS if anchors is None else anchors,DIGESTS)


class CrownEscalation512Tests(unittest.TestCase):
    def test_all_four_cumulative_milestones(self):
        for n in a.TARGETS:
            with self.subTest(n=n):
                r=check(n)
                self.assertEqual((r["checked"],r["passed"]),(n,n))
                self.assertEqual(r["remaining"],2048-n)
                self.assertEqual(len(r["checkpoints"]),n//512)
                self.assertEqual(r["verdict"],"AMBER_SOURCE_ONLY")
                self.assertTrue(r["sourceModelOnly"])
                self.assertEqual(r["crownStatus"],"STOP")
                self.assertFalse(r["runtimeGreen"] or r["deployed"] or r["agentsReleased"])

    def test_chunk_ranges_and_unique_receipts(self):
        r=check(2048)
        self.assertEqual([c["start"] for c in r["checkpoints"]],[0,512,1024,1536])
        self.assertEqual([c["endExclusive"] for c in r["checkpoints"]],[512,1024,1536,2048])
        self.assertEqual(len({row["id"] for row,raw in CASES}),2048)
        self.assertEqual(len({c["cumulativeChainSha256"] for c in r["checkpoints"]}),4)
        self.assertTrue(all(c["checked"]==512 and c["passed"]==512 and c["binaryBytes"]==32768 for c in r["checkpoints"]))

    def test_invalid_milestone_fails(self):
        for n in (-512,0,1,511,513,1023,2049):
            with self.subTest(n=n):
                with self.assertRaises(ValueError):
                    check(n)

    def test_wrong_source_sha_fails(self):
        with self.assertRaises(ValueError):
            check(actual="b"*40)

    def test_missing_scenario_fails(self):
        with self.assertRaises(ValueError):
            check(2048,cases=CASES[:-1])

    def test_order_drift_fails(self):
        m=copy.deepcopy(DOC)
        m["checkpoints"][0]["families"].reverse()
        with self.assertRaises(ValueError):
            check(2048,manifest=m)

    def test_crown_escalation_fails(self):
        m=copy.deepcopy(DOC)
        m["crownStatus"]="GREEN"
        with self.assertRaises(ValueError):
            check(512,manifest=m)

    def test_false_mutation_authority_fails(self):
        m=copy.deepcopy(DOC)
        m["denied"].remove("productionDeploy")
        with self.assertRaises(ValueError):
            check(512,manifest=m)

    def test_corrupt_checksum_second_chunk_stops(self):
        rows=list(CASES)
        row,raw=rows[512]
        b=bytearray(raw)
        b[20]^=1
        rows[512]=(row,bytes(b))
        r=check(2048,cases=rows)
        self.assertEqual(r["verdict"],"RED_SOURCE_GATE")
        self.assertEqual(r["checked"],1024)
        self.assertEqual(len(r["checkpoints"]),2)
        self.assertEqual(r["checkpoints"][-1]["firstFailed"],"0x200")

    def test_corrupt_reserved_last_chunk_stops(self):
        rows=list(CASES)
        row,raw=rows[1536]
        b=bytearray(raw)
        b[-1]=1
        rows[1536]=(row,bytes(b))
        r=check(2048,cases=rows)
        self.assertEqual(r["verdict"],"RED_SOURCE_GATE")
        self.assertEqual(r["checkpoints"][-1]["firstFailed"],"0x600")

    def test_malformed_decision_stops_first_chunk(self):
        rows=list(CASES)
        row,raw=rows[0]
        rows[0]=(dict(row,decision="PROPOSED_ONLY"),raw)
        r=check(2048,cases=rows)
        self.assertEqual(r["verdict"],"RED_SOURCE_GATE")
        self.assertEqual(len(r["checkpoints"]),1)

    def test_source_anchor_lost_is_not_green(self):
        r=check(512,anchors=dict(ANCHORS,companyQuarantined=False))
        self.assertEqual(r["verdict"],"RED_SOURCE_GATE")

    def test_source_fingerprints_required(self):
        with self.assertRaises(ValueError):
            a.audit(DOC,REF,REF,512,CASES,ANCHORS,{})


if __name__=="__main__":
    unittest.main()
