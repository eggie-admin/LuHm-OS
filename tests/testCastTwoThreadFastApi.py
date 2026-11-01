#!/usr/bin/env python3
"""Private authenticated CAST Bridge API source-only smoke and negative tests."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "host/api"))
from luhmClientFastApi import create_app

TOKEN = "k" * 48
SHA = "f0cb6ee54066b490c0e80efc2c96200fec76ee2d"
TASK = {
    "taskId": "demoCast", "sourceRef": SHA, "scopeId": "personalStudio",
    "goal": "Keep private goal only in memory and return its hash",
    "tier": 0, "requestedStage": "sanityCheck"
}


class TestPrivateCastBridgeApi(unittest.TestCase):
    def test_all_cast_routes_reject_unauthenticated_and_empty_token(self):
        with TestClient(create_app(admin_token=TOKEN)) as c:
            self.assertEqual(c.get("/v1/cast-bridge/status").status_code, 401)
            self.assertEqual(c.post("/v1/cast-bridge/plan", json=TASK).status_code, 401)
            self.assertEqual(c.post("/v1/cast-bridge/review", json=TASK).status_code, 401)
            self.assertEqual(c.get("/v1/cast-bridge/status",
                headers={"X-LuHm-Control-Token": "bad"}).status_code, 401)
        with TestClient(create_app(admin_token="")) as c:
            self.assertEqual(c.get("/v1/cast-bridge/status").status_code, 503)

    def test_private_host_status_and_plan_has_two_view_models(self):
        headers = {"X-LuHm-Control-Token": TOKEN}
        with TestClient(create_app(admin_token=TOKEN)) as c:
            status = c.get("/v1/cast-bridge/status", headers=headers)
            self.assertEqual(status.status_code, 200, status.text)
            self.assertEqual(status.json()["matrixCells"], 16)
            self.assertEqual(status.json()["activeAgentThreads"], 0)
            planned = c.post("/v1/cast-bridge/plan", json=TASK, headers=headers)
            self.assertEqual(planned.status_code, 200, planned.text)
            payload = planned.json()
            self.assertEqual(len(payload["threads"]), 2)
            self.assertEqual(len(payload["typedLanes"]), 4)
            self.assertEqual(payload["actualMeshAgentsStarted"], 0)
            self.assertFalse(payload["productionDeployment"])
            self.assertFalse(payload["greenAuthority"])
            self.assertNotIn(TASK["goal"], planned.text)
            self.assertEqual(planned.headers["cache-control"], "no-store")

    def test_evidence_claim_not_verified_and_bad_input_is_rejected(self):
        headers = {"X-LuHm-Control-Token": TOKEN}
        good = {
            "taskId": "demoCast", "sourceRef": SHA,
            "scopeId": "personalStudio", "stage": "sanityCheck",
            "evidenceSha256": "a" * 64
        }
        with TestClient(create_app(admin_token=TOKEN)) as c:
            claimed = c.post("/v1/cast-bridge/review", json={
                **TASK, "evidenceClaims": [good]
            }, headers=headers)
            self.assertEqual(claimed.status_code, 200, claimed.text)
            self.assertFalse(claimed.json()["evidenceReview"]["proofOriginTrusted"])
            self.assertFalse(claimed.json()["greenAuthority"])
            for body in (
                {**TASK, "shellCommand": "echo unsafe"},
                {**TASK, "tier": 4},
                {**TASK, "requestedStage": "CASTED"},
            ):
                with self.subTest(body=body):
                    r = c.post("/v1/cast-bridge/plan", json=body, headers=headers)
                    self.assertEqual(r.status_code, 422)
            mismatch = c.post("/v1/cast-bridge/review",
                json={**TASK, "evidenceClaims": [
                    {**good, "sourceRef": "b" * 40}
                ]}, headers=headers)
            self.assertEqual(mismatch.status_code, 422)
            self.assertEqual(mismatch.json()["detail"], "INVALID_CAST_BRIDGE_RECEIPT")
            self.assertEqual(c.get("/openapi.json").status_code, 404)


if __name__ == "__main__":
    unittest.main()
