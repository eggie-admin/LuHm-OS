#!/usr/bin/env python3
"""Adversarial regression tests for bounded machine bytes, queue and SQL receipts."""
import hashlib
import unittest

from tools import castMachineByteAudit as m

class MachineByteAuditTests(unittest.TestCase):
    def testUtf8BytesNotCharacterCount(self):
        frame, sha = m.frame_text("優先⚡")
        self.assertEqual(len(frame), 4 + len("優先⚡".encode("utf-8")))
        self.assertEqual(m.unframe_text(frame, sha), "優先⚡")
        self.assertGreater(len(frame) - 4, len("優先⚡"))

    def testRejectOversizedUtf8EvenIfShortCharacterCount(self):
        with self.assertRaisesRegex(m.MachineBoundaryError, "UTF8_BYTE_BUDGET"):
            m.frame_text("⚡" * 1500)

    def testRejectSurrogatesAndNonCanonicalText(self):
        for bad in ("\ud800", "e\u0301", "", 42):
            with self.subTest(value=repr(bad)), self.assertRaises(m.MachineBoundaryError):
                m.frame_text(bad)

    def testRejectForgedLengthsAndTrailingBytes(self):
        frame, sha = m.frame_text("safe")
        for bad in (b"", b"\x00\x00\x00\x08" + frame[4:],
                    frame + b"X", b"\xff\xff\xff\xff" + frame[4:]):
            with self.subTest(frame=bad), self.assertRaises(m.MachineBoundaryError):
                m.unframe_text(bad, sha)

    def testRejectDigestForgeryAndInvalidFrameUtf8(self):
        frame, sha = m.frame_text("safe")
        with self.assertRaisesRegex(m.MachineBoundaryError, "SHA256_MISMATCH"):
            m.unframe_text(frame, "0" * 64)
        with self.assertRaisesRegex(m.MachineBoundaryError, "DIGEST_SHAPE"):
            m.unframe_text(frame, "xyz")
        invalid = b"\x00\x00\x00\x01\xff"
        with self.assertRaisesRegex(m.MachineBoundaryError, "FRAME_UTF8"):
            m.unframe_text(invalid, hashlib.sha256(b"\xff").hexdigest())

    def testPriorityAndBoundedWaitAging(self):
        rows = m.rank_work([{"sequence": 1, "priority": 0, "enqueuedNs": 0},
                           {"sequence": 2, "priority": 3, "enqueuedNs": 9_000_000_000},
                           {"sequence": 3, "priority": 1, "enqueuedNs": 8_000_000_000}],
                           10_000_000_000)
        self.assertEqual([r["sequence"] for r in rows], [1, 2, 3])
        self.assertEqual(rows[0]["effectivePriority"], 3)
        self.assertEqual(rows[0]["waitNs"], 10_000_000_000)

    def testRejectUnboundedQueueAndInvalidPriority(self):
        item = {"sequence": 0, "priority": 2, "enqueuedNs": 0}
        for items, now in (([item] * 33, 10), ([dict(item, priority=4)], 10),
                           ([dict(item, priority=True)], 10),
                           ([dict(item, enqueuedNs=11)], 10), ([item, item], 10)):
            with self.subTest(items=len(items)), self.assertRaises(m.MachineBoundaryError):
                m.rank_work(items, now)

    def testSqlReceiptNumericAndInMemory(self):
        frame, sha = m.frame_text("hello")
        rows = m.rank_work([{"sequence": 3, "priority": 1, "enqueuedNs": 0},
                            {"sequence": 1, "priority": 3, "enqueuedNs": 0}], 0)
        result = m.sqlite_receipt(rows, sha, len(frame) - 4)
        self.assertEqual(result["prioritySequence"], [1, 3])
        self.assertFalse(result["serviceOpened"])
        for invalid in (True, -1, 4097):
            with self.assertRaises(m.MachineBoundaryError):
                m.sqlite_receipt(rows, sha, invalid)

    def testRegistryAndAuthorityRemainSourceOnly(self):
        report = m.audit()
        self.assertEqual(report["status"], "AMBER_SOURCE_ONLY")
        self.assertEqual(report["matrix"]["logicalCells"], [f"0x{i:02X}" for i in range(16)])
        self.assertEqual(report["matrix"]["cellsPhysicallyProven"], 0)
        self.assertEqual([v["kind"] for v in report["registry"]], sorted(m.REGISTRY))
        self.assertFalse(report["kernelChanged"])
        self.assertFalse(report["physicalDeviceVerified"])
        self.assertEqual(report["crownStatus"], "STOP")

if __name__ == "__main__":
    unittest.main()
