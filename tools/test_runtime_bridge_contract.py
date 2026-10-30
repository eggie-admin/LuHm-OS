#!/usr/bin/env python3
"""Offline stdlib-only npm/Python/AI bridge contract checks; no commands executed."""
import json
import re
import unittest

SCHEMA = "luhm.runtimeBridge.v1"
RUNTIMES = frozenset({"npm", "python3", "ai"})
CAPABILITIES = frozenset({"inventory.read", "job.status.read", "studio.manifest.validate"})
ID = re.compile(r"[a-z][a-z0-9-]{2,63}\Z")


def validate(message):
    if not isinstance(message, dict):
        raise ValueError("message must be an object")
    fields = {"schema", "requestId", "runtime", "capability", "payload"}
    if set(message) != fields or message["schema"] != SCHEMA:
        raise ValueError("schema or fields invalid")
    if not isinstance(message["requestId"], str) or not ID.fullmatch(message["requestId"]):
        raise ValueError("invalid request id")
    if message["runtime"] not in RUNTIMES:
        raise ValueError("unknown runtime")
    if message["capability"] not in CAPABILITIES:
        raise PermissionError("capability denied")
    if not isinstance(message["payload"], dict) or message["payload"]:
        raise ValueError("only empty discovery payload is supported")
    if len(json.dumps(message, sort_keys=True)) > 2048:
        raise ValueError("oversize request")
    return {"schema": SCHEMA, "requestId": message["requestId"],
            "status": "VALIDATED_ONLY", "executionAllowed": False}


class BridgeContractTests(unittest.TestCase):
    def setUp(self):
        self.request = {"schema": SCHEMA, "requestId": "test-001",
                        "runtime": "python3", "capability": "inventory.read", "payload": {}}

    def test_discovery_only(self):
        self.assertFalse(validate(self.request)["executionAllowed"])

    def test_reject_unknown_fields(self):
        with self.assertRaises(ValueError):
            validate({**self.request, "shell": "id"})

    def test_reject_privileged_capability(self):
        with self.assertRaises(PermissionError):
            validate({**self.request, "capability": "firmware.flash"})

    def test_reject_prompt_payload(self):
        with self.assertRaises(ValueError):
            validate({**self.request, "payload": {"command": "npm install"}})

    def test_reject_runtime(self):
        with self.assertRaises(ValueError):
            validate({**self.request, "runtime": "shell"})

    def test_reject_bad_id(self):
        with self.assertRaises(ValueError):
            validate({**self.request, "requestId": "../escape"})


if __name__ == "__main__":
    unittest.main()
