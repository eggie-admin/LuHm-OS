#!/usr/bin/env python3
"""Offline synthetic one-minute delivery fixture for the GPU video pipeline.

Produces no model output or user media. When --run is explicitly given,
FFmpeg makes ten six-second testsrc2 videos in a TemporaryDirectory,
concatenates them with a fixed argument vector, verifies duration with
ffprobe and returns a SHA-256 receipt. No GPU, VM, network, AI or permanent
file is used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def run_fixture() -> dict:
    ffmpeg, ffprobe = shutil.which("ffmpeg"), shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        raise RuntimeError("RED_FFMPEG_OR_FFPROBE_MISSING")
    with tempfile.TemporaryDirectory(prefix="luhm-minute-fixture-") as tmp:
        root = Path(tmp)
        entries = ["ffconcat version 1.0"]
        for i in range(10):
            name = f"shot{i:03d}.mp4"
            filename = root / name
            cmd = [
                ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
                "-f", "lavfi", "-i", "testsrc2=size=256x144:rate=12",
                "-t", "6", "-c:v", "mpeg4", "-q:v", "10",
                "-pix_fmt", "yuv420p", "-an", name,
            ]
            subprocess.run(cmd, cwd=root, check=True, stdout=subprocess.DEVNULL,
                           stderr=subprocess.PIPE, timeout=40)
            if not filename.is_file() or filename.stat().st_size <= 0:
                raise RuntimeError("RED_SYNTHETIC_SHOT_MISSING")
            entries.append(f"file '{name}'")
        (root / "list.ffconcat").write_text("\n".join(entries) + "\n", encoding="ascii")
        out = root / "minute.mp4"
        subprocess.run([
            ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
            "-safe", "1", "-f", "concat", "-i", "list.ffconcat",
            "-c", "copy", str(out),
        ], cwd=root, check=True, stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE, timeout=60)
        checked = subprocess.run([
            ffprobe, "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(out),
        ], check=True, capture_output=True, text=True, timeout=15)
        duration = float(checked.stdout.strip())
        if not 59.8 <= duration <= 60.2:
            raise RuntimeError("RED_MINUTE_DURATION_MISMATCH")
        return {
            "schema": "luhmOs.syntheticMinuteFixture.v1",
            "state": "OFFLINE_SYNTHETIC_MINUTE_VERIFIED",
            "syntheticShots": 10,
            "measuredDurationSeconds": duration,
            "outputSha256": sha256_file(out),
            "videoFormat": "mpeg4/mp4",
            "rights": "proceduralTestPatternOnly",
            "mediaRetained": False,
            "actualAIFrames": False,
            "gpuMemoryAllocated": False,
            "networkCalls": 0,
            "greenAuthority": False,
            "crownAuthority": False,
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true",
                        help="explicitly run ephemeral 60-second synthetic FFmpeg proof")
    args = parser.parse_args()
    if not args.run:
        print(json.dumps({
            "schema": "luhmOs.syntheticMinuteFixture.v1",
            "state": "DRY_RUN_ONLY", "durationSeconds": 60,
            "shots": 10, "ffmpegExecution": False
        }))
        return 0
    print(json.dumps(run_fixture(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
