#!/usr/bin/env python3
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from host.openai.lumHost import (
    ENDPOINT, PROBE_EXPECTED, ConfigurationError,
    create_response, probe, status,
)

class FakeResponse:
    def __init__(self, payload):
        self._raw = json.dumps(payload).encode("utf-8")
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self):
        return self._raw

seen = {}
def fake_open(request, timeout):
    seen["url"] = request.full_url
    seen["auth"] = request.headers.get("Authorization")
    seen["body"] = json.loads(request.data.decode("utf-8"))
    return FakeResponse({
        "id": "resp_test",
        "model": "test-model",
        "output": [{
            "type": "message",
            "content": [{"type": "output_text", "text": PROBE_EXPECTED}]
        }]
    })

env = {"OPENAI_API_KEY": "unit-test-secret", "LUHM_OPENAI_MODEL": "test-model"}
payload = create_response("hello", env=env, opener=fake_open)
assert payload["id"] == "resp_test"
assert seen["url"] == ENDPOINT
assert seen["auth"] == "Bearer unit-test-secret"
assert seen["body"]["model"] == "test-model"
assert seen["body"]["store"] is False
assert "Professor" in seen["body"]["instructions"]
assert "recursive" in seen["body"]["instructions"]
receipt = probe(env=env, opener=fake_open)
assert receipt["status"] == "OPENAI_LIVE_GREEN"
assert receipt["response_id"] == "resp_test"
assert "unit-test-secret" not in json.dumps(receipt)
assert status({}) == "RED_OPENAI_LIVE_RECEIPT_MISSING"
assert status({"OPENAI_API_KEY": "x"}) == "AMBER_OPENAI_MODEL_NOT_CONFIGURED"
assert status(env) == "AMBER_OPENAI_CONFIG_PRESENT_LIVE_PROBE_REQUIRED"
try:
    create_response("x", env={}, opener=fake_open)
    raise AssertionError("missing key should fail")
except ConfigurationError:
    pass
print("OPENAI_HOST_ADAPTER_SMOKE=PASS")
