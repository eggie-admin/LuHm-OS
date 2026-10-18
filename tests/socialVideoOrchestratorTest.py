#!/usr/bin/env python3
"""Orchestration source preflight fixtures; no secret keys or external services."""
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory

p = Path(__file__).resolve().parents[1] / "tools/socialVideoOrchestrator.py"
spec = importlib.util.spec_from_file_location("orchestrator", p)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

with TemporaryDirectory() as t:
    root = Path(t)
    media = root / "media"
    out = root / "out"
    media.mkdir()
    out.mkdir()
    shots = []
    for name in mod.SHOTS:
        file = media / (name + ".png")
        file.write_bytes(b"fixture")
        shots.append({"id": name, "source": file.name, "seconds": 2, "fit": "contain"})
    job = {"schema": "luhm.aiFfmpegJob.v1", "jobId": "test-001",
           "reviewApproved": False, "output": "test-001.mp4", "shots": shots}
    assert mod.preflight(job, media, out)["status"] == "READY_FOR_PRIVATE_RENDER"
    shots[0]["source"] = "../../outside.png"
    assert mod.preflight(job, media, out)["status"] == "RED"
    shots[0]["source"] = "100.png"
    shots[-1]["seconds"] = 90
    assert mod.preflight(job, media, out)["status"] == "RED"
    shots[-1]["seconds"] = 2
    (out / "test-001.mp4").write_bytes(b"existing")
    assert "output-exists" in mod.preflight(job, media, out)["errors"]
    print("GREEN_SOCIAL_VIDEO_PREFLIGHT_FIXTURES")
