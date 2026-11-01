#!/usr/bin/env python3
"""Dry-run GPU/VRAM and 60-second AI video plan tests, no model/hardware calls."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "luhmGpuVideoPlanner", ROOT / "host/api/luhmGpuVideoPlanner.py")
assert spec is not None and spec.loader is not None
planner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(planner)

SHA = "f0cb6ee54066b490c0e80efc2c96200fec76ee2d"
BASE = {
    "task_id": "videoJobOne", "source_ref": SHA, "scope_id": "studioScope",
    "seconds": 125, "prompt": "A private original character performs a dance",
}


class GpuVideoPlannerTests(unittest.TestCase):
    def test_status_remains_offline_quarantined(self):
        st = planner.status()
        self.assertEqual(st["securityProfiles"],
                         ["localhost", "privateHost", "remoteGpu", "enterprise"])
        self.assertEqual(st["lanes"], ["security", "compute", "media", "evidence"])
        self.assertEqual(st["activeGpuDrivers"], [])
        self.assertFalse(st["videoRendered"])
        self.assertFalse(st["crownAuthority"])

    def test_minute_boundaries_stable_ids_and_no_prompts(self):
        a = planner.plan(**BASE)
        b = planner.plan(**BASE)
        self.assertEqual(a["minuteCount"], 3)
        self.assertEqual([c["durationSeconds"] for c in a["minuteDeliveries"]],
                         [60, 60, 5])
        self.assertEqual(a["modelShotCount"], 21)
        self.assertEqual(a["minuteDeliveries"], b["minuteDeliveries"])
        self.assertEqual(a["status"], "HOLD_NOT_ADMITTED")
        self.assertEqual(a["paidProviderCalls"], 0)
        self.assertEqual(a["renderSchedulingStarted"], False)
        self.assertFalse(a["rawPromptReturned"])
        self.assertNotIn(BASE["prompt"], str(a))
        self.assertIn("COMPANY_WORKER_QUARANTINE", a["blockingConditions"])

    def test_max_vram_uses_headroom_even_for_saucy_mode(self):
        report = {"totalMiB": 24576, "freeMiB": 24000, "reservedMiB": 100}
        res = planner.assess_vram(report, mode="maxApproved", model_estimate_mib=8192)
        self.assertEqual(res["state"], "CAPACITY_FIT_SUGGESTED_UNVERIFIED")
        self.assertLess(res["candidateUsableMiB"], report["freeMiB"])
        self.assertLess(res["candidateUsableMiB"], report["totalMiB"])
        self.assertFalse(res["telemetryTrusted"])
        self.assertFalse(res["allocationAuthorized"])
        pkt = planner.plan(**BASE, vram_mode="maxApproved", reported_gpu=report)
        self.assertEqual(pkt["status"], "HOLD_NOT_ADMITTED")
        self.assertIn("GPU_TELEMETRY_UNATTESTED", pkt["blockingConditions"])

    def test_memory_missing_or_insufficient_holds(self):
        no = planner.plan(**BASE)
        self.assertEqual(no["vram"]["candidateUsableMiB"], 0)
        self.assertIn("GPU_MEMORY_ADMISSION_UNPROVEN", no["blockingConditions"])
        too_small = planner.assess_vram(
            {"totalMiB": 8192, "freeMiB": 2000, "reservedMiB": 0},
            mode="maxApproved", model_estimate_mib=4096)
        self.assertEqual(too_small["state"], "CAPACITY_INSUFFICIENT_OR_UNVERIFIED")

    def test_refuses_resource_counter_inconsistency_and_extra_fields(self):
        for report in (
            {"totalMiB": 8192, "freeMiB": 8000, "reservedMiB": 1200},
            {"totalMiB": 8192, "freeMiB": "8192", "reservedMiB": 0},
            {"totalMiB": 8192, "freeMiB": 8000, "reservedMiB": 0,
             "hostToken": "secret"},
        ):
            with self.subTest(report=report), self.assertRaises(ValueError):
                planner.plan(**BASE, reported_gpu=report)
        with self.assertRaises(ValueError):
            planner.plan(**BASE, vram_mode="allUnsafe")

    def test_bad_source_and_duration_and_frames_rejected(self):
        for updates in (
            {"source_ref": "main"},
            {"seconds": 3601},
            {"seconds": True},
            {"fps": 25},
            {"width": 1279},
            {"model_shot_seconds": 0},
            {"prompt": " "},
            {"prompt": "p" * 1025},
            {"task_id": "../data"},
        ):
            with self.subTest(update=updates), self.assertRaises(ValueError):
                planner.plan(**{**BASE, **updates})

    def test_minute_receipt_comparison_is_never_video_proof(self):
        pkt = planner.plan(**BASE)
        shots = [
            {"shotId": s["shotId"], "durationSeconds": s["durationSeconds"],
             "artifactSha256": "a" * 64}
            for s in pkt["minuteDeliveries"][0]["shots"]
        ]
        result = planner.verify_minute_metadata(pkt, 0, shots)
        self.assertEqual(result["state"], "METADATA_CONSISTENT_UNVERIFIED")
        self.assertFalse(result["bytesProven"])
        self.assertFalse(result["ffprobeVerified"])
        altered = [dict(s) for s in shots]
        altered[0]["shotId"] = "other"
        self.assertEqual(planner.verify_minute_metadata(pkt, 0, altered)["state"],
                         "STOP_METADATA_MISMATCH")
        self.assertEqual(planner.verify_minute_metadata(pkt, 0, shots[:2])["state"],
                         "STOP_COUNT_MISMATCH")

    def test_one_hour_sixty_review_chunks_and_bounded_shots(self):
        pkt = planner.plan(**{**BASE, "seconds": 3600})
        self.assertEqual(pkt["minuteCount"], 60)
        self.assertEqual(pkt["modelShotCount"], 600)
        self.assertEqual(pkt["minuteDeliveries"][-1]["startSecond"], 3540)


if __name__ == "__main__":
    unittest.main()
