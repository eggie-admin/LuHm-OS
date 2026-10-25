#!/usr/bin/env python3
"""Actual SQL JSON1 tuning tests, including transactions and negative controls."""
from __future__ import annotations

import importlib.util
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("fnCastSqlJson", root / "tools/fnCastSqlJson.py")
assert spec is not None and spec.loader is not None
tuner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tuner)
contract = json.loads((root / "doctrine/fnCastV1.yaml").read_text())


class FnCastSqlJsonTests(unittest.TestCase):
    def testRealSqlJson1TuningPreview(self):
        receipt = tuner.tuneSqlJson({"ui.glassOpacity": 0.84, "render.frameCap": 90}, contract)
        self.assertEqual(receipt["engine"], "SQLite JSON1")
        self.assertEqual(receipt["mode"], "PREVIEW_ONLY")
        self.assertIn("json_set", receipt["sqlOperations"])
        self.assertEqual(receipt["revisionAfter"], 2)
        self.assertNotEqual(receipt["beforeSha256"], receipt["afterSha256"])
        self.assertEqual(receipt["tunedDocument"]["systemVariables"]["ui"]["glassOpacity"], 0.84)
        self.assertEqual(receipt["tunedDocument"]["systemVariables"]["render"]["frameCap"], 90)
        self.assertIsNone(receipt["persistentDatabase"])
        self.assertFalse(receipt["crownAuthority"])

    def testTypedParameterBindingRejectsInjectionPaths(self):
        for path in ('ui.glassOpacity);DROP TABLE systemVariables;--',
                     "$.crownStatus", "crownCondition", "releaseAuthority", "audio;delete"):
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    tuner.tuneSqlJson({path: 0.7}, contract)

    def testInvalidValueAndJsonRejected(self):
        bad = [
            {"ui.glassOpacity": -1},
            {"render.frameCap": 30.1},
            {"audio.voiceGain": True},
            {"gameplay.dialogueSpeed": None},
            {"ui.glassOpacity": float("nan")},
            {"ui.glassOpacity": 100},
            {"render.frameCap": "60"},
        ]
        for updates in bad:
            with self.subTest(updates=str(updates)):
                with self.assertRaises(ValueError):
                    tuner.tuneSqlJson(updates, contract)
        with self.assertRaises(ValueError):
            tuner.parseJsonAssignments(['ui.glassOpacity={"oops":'])
        with self.assertRaises(ValueError):
            tuner.parseJsonAssignments(['render.frameCap=NaN'])
        with self.assertRaises(ValueError):
            tuner.parseJsonAssignments(['ui.glassOpacity=0.1', 'ui.glassOpacity=0.2'])

    def testActualSqlitePersistenceAndAtomicity(self):
        with tempfile.TemporaryDirectory() as workDir:
            dbPath = Path(workDir) / "candidate.sqlite3"
            preview = tuner.tuneSqlJson({"audio.musicVolume": 0.33}, contract, dbPath=dbPath)
            self.assertFalse(dbPath.exists(), "preview must not persist a database")
            self.assertEqual(preview["mode"], "PREVIEW_ONLY")
            with self.assertRaises(PermissionError):
                tuner.tuneSqlJson({"audio.voiceGain": 1.2}, contract, dbPath=dbPath, apply=True)
            self.assertFalse(dbPath.exists(), "unarmed apply must never open database")
            applied = tuner.tuneSqlJson({"audio.voiceGain": 1.45}, contract,
                                         dbPath=dbPath, apply=True, authorized=True)
            self.assertTrue(dbPath.exists())
            self.assertEqual(applied["mode"], "APPLIED_LOCAL_CANDIDATE")
            self.assertEqual(applied["revisionAfter"], 1)
            with sqlite3.connect(dbPath) as connection:
                row = connection.execute(
                    "SELECT json_valid(stateJson), json_extract(stateJson, '$.systemVariables.audio.voiceGain') "
                    "FROM systemVariables"
                ).fetchone()
            self.assertEqual(row, (1, 1.45))
            again = tuner.tuneSqlJson({"ui.glassOpacity": 0.99}, contract,
                                       dbPath=dbPath, apply=True, authorized=True)
            self.assertEqual(again["revisionBefore"], 1)
            self.assertEqual(again["revisionAfter"], 2)
            self.assertEqual(again["tunedDocument"]["systemVariables"]["audio"]["voiceGain"], 1.45)
            with self.assertRaises(ValueError):
                tuner.tuneSqlJson({"audio.voiceGain": 1.6, "tier.finalForm": 1},
                                   contract, dbPath=dbPath, apply=True, authorized=True)
            with sqlite3.connect(dbPath) as connection:
                row = connection.execute(
                    "SELECT revision, json_extract(stateJson, '$.systemVariables.audio.voiceGain') "
                    "FROM systemVariables"
                ).fetchone()
            self.assertEqual(row, (2, 1.45), "invalid batch must roll back completely")

    def testOnlyAllowedJsonRootsAndNoCrownSideEffects(self):
        receipt = tuner.tuneSqlJson({"gameplay.dialogueSpeed": 2.2}, contract)
        self.assertEqual(sorted(receipt["tunedDocument"]), ["project", "schema", "systemVariables"])
        self.assertFalse(receipt["canonicalDoctrineMutated"])
        self.assertFalse(receipt["externalDatabaseMutated"])
        self.assertFalse(receipt["releaseAuthority"])
        self.assertFalse(receipt["crownAuthority"])
        self.assertEqual(tuner.parseJsonAssignments(["render.frameCap=60"]), {"render.frameCap": 60})


if __name__ == "__main__":
    unittest.main()
