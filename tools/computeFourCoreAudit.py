#!/usr/bin/env python3
"""LuHm compute 4x4: reject server creep; inspect runner hints without any host writes."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/"doctrine/computeFourCoreV1.json"
ROWS=("gpu","cpu","memory","firmware")
PHASES=("identify","bound","probe","verify")
ALLOWED_PACKAGES=("ca-certificates","curl","git","python3","python3-venv","blender","ffmpeg",
                  "libgl1","libfontconfig1","libasound2t64","fonts-dejavu-core")
PACKAGE=re.compile("[a-z0-9][a-z0-9+.-]*" + chr(92) + "Z")
MAX_MEMORY_CLAIM=1<<50

class FourCoreError(ValueError):
    pass

def canonical_path(value: object, root: Path=ROOT) -> bool:
    if type(value) is not str or not value or chr(92) in value or Path(value).is_absolute() or ".." in Path(value).parts:
        return False
    target=root/value
    return target.is_file() and not target.is_symlink() and target.resolve().is_relative_to(root.resolve())

def apt_names(text: str) -> list[str]:
    marker="apt-get install -y --no-install-recommends"
    if type(text) is not str or text.count(marker)!=1:
        raise FourCoreError("APT_DECLARATION_NOT_EXACT")
    fragment=text.split(marker,1)[1].split(";",1)[0]
    tokens=fragment.replace(chr(92)," ").split()
    if len(tokens)!=len(ALLOWED_PACKAGES) or len(set(tokens))!=len(tokens):
        raise FourCoreError("PACKAGE_SET_SIZE")
    if any(PACKAGE.fullmatch(token) is None for token in tokens):
        raise FourCoreError("MALFORMED_PACKAGE")
    return tokens

def verify_dockerfile(text: str, policy: dict) -> dict:
    if type(text) is not str or not text.startswith("# LuHm-OS four-core compute:"):
        raise FourCoreError("IMAGE_IDENTITY")
    if text.count("FROM ubuntu:26.04")!=1 or "USER studio" not in text or 'CMD ["/bin/bash"]' not in text:
        raise FourCoreError("BASE_USER_OR_COMMAND_DRIFT")
    if "FROM " in text.replace("FROM ubuntu:26.04",""):
        raise FourCoreError("MULTI_STAGE_UNKNOWN")
    if policy["image"]["entrypoint"]!="/bin/bash" or policy["image"]["runAs"]!="studio":
        raise FourCoreError("USER_AUTHORITY")
    packages=apt_names(text)
    if sorted(packages)!=sorted(ALLOWED_PACKAGES) or sorted(policy["image"]["dependencyPackages"])!=sorted(ALLOWED_PACKAGES):
        raise FourCoreError("EXTRANEOUS_PACKAGE")
    for name in policy["image"]["forbiddenPackages"]:
        if name in packages:
            raise FourCoreError("FORBIDDEN_SERVER_PACKAGE")
    if re.search(r"(?im)^[ \t]*(?:EXPOSE|ENTRYPOINT|HEALTHCHECK|ONBUILD|VOLUME)(?:[ \t]|$)",text):
        raise FourCoreError("NETWORK_OR_AUTOSTART_DIRECTIVE")
    if len(re.findall(r"(?im)^[ \t]*CMD(?:[ \t]|$)",text)) != 1:
        raise FourCoreError("CMD_DUPLICATE")
    for term in ("service nginx start","systemctl enable","supervisord","listen 0.0.0.0",
                 "listen [::]","sudo ","modprobe ","flashrom ","efibootmgr ","grub-install ",
                 "wget | sh","curl | sh"):
        if term in text:
            raise FourCoreError("UNAUTHORIZED_RUNTIME_OR_FIRMWARE")
    if policy["image"]["godotRelease"] not in text or policy["image"]["godotDownloadSha256"] not in text or "sha256sum --check" not in text:
        raise FourCoreError("GODOT_PIN_DRIFT")
    if "ARG TARGETARCH" not in text or 'test "${TARGETARCH:-amd64}" = amd64' not in text:
        raise FourCoreError("ARCHITECTURE_NOT_BOUNDED")
    return {"declaredPackages":len(packages),"serverPackagesSelected":0,"startsServer":False,
            "imageBuilt":False,"kernelOrFirmwareMutated":False}

def parse_memory_max(raw: object) -> int | None:
    if raw is None:
        return None
    if type(raw) is not str or len(raw)>64:
        raise FourCoreError("CGROUP_MEMORY_MAX_INVALID")
    value=raw.strip()
    if value=="max":
        return None
    if not value or not value.isascii() or not value.isdecimal():
        raise FourCoreError("CGROUP_MEMORY_MAX_INVALID")
    limit=int(value)
    if limit<=0 or limit>MAX_MEMORY_CLAIM:
        raise FourCoreError("CGROUP_MEMORY_MAX_UNTRUSTED")
    return limit

def advisory_cpu_workers(value: object) -> int | None:
    if value is None:
        return None
    if type(value) is not int or value<1 or value>1048576:
        raise FourCoreError("CPU_COUNT_INVALID")
    return min(4,value)

def safe_read_cgroup(root: Path=Path("/")) -> str | None:
    p=root/"sys/fs/cgroup/memory.max"
    try:
        if not p.is_file() or p.is_symlink():
            return None
        with p.open("rb") as fh:
            raw=fh.read(65)
        if len(raw)>64:
            raise FourCoreError("MEMORY_LIMIT_TEXT_TOO_LONG")
        return raw.decode("ascii")
    except (FileNotFoundError,PermissionError,UnicodeError,OSError):
        return None

def runner_probe(root: Path=Path("/")) -> dict:
    if not root.is_absolute():
        raise FourCoreError("PROBE_ROOT_ABSOLUTE_REQUIRED")
    try:
        logical=os.cpu_count()
    except OSError:
        logical=None
    try:
        affinity=len(os.sched_getaffinity(0))
    except (AttributeError,OSError):
        affinity=None
    capacities=[x for x in (logical,affinity) if type(x) is int and x>=1]
    cpu=min(capacities) if capacities else None
    try:
        memory_limit=parse_memory_max(safe_read_cgroup(root))
    except FourCoreError:
        memory_limit=None
    working_set=min(67108864,memory_limit//4) if memory_limit is not None else None
    # Presence is only a hint, never a GPU/UEFI attestation or a driver capability grant.
    drm=(root/"dev/dri/renderD128")
    efi=(root/"sys/firmware/efi")
    return {"schema":"luhmOs.fourCoreRunnerHint.v1","system":platform.system(),
      "cpuLogicalAdvertised":logical,"cpuAffinityVisible":affinity,"cpuEffectiveHint":cpu,
      "cpuWorkersAdvisory":advisory_cpu_workers(cpu),
      "memoryCgroupLimitBytesHint":memory_limit,"memoryWorkingSetBytesAdvisory":working_set,
      "gpuRenderNodePresentHint":drm.exists(),"gpuHardwareAccelerationVerified":False,
      "firmwareEfiDirectoryPresentHint":efi.is_dir(),"uefiFirmwareVerified":False,
      "grubInstalledVerified":False,"samsungAvbVerified":False,
      "deviceControllerQueried":False,"hostSettingsModified":False}

def audit(config: dict, root: Path=ROOT) -> dict:
    if type(config) is not dict or config.get("schema")!="luhmOs.computeFourCore.v1":
        raise FourCoreError("SCHEMA_DRIFT")
    if (config.get("authority")!="Professor" or config.get("status")!="PROPOSED_OPT_IN_COMPUTE_SOURCE"
        or config.get("crownStatus")!="STOP"
        or config.get("sourceLaw")!="AI proposes. Policy authorizes. CI proves. Human promotes."):
        raise FourCoreError("AUTHORITY_DRIFT")
    if config.get("namespace")!="castComputeFourCore4x4V1":
        raise FourCoreError("MATRIX_NAMESPACE_DRIFT")
    rows=config.get("rows",[])
    if [x.get("id") for x in rows]!=list(ROWS) or config.get("phases")!=list(PHASES):
        raise FourCoreError("4X4_AXES")
    cells=config.get("matrix",[])
    if len(cells)!=16:
        raise FourCoreError("4X4_CELL_COUNT")
    for ix,cell in enumerate(cells):
        if (cell.get("index")!=ix or cell.get("hex")!=f"0x{ix:02X}"
            or cell.get("row")!=ROWS[ix//4] or cell.get("phase")!=PHASES[ix%4]
            or cell.get("source")!=rows[ix//4].get("source")
            or cell.get("status")!="SOURCE_ROUTE_ONLY"):
            raise FourCoreError("4X4_INDEX_DRIFT")
    if any(not canonical_path(x.get("source"),root) for x in rows):
        raise FourCoreError("NONCANONICAL_SOURCE")
    if any(not canonical_path(x,root) for x in config.get("sourceRefs",[])):
        raise FourCoreError("SOURCE_REFS")
    p=config.get("stackedOn",{})
    if p.get("pr")!=472 or p.get("branch")!="candidate/cast-processor-byte-ceilings-20261031":
        raise FourCoreError("STACKED_SOURCE_DRIFT")
    image=config.get("image",{})
    if not canonical_path(image.get("path"),root) or image.get("expectedDeclaredCount")!=11 or image.get("base")!="ubuntu:26.04":
        raise FourCoreError("COMPUTE_IMAGE_PATH")
    if (image.get("requiresGpuDevice") is not False or image.get("requiresRoot") is not False
        or image.get("exposesPorts") is not False or image.get("startsDaemon") is not False
        or image.get("actualImageBuilt") is not False or image.get("installedPackagesProven") is not False
        or image.get("notDefaultCodespaceDockerfile") is not True):
        raise FourCoreError("IMAGE_FALSE_RUNTIME")
    if sorted(image.get("forbiddenPackages",[]))!=sorted(
        ["nginx","apache2","lighttpd","mariadb-server","mysql-server","postgresql","postfix","exim4",
         "sendmail","dovecot-core","bind9","dnsmasq","certbot","nodejs","npm"]):
        raise FourCoreError("FORBIDDEN_PACKAGES_EDITED")
    if image.get("forbiddenRuntimeDirectives")!=["EXPOSE","ENTRYPOINT"]:
        raise FourCoreError("RUNTIME_BOUNDARY")
    docker=verify_dockerfile((root/image["path"]).read_text(encoding="utf8"),config)
    cap=config.get("ceiling",{})
    if (cap.get("maxCpuAdvisoryWorkers")!=4 or cap.get("maxWorkingSetAdvisoryBytes")!=67108864
        or cap.get("maxReadBytes")!=64 or cap.get("maxCgroupClaimBytes")!=MAX_MEMORY_CLAIM
        or cap.get("actualHardwareMemoryStress") is not False or cap.get("actualGpuBenchmark") is not False):
        raise FourCoreError("CPU_MEMORY_BUDGET_DRIFT")
    runtime=config.get("runtime",{})
    if any(runtime.get(x) is not True for x in ("gpuDeviceHintOnly","cpuAffinityHintOnly",
        "cgroupMemoryLimitHintOnly","uefiDirectoryHintOnly")):
        raise FourCoreError("HINT_GUARD")
    if any(runtime.get(x) is not False for x in (
        "physicalSamsungVerified","deviceDriverVerified","hostGpuAccelerationVerified","firmwareVersionVerified",
        "biosChange","grubChange","cpuGovernorChange","memoryClockChange","gpuDriverInstall",
        "dmaOrKernelModuleLoad","networkListener","paidProvider","agentActivated")):
        raise FourCoreError("FALSE_DEVICE_OR_TUNING_CLAIM")
    if any(config.get(k) is not True for k in ("noHardwareMutation","noPackageMutation","noProductionDeploy","noAutomaticMerge")):
        raise FourCoreError("MUTATION_FLAG_MISSING")
    if config.get("notRequired")!=["websiteHosting","mailServer","publicDatabase","dnsServer","publicProxy",
        "gpuCloudVm","secondKernel","bareMetalFirmwareToolkit"]:
        raise FourCoreError("SERVICE_SCOPE_CREEP")
    quarantine=json.loads((root/"doctrine/companyWideOperationalQuarantineV1.json").read_text(encoding="utf8"))
    if quarantine.get("state")!="QUARANTINED" or quarantine.get("activeTaskWorkersAllowed") is not False:
        raise FourCoreError("AGENT_QUARANTINE")
    return {"schema":"luhmOs.computeFourCoreReceipt.v1","status":"AMBER_SOURCE_ONLY",
      "matrixCells":16,"coreDimensions":list(ROWS),"computePackages":docker["declaredPackages"],
      "serverPackages":0,"actualDockerBuild":False,"physicalGpuTested":False,"physicalFirmwareTested":False,
      "hostMutations":False,"crownStatus":"STOP",
      "contractSha256":hashlib.sha256(json.dumps(config,sort_keys=True,separators=(",",":")).encode("utf8")).hexdigest()}

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe-runner",action="store_true",help="Read-only runtime hints on THIS runner, not Samsung")
    args=parser.parse_args()
    contract=json.loads(CONTRACT.read_text(encoding="utf8"))
    result=audit(contract)
    if args.probe_runner:
        result["runnerHints"]=runner_probe()
        result["status"]="AMBER_RUNNER_HINTS_ONLY"
    print(json.dumps(result,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
