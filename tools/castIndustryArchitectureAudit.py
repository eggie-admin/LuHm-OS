#!/usr/bin/env python3
"""Read-only CAST upstream lifecycle and four-platform 4x4 source-contract audit."""
from __future__ import annotations
from datetime import date
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse
ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine/castIndustryArchitectureReductionV1.json"
CORE = ("gpu", "cpu", "memory", "firmware")
PLATFORMS = ("apple", "android", "linux", "googleCompute")
DIMS = ("abi", "kernel", "accelerator", "delivery")
ALLOWED_DECISIONS = {
    "AVOID_NEW_BASELINE", "SUPPORTED_CANDIDATE", "TESTING_CANDIDATE",
    "MIGRATION_WATCH", "UPSTREAM_EOL_WATCH", "DISTRO_SUPPORT_REQUIRED"
}
ALLOWED_HOSTS = {
    "devguide.python.org", "github.com", "www.kernel.org", "ubuntu.com",
    "www.postgresql.org", "docs.github.com", "docs.n8n.io",
    "gparted.org", "www.gnu.org", "www.damnsmalllinux.org",
    "stat.ethz.ch", "docs.kernel.org", "docs.python.org",
    "docs.godotengine.org", "onnxruntime.ai"
}
class IndustryAuditError(ValueError):
    pass

def safe_local_file(value, root=ROOT):
    if type(value) is not str or not value or "\\" in value or ".." in Path(value).parts or Path(value).is_absolute():
        return False
    file = root / value
    return file.is_file() and not file.is_symlink() and file.resolve().is_relative_to(root.resolve())

def trusted_reference(url):
    if type(url) is not str or len(url) > 240:
        return False
    p = urlparse(url)
    return p.scheme == "https" and p.hostname in ALLOWED_HOSTS and not p.username and not p.password and not p.fragment

def audit(contract, root=ROOT):
    if type(contract) is not dict or contract.get("schema") != "luhmOs.castIndustryArchitectureReduction.v1":
        raise IndustryAuditError("SCHEMA")
    if contract.get("authority") != "Professor" or contract.get("status") != "PROPOSED_SOURCE_RESEARCH_ONLY" or contract.get("crownStatus") != "STOP":
        raise IndustryAuditError("AUTHORITY")
    if contract.get("sourceLaw") != "AI proposes. Policy authorizes. CI proves. Human promotes.":
        raise IndustryAuditError("SOURCE_LAW")
    asof = date.fromisoformat(contract["observedAsOf"])
    ps = contract.get("platforms", [])
    if [p.get("id") for p in ps] != list(PLATFORMS) or contract.get("dimensions") != list(DIMS):
        raise IndustryAuditError("PLATFORM_AXES")
    cells = contract.get("matrix", [])
    if len(cells) != 16:
        raise IndustryAuditError("MATRIX_LENGTH")
    for i, cell in enumerate(cells):
        if cell != {"index":i, "hex":f"0x{i:02X}", "platform":PLATFORMS[i//4],
                    "dimension":DIMS[i%4], "proof":"SOURCE_RESEARCH_ONLY"}:
            raise IndustryAuditError("MATRIX_HEX_IDENTITY")
    fs = contract.get("functionClasses", [])
    if [f.get("id") for f in fs] != ["route", "reason", "execute", "verify"]:
        raise IndustryAuditError("FUNCTION_CLASS_ORDER")
    if any(type(f.get("requires")) is not list or not f["requires"] for f in fs):
        raise IndustryAuditError("FUNCTION_GATES")
    if any(f.get("humanPromotion") is not True for f in fs[2:]):
        raise IndustryAuditError("TOOL_EXECUTION_PROMOTION")
    if not contract.get("lifecycle"):
        raise IndustryAuditError("NO_LIFECYCLE")
    seen = set()
    expired = []
    for item in contract["lifecycle"]:
        key = (item.get("family"), item.get("baseline"))
        if key in seen or item.get("decision") not in ALLOWED_DECISIONS:
            raise IndustryAuditError("LIFECYCLE_DUPLICATE_OR_UNKNOWN")
        seen.add(key)
        end = date.fromisoformat(item["eol"])
        if not trusted_reference(item.get("source")):
            raise IndustryAuditError("LIFECYCLE_UNTRUSTED_REFERENCE")
        if end < asof:
            expired.append(key)
            if item["decision"] != "AVOID_NEW_BASELINE":
                raise IndustryAuditError("EOL_MARKED_ACTIVE")
    if ("Python", "3.10") not in expired:
        raise IndustryAuditError("PYTHON_310_EOL_NOT_CAPTURED")
    t = contract.get("tools", [])
    if len({x.get("id") for x in t}) != len(t) or len(t) < 8:
        raise IndustryAuditError("TOOLS_DUPLICATED_OR_TOO_FEW")
    if any(not trusted_reference(x.get("doc")) for x in t):
        raise IndustryAuditError("TOOLS_UNTRUSTED_DOCS")
    indexed = {x["id"]:x for x in t}
    if indexed["grub"].get("androidBootAllowed") is not False or indexed["gparted"].get("needsBackup") is not True:
        raise IndustryAuditError("DISK_BOOT_SAFETY")
    if indexed["n8n"].get("state") != "EVALUATE_ONLY" or indexed["n8n"].get("license") != "FAIR_CODE_NOT_ASSUMED_APACHE":
        raise IndustryAuditError("NO_CODE_VENDOR_BOUNDARY")
    if any(not safe_local_file(s, root) for s in contract.get("sourceRefs", [])):
        raise IndustryAuditError("SOURCE_REF_MISSING")
    if any(val is not True for val in contract.get("limits", {}).values()):
        raise IndustryAuditError("MUTATION_BARRIER_REMOVED")
    a = contract.get("adoption", {})
    if (a.get("canonicalFourCores") != list(CORE) or a.get("applicationPayloadBytesCap") != 4096 or
        any(a.get(k) is not True for k in ("hexUsedForLogicIndexesOnly", "noByteLabelAsKernelAddress",
           "strictSqlInMemoryOnly", "runtimeUpgradeRequiresExactHostABI", "devicePageSizeMustBeMeasured",
           "linuxKernelVersionMustNotBeInferredFromContainer", "physicalBenchmarksStillMissing"))):
        raise IndustryAuditError("FALSE_ARCHITECTURE_PROMOTION")
    if contract.get("reviewGates") != [
        "androidNative16KiBPageAlignment","appleArm64NativeOrUniversalAppSlice","exactSourceLifecyclePinned",
        "p95FrameTimeAndRssPerPhysicalDevice","cpuQuotaAndPerfRights","trustedOemDriverAbi",
        "reproducibleBenchmarkBaseline","signingAndManualPromotion"]:
        raise IndustryAuditError("MISSING_RELEASE_REVIEW_GATES")
    return {"schema":"luhmOs.castIndustryArchitectureReceipt.v1", "status":"AMBER_SOURCE_REVIEW_ONLY",
       "platforms":len(ps), "matrixCells":len(cells), "functionClasses":len(fs),
       "lifecycleEntries":len(seen), "observedExpired":[f"{f} {v}" for f,v in expired],
       "studyTools":len(t), "physicalDeviceAudited":False,"softwareInstalled":False,
       "kernelModified":False,"bootDiskModified":False,"crownStatus":"STOP",
       "contractSha256":hashlib.sha256(json.dumps(contract,sort_keys=True,separators=(",",":")).encode("utf-8")).hexdigest()}

if __name__=="__main__":
    print(json.dumps(audit(json.loads(CONTRACT.read_text(encoding="utf-8"))),sort_keys=True))
