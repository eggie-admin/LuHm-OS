#!/usr/bin/env python3
"""LuHm social-video job orchestrator: preflight -> bounded render -> verify -> receipt.

One deterministic executor, three logical roles (Lum/Yume/Skuld). No cloud calls,
publishing, arbitrary model-generated shell, or public media exposure.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

SHOTS = ("100", "200", "300", "401", "402", "403", "500")
EXT = {".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov", ".mkv"}

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()

def preflight(manifest, input_root, output_root):
    errors = []
    if manifest.get("schema") != "luhm.aiFfmpegJob.v1":
        errors.append("invalid-job-schema")
    shots = manifest.get("shots")
    if not isinstance(shots, list) or tuple(s.get("id") for s in shots if isinstance(s, dict)) != SHOTS:
        errors.append("invalid-storyboard")
        shots = []
    sources = []
    root = input_root.resolve()
    for shot in shots:
        rel = shot.get("source")
        if not isinstance(rel, str):
            errors.append("invalid-source")
            continue
        candidate = (root / rel).resolve()
        if root not in candidate.parents or candidate.suffix.lower() not in EXT:
            errors.append("unsafe-source:" + shot["id"])
        elif not candidate.is_file():
            errors.append("missing-source:" + shot["id"])
        elif candidate.stat().st_size > 500 * 1024 * 1024:
            errors.append("oversize-source:" + shot["id"])
        else:
            sources.append({"id": shot["id"], "sha256": digest(candidate)})
        if type(shot.get("seconds")) not in (float, int) or not 0.5 <= shot["seconds"] <= 20:
            errors.append("invalid-duration:" + shot["id"])
    output = manifest.get("output")
    if not isinstance(output, str):
        errors.append("invalid-output")
    else:
        candidate = (output_root.resolve() / output).resolve()
        if candidate.parent != output_root.resolve() or candidate.suffix != ".mp4":
            errors.append("unsafe-output")
        elif candidate.exists():
            errors.append("output-exists")
    return {"schema": "luhm.socialVideoPreflight.v1",
            "status": "READY_FOR_PRIVATE_RENDER" if not errors else "RED",
            "jobId": manifest.get("jobId"), "sources": sources,
            "errors": errors, "publicationApproved": False}

def run(args):
    job = json.loads(args.manifest.read_text(encoding="utf-8"))
    report = preflight(job, args.input_root, args.output_root)
    if args.action == "preflight":
        print(json.dumps(report, indent=2))
        return 0 if report["status"] == "READY_FOR_PRIVATE_RENDER" else 1
    if report["errors"]:
        print(json.dumps(report, indent=2))
        return 1
    if not args.approve_private_render:
        print("CROWN_STOP_EXPLICIT_PRIVATE_RENDER_APPROVAL_REQUIRED", file=sys.stderr)
        return 1
    if job.get("reviewApproved") is not True:
        print("CROWN_STOP_MANIFEST_REVIEW_REQUIRED", file=sys.stderr)
        return 1
    worker = Path(__file__).resolve().parents[1] / "host/ai-ffmpeg/ai-ffmpeg.py"
    command = [sys.executable, str(worker), "render", "--manifest", str(args.manifest),
               "--input-root", str(args.input_root), "--output-root", str(args.output_root),
               "--approve-render"]
    # Never run model-generated commands. A fixed argv invokes the existing bounded renderer.
    result = subprocess.run(command, check=False, capture_output=True, text=True, timeout=1800)
    if result.returncode:
        print("RED_WORKER_RENDER_FAILED", file=sys.stderr)
        return 1
    output = args.output_root / job["output"]
    receipt = output.with_suffix(".receipt.json")
    if not output.is_file() or not receipt.is_file():
        print("RED_OUTPUT_OR_RECEIPT_MISSING", file=sys.stderr)
        return 1
    worker_receipt = json.loads(receipt.read_text())
    if worker_receipt.get("sha256") != digest(output):
        print("RED_OUTPUT_DIGEST_MISMATCH", file=sys.stderr)
        return 1
    report["status"] = "REVIEW_CANDIDATE"
    report["outputSha256"] = digest(output)
    report["workerReceipt"] = str(receipt)
    report["crown"] = "REVIEW_PENDING"
    report_path = output.with_suffix(".orchestration.json")
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0

def main():
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=("preflight", "render"))
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--input-root", type=Path, required=True)
    p.add_argument("--output-root", type=Path, required=True)
    p.add_argument("--approve-private-render", action="store_true")
    a = p.parse_args()
    sys.exit(run(a))

if __name__ == "__main__":
    main()
