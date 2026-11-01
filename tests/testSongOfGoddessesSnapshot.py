#!/usr/bin/env python3
"""Negative checks for existing Song/CAST Canon, no live execution."""
import copy
import json
import unittest
from pathlib import Path
from tools import songOfGoddessesSnapshot as song

SNAPSHOT=Path(__file__).resolve().parents[1]/"doctrine/songOfGoddessesSnapshotV1.json"

class SongOfGoddessesTests(unittest.TestCase):
    def setUp(self):
        self.s=json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    def testCurrent4x4BoundedSourceOnly(self):
        result=song.validate(self.s)
        self.assertEqual((result["architectureCells"],result["environmentSqlCells"]),(16,16))
        self.assertEqual(result["allocated"],32)
        self.assertEqual(result["unverifiedCapacity"],2016)
        self.assertEqual(result["activeWorkers"],0)
        self.assertEqual(result["crownStatus"],"STOP")

    def testAddressUpperSentinelDenied(self):
        self.assertEqual(song.index_slot(0),"0x000")
        self.assertEqual(song.index_slot(31),"0x01F")
        self.assertEqual(song.index_slot(2047),"0x7FF")
        for value in (-1,2048,4096,False,1.0,"0x001"):
            with self.subTest(value=value),self.assertRaises(song.SnapshotError):
                song.index_slot(value)

    def testBadHexOrDuplicateAliasesRejected(self):
        s=copy.deepcopy(self.s)
        s["matrix"][2]["address"]="0x001"
        with self.assertRaisesRegex(song.SnapshotError,"ARCHITECTURE_ADDRESS_DRIFT"):
            song.validate(s)

    def testHigherStagesAreNotWorkers(self):
        s=copy.deepcopy(self.s)
        s["boundaries"]["activeAgentWorkers"]=2048
        with self.assertRaisesRegex(song.SnapshotError,"AUTHORITY_DRIFT"):
            song.validate(s)

    def testForbiddenReleaseAuthorityRejected(self):
        for key in ("automaticMerge","automaticAgentLaunch","signingAuthorized","paidApisAuthorized",
                    "deviceFirmwareWrite","claimedSamsungProof","claimedBlenderRuntimeProof"):
            with self.subTest(key=key):
                s=copy.deepcopy(self.s)
                s["boundaries"][key]=True
                with self.assertRaisesRegex(song.SnapshotError,"AUTHORITY_DRIFT"):
                    song.validate(s)

    def testBase44MisreadRejected(self):
        s=copy.deepcopy(self.s)
        s["transport"]["base44IsEncoding"]=True
        with self.assertRaisesRegex(song.SnapshotError,"TRANSPORT_MEANING"):
            song.validate(s)

    def testReservedLogicalSlotsAreNotProven(self):
        s=copy.deepcopy(self.s)
        s["addressing"]["allocatedAliases"]=2048
        with self.assertRaisesRegex(song.SnapshotError,"ADDRESS_CAPACITY"):
            song.validate(s)

    def testNoPhantomSourcePaths(self):
        s=copy.deepcopy(self.s)
        s["matrix"][0]["source"]="../private-source"
        with self.assertRaisesRegex(song.SnapshotError,"ARCHITECTURE_ADDRESS_DRIFT"):
            song.validate(s)

    def testNoProtocolAliasSurreptitiousShell(self):
        s=copy.deepcopy(self.s)
        s["environmentSqlMatrix"][0]["entry"]="/etc/passwd"
        with self.assertRaisesRegex(song.SnapshotError,"SQL_ENV_ADDRESS_DRIFT"):
            song.validate(s)

    def testNoWrongOrchestraRoleOrder(self):
        s=copy.deepcopy(self.s)
        s["godddesses"][0]["id"]="newGodOfWorkers"
        with self.assertRaisesRegex(song.SnapshotError,"GODDESS_IDENTITY"):
            song.validate(s)

if __name__ == "__main__":
    unittest.main()
