#!/usr/bin/env python3
import hashlib,json,tempfile
from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location("vendorAudit","tools/vendorArtAudit.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
asset=Path("frontEnd/assets/v1/svg/cathedralSignal.svg")
digest=hashlib.sha256(asset.read_bytes()).hexdigest()
base={"assetId":"cathedralSignal","sourceClass":"firstParty","sourceName":"LuHm OS","licenseId":"GPL-3.0-project","licenseDisposition":"approvedForUse","sourceSha256":digest,"candidateSha256":digest,"destination":str(asset),"approvalState":"professorApproved","kind":"svg","runtimeUrl":""}
def run(obj,should_pass):
    with tempfile.NamedTemporaryFile("w",suffix=".json",delete=False) as f:
        json.dump(obj,f); name=f.name
    ok=True
    try: m.audit(name)
    except SystemExit: ok=False
    Path(name).unlink()
    assert ok is should_pass
run(base,True)
for patch in [
    {"sourceClass":"protectedReference","approvalState":"runtimeImported"},
    {"runtimeUrl":"https://vendor.example/art.svg"},
    {"licenseDisposition":"unknown"},
    {"candidateSha256":"0"*64}
]:
    bad=dict(base); bad.update(patch); run(bad,False)
print("VENDOR ART NEGATIVE CONTROLS GREEN")
