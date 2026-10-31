#!/usr/bin/env python3
"""LuHm-OS: Project Premonition | reproducible frontend vendor/size profile checks."""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "frontEnd/prototypes/glassWorld"
POLICY = ROOT / "doctrine/vendorReductionV1.json"

def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()

def inspectDependencies(policy: dict, package: dict, lock: dict, worldSource: str, html: str) -> tuple[list[str], dict]:
    npm = policy["npm"]
    problems: list[str] = []
    if package.get("private") is not True:
        problems.append("NPM_PACKAGE_MUST_REMAIN_PRIVATE")
    if package.get("dependencies") != npm["exactDirectDependencies"]:
        problems.append("UNEXPECTED_RUNTIME_DEPENDENCY")
    if package.get("devDependencies") != npm["exactBuildDependencies"]:
        problems.append("UNEXPECTED_BUILD_DEPENDENCY")
    if lock.get("lockfileVersion") != npm["lockfileVersion"]:
        problems.append("LOCKFILE_FORMAT_DRIFT")
    rootPackage = lock.get("packages", {}).get("", {})
    if rootPackage.get("dependencies") != package.get("dependencies") or rootPackage.get("devDependencies") != package.get("devDependencies"):
        problems.append("LOCKFILE_PACKAGE_MISMATCH")
    forbidden = {"preinstall", "install", "postinstall", "prepare", "prepublish", "prepack", "postpack"}
    if any(name in package.get("scripts", {}) for name in forbidden):
        problems.append("NPM_LIFECYCLE_SCRIPT_UNEXPECTED")
    # Deep imports are essential; the Babylon barrel import previously made the demo ~7 MB.
    if 'from "@babylonjs/core"' in worldSource or "from '@babylonjs/core'" in worldSource:
        problems.append("BABYLON_BARREL_IMPORT_REGRESSION")
    if '@babylonjs/core/Engines/engine.js' not in worldSource:
        problems.append("BABYLON_DEEP_IMPORT_MISSING")
    if re.search(r"""<script[^>]+src\s*=\s*["'](?:https?:)?//""", html, re.I):
        problems.append("EXTERNAL_SCRIPT_NOT_ALLOWED")
    if re.search(r"""<link[^>]+href\s*=\s*["'](?:https?:)?//""", html, re.I):
        problems.append("EXTERNAL_STYLESHEET_NOT_ALLOWED")
    byLicense: Counter[str] = Counter()
    byDev: Counter[str] = Counter()
    missing = []
    installScripts = []
    packages = lock.get("packages", {})
    for name, record in sorted(packages.items()):
        if not name:
            continue
        if not isinstance(record, dict):
            problems.append("INVALID_PACKAGE_LOCK_RECORD")
            continue
        byLicense[str(record.get("license") or "UNKNOWN")] += 1
        byDev["buildTime" if record.get("dev") else "runtimeDeclared"] += 1
        if record.get("license") is None or record.get("integrity") is None:
            missing.append(name)
        if record.get("hasInstallScript"):
            installScripts.append(name)
        if not re.fullmatch(r"[0-9]+(?:\.[0-9]+){2}(?:[-+][A-Za-z0-9.+-]+)?", str(record.get("version") or "")):
            problems.append("UNPINNED_LOCKED_PACKAGE_VERSION")
    if not packages or len(packages) < 4:
        problems.append("LOCKFILE_INCOMPLETE")
    if missing:
        problems.append("MISSING_LOCK_INTEGRITY_OR_LICENSE_METADATA")
    metrics = {
        "lockedPackageRecords": max(0, len(packages) - 1),
        "declaredRuntimeOrPeerPackages": byDev.get("runtimeDeclared", 0),
        "buildTimePackageRecords": byDev.get("buildTime", 0),
        "licenseMetadata": dict(sorted(byLicense.items())),
        "packagesWithInstallScriptMetadata": installScripts,
        "missingLicenseOrIntegrity": missing,
        "note": "Lockfile metadata is an inventory, not an exploit/vulnerability or legal review."
    }
    return sorted(set(problems)), metrics

