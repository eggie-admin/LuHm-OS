#!/usr/bin/env python3
"""Read-only LuHm platform recipe: a portable capability manifest, NOT a BIOS.

Four target platforms × four evidence categories. Does not run apt, Gradle,
build kernels, flash firmware, inspect the OS, or create bootable images.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
POLICY=ROOT/"doctrine/finalThreeMachineMutationsV1.json"
QUARANTINE=ROOT/"doctrine/companyWideOperationalQuarantineV1.json"
TARGETS=("debian","ubuntu","androidGki","raspberryPi")
LAYERS=("bootOwnership","kernelSeparation","devicePermissions","packageAndLicense")
SHA=re.compile(r"[0-9a-f]{40}\Z")
PACKAGES=("python3","git","nodejs","ffmpeg","blender","godot","r-base-core","weston")
ARCH=("x86_64","aarch64","riscv64","ppc64le")
PACKAGE_MANAGERS={
    "debian":"apt-reviewed", "ubuntu":"apt-reviewed",
    "androidGki":"android-sdk-gradle-reviewed", "raspberryPi":"apt-reviewed",
}


def _read(path:Path)->dict[str,Any]:
    v=json.loads(path.read_text(encoding="utf8"))
    if not isinstance(v,dict):
        raise ValueError("RED_OS_POLICY_SHAPE")
    return v


def source_audit()->dict[str,Any]:
    p=_read(POLICY)
    m=next((x for x in p.get("mutations",[]) if x.get("id")=="portableOsRecipe"),{})
    platform=p.get("platform",{})
    issues=[]
    if p.get("schema")!="luhmOs.finalThreeMachineMutations.v1":
        issues.append("RED_OS_SCHEMA")
    if m.get("axes")!=list(TARGETS) or m.get("checks")!=list(LAYERS):
        issues.append("RED_OS_4X4")
    for key in ("noCustomKernelCompiled","noFirmwareFlash","noDistroIsoProduced",
                "noRealImageBooted","noOfficialDebianUbuntuFlavorClaim",
                "sourceGPL3Unchanged","licenseByPackage","avoidRootAccess",
                "androidUsesGkiAndVendorModuleSeparation"):
        if platform.get(key) is not True:
            issues.append("RED_OS_AUTHORITY")
            break
    if platform.get("commonInterface")!="CAPABILITY_MANIFEST_NOT_UNIVERSAL_BIOS":
        issues.append("RED_OS_FALSE_UNIVERSAL_BIOS")
    if p.get("crown")!="STOP":
        issues.append("RED_OS_CROWN")
    q=_read(QUARANTINE)
    if q.get("state")!="QUARANTINED" or q.get("activeTaskWorkersAllowed") is not False:
        issues.append("RED_OS_QUARANTINE")
    return {
      "schema":"luhmOs.portableOsRecipeAudit.v1",
      "state":"SOURCE_ONLY" if not issues else "RED_SOURCE_DRIFT",
      "issues":issues,"platforms":len(TARGETS),"layers":len(LAYERS),
      "matrixCells":16,"kernelCompiled":False,"biosFlashed":False,
      "androidBootloaderTouched":False,"debianImageProduced":False,
      "ubuntuOfficialFlavor":False,"greenAuthority":False,
    }


def plan(*,target:str,architecture:str,source_ref:str,
         requested_packages:Any)->dict[str,Any]:
    if type(target) is not str or target not in TARGETS:
        raise ValueError("RED_OS_TARGET")
    if type(architecture) is not str or architecture not in ARCH:
        raise ValueError("RED_OS_ARCH")
    if type(source_ref) is not str or SHA.fullmatch(source_ref) is None:
        raise ValueError("RED_OS_EXACT_SOURCE")
    if (type(requested_packages) not in (list,tuple)
        or len(requested_packages)>8
        or any(type(k) is not str or k not in PACKAGES for k in requested_packages)
        or len(set(requested_packages))!=len(requested_packages)):
        raise ValueError("RED_OS_PACKAGES")
    if target=="androidGki" and requested_packages:
        raise ValueError("RED_OS_ANDROID_APT_MISROUTING")
    if target=="raspberryPi" and architecture!="aarch64":
        raise ValueError("RED_OS_RPI_ARCH_PROOF")
    if target=="androidGki" and architecture!="aarch64":
        raise ValueError("RED_OS_ANDROID_TARGET_ARCH")
    source=source_audit()
    if source["issues"]:
        return {"state":"STOP_SOURCE_DRIFT","issues":source["issues"]}
    cells=[
        {"layer":layer,"status":"HOLD_REAL_MACHINE_EVIDENCE",
         "hardwareObserved":False,"rightsApproved":False}
        for layer in LAYERS]
    return {
       "schema":"luhmOs.portableOsRecipePlan.v1",
       "target":target,"architecture":architecture,"sourceRef":source_ref,
       "packageManagerReference":PACKAGE_MANAGERS[target],
       "packages":sorted(requested_packages),
       "fourEvidenceCells":cells,
       "sourceOnly":True,"commonCapabilityApi":"hardware-and-boot-evidence",
       "sourceLicense":"GPL-3.0_REPO_WITH_COMPONENT_REVIEW",
       "firmwareOwnership":"OEM_OR_PLATFORM_PROVENANCE_REQUIRED",
       "actualKernelConfigured":False,
       "bootImageBuilt":False,"vendorDriversReplaced":False,
       "packageInstallationPerformed":False,"rootRequired":False,
       "releaseOrDistributionAuthorized":False,
       "status":"HOLD_SOURCE_PACKAGE_LICENSE_AND_REAL_DEVICE_BOOT_PROOF",
    }


if __name__=="__main__":
    print(json.dumps(plan(target="debian",architecture="x86_64",
        source_ref="0"*40,requested_packages=["python3","git"]),indent=2))
