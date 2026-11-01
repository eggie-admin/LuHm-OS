#!/usr/bin/env python3
"""Read-only 4x4 CAST processor/byte benchmark with strict bounded synthetic buffers.

No GRUB, kernel, network, BIOS, firmware, clock, governor, or affinity mutation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
from statistics import median
import time

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine/processorHexCeilingsV1.json"
ROWS = ("bootAndFirmware","kernelAndDrivers","hardwareNetworking","processorAndMemory")
PHASES = ("identify","bound","measure","verify")
SIZES = (4096,65536,1048576)
MAX_BUFFER = 1048576
MAX_REPEATS = 3

class ProcessorCeilingError(ValueError):
    pass

def source_path(value: object, root: Path = ROOT) -> bool:
    if type(value) is not str or not value or chr(92) in value or Path(value).is_absolute() or ".." in Path(value).parts:
        return False
    path = root / value
    return path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(root.resolve())

def checked_size(value: object) -> int:
    if type(value) is not int or value not in SIZES or value > MAX_BUFFER:
        raise ProcessorCeilingError("SIZE_OUTSIDE_APPROVED_BYTE_LADDER")
    return value

def synthetic_payload(size: int) -> bytes:
    size = checked_size(size)
    return bytes(range(256)) * (size // 256) + bytes(range(size % 256))

def select_worker_ceiling(effective_cpu_count: object, max_workers: int=4) -> int:
    if type(effective_cpu_count) is not int or effective_cpu_count < 1:
        raise ProcessorCeilingError("CPU_COUNT_MUST_BE_POSITIVE_INTEGER")
    if type(max_workers) is not int or max_workers < 1 or max_workers > 4:
        raise ProcessorCeilingError("WORKER_CEILING_OUT_OF_POLICY")
    return min(max_workers,effective_cpu_count)

def validate(policy: dict, root: Path = ROOT) -> dict:
    if type(policy) is not dict or policy.get("schema")!="luhmOs.processorHexCeilings.v1":
        raise ProcessorCeilingError("SCHEMA_DRIFT")
    if (policy.get("status")!="PROPOSED_SOURCE_AND_RUNNER_PROOF_ONLY"
        or policy.get("crownStatus")!="STOP" or policy.get("authority")!="Professor"
        or policy.get("sourceLaw")!="AI proposes. Policy authorizes. CI proves. Human promotes."):
        raise ProcessorCeilingError("SOURCE_PROMOTION_BOUNDARY")
    if policy.get("namespace")!="castProcessorRuntimeFourByFourV1":
        raise ProcessorCeilingError("NAMESPACE_DRIFT")
    rows=policy.get("rows",[])
    if [x.get("id") for x in rows] != list(ROWS) or policy.get("columns")!=list(PHASES):
        raise ProcessorCeilingError("FOUR_BY_FOUR_AXES")
    if len(policy.get("matrix",[]))!=16:
        raise ProcessorCeilingError("FOUR_BY_FOUR_SIZE")
    for index,item in enumerate(policy["matrix"]):
        row=index//4
        if (item.get("address") != f"0x{index:02X}"
            or item.get("row")!=ROWS[row] or item.get("phase")!=PHASES[index%4]
            or item.get("source")!=rows[row]["reference"] or item.get("proof")!="INDEX_ONLY"):
            raise ProcessorCeilingError("FOUR_BY_FOUR_CELL")
    if not all(source_path(x["reference"],root) for x in rows):
        raise ProcessorCeilingError("SOURCE_PATH_UNAVAILABLE")
    if not all(source_path(x,root) for x in policy.get("sourceRefs",[])):
        raise ProcessorCeilingError("CANON_POINTER_MISSING")
    parent=policy.get("stackedOn",{})
    if parent.get("pr")!=471 or parent.get("branch")!="candidate/hardware-4x4-vendor-minimum-20261031":
        raise ProcessorCeilingError("PARENT_PROVENANCE_DRIFT")
    b=policy.get("bufferCeilings",{})
    if (policy.get("byteLadder")!=list(SIZES)
        or policy.get("hexLadder") != ["0x001000","0x010000","0x100000"]
        or b.get("samplePayloadMaxBytes")!=MAX_BUFFER
        or b.get("sampleCount")!=MAX_REPEATS or b.get("maxCandidateWorkers")!=4
        or b.get("maxBoundedReceiptBytes")!=65536
        or b.get("benchmarkUsesSyntheticBytes") is not True
        or b.get("benchmarkedOnRealSamsung") is not False):
        raise ProcessorCeilingError("BYTE_CEILING_DRIFT")
    systems=policy.get("platforms",{})
    if (systems.get("pcLinux",{}).get("grubMayBeUsed") is not True
        or systems.get("pcLinux",{}).get("grubPresenceUnproven") is not True
        or systems.get("androidSamsung",{}).get("grubMayBeUsed") is not False
        or systems.get("androidSamsung",{}).get("androidVerifiedBootPreserved") is not True
        or systems.get("codespaces",{}).get("kernelIsHostControlled") is not True
        or systems.get("codespaces",{}).get("containerCannotInferHostBootloader") is not True):
        raise ProcessorCeilingError("BOOT_CHAIN_CONFLATION")
    for name in ("pcLinux","androidSamsung"):
        if systems[name].get("bootWriteAuthorized") is not False:
            raise ProcessorCeilingError("BOOT_WRITE_AUTHORITY")
    controls=policy.get("optimization",{})
    if controls.get("selectedChunkAdvisoryOnly") is not True:
        raise ProcessorCeilingError("PREMATURE_TUNE")
    if any(controls.get(k) is not False for k in (
       "performanceRegressionThresholdEnforced","clockGovernorChange","ramFrequencyChange","socketBufferSet",
       "irqAffinityChange","threadsSpawned","backgroundServiceStarted")):
        raise ProcessorCeilingError("SYSTEM_TUNING_NOT_AUTHORIZED")
    if any(policy.get(k) is not False for k in (
       "physicalBootStateVerified","physicalDeviceVerified","hostKernelModified",
       "anySystemSettingsChanged","protectedMainMerged")) or policy.get("workersActive")!=0:
        raise ProcessorCeilingError("FALSE_RUNTIME_OR_AUTHORITY_CLAIM")
    stops=set(policy.get("neverRun",[]))
    if not {"grubInstall","updateGrub","flashFirmware","sysctlWrite","cpufreqGovernorWrite",
        "loadKernelModule","aptInstall","deployProduction"}.issubset(stops):
        raise ProcessorCeilingError("PROTECTED_STOP_MISSING")
    quarantine=json.loads((root/"doctrine/companyWideOperationalQuarantineV1.json").read_text(encoding="utf-8"))
    if quarantine.get("state")!="QUARANTINED" or quarantine.get("activeTaskWorkersAllowed") is not False:
        raise ProcessorCeilingError("QUARANTINE_AUTHORITY_DRIFT")
    return {"schema":"luhmOs.processorHexCeilingReceipt.v1",
      "status":"AMBER_SOURCE_ONLY","sourceRoutes":16,"runnerBenchmarked":False,
      "androidDeviceBenchmarked":False,"firmwareMutations":False,
      "kernelMutations":False,"networkMutations":False,"crownStatus":"STOP"}

def observed_cpu_context() -> dict:
    advertised = os.cpu_count()
    try:
        affinity = len(os.sched_getaffinity(0))
    except (AttributeError,OSError):
        affinity = None
    candidates=[x for x in (affinity,advertised) if type(x) is int and x > 0]
    effective=min(candidates) if candidates else 1
    try:
        page_size=os.sysconf("SC_PAGE_SIZE")
    except (OSError,AttributeError,ValueError):
        page_size=None
    if type(page_size) is not int or page_size<=0:
        page_size=None
    return {"runtimeSystem":platform.system(),"runtimeArchitecture":platform.machine(),
       "reportedLogicalCpus":advertised,"affinityVisibleLogicalCpus":affinity,
       "effectiveCpuCountEstimate":effective,"cgroupQuotaProven":False,
       "physicalCoreCountProven":False,"pageSizeBytes":page_size,
       "pageSizeHex":f"0x{page_size:X}" if page_size is not None else None,
       "maxCandidateConcurrentWorkers":select_worker_ceiling(effective),
       "actualClockFrequencyProven":False,"kernelGovernorChanged":False}

def measure_synthetic(sizes: tuple[int,...]=SIZES, repeats: int=MAX_REPEATS) -> dict:
    if type(repeats) is not int or repeats!=MAX_REPEATS or tuple(sizes)!=SIZES:
        raise ProcessorCeilingError("BENCH_WORK_LIMIT_EXCEEDED")
    scores=[]
    for size in sizes:
        buffer=synthetic_payload(size)
        expected=hashlib.sha256(buffer).digest()
        samples=[]
        for repetition in range(repeats):
            hash_stream=hashlib.sha256()
            start=time.perf_counter_ns()
            view=memoryview(buffer)
            for offset in range(0,size,size):
                hash_stream.update(view[offset:offset+size])
            elapsed=max(1,time.perf_counter_ns()-start)
            if hash_stream.digest()!=expected:
                raise ProcessorCeilingError("BENCH_DIGEST_MISMATCH")
            samples.append(elapsed)
        mid=int(median(samples))
        scores.append({"sizeBytes":size,"sizeHex":f"0x{size:06X}",
            "sampleCount":repeats,"medianDurationNs":mid,
            "estimatedMiBPerSecond":round((size*1e9)/(1048576*mid),3),
            "syntheticPayloadSha256":expected.hex(),
            "runtimeEnvironmentScope":"THIS_PROCESS_ONLY"})
    fastest=max(scores,key=lambda x:(x["estimatedMiBPerSecond"],-x["sizeBytes"]))
    return {"observedScores":scores,
       "bestObservedPayloadSizeBytes":fastest["sizeBytes"],
       "bestObservedPayloadSizeHex":fastest["sizeHex"],
       "advisoryOnly":True,"repeatabilityUnproven":True,
       "thermalAndCpuQuotaUnverified":True}

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--measure",action="store_true",help="Run one bounded deterministic synthetic CPU hash microbenchmark")
    p.add_argument("--output",type=Path,default=None,help="Optional JSON receipt in ephemeral CI workspace")
    args=p.parse_args()
    contract=json.loads(CONTRACT.read_text(encoding="utf-8"))
    result=validate(contract)
    result["cpuContext"]=observed_cpu_context()
    if args.measure:
        result["microbench"]=measure_synthetic()
        result["runnerBenchmarked"]=True
        result["status"]="AMBER_RUNNER_MEASURED_ONLY"
    packed=json.dumps(result,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n"
    if len(packed.encode("utf-8"))>contract["bufferCeilings"]["maxBoundedReceiptBytes"]:
        raise ProcessorCeilingError("RECEIPT_TOO_LARGE")
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(packed,encoding="utf-8")
    print(packed,end="")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
