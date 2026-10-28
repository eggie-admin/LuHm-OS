#!/usr/bin/env python3
"""64 matrix coordinates and negative transition/evidence proof."""
import importlib.util
import itertools
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def module(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

matrix = module("tools/fnCastMatrix.py", "fnCastMatrix")
fn = module("tools/fnCast.py", "fnCast")
contract = fn.loadContract()
conf = contract["castMatrix"]
sha = "a" * 40
base = dict(taskId="premonitionCastMatrix", scopeId="samsungStudio",
            requestedSourceRef=sha, checkedOutSourceRef=sha, voiceAccepted=True)

class CastMatrixTests(unittest.TestCase):
    def testCanonicalFourArraysAndLegacyAliases(self):
        self.assertEqual(contract["displayBrand"], "LuHm-OS")
        self.assertEqual(conf["stages"], ["castTesting", "castProposed", "castBridge", "cast"])
        self.assertEqual(conf["beats"], ["hear", "resolve", "act", "verify"])
        self.assertEqual(conf["tiers"], ["technologyFastPath", "forFuckSake", "scorchedEarth", "finalForm"])
        for alias in ("castDev", "devCast"):
            data = matrix.compileMatrixIntent(contract,stage=alias,beat="hear",
                                              tier="technologyFastPath",**base)
            self.assertEqual(data["coordinate"]["stage"],"castTesting")
    def testAllSixtyFourCoordinatesWithNoAuthority(self):
        total = 0
        for stage,beat,tier in itertools.product(conf["stages"],conf["beats"],conf["tiers"]):
            with self.subTest(stage=stage,beat=beat,tier=tier):
                row = matrix.compileMatrixIntent(contract,stage=stage,beat=beat,tier=tier,
                                                 fromStage=stage,**base)
                self.assertEqual(row["matrixSize"],64)
                self.assertEqual(row["status"],"INTENT_ACCEPTED_CANDIDATE_ONLY")
                self.assertEqual(row["product"],"LuHm-OS")
                self.assertTrue(row["stageTransitionValid"])
                self.assertFalse(row["buildDispatched"])
                self.assertFalse(row["releasePublished"])
                self.assertFalse(row["crownGranted"])
                self.assertEqual(row["authorityEffect"],"none")
                total += 1
        self.assertEqual(total,64)
    def testInitialAndOneStepTransitions(self):
        for i,stage in enumerate(conf["stages"]):
            previous = conf["stages"][i-1] if i>0 else None
            row=matrix.compileMatrixIntent(contract,stage=stage,fromStage=previous,
                                           beat="verify",tier="finalForm",**base)
            self.assertEqual(row["status"],"INTENT_ACCEPTED_CANDIDATE_ONLY")
    def testIllegalSkipsAndBacktrackingHold(self):
        for before,after in [(None,"castBridge"),("castTesting","castBridge"),
                             ("castBridge","castTesting"),("cast","castProposed")]:
            row=matrix.compileMatrixIntent(contract,stage=after,fromStage=before,
                                           beat="act",tier="finalForm",**base)
            self.assertEqual(row["status"],"HOLD_ILLEGAL_STAGE_TRANSITION")
            self.assertFalse(row["buildDispatched"])
    def testUnarmedOrStaleSourceHolds(self):
        args=dict(base)
        args["voiceAccepted"]=False
        row=matrix.compileMatrixIntent(contract,stage="castTesting",beat="hear",
                                       tier="technologyFastPath",**args)
        self.assertEqual(row["status"],"HOLD_UNARMED_OR_UNSCOPED")
        args=dict(base)
        args["checkedOutSourceRef"]="b"*40
        row=matrix.compileMatrixIntent(contract,stage="castTesting",beat="hear",
                                       tier="technologyFastPath",**args)
        self.assertEqual(row["status"],"HOLD_EXACT_SOURCE_REQUIRED")
    def testInvalidCoordinatesAndIdentityRejected(self):
        cases=[
          dict(stage="CAST",beat="hear",tier="finalForm"),
          dict(stage="castTesting",beat="AUDIT",tier="finalForm"),
          dict(stage="castTesting",beat="hear",tier="fake"),
          dict(stage="castTesting",beat="hear",tier="finalForm",taskId="../inject"),
          dict(stage="castTesting",beat="hear",tier="finalForm",scopeId=""),
          dict(stage="castTesting",beat="hear",tier="finalForm",fromStage="unknown"),
        ]
        for kwargs in cases:
            with self.subTest(kwargs=kwargs):
                payload=dict(base)
                payload.update(kwargs)
                with self.assertRaises(ValueError):
                    matrix.compileMatrixIntent(contract,**payload)

if __name__=="__main__":
    unittest.main()
