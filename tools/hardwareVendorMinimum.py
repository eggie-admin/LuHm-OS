#!/usr/bin/env python3
"""Minimal vendor/package source classifier; never probes or mutates a live device."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine/hardwareVendorMinimumV1.json"
ROWS=("legacyPc","modernPc","samsungArm","hostedDev")
COLS=("topology","boot","driver","packages")
PACKAGE=re.compile("[a-z0-9][a-z0-9+.-]*" + chr(92) + "Z")

class ProfileError(ValueError):
    pass

def _relpath(root: Path, value: object) -> bool:
    if type(value) is not str or not value or chr(92) in value or ".." in Path(value).parts or Path(value).is_absolute():
        return False
    p=root / value
    return p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(root.resolve())

def parse_declared_apt(dockerfile: str) -> list[str]:
    tag="apt-get install -y --no-install-recommends"
    if type(dockerfile) is not str or dockerfile.count(tag)!=1:
        raise ProfileError("APT_DECLARATION_NOT_UNIQUE")
    segment=dockerfile.split(tag,1)[1].split(";",1)[0]
    parts=segment.replace(chr(92)," ").split()
    if not parts or len(parts)>100 or any(PACKAGE.fullmatch(x) is None for x in parts):
        raise ProfileError("APT_DECLARATION_UNSAFE")
    if len(set(parts)) != len(parts):
        raise ProfileError("APT_DECLARATION_DUPLICATE")
    return parts

def package_projection(contract: dict, profile: str, root: Path = ROOT) -> dict:
    deb=contract["debian"]
    profiles=deb["profiles"]
    if type(profile) is not str or profile not in profiles:
        raise ProfileError("UNKNOWN_PROFILE")
    declared=parse_declared_apt((root / deb["declaredSource"]).read_text(encoding="utf-8"))
    selected=profiles[profile]["packages"]
    if type(selected) is not list or any(type(x) is not str for x in selected) or len(selected)!=len(set(selected)):
        raise ProfileError("PROFILE_DUPLICATE_OR_MALFORMED")
    if not set(selected).issubset(set(declared)):
        raise ProfileError("PROFILE_PACKAGE_NOT_DECLARED")
    if profile=="samsungCockpit" and selected:
        raise ProfileError("SAMSUNG_APT_FORBIDDEN")
    return {"profile":profile,"declaredCount":len(declared),
      "selectedCount":len(selected),"selectedPackages":list(selected),
      "excludedCount":len(declared)-len(selected),"installCommand":None,
      "declaredNotInstalled":True,"actualDeviceVerified":False,
      "packageMutationPerformed":False,"crownStatus":"STOP"}

def validate(contract: dict, root: Path = ROOT) -> dict:
    if type(contract) is not dict or contract.get("schema")!="luhmOs.hardwareVendorMinimum.v1":
        raise ProfileError("SCHEMA")
    if contract.get("status")!="AMBER_SOURCE_CANDIDATE" or contract.get("crownStatus")!="STOP":
        raise ProfileError("PREMATURE_PROMOTION")
    if contract.get("sourceLaw")!="AI proposes. Policy authorizes. CI proves. Human promotes.":
        raise ProfileError("LAW")
    if contract.get("matrixNamespace")!="hardwareVendorFourByFourV1" or contract.get("claimPhysicalChipset") is not False:
        raise ProfileError("NO_HARDWARE_PROOF")
    rows=contract.get("rows",[])
    if [r.get("id") for r in rows] != list(ROWS) or contract.get("columns")!=list(COLS):
        raise ProfileError("MATRIX_AXES")
    for r in rows:
        if not _relpath(root,r.get("source")):
            raise ProfileError("MATRIX_SOURCE")
    for i,cell in enumerate(contract.get("matrix",[])):
        if (cell.get("address")!=f"0x{i:02X}" or cell.get("row")!=ROWS[i//4]
            or cell.get("dimension")!=COLS[i%4] or cell.get("source")!=rows[i//4]["source"]
            or cell.get("evidence")!="SOURCE_MODEL_ONLY"):
            raise ProfileError("CELL_MISMATCH")
    if len(contract.get("matrix",[]))!=16 or contract.get("sourceOnlyCellCount")!=16:
        raise ProfileError("NOT_4_BY_4")
    deb=contract.get("debian",{})
    if not _relpath(root,deb.get("declaredSource")) or not _relpath(root,deb.get("sourceAuthority")):
        raise ProfileError("DEBIAN_POINTER")
    if (deb.get("proof")!="DECLARATION_ONLY_NO_DPKG_RUNTIME_PROOF" or
        deb.get("packageInstallAuthorized") is not False or
        deb.get("actualPackageRemoval") is not False or
        deb.get("hostKernelControlled") is not False):
        raise ProfileError("DEBIAN_AUTHORITY")
    groups=deb.get("packageGroups",{})
    if set(groups)!= {"foundation","build","python","studio","optionalServices"}:
        raise ProfileError("PACKAGE_CLASSES")
    inventories=[x for values in groups.values() for x in values]
    if any(type(x) is not str or PACKAGE.fullmatch(x) is None for x in inventories) or len(inventories)!=len(set(inventories)):
        raise ProfileError("PACKAGE_CLASS_DUPLICATE")
    declared=parse_declared_apt((root/deb["declaredSource"]).read_text(encoding="utf-8"))
    if len(declared)!=34 or deb.get("declaredPackageCount")!=34 or set(declared)!=set(inventories):
        raise ProfileError("APT_SOURCE_DRIFT")
    profiles=deb.get("profiles",{})
    if set(profiles)!={"samsungCockpit","linuxHeadless","linuxWebBuild","linuxStudio","existingCodespace"}:
        raise ProfileError("PROFILE_SET")
    selected={}
    for profile,model in profiles.items():
        if model.get("approval")!="SOURCE_REVIEW_ONLY" and profile!="samsungCockpit":
            raise ProfileError("APPROVAL_DRIFT")
        if profile=="samsungCockpit" and model.get("approval")!="APP_AND_PERMISSIONS_ONLY":
            raise ProfileError("ANDROID_APPROVAL_DRIFT")
        selected[profile]=package_projection(contract,profile,root)
    if selected["linuxHeadless"]["selectedPackages"] != ["ca-certificates","git","python3","python3-venv"]:
        raise ProfileError("HEADLESS_NOT_MINIMAL")
    if not set(selected["linuxHeadless"]["selectedPackages"]).issubset(selected["linuxWebBuild"]["selectedPackages"]):
        raise ProfileError("BUILD_DID_NOT_INHERIT")
    if not set(selected["linuxWebBuild"]["selectedPackages"]).issubset(selected["linuxStudio"]["selectedPackages"]):
        raise ProfileError("STUDIO_DID_NOT_INHERIT")
    if set(selected["linuxStudio"]["selectedPackages"]) & set(groups["optionalServices"]):
        raise ProfileError("STUDIO_UNNEEDED_SERVERS")
    if set(selected["existingCodespace"]["selectedPackages"])!=set(declared):
        raise ProfileError("CODESPACE_DECLARED_MISMATCH")
    if selected["samsungCockpit"]["selectedCount"]!=0:
        raise ProfileError("ANDROID_APT")
    for ref in contract.get("links",{}).values():
        if not _relpath(root,ref):
            raise ProfileError("REFERENCE_MISSING")
    vendor=contract.get("vendorBoundaries",{})
    required_true=("fossPreferred","androidOemFirmwareNotFossClaim","linuxKernelHasGPLLicense",
       "blenderHasGPLLicense","officialVendorFirmwareOnlyForOwnerDevice","ubuntuUserlandIsNotSamsungFirmware",
       "doNotInstallExtraStackForConvenience","registryDownloadRequiresReview")
    if any(vendor.get(key) is not True for key in required_true):
        raise ProfileError("LICENSING_OR_VENDOR_SAFETY")
    safety=contract.get("safety",{})
    if safety.get("readOnly") is not True or safety.get("androidBootloaderPreserved") is not True:
        raise ProfileError("PROTECTED_BOOT")
    if any(safety.get(key) is not False for key in (
        "uefiOrBiosWrites","firmwareFlashing","kernelModuleLoads","driverBindingChanges",
        "driverAssumptions","serviceStarts","networkListenerStarts","packageInstalls",
        "repositoryMerge","agentStarts","releaseSigning","paidApiCalls")):
        raise ProfileError("UNAUTHORIZED_OPERATION")
    quarantine=json.loads((root / contract["links"]["agentQuarantine"]).read_text(encoding="utf-8"))
    if quarantine.get("state")!="QUARANTINED" or quarantine.get("activeTaskWorkersAllowed") is not False:
        raise ProfileError("QUARANTINE_VIOLATED")
    return {"schema":"luhmOs.hardwareVendorMinimumReceipt.v1","status":"AMBER_SOURCE_ONLY",
       "matrixCells":16,"hostProfiles":len(rows),"declaredAptPackages":len(declared),
       "selectedByProfile":{key:value["selectedCount"] for key,value in selected.items()},
       "sourceOnly":True,"actualPackageInstall":False,"firmwareWritten":False,
       "kernelModified":False,"physicalDeviceVerified":False,"crownStatus":"STOP",
       "contractSha256":hashlib.sha256(json.dumps(contract,sort_keys=True,separators=(",",":")).encode()).hexdigest()}

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile",default="linuxHeadless",
                        choices=["samsungCockpit","linuxHeadless","linuxWebBuild","linuxStudio","existingCodespace"])
    args=parser.parse_args()
    contract=json.loads(CONTRACT.read_text(encoding="utf-8"))
    receipt=validate(contract)
    receipt["selection"]=package_projection(contract,args.profile)
    print(json.dumps(receipt,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
