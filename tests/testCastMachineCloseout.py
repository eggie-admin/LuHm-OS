#!/usr/bin/env python3
"""CAST machine-to-OS handoff: adversarial source and promotion checks."""
from __future__ import annotations
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("machine_cast",ROOT/"tools/castMachineCloseoutAudit.py")
mod=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

class MachineCastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=json.loads(mod.MANIFEST.read_text(encoding="utf-8"))
    def testMachineSourceOnlyReadyButNoCastOrRelease(self):
        r=mod.receipt(self.model)
        self.assertEqual(r["status"],"AMBER_MACHINE_SOURCE_READY_FOR_PROPOSED_REVIEW")
        self.assertTrue(r["machineSourcePrototyped"])
        self.assertTrue(r["nextOsPlanningAllowed"])
        self.assertEqual(len(r["sourceDigests"]),9)
        self.assertEqual([x["pr"] for x in r["historicalPrChain"]],[477,478,479,480])
        self.assertEqual(len(r["nextBlockers"]),5)
        for key in ("currentHeadReverified","actualPiBooted","kioskAccessibleFromPhone",
                    "physicalBackendComplete","betaReleaseReady","finalReleaseReady",
                    "castAuthorized","castDispatched","publicDeployment","liveData"):
            self.assertFalse(r[key],key)
        self.assertEqual(r["sourceChangesUntilHardwareEvidence"],"SECURITY_FIXES_ONLY")
        self.assertEqual(r["crownStatus"],"STOP")
    def testSourceParentStackCannotBeFlattenedOrInvented(self):
        for mutate in (
            lambda v: v["chain"][2].update(base="main"),
            lambda v: v["chain"][3].update(pr=0),
            lambda v: v["chain"][2].update(sha="a"*40),
            lambda v: v["chain"][1].update(sourceRun=1),
            lambda v: v.update(mainBaseline="c"*40),
        ):
            m=deepcopy(self.model);mutate(m)
            with self.assertRaises(mod.MachineCastError):
                mod.validate(m)
    def testMachineHexNeverBecomesHardwareRegisterOrGreen(self):
        for updates in ({"indices":["0xDE"]*16},{"namespace":"kernelPhysicalRegister"},
                        {"layers":["kernel"]*4}):
            m=deepcopy(self.model);m["machineFourByFour"].update(updates)
            with self.assertRaisesRegex(mod.MachineCastError,"HEX_MATRIX"):
                mod.validate(m)
    def testNoFakedOwnerAuthorizationOrDeviceCompletion(self):
        for key in mod.UNCERTAIN:
            with self.subTest(evidence=key):
                m=deepcopy(self.model);m["observations"][key]=True
                with self.assertRaisesRegex(mod.MachineCastError,"EVIDENCE_CANNOT_SELF_PROMOTE"):
                    mod.validate(m)
        m=deepcopy(self.model);m["readyForPhysicalBackend"]=True
        with self.assertRaisesRegex(mod.MachineCastError,"MACHINE_TRUTH"):
            mod.validate(m)
    def testNoImplicitCastOrPublicServerEscalation(self):
        for key in mod.DECISIONS:
            with self.subTest(guard=key):
                m=deepcopy(self.model);m["contractDecisions"][key]=False
                with self.assertRaisesRegex(mod.MachineCastError,"NO_VENDOR_OR_PRIVILEGE_ESCALATION"):
                    mod.validate(m)
        m=deepcopy(self.model);m["promotionLaw"]["prohibitedActions"].remove("productionMerge")
        with self.assertRaisesRegex(mod.MachineCastError,"PROMOTION_LAW"):
            mod.validate(m)
    def testBetaRequiresRealPiAndFreshSingleUseCast(self):
        m=deepcopy(self.model)
        m["lanes"][3]["criteria"].remove("physicalPiBoot")
        with self.assertRaisesRegex(mod.MachineCastError,"PROMOTION_SCOPE"):
            mod.validate(m)
        m=deepcopy(self.model)
        m["lanes"][3]["criteria"].remove("explicitOneUseCast")
        with self.assertRaisesRegex(mod.MachineCastError,"PROMOTION_SCOPE"):
            mod.validate(m)
        m=deepcopy(self.model);m["lanes"][4]["authorization"]="automaticOnCi"
        with self.assertRaisesRegex(mod.MachineCastError,"LANE_AUTHORITY"):
            mod.validate(m)
    def testAllFiveBlockersRemainVisible(self):
        m=deepcopy(self.model);m["requiredNextEvidence"].pop()
        with self.assertRaisesRegex(mod.MachineCastError,"HONEST_BLOCKERS"):
            mod.validate(m)
        m=deepcopy(self.model);m["requiredNextEvidence"][0]["status"]="PASS"
        with self.assertRaisesRegex(mod.MachineCastError,"HONEST_BLOCKERS"):
            mod.validate(m)
    def testOnlyCanonSourceFilesAllowed(self):
        with self.assertRaisesRegex(mod.MachineCastError,"FILE_ALLOWLIST"):
            mod.safe_file("../private-key")
        with self.assertRaisesRegex(mod.MachineCastError,"FILE_ALLOWLIST"):
            mod.safe_file("/etc/shadow")
        m=deepcopy(self.model);m["sourceReceipts"][0]["path"]="../../secret"
        with self.assertRaisesRegex(mod.MachineCastError,"SOURCE_INVENTORY"):
            mod.validate(m)
    def testCannotSelfAuthorizeNextLayerOrRelease(self):
        m=deepcopy(self.model);m["crownStatus"]="RELEASED"
        with self.assertRaisesRegex(mod.MachineCastError,"CONTRACT"):
            mod.validate(m)
        m=deepcopy(self.model);m["readyToPlanNextOsLayer"]=False
        with self.assertRaisesRegex(mod.MachineCastError,"MACHINE_TRUTH"):
            mod.validate(m)
        m=deepcopy(self.model);m["promotionLaw"]["automaticDestination"]="BETA"
        with self.assertRaisesRegex(mod.MachineCastError,"PROMOTION_LAW"):
            mod.validate(m)

if __name__=="__main__":
    unittest.main()
