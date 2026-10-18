#!/usr/bin/env python3
"""Deterministic negative tests: no media player needed."""
import importlib.util
from pathlib import Path
import tempfile

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("release_gate", root / "tools/mediaReleaseGate.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "candidate.mp4"
    path.write_bytes(b"fixture-not-video")
    digest = module.sha256(path)
    packet = {
        "schema": "luhm.mediaReleasePacket.v1",
        "sourceCommit": "a" * 40,
        "sourceSha256": "b" * 64,
        "outputSha256": digest,
        "contentLane": "cathedralPublic",
        "publicAllowed": True,
        "assetRights": [{"assetId": "test", "provenance": "original",
                          "licenseEvidence": "owned-and-reviewed", "sha256": "c" * 64,
                          "publicAllowed": True}],
        "professorApproval": {"approved": True, "receipt": "fixture-only"},
        "destination": "instagram",
    }
    probe = {"streams": [{"codec_type": "video", "codec_name": "h264",
                          "width": 1080, "height": 1920}],
             "format": {"duration": "3.0"}}
    assert module.evaluate(packet, path, probe)["status"].startswith("GREEN")
    cases = [
        ("empty", {}, ["schema"]),
        ("private", {**packet, "contentLane": "privateMutation"}, ["publicLane"]),
        ("unapproved", {**packet, "professorApproval": {"approved": False}}, ["professorApproval"]),
        ("no-rights", {**packet, "assetRights": []}, ["assetRightsMissing"]),
        ("bad-digest", {**packet, "outputSha256": "0" * 64}, ["mediaHashMismatchOrMissing"]),
    ]
    for label, data, expected in cases:
        result = module.evaluate(data, path, probe)
        assert result["status"] == "RED" and all(e in result["errors"] for e in expected), label
    assert module.evaluate(packet, path, None)["status"] == "RED"
    print("GREEN_RELEASE_GATE_NEGATIVE_FIXTURES")
