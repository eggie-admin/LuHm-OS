#!/usr/bin/env python3
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import sys
sys.path.insert(0, str(ROOT / "scripts"))
from oniPetActivityRuntime import WorkerActivity, build_snapshot


class OniPetActivityTests(unittest.TestCase):
    def test_three_support_workers_allowed(self):
        snap = build_snapshot(
            task_id="task-1",
            source_ref="abc123",
            phase="VERIFY",
            workers=[
                WorkerActivity("kiri", "SUCCESS", "resolved source"),
                WorkerActivity("tetsu", "VERIFYING", "build"),
                WorkerActivity("drNao", "ACTIVE", "doctor"),
            ],
        )
        self.assertEqual(snap["workers"][0]["id"], "lum")
        self.assertEqual(snap["backgroundAutonomy"], False)
        self.assertEqual(len([w for w in snap["workers"] if w["id"] != "lum"]), 3)

    def test_four_support_workers_rejected(self):
        with self.assertRaises(ValueError):
            build_snapshot(
                task_id="task-2",
                source_ref="abc123",
                phase="ROUTE",
                workers=[
                    WorkerActivity("kiri", "ACTIVE"),
                    WorkerActivity("momo", "ACTIVE"),
                    WorkerActivity("fumi", "ACTIVE"),
                    WorkerActivity("shiori", "ACTIVE"),
                ],
            )

    def test_unknown_role_rejected(self):
        with self.assertRaises(ValueError):
            build_snapshot(
                task_id="task-3",
                source_ref="abc123",
                phase="OBSERVE",
                workers=[WorkerActivity("phantomAgent", "ACTIVE")],
            )

    def test_crown_stop_is_waiting_not_success(self):
        snap = build_snapshot(task_id="task-4", source_ref="abc123", phase="CROWN_STOP", workers=[])
        self.assertEqual(snap["workers"][0]["id"], "lum")
        self.assertEqual(snap["workers"][0]["state"], "WAITING")

    def test_manifest_contains_control_plane_roles(self):
        manifest = json.loads((ROOT / "assets/pet/oni/manifest.json").read_text(encoding="utf-8"))
        ids = {role["id"] for role in manifest["roles"]}
        self.assertEqual(ids, {"lum","fumi","drNao","tetsu","kaji","kiri","momo","shiori","kugi","yume","koe","sumi"})
        self.assertEqual(manifest["maxVisibleSupportWorkers"], 3)
        self.assertIn("never implies hidden background work", manifest["displayTruthRule"])

    def test_frontend_mounts_event_driven_dock(self):
        html = (ROOT / "frontEnd/index.html").read_text(encoding="utf-8")
        js = (ROOT / "frontEnd/jquery/luhm.oni.activity.js").read_text(encoding="utf-8")
        doctrine = json.loads((ROOT / "doctrine/ONI_PET_ACTIVITY_DOCK_V2.json").read_text(encoding="utf-8"))
        self.assertIn("data-luhm-oni-dock", html)
        self.assertIn("luhm:oni-activity", js)
        self.assertIn("support-worker cap exceeded", js)
        self.assertFalse(doctrine["transport"]["polling"])
        self.assertFalse(doctrine["transport"]["backgroundAutonomy"])


if __name__ == "__main__":
    unittest.main()
