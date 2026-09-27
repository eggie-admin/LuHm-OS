#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "assets/registry/BETA_ASSET_SOURCES_V1.json"
DOCTRINE = ROOT / "doctrine/GODOT4_BETA_ENGINE_HARDENING_V1.json"
OUT = ROOT / "build/beta-engine/asset-registry-audit.json"

def die(msg: str) -> None:
    raise SystemExit(f"BETA_ASSET_AUDIT_RED: {msg}")

registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
doctrine = json.loads(DOCTRINE.read_text(encoding="utf-8"))
if registry.get("schema") != "luhm-os.beta-asset-sources.v1": die("wrong registry schema")
if registry.get("runtimeNetwork") is not False: die("runtime network must stay disabled")
if doctrine.get("status") != "BETA_LANE_STAGED": die("beta doctrine not staged")
sources = registry.get("sources")
if not isinstance(sources, list) or len(sources) < 6: die("asset source registry incomplete")
keys = {s.get("key") for s in sources if isinstance(s, dict)}
required = {"repo-community-cc0","drive-original-vault","drive-community-open-license","drive-third-party-private-reference","chatgpt-library-asset-dungeon","meshy-lum-runtime-donor"}
missing = sorted(required - keys)
if missing: die(f"missing source lanes: {missing}")
for source in sources:
    if not isinstance(source, dict): die("non-object source")
    rights = source.get("rights")
    package = source.get("package")
    if rights == "PRIVATE_REFERENCE" and package is not False: die(f"private reference marked packageable: {source.get('key')}")
    if rights == "UNKNOWN" and package not in (False, "QUARANTINE"): die(f"unknown rights escaped quarantine: {source.get('key')}")
public_text = REGISTRY.read_text(encoding="utf-8")
if "drive.google.com/" in public_text or re.search(r"\b1[A-Za-z0-9_-]{20,}\b", public_text): die("private Drive locator leaked into public registry")
if re.search(r"\bfile_[0-9a-f]{20,}\b", public_text): die("ChatGPT Library locator leaked into public registry")
community = next(s for s in sources if s.get("key") == "repo-community-cc0")
if int(community.get("expectedAssetCount", 0)) != 77: die("community asset count contract drift")
library = next(s for s in sources if s.get("key") == "chatgpt-library-asset-dungeon")
if int(library.get("indexedAssetCount", 0)) != 28: die("ChatGPT Library asset index count drift")
result = {"status":"GREEN","schema":registry["schema"],"source_count":len(sources),"community_expected":77,"library_indexed":28,"runtime_network":False,"private_reference_packaging":False}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print("BETA_ASSET_AUDIT=GREEN", json.dumps(result, sort_keys=True))
