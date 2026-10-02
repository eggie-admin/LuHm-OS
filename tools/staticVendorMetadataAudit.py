#!/usr/bin/env python3
import json
from pathlib import Path
catalog=json.loads(Path("doctrine/staticVendorCatalogV1.json").read_text())
lock=json.loads(Path("frontEnd/vendor/vendor-lock.json").read_text())
assert catalog["status"]=="candidateMetadataOnly"
law=catalog["fetchLaw"]
assert law["liveVendorRuntimeUrl"] is False
assert law["unpinnedFetch"] is False
assert law["hashVerificationRequired"] is True
assert law["cloudflareServesAuditedMirrorOnly"] is True
allowed={v["id"]:v for v in catalog["vendors"]}
for a in lock["artifacts"]:
    assert a["vendorId"] in allowed
    v=allowed[a["vendorId"]]
    if not v["mirrorEligible"]:
        assert a["approvalState"]=="metadataOnly"
        assert a["cdnPath"]==""
        continue
    if a["approvalState"]=="approvedMirror":
        assert a["version"] and a["sourceUrl"] and len(a["sourceSha256"])==64
        assert a["localPath"].startswith("frontEnd/vendor/")
        assert a["cdnPath"].startswith("assets/")
    else:
        assert a["approvalState"]=="unresolved"
print("STATIC VENDOR METADATA GREEN")
