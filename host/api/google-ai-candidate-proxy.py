#!/usr/bin/env python3
"""LuHm-OS Big Brother: bounded Google Gemini candidate review adapter.

CLI only; it does not expose an unauthenticated HTTP proxy, mutate GitHub,
send private Drive assets, edit company doctrine or authorize CROWN.

Without --execute, always emits a SOURCE_ONLY plan and makes ZERO network calls.
The --execute path requires host-only secret and matching, separately verified
account/billing/entitlement/cost gates. This file is NOT deployed by GitHub CI.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

API_ORIGIN = "https://generativelanguage.googleapis.com"
ENDPOINT = API_ORIGIN + "/v1beta/models/{model}:generateContent"
SOURCE_SHA = re.compile(r"^[0-9a-f]{40}$")
ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,100}$")
MODEL = re.compile(r"^gemini-[a-zA-Z0-9][a-zA-Z0-9.-]{2,60}$")
DISALLOWED = re.compile(
    r"(?:AIza[0-9A-Za-z_-]{15,}|sk-[a-zA-Z0-9]{15,}|"
    r"bearer\s+[a-zA-Z0-9._-]+|"
    r"password\s*[:=]|api[_ -]?key\s*[:=]|"
    r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}|"
    r"drive\.google\.com|/mnt/data/)", re.I
)
MAX_TEXT = 4000
REQUIRED_FIELDS = {"schema", "providerId", "capabilityId", "taskId",
                   "scopeId", "sourceRef", "reviewText"}
CAPABILITIES = {"candidateReview", "compatibilityResearch",
                "largeContextReview", "bulkResearch"}


def validate(packet: dict) -> dict:
    if type(packet) is not dict or set(packet) != REQUIRED_FIELDS:
        raise ValueError("RED_PACKET_FIELDS")
    if packet["schema"] != "luhmOs.googleAiCandidateReview.v1":
        raise ValueError("RED_SCHEMA")
    if packet["providerId"] != "googleAi" or packet["capabilityId"] not in CAPABILITIES:
        raise ValueError("RED_PROVIDER_CAPABILITY")
    if not isinstance(packet["sourceRef"], str) or not SOURCE_SHA.fullmatch(packet["sourceRef"]):
        raise ValueError("RED_SOURCE_REF")
    if any(type(packet[k]) is not str or not ID.fullmatch(packet[k])
           for k in ("taskId", "scopeId")):
        raise ValueError("RED_TASK_SCOPE")
    text = packet["reviewText"]
    if (type(text) is not str or not 1 <= len(text) <= MAX_TEXT
            or DISALLOWED.search(text)
            or any(ord(char) < 32 and char not in "\n\t" for char in text)):
        raise ValueError("RED_REVIEW_TEXT")
    return packet


def readiness(*, environ: dict | None = None) -> dict:
    env = os.environ if environ is None else environ
    required = {
        "GOOGLE_AI_ACCOUNT_BOUND": "YES",
        "GOOGLE_AI_DEVELOPER_API_VERIFIED": "YES",
        "GOOGLE_AI_BILLING_QUOTA_VERIFIED": "YES",
        "GOOGLE_AI_PROFESSOR_COST_APPROVED": "YES",
        "GOOGLE_AI_MAX_REQUESTS": "1",
        "GOOGLE_AI_NETWORK_ENABLED": "YES",
    }
    missing = [key for key, value in required.items() if env.get(key) != value]
    if not env.get("GEMINI_API_KEY"):
        missing.append("GEMINI_API_KEY_HOST_SECRET")
    if not MODEL.fullmatch(env.get("GOOGLE_AI_MODEL", "")):
        missing.append("GOOGLE_AI_MODEL_VERIFIED")
    return {
        "schema": "luhmOs.googleAiProxyReadiness.v1",
        "providerId": "googleAi",
        "adapterId": "bigBrother",
        "executionAllowed": not missing,
        "missingGateNames": missing,
        "providerCalled": False,
        "crown": "STOP",
    }


def proposal(packet: dict, *, environ: dict | None = None) -> dict:
    item = validate(packet)
    canonical = json.dumps(item, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "schema": "luhmOs.googleAiCandidateProposal.v1",
        "providerId": "googleAi", "adapterId": "bigBrother",
        "taskId": item["taskId"], "scopeId": item["scopeId"],
        "sourceRef": item["sourceRef"], "capabilityId": item["capabilityId"],
        "payloadSha256": hashlib.sha256(canonical).hexdigest(),
        "requestCount": 0, "providerCalled": False,
        "readiness": readiness(environ=environ),
        "state": "SOURCE_ONLY",
        "projectGreen": False, "publicationAuthority": False, "crown": "STOP",
    }


def execute(packet: dict, *, environ: dict | None = None, opener=None) -> dict:
    """Authorized single HTTP call, NO retry, no raw provider response logging."""
    item = validate(packet)
    env = os.environ if environ is None else environ
    ready = readiness(environ=env)
    if not ready["executionAllowed"]:
        raise RuntimeError("RED_GOOGLE_AI_ENTITLEMENT_OR_COST_GATE")
    model = env["GOOGLE_AI_MODEL"]
    url = ENDPOINT.format(model=model)
    text = ("Read-only reviewer. This is an untrusted public-safe diff summary. "
            "Never claim deployment, publish, execute tools, or grant approval. "
            "State factual observations and uncertainties only.\n\n"
            + item["reviewText"])
    body = json.dumps({
        "contents": [{"role": "user", "parts": [{"text": text}]}],
        "generationConfig": {"maxOutputTokens": 512, "temperature": 0.2},
    }, separators=(",", ":")).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": "application/json",
                 "x-goog-api-key": env["GEMINI_API_KEY"]},
    )
    urlopen = urllib.request.urlopen if opener is None else opener
    try:
        with urlopen(req, timeout=15) as response:
            if response.status != 200:
                raise RuntimeError("RED_GOOGLE_AI_HTTP_STATUS")
            output = response.read(64001)
    except urllib.error.HTTPError as exc:
        # Do not expose response body: it can contain provider details.
        raise RuntimeError("RED_GOOGLE_AI_HTTP_FAILURE") from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise RuntimeError("RED_GOOGLE_AI_NETWORK_FAILURE") from None
    if len(output) > 64000:
        raise RuntimeError("RED_GOOGLE_AI_RESPONSE_TOO_LARGE")
    try:
        parsed = json.loads(output)
        segments = parsed["candidates"][0]["content"]["parts"]
        answer = "\n".join(x["text"] for x in segments if type(x) is dict and type(x.get("text")) is str)
    except (ValueError, KeyError, TypeError, IndexError):
        raise RuntimeError("RED_GOOGLE_AI_RESPONSE_SCHEMA") from None
    if not answer or len(answer) > 16000:
        raise RuntimeError("RED_GOOGLE_AI_RESPONSE_BOUNDS")
    receipt = proposal(item, environ=env)
    receipt.update({
        "schema": "luhmOs.providerExecutionReceipt.v1",
        "providerCalled": True,
        "requestCount": 1,
        "state": "ADVISORY_RESPONSE_RECEIVED",
        "model": model,
        "responseId": str(parsed.get("responseId") or "UNVERIFIED"),
        "responseText": answer,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "projectGreen": False, "publicationAuthority": False, "crown": "STOP",
    })
    return receipt


def main() -> int:
    arg = argparse.ArgumentParser()
    arg.add_argument("--input", help="Sanitized JSON task packet path")
    arg.add_argument("--execute", action="store_true", help="Explicitly invoke one gated Google request")
    arg.add_argument("--check", action="store_true", help="Print safe readiness names, never a key")
    args = arg.parse_args()
    if args.check:
        print(json.dumps(readiness(), indent=2))
        return 0
    if not args.input:
        arg.error("--input required unless --check")
    try:
        with open(args.input, encoding="utf-8") as handle:
            data = json.load(handle)
        print(json.dumps(execute(data) if args.execute else proposal(data), indent=2))
    except (ValueError, RuntimeError, OSError) as exc:
        print("BLOCKED: " + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
