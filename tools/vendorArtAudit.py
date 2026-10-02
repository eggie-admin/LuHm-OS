#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
policy=json.loads(Path("doctrine/vendorArtIngestV1.json").read_text())
required=set(policy["receiptRequired"])
allowed=set(sum(policy["allowedKinds"].values(),[]))
def fail(code): raise SystemExit(code)
def audit(receipt_path):
    r=json.loads(Path(receipt_path).read_text())
    if not required.issubset(r): fail("RED_VENDOR_RECEIPT_FIELDS")
    if r.get("kind") not in allowed: fail("RED_VENDOR_KIND")
    if r["sourceClass"]=="protectedReference" and r["approvalState"]=="runtimeImported": fail("RED_PROTECTED_REFERENCE_SHIP")
    if r["licenseDisposition"]!="approvedForUse": fail("RED_VENDOR_LICENSE")
    if r["approvalState"] not in ("professorApproved","runtimeImported"): fail("RED_VENDOR_APPROVAL")
    candidate=Path(r["destination"])
    if not candidate.is_file(): fail("RED_VENDOR_DESTINATION")
    digest=hashlib.sha256(candidate.read_bytes()).hexdigest()
    if digest!=r["candidateSha256"]: fail("RED_VENDOR_HASH")
    if r.get("runtimeUrl","").startswith(("http://","https://")): fail("RED_VENDOR_HOTLINK")
    return r
if __name__=="__main__":
    if len(sys.argv)<2: fail("usage: vendorArtAudit.py RECEIPT...")
    for item in sys.argv[1:]: audit(item)
    print("VENDOR ART AUDIT GREEN",len(sys.argv)-1)
