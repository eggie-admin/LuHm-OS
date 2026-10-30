#!/usr/bin/env python3
"""Read-only Samsung / Linux studio / GitHub 500-slot CAST readiness.
5 targets x 4 domains x 25 unique controls = 500. Source GREEN != hardware GREEN.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import platform
import re
import sqlite3
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
DOMAINS={
"firmwareAndBoot":"""exactDeviceId currentBuild currentSecurityPatch officialUpdateEligibility
 officialBetaEnrollmentVerified recoveryImageAvailable backupBeforeUpdate
 rollbackRestoreDrill knoxIntegrity bootloaderLocked stockSignedKernel
 verifiedBootStatus vendorPartitionIntegrity firmwareSignedDownload
 antiRollbackState firmwareVersionMatchesBoard vendorFirmwareProcedure
 UefiBootState SecureBootState tpmState grubMenuBackup
 efiBootEntries gpartedReadOnlySnapshot firmwarePowerSafety
 ownerFlashAuthorization""".split(),
"osAndDrivers":"""osRelease kernelRelease cpuArchitecture usbHostSupport
 usbControllerTopology usbBusBandwidth poweredHubBudget
 thermalLimits powerManagement audioClassEnumerated
 bluetoothControllerEnumerated pipewireRouteStatus
 v4l2UvcDevices cameraPermissionGrant videoLatency
 gdmDisplayManagerStatus waylandOrX11 netplanRenderer
 networkPrivateBind tlsConnectivity sandboxedAppData
 browserKioskCompatibility apkPermissionScope
 appDataBackup andRestoreProof""".split(),
"aiAndMedia":"""openvinoCpuPresence openvinoCpuBenchmark
 openvinoGpuDriverVerified npuHardwareProven
 localModelLicenseApproved remoteProviderBudget
 inferenceOutputSchema exactSourceModelPin
 aiTokensScoped noAutoAgentStart signedJobEnvelope
 studioBlenderAvailable blenderHeadlessSmoke
 sixCameraCaptureProof captureFrameTimestamps
 stereoLensCalibration charucoReprojectionError
 bodySkeletonTrackingRig motionExportGlb
 ffmpegCodecLicenseProof audioSyncLatency
 microphoneLoopbackPermission motionPipelinePrivacy
 videoCpuBudget renderThermalBudget""".split(),
"forgeAndRelease":"""sourceShaPresent sourceShaMatchesCheckout
 agentQuarantine sourceLicenseProven
 apkExportPresetVerified devZipVerified
 npmLockfileChecked dmgOwnerGate
 androidCastGate trueAndroidDebugBuild
 samsungApkInstalled physicalBenchmarkProof
 dataLaneRollbackProof ltsRebuildProof
 experimentalIsolationProof ownerSignatureGate
 sshProxyAuthentication noPublicSql
 dnsUnchanged githubActionsProven
 blenderStudioManifestJson SqliteJson1Bridge
 frontendSafeJs bridgeEventConsent
 crownStopObserved""".split()
}
TARGETS=("samsungS24FE","samsungTabS10Lite","samsungTabA8","linuxMintStudio","githubRunner")
TRACKS=("proposed","dataLane","lts","studioForge")

def load(root=ROOT):
    return json.loads((root/"doctrine/samsungCast500V1.json").read_text(encoding="utf8"))

def checks(policy,root=ROOT):
    p=policy
    failed=[]
    def ok(name,condition):
        if not condition:failed.append(name)
    ok("500_MATRIX",len(DOMAINS)==4 and all(len(v)==25 and len(set(v))==25 for v in DOMAINS.values()))
    ok("100_DISTINCT_DEFS",len({x for v in DOMAINS.values() for x in v})==100)
    ok("TARGETS",p.get("auditedDevices")==list(TARGETS))
    ok("DOMAINS",p.get("auditDomains")==list(DOMAINS))
    ok("SLOTS",p.get("assessmentSlots")==500 and p.get("controlsPerDomain")==25 and p.get("distinctControls")==100)
    ok("TRACKS",p.get("tracks")==list(TRACKS) and p.get("tracksAreAuthorityTiers") is False)
    ok("ESCALATION",p.get("canonicalTierLevels")==[0,1,2,3])
    ok("SAMSUNG_MODELS",all(x in str(p.get("samsung",{})) for x in ("SM-S721U1","SM-X400","SM-X200")))
    ok("DEX_LIMIT",p.get("samsung",{}).get("s10LiteDex")=="UNSUPPORTED_STANDALONE_WIRELESS_AND_HDMI")
    ok("NO_SAMSUNG_FLASH",all(p["samsung"].get(k) is False for k in ("flashFirmware","bootloaderUnlock","rootBypass")))
    ok("OFFICIAL_BETA_UNPROVEN",p["samsung"].get("officialBetaEligible")=="UNKNOWN_PER_DEVICE")
    ok("STOCK_KERNEL",p["samsung"].get("stockVendorKernel") is True)
    ok("CURRENT_MINT_NO_MIGRATION",p["studio"].get("host")=="Linux Mint 22.3 Zena; Intel i9-12900K")
    ok("NO_INVENTED_NPU",p["studio"].get("npuPresent") is False)
    ok("MOTHERBOARD_MODEL_UNKNOWN",p["studio"].get("motherboard")=="MODEL_NOT_VERIFIED_ASROCK_OR_ASUS")
    ok("NO_GPARTED_OR_GRUB_MUTATION",p["studio"].get("gparted")=="OPERATOR_ONLY" and p["studio"].get("grub")=="READ_ONLY_INSPECTION")
    ok("SIX_CAMERA_UNPROVEN",p["studio"].get("usbCameraTarget")==6 and p["studio"].get("usbCameraVerified")==0)
    ok("NO_CAPTURE",p["motionCapture"].get("rawImageCapture") is False and p["motionCapture"].get("streaming") is False)
    ok("BLENDER_LOCAL_NOT_VM_PROVEN",p["studio"].get("blender")=="LOCAL_HEADLESS_CANDIDATE")
    ok("NO_PROVIDER_AUTO_USE",p["ai"].get("activeWorkers")==0 and "opt-in" in p["ai"].get("cloud",""))
    ok("BASE44_NOT_CRYPTO",p["ai"].get("base44")=="NOT_ENCODING_AND_NOT_TRUST")
    ok("FOUR_PACKAGES",p["app"].get("packages")==["dev","npm","dmg","apk"])
    ok("WEBVIEW_NO_FLASH",p["app"].get("firmwareFromWebView") is False)
    ok("ALL_DESTRUCTIVE_BLOCKED",all(p["approval"].get(k) is False for k in
       ("grubWrite","gpartedWrite","firmwareFlash","customRom","knoxBypass",
        "automaticSamsungBetaEnroll","cloudProvision","paidCalls","enableAgents","mainMerge","signing")))
    ok("CROWN_STOP",p["approval"].get("crownStatus")=="STOP")
    profile=(root/p["profilesYaml"]).read_text(encoding="utf8")
    ok("YAML_FOUR_LANES",all("  "+k+":" in profile for k in TRACKS))
    ok("YAML_NO_FLASH",profile.count("firmware: DENY")==4 and profile.count("install: false")==4)
    ok("YAML_NO_RUN_SHELL","sudo " not in profile and "flashFirmware" not in profile)
    hardware=json.loads((root/"doctrine/k9000UniversalHardwareV1.json").read_text())
    ok("CANON_HARDWARE_PRESENT",len(hardware["inventory"])>=9 and all(x["verifiedRuntime"] is False for x in hardware["inventory"]))
    quarantine=json.loads((root/"doctrine/companyWideOperationalQuarantineV1.json").read_text())
    ok("QUARANTINE_UNCHANGED",quarantine.get("registeredCount")==15 and quarantine.get("activeTaskWorkersAllowed") is False)
    return sorted(set(failed))

def exact_ref(root=ROOT):
    p=subprocess.run(["git","rev-parse","HEAD"],cwd=root,capture_output=True,text=True)
    sha=p.stdout.strip()
    if p.returncode or not re.fullmatch(r"[a-f0-9]{40}",sha):
        raise ValueError("NO_EXACT_GITHUB_SHA")
    if os.getenv("LUHM_SOURCE_REF") and sha!=os.environ["LUHM_SOURCE_REF"]:
        raise ValueError("SOURCE_REF_MISMATCH")
    return sha

def runner_evidence():
    # These checks describe only the ephemeral CI runner, NEVER the Samsung devices.
    result={}
    result["osAndDrivers/osRelease"]=("PASS" if Path("/etc/os-release").is_file() else "UNVERIFIED","runner_os_release_exists")
    result["osAndDrivers/kernelRelease"]=("PASS" if platform.release() else "UNVERIFIED","runner_kernel_release")
    result["osAndDrivers/cpuArchitecture"]=("PASS" if platform.machine() else "UNVERIFIED","runner_platform_machine")
    result["forgeAndRelease/sourceShaPresent"]=("PASS","git_rev_parse_HEAD")
    try:
        with sqlite3.connect(":memory:") as db:
            db.execute("CREATE TABLE x (value TEXT) STRICT")
            db.execute("INSERT INTO x VALUES (?)",("test",))
            verified=db.execute("SELECT json_valid(?)",('{"ok":true}',)).fetchone()
        result["forgeAndRelease/SqliteJson1Bridge"]=("PASS" if verified==(1,) else "GAP","in_memory_sqlite_strict_json1")
    except sqlite3.Error:
        result["forgeAndRelease/SqliteJson1Bridge"]=("UNVERIFIED","runner_sqlite_unavailable")
    return result

def assess(policy,run_runner=False):
    obs=runner_evidence() if run_runner else {}
    rows=[]
    for target in TARGETS:
        for domain,control_names in DOMAINS.items():
            for name in control_names:
                value,proof=(obs.get(domain+"/"+name,("UNVERIFIED","runner_receipt_not_collected"))
                    if target=="githubRunner" else ("UNVERIFIED","physical_or_remote_device_not_connected"))
                rows.append({"target":target,"domain":domain,"control":name,
                    "id":target+"/"+domain+"/"+name,"verdict":value,"evidence":proof})
    if len(rows)!=500 or len({r["id"] for r in rows})!=500:raise ValueError("500_UNIQUE_SLOTS_REQUIRED")
    return rows

def audit(run_runner=False):
    policy=load()
    bad=checks(policy)
    rows=assess(policy,run_runner)
    return {"schema":"luhmOs.samsungCast500Receipt.v1",
       "sourceRef":exact_ref(),"sourceChecks":30,"sourceErrors":bad,
       "assessmentSlots":len(rows),"distinctControls":sum(map(len,DOMAINS.values())),
       "counts":dict(Counter(r["verdict"] for r in rows)),
       "sourceVerdict":"GREEN" if not bad else "RED",
       "runtimeVerdict":"AMBER_UNVERIFIED","machineScope":"GitHub runner only" if run_runner else "No runtime",
       "samsungFirmwareRead":False,"samsungFirmwareFlashed":False,
       "linuxBootModified":False,"cameraStreamStarted":False,"apksInstalled":False,
       "crownStatus":"STOP","assessments":rows}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--runner",action="store_true")
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    receipt=audit(args.runner)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf8")
    print(json.dumps({k:v for k,v in receipt.items() if k!="assessments"},indent=2))
    return 1 if receipt["sourceErrors"] else 0

if __name__=="__main__":
    raise SystemExit(main())
