"""LuHm FFmpeg guardrails and true seven-shot video render, with no cloud calls."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen
import zlib

root = Path(__file__).resolve().parents[1]
path = root / "host/ai-ffmpeg/ai-ffmpeg.py"
spec = importlib.util.spec_from_file_location("aiFfmpeg", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
source = json.loads((root / "media/pirate-daddy-film/episode-template.json").read_text())

def reject(value, inputRoot, outputRoot, marker):
    try:
        mod.validate(value, inputRoot, outputRoot)
        raise AssertionError("negative control missed: " + marker)
    except (ValueError, PermissionError) as exc:
        assert marker in str(exc), str(exc)


def png(color):
    # Portable 32x32 RGB PNG, no Pillow and no downloaded test assets.
    width, height = 32, 32
    raw = b"".join(b"\x00" + bytes(color) * width for _ in range(height))
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))

with tempfile.TemporaryDirectory() as scratch:
    inputRoot = Path(scratch) / "inputs"
    outputRoot = Path(scratch) / "outputs"
    inputRoot.mkdir()
    outputRoot.mkdir()
    candidate = copy.deepcopy(source)
    candidate["reviewApproved"] = True
    for index, shot in enumerate(candidate["shots"]):
        shot["seconds"] = 0.5
        (inputRoot / shot["source"]).write_bytes(png(((index + 1) * 24, 12, 25)))

    reject(source, inputRoot, outputRoot, "CROWN_STOP_REVIEW_REQUIRED")
    copyJob = copy.deepcopy(candidate)
    copyJob["shots"][0]["source"] = "../../etc/passwd"
    reject(copyJob, inputRoot, outputRoot, "RED_PATH_ESCAPE")
    copyJob = copy.deepcopy(candidate)
    copyJob["shots"][0]["source"] = "https://example.com/file.mp4"
    reject(copyJob, inputRoot, outputRoot, "RED_INPUT_MISSING")
    copyJob = copy.deepcopy(candidate)
    copyJob["shots"][0]["source"] = "-filter_complex;touch /tmp/uh-oh"
    reject(copyJob, inputRoot, outputRoot, "RED_INPUT_MISSING")
    copyJob = copy.deepcopy(candidate)
    copyJob["shots"][4]["id"] = "999"
    reject(copyJob, inputRoot, outputRoot, "RED_SHOT_ORDER")
    copyJob = copy.deepcopy(candidate)
    copyJob["shots"][0]["seconds"] = 120
    reject(copyJob, inputRoot, outputRoot, "RED_SHOT_DURATION")
    copyJob = copy.deepcopy(candidate)
    copyJob["shots"][0]["fit"] = "drawtext=evil"
    reject(copyJob, inputRoot, outputRoot, "RED_FIT")
    copyJob = copy.deepcopy(candidate)
    copyJob["arbitraryCommand"] = "rm -rf /"
    reject(copyJob, inputRoot, outputRoot, "RED_MANIFEST_FIELDS")

    # Distinct output from true FFmpeg execution, never a fake GREEN.
    receipt = mod.render(candidate, inputRoot, outputRoot)
    movie = outputRoot / "pirate-daddy-pilot-001.mp4"
    assert receipt["status"] == "CANDIDATE_RENDERED"
    assert receipt["publicationApproved"] is False and receipt["crown"] == "STOP"
    assert receipt["sha256"] == hashlib.sha256(movie.read_bytes()).hexdigest()
    assert 3.4 <= receipt["durationSeconds"] <= 3.8, receipt
    assert (outputRoot / "pirate-daddy-pilot-001.receipt.json").is_file()
    assert mod.probe(movie)["streams"][0]["codec_type"] == "video"
    proofDir = os.getenv("LUHM_FFMPEG_PROOF_DIR", "")
    if proofDir:
        import shutil
        destination = Path(proofDir).resolve()
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copy2(movie, destination / movie.name)
        shutil.copy2(outputRoot / "pirate-daddy-pilot-001.receipt.json", destination / "pirate-daddy-pilot-001.receipt.json")
        (destination / "readme.txt").write_text("Synthetic 7-shot FFmpeg CI preview. Not approved Pirate Daddy canon or production footage.\\n")
    reject(candidate, inputRoot, outputRoot, "RED_OUTPUT_EXISTS_OR_TYPE")

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    env = dict(os.environ, LUHM_FFMPEG_TOKEN="x" * 32)
    proc = subprocess.Popen([sys.executable, str(path), "serve", "--port", str(port),
                             "--input-root", str(inputRoot), "--output-root", str(outputRoot)],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    try:
        health = None
        for attempt in range(60):
            try:
                with urlopen(f"http://127.0.0.1:{port}/healthz", timeout=1) as response:
                    health = json.load(response)
                break
            except Exception:
                time.sleep(0.1)
        assert health is not None, "service failed to start"
        assert health["status"] == "ALIVE" and health["scope"] == "loopback"
        assert health["publicationApproved"] is False
    finally:
        proc.terminate()
        proc.communicate(timeout=10)
    try:
        mod.serve("0.0.0.0", 8797, inputRoot, outputRoot)
        raise AssertionError("public binding should fail")
    except ValueError as exc:
        assert "RED_LOOPBACK_ONLY" in str(exc)
print("AI_FFMPEG_LOCAL_RENDER_AND_NEGATIVE_CONTROLS_GREEN")
