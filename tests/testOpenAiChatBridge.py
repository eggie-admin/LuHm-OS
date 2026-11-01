#!/usr/bin/env python3
"""Offline regression tests: no OpenAI credentials, network or paid API calls."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "host" / "api" / "luhmOpenAiChatBridge.py"
spec = importlib.util.spec_from_file_location("luhmOpenAiChatBridge", PATH)
assert spec is not None and spec.loader is not None
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)
SHA = "f0cb6ee54066b490c0e80efc2c96200fec76ee2d"


class BridgeTests(unittest.TestCase):
    def test_status_is_quarantined_and_does_not_echo_secret(self) -> None:
        status = bridge.bridge_status({
            "OPENAI_API_KEY": "fake-secret-never-echo",
            "LUHM_OPENAI_ENABLE_LIVE": "1",
            "LUHM_OPENAI_BILLING_APPROVED": "1",
            "LUHM_OPENAI_MODEL": "example-model",
        })
        self.assertIn("COMPANY_QUARANTINE", status["blockingConditions"])
        self.assertFalse(status["liveExecutionEnabled"])
        self.assertNotIn("fake-secret-never-echo", str(status))

    def test_plan_stays_offline_and_never_echoes_prompt(self) -> None:
        plan = bridge.plan_request(
            "test-1", SHA, "read-only", "semanticSynthesis",
            "private example text", env={}
        )
        self.assertEqual(plan["networkCalls"], 0)
        self.assertEqual(plan["state"], "BLOCKED")
        self.assertNotIn("private example text", str(plan))
        self.assertIn("BILLING_NOT_APPROVED", plan["blockingConditions"])

    def test_scope_and_capability_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            bridge.plan_request("test", "main", "scope")
        with self.assertRaises(ValueError):
            bridge.plan_request("test", SHA, "scope", "sendEmail")
        with self.assertRaises(ValueError):
            bridge.plan_request("test", SHA, "scope", input_text="x" * 6001)
        with self.assertRaises(ValueError):
            bridge.plan_request("test", SHA, "scope", max_output_tokens=9999)

    def test_execution_never_calls_transport_during_quarantine(self) -> None:
        calls = []
        def forbidden_transport(*args: object, **kwargs: object) -> object:
            calls.append((args, kwargs))
            raise AssertionError("never contact provider")
        env = {
            "OPENAI_API_KEY": "not-real",
            "LUHM_OPENAI_ENABLE_LIVE": "1",
            "LUHM_OPENAI_BILLING_APPROVED": "1",
            "LUHM_OPENAI_MODEL": "example-model",
        }
        with self.assertRaisesRegex(PermissionError, "COMPANY_QUARANTINE"):
            bridge.execute_request(
                "test-1", SHA, "read-only", "test", transport=forbidden_transport, env=env
            )
        self.assertEqual(calls, [])

    def test_provider_output_reduced_to_text(self) -> None:
        sample = {
            "output": [
                {"type": "message", "content": [
                    {"type": "output_text", "text": "sample answer"},
                    {"type": "refusal", "refusal": "skip"},
                ]},
                {"type": "function_call", "arguments": "not relayed"},
            ]
        }
        self.assertEqual(bridge._extract_output(sample), "sample answer")


if __name__ == "__main__":
    unittest.main()
