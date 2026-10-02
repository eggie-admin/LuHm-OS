#!/usr/bin/env python3
import base64,hashlib,json,shutil
from pathlib import Path
root=Path("frontEnd")
src=json.loads((root/"assets/v1/manifest.json").read_text())
out=root/"distAssets"
if out.exists(): shutil.rmtree(out)
records=[]
for item in src["assets"]:
    source=root/item["path"]
    data=source.read_bytes()
    digest=hashlib.sha256(data).hexdigest()
    target=out/"assets"/src["version"]/digest/source.name
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(data)
    records.append({**item,"sha256":digest,"integrity":"sha256-"+base64.b64encode(hashlib.sha256(data).digest()).decode("ascii"),"cacheControl":"public,max-age=31536000,immutable","cdnPath":str(target.relative_to(out))})
(out/"asset-manifest.json").write_text(json.dumps({"schema":"luhmOs.cdnAssetManifest.v1","version":src["version"],"assets":records},indent=2)+"\n")
print("STATIC ASSET DIST GREEN",len(records))
