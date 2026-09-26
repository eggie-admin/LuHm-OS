#!/usr/bin/env python3
import json
from pathlib import Path

catalog = json.loads(Path("assets/community/catalog.json").read_text())
selection = json.loads(Path("assets/community/selected-assets.json").read_text())

assert catalog["policy"] == "CURATED_CC0_FIRST_NO_BLIND_VENDOR_INGEST"
assert catalog["provenance_required"] is True
assert len(catalog["sources"]) >= 6
for source in catalog["sources"]:
    assert source["url"].startswith("https://github.com/")
licenses = " ".join(str(s["license"]) for s in catalog["sources"])
assert "unknown" not in licenses.lower()

source = selection["source"]
assert source["repository"] == "shorepine/kenney"
assert source["license"] == "CC0"
assert source["runtime_network"] is False
assert source["build_time_fetch_only"] is True
assert len(source["commit"]) == 40

assets = []
for kit, names in selection["groups"].items():
    assert kit in {"city-industrial", "factory", "furniture"}
    for name in names:
        assert name.endswith(".glb")
        assert "/" not in name and "\\" not in name
        assets.append(f"{kit}/{name}")
assert len(assets) == len(set(assets))
assert 60 <= len(assets) <= int(selection["budget"]["max_assets"])
assert int(selection["budget"]["max_total_bytes"]) <= 8 * 1024 * 1024

required_files = [
    "tools/stageCommunityAssets.py",
    "scripts/game/communitySetDress.gd",
    "tests/communityAssetSmoke.gd",
]
for path in required_files:
    assert Path(path).is_file(), path

stager = Path("tools/stageCommunityAssets.py").read_text()
assert "raw.githubusercontent.com" in stager
assert "runtime_network" in stager
assert "PROVENANCE.json" in stager
assert "http://" not in stager

setdress = Path("scripts/game/communitySetDress.gd").read_text()
assert "ResourceLoader.exists" in setdress
assert "http://" not in setdress and "https://" not in setdress

print("COMMUNITY_ASSET_CATALOG=PASS")
print("CURATED_ASSET_COUNT=" + str(len(assets)))
print("IMMUTABLE_SOURCE_COMMIT=" + source["commit"])
