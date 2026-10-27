#!/usr/bin/env python3
"""Offline LuHm AI-manifest bridge into the existing typed duplex bus.

RSS/Atom carries references, base64 carries canonical JSON, and the v1 duplex
bus carries real bytes. None of those transports grants agent authority.
NO network, Google API call, SQL migration, credential read or backend workers.
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from duplexTypedBusCodec import Frame, WireError, decode_frame, encode_frame, MAX_PAYLOAD

TASK_SCHEMA = "luhmOs.aiTaskManifest.v2"
RECEIPT_SCHEMA = "luhmOs.providerExecutionReceipt.v1"
FEED_SCHEMA = "luhmOs.aiManifestFeedProjection.v1"
STREAM_IDS = {"app": 11, "plugin": 12}
REQUIRED = {"schema", "providerId", "capabilityId", "taskId",
            "sourceRef", "scopeId", "inputRefs", "requiredOutputSchema",
            "budget", "stopConditions", "authority"}
SHA = re.compile(r"[0-9a-f]{40}\Z")
SAFE_ID = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9._-]{2,100}\Z")
SAFE_GITHUB_REF = re.compile(
    r"github:[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+@[0-9a-f]{40}:[a-zA-Z0-9_./-]+\Z"
)
FORBIDDEN = re.compile(r"api.?key|password|credentials?|private.?key|access.?token|bearer", re.I)


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def no_duplicates(pairs: list[tuple[str, object]]) -> dict:
    obj = {}
    for name, value in pairs:
        if name in obj:
            raise ValueError("RED_DUPLICATE_JSON_KEY")
        obj[name] = value
    return obj


def validate_manifest(packet: dict) -> bytes:
    if type(packet) is not dict or set(packet) != REQUIRED:
        raise ValueError("RED_MANIFEST_FIELDS")
    if packet["schema"] != TASK_SCHEMA or packet["providerId"] not in ("googleAi", "deterministicLocal"):
        raise ValueError("RED_SCHEMA_OR_PROVIDER")
    if packet["requiredOutputSchema"] != RECEIPT_SCHEMA:
        raise ValueError("RED_RECEIPT_SCHEMA")
    if not isinstance(packet["sourceRef"], str) or not SHA.fullmatch(packet["sourceRef"]):
        raise ValueError("RED_SOURCE_SHA")
    for key in ("taskId", "scopeId", "capabilityId"):
        if not isinstance(packet[key], str) or not SAFE_ID.fullmatch(packet[key]):
            raise ValueError("RED_IDENTITY")
    budget = packet["budget"]
    if (type(budget) is not dict or set(budget) != {"maxRequests", "maxParallel", "maxPasses"}
            or any(type(v) is not int or not 1 <= v <= 3 for v in budget.values())
            or budget["maxParallel"] != 1):
        raise ValueError("RED_BUDGET")
    if packet["authority"] != {"mutation": False, "green": False, "crown": False}:
        raise ValueError("RED_AUTHORITY")
    refs = packet["inputRefs"]
    if (type(refs) is not list or len(refs) > 8
            or any(not isinstance(r, str) or not SAFE_GITHUB_REF.fullmatch(r)
                   or ".." in r for r in refs)):
        raise ValueError("RED_INPUT_REFS")
    if (packet["stopConditions"] != ["scopeComplete", "evidenceConflict",
                                      "sourceMismatch", "budgetExhausted"]):
        raise ValueError("RED_STOP_CONDITIONS")
    if FORBIDDEN.search(json.dumps(packet, ensure_ascii=False)):
        raise ValueError("RED_SECRET_FIELD")
    raw = canonical(packet)
    if len(raw) > MAX_PAYLOAD:
        raise ValueError("RED_PAYLOAD_SIZE")
    return raw


def candidate_manifest(*, task_id: str, scope_id: str, source_ref: str,
                       capability_id: str = "candidateReview", provider: str = "googleAi") -> dict:
    packet = {
        "schema": TASK_SCHEMA, "providerId": provider,
        "capabilityId": capability_id, "taskId": task_id,
        "sourceRef": source_ref, "scopeId": scope_id, "inputRefs": [],
        "requiredOutputSchema": RECEIPT_SCHEMA,
        "budget": {"maxRequests": 1, "maxParallel": 1, "maxPasses": 1},
        "stopConditions": ["scopeComplete", "evidenceConflict", "sourceMismatch", "budgetExhausted"],
        "authority": {"mutation": False, "green": False, "crown": False},
    }
    validate_manifest(packet)
    return packet


def feed_projection(packet: dict) -> dict:
    """RSS/Atom projection only. Base64 is encoding, NOT security."""
    raw = validate_manifest(packet)
    return {
        "schema": FEED_SCHEMA, "encoding": "base64-utf8-json",
        "taskId": packet["taskId"], "sourceRef": packet["sourceRef"],
        "sha256": hashlib.sha256(raw).hexdigest(),
        "payloadBase64": base64.b64encode(raw).decode("ascii"),
        "executable": False,
    }


def decode_projection(feed: dict) -> dict:
    if type(feed) is not dict or set(feed) != {
            "schema", "encoding", "taskId", "sourceRef", "sha256", "payloadBase64", "executable"}:
        raise ValueError("RED_FEED_FIELDS")
    if feed["schema"] != FEED_SCHEMA or feed["encoding"] != "base64-utf8-json" or feed["executable"] is not False:
        raise ValueError("RED_FEED_AUTHORITY")
    if not isinstance(feed["payloadBase64"], str):
        raise ValueError("RED_FEED_BASE64")
    try:
        raw = base64.b64decode(feed["payloadBase64"], validate=True)
        obj = json.loads(raw.decode("utf-8"), object_pairs_hook=no_duplicates,
                         parse_constant=lambda _: (_ for _ in ()).throw(ValueError("RED_NONFINITE")))
    except (ValueError, UnicodeError, base64.binascii.Error) as error:
        raise ValueError("RED_FEED_DECODE") from error
    if (hashlib.sha256(raw).hexdigest() != feed["sha256"]
            or raw != validate_manifest(obj)
            or feed["taskId"] != obj["taskId"] or feed["sourceRef"] != obj["sourceRef"]):
        raise ValueError("RED_FEED_TAMPER_OR_NONCANONICAL")
    return obj


def offline_frame(packet: dict, *, track: str, correlation_id: int) -> bytes:
    if track not in STREAM_IDS:
        raise ValueError("RED_UNKNOWN_TRACK")
    return encode_frame(Frame(version=1, lane=3, kind=1,
                              stream_id=STREAM_IDS[track], sequence_id=1,
                              correlation_id=correlation_id,
                              payload=validate_manifest(packet)))


def decode_offline_frame(raw: bytes, *, expected_track: str, expected_sha: str) -> dict:
    if expected_track not in STREAM_IDS:
        raise ValueError("RED_UNKNOWN_TRACK")
    frame = decode_frame(raw)
    if frame.lane != 3 or frame.kind != 1 or frame.stream_id != STREAM_IDS[expected_track]:
        raise ValueError("RED_WRONG_MANIFEST_STREAM")
    try:
        packet = json.loads(frame.payload.decode("utf-8"), object_pairs_hook=no_duplicates,
                            parse_constant=lambda _: (_ for _ in ()).throw(ValueError("RED_NONFINITE")))
    except (UnicodeError, ValueError) as error:
        raise ValueError("RED_FRAME_MANIFEST_JSON") from error
    if frame.payload != validate_manifest(packet) or packet["sourceRef"] != expected_sha:
        raise ValueError("RED_FRAME_SOURCE_OR_PAYLOAD")
    return packet


def self_test() -> None:
    source = "a" * 40
    for track in STREAM_IDS:
        packet = candidate_manifest(task_id=f"cast-{track}-proof", scope_id=f"{track}-track",
                                    source_ref=source)
        assert decode_projection(feed_projection(packet)) == packet
        assert decode_offline_frame(offline_frame(packet, track=track, correlation_id=7),
                                    expected_track=track, expected_sha=source) == packet
    print("PASS_TWO_TRACK_MANIFEST_DUPLEX_SOURCE_ONLY_NO_GOOGLE_CALLS")


if __name__ == "__main__":
    self_test()
