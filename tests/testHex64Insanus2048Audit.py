"""Negative controls for the Hex64 Insanus 2048 source-policy matrix."""
import tempfile
import unittest
from pathlib import Path

from tools import hex64Insanus2048Audit as hex64


class Hex64AuditTests(unittest.TestCase):
    def test_exact_64_byte_record_layout(self):
        self.assertEqual(hex64.RECORD.size, 64)
        self.assertEqual(len(hex64.STAGES), 16)

    def test_2048_unique_cases_and_records(self):
        data = list(hex64.matrix("f" * 40))
        self.assertEqual(len(data), 2048)
        self.assertEqual(len({row["id"] for row, _ in data}), 2048)
        self.assertEqual(len(b"".join(raw for _, raw in data)), 131072)
        self.assertTrue(all(len(raw) == 64 and raw[:4] == b"LH64"
                            for _, raw in data))
        self.assertTrue(all(row["pass"] for row, _ in data))

    def test_red_unknown_stale_and_wrong_source_hold(self):
        for stage in range(16):
            for tier in range(4):
                for authority in range(4):
                    for evidence in (1, 2, 3, 4, 5, 7):
                        self.assertEqual(
                            hex64.gate_decision(stage, evidence, authority, tier),
                            "HOLD"
                        )

    def test_root_sandbox_does_not_grant_repo_mutation(self):
        for stage in (3, 5, 6, 7, 14):
            for tier in range(4):
                self.assertEqual(
                    hex64.gate_decision(stage, 0, 2, tier), "HOLD"
                )

    def test_tier_escalation_never_changes_authority(self):
        for stage in range(16):
            for evidence in range(8):
                for authority in range(4):
                    results = {hex64.gate_decision(stage, evidence, authority, tier)
                               for tier in range(4)}
                    self.assertEqual(len(results), 1)

    def test_crown_and_quarantine_always_hold(self):
        for stage in (11, 12, 13, 15):
            for evidence in range(8):
                for authority in range(4):
                    self.assertEqual(
                        hex64.gate_decision(stage, evidence, authority, 3), "HOLD"
                    )

    def test_receipt_is_source_only_and_stops_crown(self):
        with tempfile.TemporaryDirectory() as temp:
            report, ok = hex64.run(hex64.ROOT, "a" * 40, Path(temp))
            self.assertTrue(ok, report["sourceAnchors"])
            self.assertEqual(report["verdict"], "SOURCE_MODEL_PASS")
            self.assertFalse(report["runtimeProven"])
            self.assertFalse(report["productionReleased"])
            self.assertFalse(report["autoAgentsActivated"])
            self.assertEqual(report["crownStatus"], "STOP")
            self.assertEqual(
                (Path(temp) / "hex64-insanus2048.bin").stat().st_size,
                2048 * 64
            )


if __name__ == "__main__":
    unittest.main()
