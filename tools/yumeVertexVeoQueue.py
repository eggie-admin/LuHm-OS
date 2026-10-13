#!/usr/bin/env python3
"""Bounded, no-secrets-in-source Vertex AI Veo candidate queue for Pirate Daddies Film.

DRY-RUN ONLY by default. A Cloud request can incur charges, so submission requires
explicit flags, environmental Crown receipt, confirmed billing, and a cost ceiling.
Uses the Google Cloud developer/API route, NEVER consumer Gemini or a proxy service.
"""
import argparse
import json
import sys
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
    raise PermissionError('CROWN_STOP_LEGACY_SUBMIT_DISABLED_USE_SQL_VIDEO_WORKER')


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Veo shot dry-run and gated single-shot submit")
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--shot", choices=["lum", "urd", "belldandy", "skuld"], default="lum")
    p.add_argument("--submit", action="store_true")
    p.add_argument("--approve-spend", action="store_true")
    p.add_argument("--cost-ceiling-usd", type=float, default=0.0)
    p.add_argument("--output", type=Path)
    args = p.parse_args(argv)
    if args.submit:
        raise SystemExit('CROWN_STOP_LEGACY_SUBMIT_DISABLED_USE_SQL_VIDEO_WORKER')
    manifest = load_manifest(args.manifest)
    shot = next(x for x in manifest["shots"] if x["id"] == args.shot)
    storage_uri = ""
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



if __name__ == "__main__":
    sys.exit(main())

