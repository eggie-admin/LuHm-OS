#!/usr/bin/env python3
"""IPS heritage negative controls against synthetic bytes only."""
import unittest
import json
from pathlib import Path
from tools import legacyIpsTextBridge as bridge

class TestLegacyIpsTextBridge(unittest.TestCase):
    def setUp(self):
        self.base = bridge.fixture()
        self.ips = bridge.demoIps()
        self.sha = bridge.digest(self.base)

    def testEmoteIsOnlyChangedByte(self):
        receipt=bridge.preview(self.base,self.ips,self.sha)
        self.assertEqual(receipt["changedBytes"],1)
        self.assertEqual(receipt["before"][0]["tokens"][2],"<EMOTE_HAPPY>")
        self.assertEqual(receipt["after"][0]["tokens"][2],"<EMOTE_ANGRY>")
        self.assertFalse(receipt["deviceFirmwareTouched"])

    def testExistingTypedSqlProjection(self):
        receipt=bridge.preview(self.base,self.ips,self.sha)
        row=bridge.projectSql(receipt,"f0cb6ee54066b490c0e80efc2c96200fec76ee2d")
        self.assertEqual(row["textFields"],5)
        self.assertFalse(row["sqlitePersisted"])

    def testGodotFixtureExactlyMatchesBinaryPreview(self):
        expected=bridge.preview(self.base,self.ips,self.sha)
        path=Path(__file__).resolve().parents[1]/"game/story/legacyIpsEmoteDemoV1.json"
        self.assertEqual(json.loads(path.read_text(encoding="utf-8")),expected)

    def testWrongSourceRejected(self):
        with self.assertRaisesRegex(ValueError,"WRONG_SOURCE_BYTES"):
            bridge.preview(self.base,self.ips,"0"*64)

    def testPointerAndHeaderWritesRejected(self):
        for offset in (0,8,11,15,23,31):
            ips=b"PATCH"+offset.to_bytes(3,"big")+b"\x00\x02AAEOF"
            with self.subTest(offset=offset),self.assertRaisesRegex(ValueError,"OUT_OF_BOUNDS_WRITE"):
                bridge.preview(self.base,ips,self.sha)

    def testOverlapRejected(self):
        h=(18).to_bytes(3,"big")+b"\x00\x01\xF1"
        with self.assertRaisesRegex(ValueError,"OVERLAPPING_PATCH"):
            bridge.preview(self.base,b"PATCH"+h+h+b"EOF",self.sha)

    def testTruncatedOrResizedRejected(self):
        for ips in (b"PATCH",self.ips+b"\x00\x00\x20",b"PATCH\x00\x00\x12\x00\x01"):
            with self.subTest(ips=ips),self.assertRaises(ValueError):
                bridge.preview(self.base,ips,self.sha)

    def testUnknownByteRejected(self):
        ips=b"PATCH"+(18).to_bytes(3,"big")+b"\x00\x01\xE7EOF"
        with self.assertRaisesRegex(ValueError,"UNMAPPED_TEXT_BYTE"):
            bridge.preview(self.base,ips,self.sha)

    def testBoundedRleAccepted(self):
        ips=b"PATCH"+(16).to_bytes(3,"big")+b"\x00\x00\x00\x02\x41EOF"
        receipt=bridge.preview(self.base,ips,self.sha)
        self.assertEqual(receipt["after"][0]["tokens"][:2],["A","A"])

    def testMissingTerminatorRejected(self):
        altered=bytearray(self.base)
        altered[21]=0
        with self.assertRaisesRegex(ValueError,"MISSING_TERMINATOR"):
            bridge.decode(bytes(altered))

    def testNoEffectRejected(self):
        ips=b"PATCH"+(18).to_bytes(3,"big")+b"\x00\x01\xF0EOF"
        with self.assertRaisesRegex(ValueError,"NO_EFFECT"):
            bridge.preview(self.base,ips,self.sha)

if __name__ == "__main__":
    unittest.main()
