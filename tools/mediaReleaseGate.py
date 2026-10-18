#!/usr/bin/env python3
"""Fail-closed media release packet inspection. No uploads or publication."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

LANE = "cathedralPublic"
HEX = re.compile(r"^[0-9a-f]{64}$")
SHA = re.compile(r"^[0-9a-f]{40}$")

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def evaluate(packet, media, probe=None):
    errors = []
    if not isinstance(packet, dict) or packet.get("schema") != "luhm.mediaReleasePacket.v1":
        return {"status": "RED", "errors": ["schema"], "publicationApproved": False}
    required = ("sourceCommit", "sourceSha256", "outputSha256", "assetRights",
                "contentLane", "publicAllowed", "professorApproval", "destination")
    for key in required:
        if key not in packet:
            errors.append("missing:" + key)
    if not SHA.fullmatch(str(packet.get("sourceCommit", ""))):
        errors.append("sourceCommit")
    if not HEX.fullmatch(str(packet.get("sourceSha256", ""))):
        errors.append("sourceSha256")
    output_hash = packet.get("outputSha256")
    if not HEX.fullmatch(str(output_hash)):
        errors.append("outputSha256")
    elif not media.is_file() or sha256(media) != output_hash:
        errors.append("mediaHashMismatchOrMissing")
    if packet.get("contentLane") != LANE or packet.get("publicAllowed") is not True:
        errors.append("publicLane")
    rights = packet.get("assetRights")
    if not isinstance(rights, list) or not rights:
        errors.append("assetRightsMissing")
    else:
        for i, asset in enumerate(rights):
            if not isinstance(asset, dict) or not all(
                asset.get(k) for k in ("assetId", "provenance", "licenseEvidence", "sha256")
            ) or not HEX.fullmatch(str(asset.get("sha256", ""))) or asset.get("publicAllowed") is not True:
                errors.append("assetRights:" + str(i))
    approval = packet.get("professorApproval")
    if not isinstance(approval, dict) or approval.get("approved") is not True or not approval.get("receipt"):
        errors.append("professorApproval")
    if packet.get("destination") not in ("tiktok", "instagram", "facebook"):
        errors.append("destination")
    if probe is None:
        errors.append("ffprobeUnavailable")
    elif isinstance(probe, dict):
        streams = probe.get("streams", [])
        video = [s for s in streams if s.get("codec_type") == "video"]
        if len(video) != 1 or video[0].get("codec_name") != "h264":
            errors.append("videoCodec")
        elif (video[0].get("width"), video[0].get("height")) != (1080, 1920):
            errors.append("videoSize")
        audio = [s for s in streams if s.get("codec_type") == "audio"]
        if any(s.get("codec_name") != "aac" for s in audio):
            errors.append("audioCodec")
        try:
            duration = float(probe.get("format", {}).get("duration", 0))
            if not 0 < duration <= 180:
                errors.append("duration")
        except (ValueError, TypeError):
            errors.append("duration")
    return {"schema": "luhm.mediaReleaseGateReceipt.v1",
            "status": "GREEN_ELIGIBLE_FOR_MANUAL_PUBLICATION" if not errors else "RED",
            "errors": errors, "publicationApproved": False,
            "mediaSha256": sha256(media) if media.is_file() else None,
            "manualPublicationRequired": True}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--packet", required=True, type=Path)
    ap.add_argument("--media", required=True, type=Path)
    args = ap.parse_args()
    packet = json.loads(args.packet.read_text(encoding="utf-8"))
    probe = None
    if args.media.is_file():
        try:
            completed = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries",
                 "stream=codec_type,codec_name,width,height:format=duration",
                 "-of", "json", str(args.media)],
                check=True, capture_output=True, text=True, timeout=15)
            probe = json.loads(completed.stdout)
        except (OSError, ValueError, subprocess.SubprocessError):
            pass
    receipt = evaluate(packet, args.media, probe)
    print(json.dumps(receipt, indent=2))
    raise SystemExit(0 if receipt["status"].startswith("GREEN") else 1)

if __name__ == "__main__":
    main()