def inspectBuild(policy: dict, dist: Path | None) -> tuple[list[str], dict]:
    if dist is None:
        return [], {"status": "NOT_MEASURED", "runtimeBenchmarked": False}
    if not dist.is_dir() or not (dist / "index.html").is_file():
        return ["BUILD_DIRECTORY_OR_INDEX_MISSING"], {"status":"NOT_MEASURED", "runtimeBenchmarked":False}
    entries = []
    for path in sorted(dist.rglob("*")):
        if not path.is_file():
            continue
        if path.is_symlink():
            return ["SYMLINK_IN_BUNDLE"], {"status": "REJECTED"}
        data = path.read_bytes()
        if len(data) > 12_000_000:
            return ["UNEXPECTED_LARGE_ASSET"], {"status": "REJECTED"}
        entries.append({"asset": path.relative_to(dist).as_posix(), "bytes": len(data),
                        "sha256": sha256(data), "gzipBytes": len(gzip.compress(data, mtime=0))})
    js = [p for p in entries if p["asset"].endswith(".js")]
    css = [p for p in entries if p["asset"].endswith(".css")]
    main = [p for p in js if re.search(r"(?:^|/)index-[A-Za-z0-9_-]+\.js$", p["asset"])]
    problems = []
    budgets = policy["budgets"]
    if len(main) != 1 or main[0]["bytes"] > budgets["mainBundleJsBytesMax"]:
        problems.append("MAIN_JAVASCRIPT_SIZE_BUDGET")
    totalJs = sum(p["bytes"] for p in js)
    cssSize = sum(p["bytes"] for p in css)
    if totalJs > budgets["totalJavascriptBytesMax"]:
        problems.append("TOTAL_JAVASCRIPT_SIZE_BUDGET")
    if cssSize > budgets["cssBytesMax"]:
        problems.append("CSS_SIZE_BUDGET")
    return problems, {
        "status": "MEASURED_SOURCE_BUILD_ONLY", "runtimeBenchmarked": False,
        "mainJavaScriptBytes": main[0]["bytes"] if main else None,
        "mainJavaScriptGzipBytes": main[0]["gzipBytes"] if main else None,
        "totalJavaScriptBytes": totalJs, "totalCssBytes": cssSize,
        "assetCount":len(entries), "assets":entries
    }

def audit(dist: Path | None = None) -> dict:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    pkg = json.loads((PACKAGE / "package.json").read_text(encoding="utf-8"))
    lock = json.loads((PACKAGE / "package-lock.json").read_text(encoding="utf-8"))
    world = (PACKAGE / "src/babylon-world.js").read_text(encoding="utf-8")
    html = (PACKAGE / "index.html").read_text(encoding="utf-8")
    problems, dependencies = inspectDependencies(policy, pkg, lock, world, html)
    bundleProblems, bundle = inspectBuild(policy, dist)
    # Actual isolated-dependency pruning, without mutating the governed legacy frontEnd/jquery layer.
    if "node_modules/jquery" in lock.get("packages", {}):
        problems.append("ISOLATED_JQUERY_LOCK_REINTRODUCED")
    for local in ("src/jquery-bridge.js", "src/media-deck.js"):
        content = (PACKAGE / local).read_text(encoding="utf-8")
        if re.search(r"from\\s*[\\\"']jquery[\\\"']", content):
            problems.append("ISOLATED_JQUERY_IMPORT_REINTRODUCED:" + local)
        if "new CustomEvent(" not in content:
            problems.append("NATIVE_EVENT_BRIDGE_MISSING:" + local)
    problems.extend(bundleProblems)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False)
    return {
        "schema": "luhmOs.vendorReductionReceipt.v1",
        "identity": "LuHm-OS: Project Premonition",
        "sourceRef": head.stdout.strip() if head.returncode == 0 else None,
        "verdict":"RED_SOURCE" if problems else "AMBER_SOURCE_ONLY",
        "failures":sorted(set(problems)), "dependencies":dependencies, "build":bundle,
        "profiles":{k: "SOURCE_POLICY_ONLY" for k in policy["architectureProfiles"]},
        "androidPhysicalRuntime":"UNVERIFIED", "productionMediaEngine":"UNVERIFIED",
        "apkSigned":"UNVERIFIED", "crownStatus":"STOP"
    }

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist",type=Path,default=None,help="Read-only built web bundle directory")
    parser.add_argument("--output",type=Path,default=None,help="Write audit receipt JSON locally")
    args=parser.parse_args()
    receipt=audit(args.dist)
    payload=json.dumps(receipt,sort_keys=True,indent=2)+"\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload,encoding="utf-8")
    print(json.dumps({key:receipt[key] for key in ("sourceRef","verdict","failures","crownStatus")},sort_keys=True))
    return 2 if receipt["failures"] else 0

if __name__=="__main__":
    raise SystemExit(main())
