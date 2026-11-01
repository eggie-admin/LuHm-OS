#!/usr/bin/env python3
"""FastAPI host auth and SQL checkpoint tests, using in-process TestClient."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "host" / "api"))
from fastapi.testclient import TestClient
from luhmClientFastApi import create_app

SHA = "f0cb6ee54066b490c0e80efc2c96200fec76ee2d"
TOKEN = "a" * 48
TASK = {"taskId": "taskOne", "sourceRef": SHA, "scopeId": "scopeOne",
        "goal": "Inspect exact-source evidence", "tier": 0}


class TestPrivateFastApi(unittest.TestCase):
    def test_health_only_unauthenticated(self):
        with TestClient(create_app(admin_token=TOKEN)) as c:
            self.assertEqual(c.get("/healthz").status_code, 200)
            self.assertEqual(c.get("/v1/crypto/status").status_code, 401)
            self.assertEqual(c.get("/v1/sql/mariadb-status").status_code, 401)
            self.assertEqual(c.post("/v1/checkpoint", json=TASK).status_code, 401)

    def test_no_token_means_fail_closed(self):
        with TestClient(create_app(admin_token="")) as c:
            self.assertEqual(c.post("/v1/plan", json=TASK).status_code, 503)

    def test_plan_checkpoint_and_sql_exact_scope(self):
        headers = {"X-LuHm-Control-Token": TOKEN}
        with TestClient(create_app(admin_token=TOKEN)) as c:
            plan = c.post("/v1/plan", json=TASK, headers=headers)
            self.assertEqual(plan.status_code, 200)
            self.assertEqual(plan.json()["runningAgentThreads"], 0)
            self.assertIn("ACTIVE_AGENTS_QUARANTINED", plan.json()["blockingConditions"])
            written = c.post("/v1/checkpoint", json=TASK, headers=headers)
            self.assertEqual(written.status_code, 200, written.text)
            self.assertEqual(written.json()["checkpoint"], "TWO_PLANNING_EVENTS_ATOMIC")
            again = c.post("/v1/checkpoint", json=TASK, headers=headers)
            self.assertEqual(again.json()["checkpoint"], "IDEMPOTENT_REPLAY")
            records = c.get("/v1/ledger", headers=headers,
                            params={"taskId": "taskOne", "sourceRef": SHA,
                                    "scopeId": "scopeOne"}).json()
            self.assertEqual(len(records["records"]), 2)
            self.assertFalse(records["greenAuthority"])
            self.assertEqual(c.get("/v1/crypto/status", headers=headers).status_code, 200)
            db = c.get("/v1/sql/mariadb-status", headers=headers)
            self.assertIn("MARIADB_DISABLED", db.json()["blockingConditions"])
            self.assertEqual(c.get("/openapi.json").status_code, 404)

    def test_invalid_extra_fields_denied(self):
        with TestClient(create_app(admin_token=TOKEN)) as c:
            r = c.post("/v1/plan", json={**TASK, "shell": "rm -rf /"},
                       headers={"X-LuHm-Control-Token": TOKEN})
            self.assertEqual(r.status_code, 422)
            self.assertEqual(c.get("/v1/crypto/status",
                headers={"X-LuHm-Control-Token": "wrong"}).status_code, 401)


if __name__ == "__main__":
    unittest.main()
