#!/usr/bin/env python3
"""Conservative OS/browser vendor licensing census. Audit, never relicense."""
import json
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]

def check(root=ROOT):
    cfg=json.loads((root/"doctrine/vendorApacheReadinessV1.json").read_text())
    errors=[]
    def need(ok,name):
        if not ok:errors.append(name)
    root_license=(root/"LICENSE").read_text(encoding="utf-8")
    need("GNU GENERAL PUBLIC LICENSE" in root_license and "Version 3" in root_license[:160],
         "ROOT_GPL_TEXT_MUST_BE_PRESERVED")
    need(cfg.get("repositoryLicense")=="GPL-3.0-only" and cfg.get("licenseChangeAllowed") is False,
         "NO_BLANKET_APACHE_RELICENSE")
    need(cfg.get("thirdPartySourceRelicensingAllowed") is False,"NO_THIRD_PARTY_RELICENSE")
    for relative in cfg.get("existingDeclarations",[]):
        p=root/relative
        try:
            declared=json.loads(p.read_text())["license"]
            need(declared=="GPL-3.0-only","GPL_DECLARATION_NOT_PROVEN:"+relative)
        except (OSError,ValueError,KeyError):
            errors.append("MISSING_DECLARED_LICENSE:"+relative)
    rows=cfg.get("vendorRows",[])
    ids=[v.get("id") for v in rows]
    need(len(rows)>=20 and len(set(ids))==len(ids),"VENDOR_CENSUS_INCOMPLETE")
    for v in rows:
        need(v.get("exactVersionInstalled")=="UNVERIFIED" and v.get("bundledByThisMutation") is False,
             "NO_FALSE_RUNTIME_OR_BUNDLING:"+str(v.get("id")))
        need(v.get("licenseClass") not in (None,"Apache-2.0","APACHE_ONLY"),
             "NO_ASSUMED_APACHE_ONLY:"+str(v.get("id")))
    license_classes=Counter(v["licenseClass"] for v in rows)
    android=next((v for v in rows if v["id"]=="aosp"),{})
    linux=next((v for v in rows if v["id"]=="raspberryPiOs"),{})
    need("GPL" in android.get("licenseClass","") and "DEBIAN" in linux.get("licenseClass",""),
         "MIXED_OS_LICENSES_MUST_BE_VISIBLE")
    lock=json.loads((root/"frontEnd/prototypes/glassWorld/package-lock.json").read_text())
    items=list(lock.get("packages",{}).items())
    third_party=[(path,data) for path,data in items if path]
    unknown=[path for path,data in third_party if not isinstance(data.get("license"),str)]
    need(lock.get("lockfileVersion")==3,"NPM_LOCK_V3")
    need(len(third_party)>=40,"TRANSITIVE_DEPENDENCIES_MUST_BE_COUNTED")
    need(cfg.get("zipContract",{}).get("compression")=="ZIP_DEFLATED","JAVA_ZIP_COMPAT")
    need(cfg.get("zipContract",{}).get("maxEntries")==96,"BOUNDED_ZIP_COUNT")
    need(cfg.get("crownStatus")=="STOP" and cfg["distributionPolicy"]["publicShip"] is False,"CROWN_HOLD")
    return {"schema":"luhmOs.vendorApacheAudit.v1","vendorCount":len(rows),
        "licenseClasses":dict(sorted(license_classes.items())),
        "npmTransitivePackages":len(third_party),
        "npmMissingLicenseMetadata":unknown,
        "errors":sorted(errors),"verdict":"AMBER_APACHE_MIGRATION_PENDING" if not errors else "RED",
        "rootGPLPreserved":True,"apacheRelicensingDone":False,
        "proprietaryBrowserBundled":False,"remoteDeviceTested":False,"crownStatus":"STOP"}

if __name__=="__main__":
    result=check()
    print(json.dumps(result,indent=2))
    if result["errors"]:raise SystemExit(1)
