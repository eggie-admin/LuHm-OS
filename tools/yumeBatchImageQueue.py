#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "doctrine" / "yumeBatchImageWorkflowV1.json"

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = ROOT / manifest_path

    workflow = load(WORKFLOW)
    manifest = load(manifest_path)

    errors = []
    source_ref = str(manifest.get("sourceRef", "")).strip()
    if not source_ref or source_ref == "REQUIRED_EXACT_SOURCE_REF":
        errors.append("missing exact sourceRef")
    if manifest.get("publicAllowed") is not False:
        errors.append("generated draft batches must keep publicAllowed=false")
    if manifest.get("privacyClass") != "privateDraft":
        errors.append("privacyClass must be privateDraft")

    jobs = manifest.get("jobs", [])
    if not isinstance(jobs, list) or not jobs:
        errors.append("jobs must be a non-empty list")
        jobs = []

    required = set(workflow.get("jobCardRequiredFields", []))
    expanded = []
    seen = set()
    for index, job in enumerate(jobs, 1):
        if not isinstance(job, dict):
            errors.append(f"job {index} is not an object")
            continue
        job_id = str(job.get("jobId", "")).strip()
        if not job_id:
            errors.append(f"job {index} missing jobId")
            continue
        if job_id in seen:
            errors.append(f"duplicate jobId: {job_id}")
        seen.add(job_id)

        card = dict(job)
        card["batchId"] = manifest.get("batchId")
        card["sourceRef"] = source_ref
        card["sourceTruthRef"] = manifest.get("sourceTruthRef", "doctrine/currentSourceTruthV3.json")
        card.setdefault("negativeConstraints", [])
        card.setdefault("canonRefs", [])
        card.setdefault("reviewState", "queued")
        card.setdefault("privacyClass", "privateDraft")
        card.setdefault("publicAllowed", False)
        card.setdefault("providerPreference", (manifest.get("providerPreference") or ["openAiImage"])[0])
        card.setdefault("dimensions", manifest.get("output", {"width":1024,"height":1024}))
        card.setdefault("transparentBackground", manifest.get("output", {}).get("transparentBackground", False))

        missing = sorted(required - set(card))
        if missing:
            errors.append(f"{job_id}: missing fields {missing}")
        if card.get("publicAllowed") is not False:
            errors.append(f"{job_id}: publicAllowed must be false")
        if card.get("privacyClass") != "privateDraft":
            errors.append(f"{job_id}: privacyClass must be privateDraft")
        expanded.append(card)

    if errors:
        print(json.dumps({"status":"RED","errors":errors}, indent=2))
        return 1

    canonical = json.dumps(expanded, sort_keys=True, separators=(",", ":")).encode()
    queue_digest = hashlib.sha256(canonical).hexdigest()
    result = {
        "schema":"luhmOs.yumeBatchQueue.v1",
        "status":"READY_FOR_PROVIDER_DISPATCH",
        "batchId":manifest.get("batchId"),
        "sourceRef":source_ref,
        "jobCount":len(expanded),
        "maxConcurrentGenerationJobs":workflow["batchLaw"]["maxConcurrentGenerationJobs"],
        "queueSha256":queue_digest,
        "jobs":expanded,
        "driveHandoff":manifest.get("driveHandoff", {}),
        "publicationAuthority":False,
        "crownStatus":"STOP"
    }

    payload = json.dumps(result, indent=2) + "\n"
    if args.out:
        out = Path(args.out)
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
