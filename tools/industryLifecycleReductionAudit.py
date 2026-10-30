#!/usr/bin/env python3
"""Read-only lifecycle and workflow-overlap inventory for Proposed LuHm-OS.
Never runs vendor code, edits workflows, dispatches CAST, merges, or publishes.
"""
import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = "doctrine/industryLifecycleReductionV1.json"

def load(root: Path, relative: str):
    return json.loads((root / relative).read_text(encoding="utf-8"))

def evaluate(profile, brand, truth, release):
    errors = []
    identity = profile.get("identity", {})
    if (identity.get("product"), identity.get("project"), identity.get("legacyAlias"),
        identity.get("publisher")) != ("LuHm-OS", "Project Premonition", "Project Hydra", "Eggie Bagelface"):
        errors.append("canonicalIdentityDrift")
    if (brand.get("product"), brand.get("developmentProject"), brand.get("legacyProject"),
        brand.get("publisher")) != ("LuHm-OS", "Project Premonition", "Project Hydra", "Eggie Bagelface"):
        errors.append("sourceBrandDrift")
    ids = [item.get("id") for item in profile.get("lanes", []) if isinstance(item, dict)]
    if ids != ["legacy", "testing", "proposed", "privateBeta", "publicBeta", "stable"]:
        errors.append("laneOrderDrift")
    if any(item.get("releaseAllowed") is not False for item in profile.get("lanes", []) if isinstance(item, dict)):
        errors.append("unapprovedReleaseLane")
    exec_policy = profile.get("execution", {})
    for name in ("autoMerge", "autoDeploy", "autoPublish", "autoSign", "autoCrown", "roleplayIsAuthority", "agentRuntimeProven"):
        if exec_policy.get(name) is not False: errors.append("unsafeExecution:" + name)
    if exec_policy.get("readOnlyAuditDefault") is not True or exec_policy.get("singleMutableCandidate") is not True:
        errors.append("unsafeExecutionDefaults")
    auth = brand.get("authorizations", {})
    if auth.get("publicMarketing") is not False or auth.get("productionSigning") is not False:
        errors.append("brandPermissionDrift")
    if profile.get("brand", {}).get("publicMarketingAuthorized") is not False:
        errors.append("marketingNotAuthorized")
    if profile.get("crownStatus") != "STOP" or brand.get("crownStatus") != "STOP":
        errors.append("crownNotStopped")
    if truth.get("promotion") is not False:
        errors.append("truthPromotionNotHeld")
    if release.get("promotion") is not False or release.get("fullPublicReleasePublished") is not False:
        errors.append("publicReleaseNotHeld")
    if profile.get("runtimeCandidates", {}).get("python", {}).get("recommendedCandidate") == "3.10":
        errors.append("pythonEolDefault")
    if profile.get("runtimeCandidates", {}).get("node", {}).get("recommendedBaseline") in ("20", "23", "25"):
        errors.append("nodeEolDefault")
    return errors

USES = re.compile(r"^\s*(?:-\s*)?uses:\s*([^\s#]+)\s*", re.M)
PIN = re.compile(r"^[0-9a-f]{40}$")
def inspect_workflows(folder: Path):
    paths = sorted(list(folder.glob("*.yml")) + list(folder.glob("*.yaml")))
    exact = defaultdict(list)
    findings = []
    category_counts = defaultdict(int)
    for path in paths:
        content = path.read_text(encoding="utf-8")
        exact[hashlib.sha256(content.encode("utf-8")).hexdigest()].append(path.name)
        name = path.name.lower()
        if any(t in name for t in ("release", "deploy", "beta", "cast", "package", "build")):
            category = "deliveryAndCast"
        elif any(t in name for t in ("studio", "godot", "blender", "game", "video", "yume", "art")):
            category = "studioAndGame"
        elif any(t in name for t in ("audit", "security", "hardening", "canon", "truth", "vendor", "gate")):
            category = "governanceAndSecurity"
        else:
            category = "generalOrchestration"
        category_counts[category] += 1
        flags = []
        for ref in USES.findall(content):
            if ref.startswith("./"): continue
            tag = ref.rsplit("@", 1)[-1] if "@" in ref else ""
            if not PIN.fullmatch(tag):
                flags.append("actionNotPinnedToFullCommit")
        if "pull_request_target:" in content: flags.append("privilegedPrEventReview")
        if re.search(r"^\s*actions:\s*write\s*$", content, re.M): flags.append("writePermissionReview")
        if re.search(r"^\s*runs-on:\s*ubuntu-latest", content, re.M): flags.append("floatingRunnerReview")
        if re.search(r"^\s*node-version:\s*['\"]?(?:20|23|25)\b", content, re.M): flags.append("nodeEolReferenceReview")
        if "workflow_dispatch:" in content: flags.append("manualDispatchSurfaceReview")
        if flags: findings.append({"workflow": path.name, "flags": sorted(set(flags))})
    groups = [sorted(names) for names in exact.values() if len(names) > 1]
    return {"count": len(paths), "families": dict(sorted(category_counts.items())),
            "exactDuplicateGroups": sorted(groups), "reviewCandidates": findings}

def audit(root: Path, source_ref: str):
    if not re.fullmatch(r"[0-9a-f]{40}", source_ref):
        raise ValueError("EXACT_SHA_REQUIRED")
    profile = load(root, POLICY)
    brand = load(root, "doctrine/premonitionEnterpriseBrandV1.json")
    truth = load(root, "doctrine/currentSourceTruthV3.json")
    release = load(root, "doctrine/finalFormPublicReleaseGateV1.json")
    errors = evaluate(profile, brand, truth, release)
    inventory = inspect_workflows(root / ".github" / "workflows")
    if inventory["count"] == 0: errors.append("noWorkflowInventory")
    return {"schema":"luhmOs.industryLifecycleReductionReceipt.v1",
            "sourceRef":source_ref, "product":profile.get("identity",{}).get("product"),
            "lane":"PROPOSED_SOURCE_ONLY",
            "sourceGuard":"PASS" if not errors else "RED", "errors":errors,
            "workflows":inventory, "sourceOnly":True, "workflowReductionExecuted":False,
            "runtimeVersionUpgradeExecuted":False, "legacyBranchesMerged":False,
            "privateBetaReady":False, "publicBetaReady":False, "marketingPublished":False,
            "artifactSigned":False, "crown":"STOP"}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source-ref", required=True)
    p.add_argument("--output")
    args = p.parse_args()
    report = audit(ROOT, args.source_ref)
    raw = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(raw, encoding="utf-8")
    else:
        print(raw, end="")
    return int(bool(report["errors"]))

if __name__ == "__main__":
    raise SystemExit(main())
