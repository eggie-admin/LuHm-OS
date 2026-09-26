#!/usr/bin/env python3
import json
from pathlib import Path
p=Path("assets/community/catalog.json")
d=json.loads(p.read_text())
assert d["policy"]=="CURATED_CC0_FIRST_NO_BLIND_VENDOR_INGEST"
assert d["provenance_required"] is True
assert len(d["sources"])>=6
for s in d["sources"]:
    assert s["url"].startswith("https://github.com/")
bad=["CC-BY-NC","proprietary","unknown"]
licenses=" ".join(str(s["license"]) for s in d["sources"])
assert "unknown" not in licenses.lower()
print("COMMUNITY_ASSET_CATALOG=PASS")
print("SOURCES="+str(len(d["sources"])))
