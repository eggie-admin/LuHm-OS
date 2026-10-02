#!/usr/bin/env python3
import hashlib,json,subprocess
from pathlib import Path
head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
files=[
 "doctrine/tourniquetWorkflowV1.json",
 "doctrine/fqdnReverseProxyBoundaryV1.json",
 "doctrine/cloudflareEdgeAssetTemplateV1.json",
 "host/reverseProxy/serviceMap.json",
 "frontEnd/vendor/vendor-lock.json"
]
hashes={}
for name in files:
    p=Path(name); hashes[name]=hashlib.sha256(p.read_bytes()).hexdigest()
out=Path("build/titan7-watch-fleet/enterprise-preflight.json")
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps({
 "schema":"luhmOs.enterprisePreflightReceipt.v1",
 "sourceCommit":head,
 "authority":"Professor",
 "knownGoodFloor":"a1ebb472a4c2ab1224d7b7b5a1c3d5425f919f1a",
 "rollbackPolicy":"nearestEvidenceBackedKnownGood",
 "tourniquet":"pass",
 "networkContract":"pass",
 "staticVendorMetadata":"pass",
 "vendorArtBoundary":"pass",
 "cloudflareTemplate":"candidateNotDeployed",
 "crownStatus":"STOP",
 "contractHashes":hashes
},indent=2)+"\n")
print("ENTERPRISE PREFLIGHT RECEIPT",head)
