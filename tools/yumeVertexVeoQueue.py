#!/usr/bin/env python3
"""Bounded, no-secrets-in-source Vertex AI Veo candidate queue for Pirate Daddies Film.

DRY-RUN ONLY by default. A Cloud request can incur charges, so submission requires
explicit flags, environmental Crown receipt, confirmed billing, and a cost ceiling.
Uses the Google Cloud developer/API route, NEVER consumer Gemini or a proxy service.
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

veoModel = "veo-3.1-fast-generate-001"
googleRegion = "us-central1"
maxCostPerSecondUsd = 0.15  # intentionally conservative upper safety cap, not a billing quote


def load_manifest(path: Path) -> dict:
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert doc["schema"] == "luhmOs.yumeCanonLockedVeoShots.v1"
    assert doc["state"] == "PRIVATE_MUTATION_CANDIDATE"
    assert doc["sourceRef"] and len(doc["sourceRef"]) == 40
    assert doc["rights"]["publicAllowed"] is False
    assert doc["gates"]["publication"] == "STOP"
    assert doc["model"] == veoModel
    assert doc["output"]["durationSeconds"] in (4, 6, 8)
    assert doc["output"]["sampleCount"] == 1
    assert doc["output"]["aspectRatio"] == "9:16"
    assert [x["id"] for x in doc["shots"]] == ["lum", "urd", "belldandy", "skuld"]
    for shot in doc["shots"]:
        assert "adult" in shot["age"]
        assert shot["identityRef"].endswith("Pending")
    return doc


def make_request(doc: dict, shot: dict, storage_uri: str = "") -> dict:
    consistent = doc["consistency"]
    prompt = " ".join([
        "A single six-second original cinematic animation candidate. One woman only, an adult original fictional character named " + shot["id"] + ".",
        consistent["visualLanguage"], shot["characterIdentity"],
        shot["action"], "Camera movement: " + shot["camera"] + ".",
        "Color script: " + shot["palette"] + ".",
        "Silhouette, clothing, face, and hairstyle consistent through every frame.",
        "Original cinematography, fine ink texture and handcrafted finish, physically believable motion.",
        "No text, no title graphics, no narration, no music, no logos. 9:16 vertical framing."
    ])
    params = {
        "aspectRatio": doc["output"]["aspectRatio"],
        "resolution": doc["output"]["resolution"],
        "durationSeconds": doc["output"]["durationSeconds"],
        "sampleCount": 1,
        "personGeneration": "allow_adult",
        "generateAudio": False,
        "negativePrompt": ", ".join(consistent["forbidden"])
    }
    if storage_uri:
        if not storage_uri.startswith("gs://"):
            raise ValueError("output must be a gs:// bucket prefix")
        params["storageUri"] = storage_uri.rstrip("/") + "/" + shot["id"] + "/"
    return {"instances": [{"prompt": prompt}], "parameters": params}


def submit_one(project: str, shot_id: str, request: dict) -> str:
    # Never print access tokens, even during errors.
    raw = subprocess.run(["gcloud", "auth", "print-access-token"], capture_output=True, text=True, check=True)
    token = raw.stdout.strip()
    if not token:
        raise RuntimeError("Google ADC/gcloud login unavailable")
    url = f"https://{googleRegion}-aiplatform.googleapis.com/v1/projects/{project}/locations/{googleRegion}/publishers/google/models/{veoModel}:predictLongRunning"
    req = urllib.request.Request(url, data=json.dumps(request).encode("utf-8"), method="POST", headers={
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json; charset=utf-8"
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as f:
            response = json.load(f)
    except urllib.error.HTTPError as error:
        # Body could contain sensitive provider detail; return only status.
        raise RuntimeError(f"Cloud returned HTTP {error.code}; check billing, service, IAM, quota") from None
    return response["name"]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Veo shot dry-run and gated single-shot submit")
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--shot", choices=["lum", "urd", "belldandy", "skuld"], default="lum")
    p.add_argument("--submit", action="store_true")
    p.add_argument("--approve-spend", action="store_true")
    p.add_argument("--cost-ceiling-usd", type=float, default=0.0)
    p.add_argument("--output", type=Path)
    args = p.parse_args(argv)
    manifest = load_manifest(args.manifest)
    shot = next(x for x in manifest["shots"] if x["id"] == args.shot)
    storage_uri = os.getenv("LUHM_VERTEX_GCS_OUTPUT", "") if args.submit else ""
    request = make_request(manifest, shot, storage_uri)
    if not args.submit:
        result = {"status": "DRY_RUN_NO_NETWORK_NO_CHARGE", "sourceRef": manifest["sourceRef"],
                  "provider": "vertexAi", "shot": args.shot, "model": veoModel, "request": request}
        content = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content, encoding="utf-8")
        else:
            print(content)
        return 0
    estimated_ceiling = maxCostPerSecondUsd * manifest["output"]["durationSeconds"]
    if not args.approve_spend or args.cost_ceiling_usd < estimated_ceiling:
        raise SystemExit(f"CROWN_STOP: one shot requires --approve-spend and --cost-ceiling-usd >= {estimated_ceiling:.2f}")
    if os.getenv("LUHM_CROWN_VIDEO_COST_APPROVED") != "yes":
        raise SystemExit("CROWN_STOP: LUHM_CROWN_VIDEO_COST_APPROVED=yes required")
    if os.getenv("LUHM_GOOGLE_BILLING_CURRENT_CONFIRMED") != "yes":
        raise SystemExit("CROWN_STOP: LUHM_GOOGLE_BILLING_CURRENT_CONFIRMED=yes required")
    project = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    if not project or not storage_uri:
        raise SystemExit("CROWN_STOP: GOOGLE_CLOUD_PROJECT and LUHM_VERTEX_GCS_OUTPUT required")
    operation = submit_one(project, args.shot, request)
    # Operation name is not a secret; do not automatically fetch/export completed video.
    print(json.dumps({"status": "SUBMITTED_NOT_COMPLETED", "shot": args.shot, "operation": operation, "project": project}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
