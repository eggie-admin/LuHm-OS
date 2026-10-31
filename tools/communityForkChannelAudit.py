#!/usr/bin/env python3
"""Read-only LuHm community fork, channel and vendor-source contract checker."""
import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = "doctrine/communityForkChannelsV1.json"
SHA = re.compile(r"^[0-9a-f]{40}$")
VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[.\-][0-9A-Za-z.\-]+)?$")

def evaluate(policy, root=ROOT):
    errors = []
    def require(test, code):
        if not test:
            errors.append(code)
    require(policy.get("schema") == "luhmOs.communityForkChannels.v1", "SCHEMA")
    require(policy.get("state") == "SOURCE_CANDIDATE" and policy.get("crown") == "STOP", "FALSE_CROWN")
    require(policy.get("repository") == "eggie-admin/LuHm-OS", "REPOSITORY")
    require(policy.get("rootLicense") == "GPL-3.0-only", "ROOT_LICENSE")
    for key in ("autoForkVendors", "autoMerge", "autoRelease", "autoDeploy", "autoSign", "autoUnquarantine",
                "sourceIsNotInstallableBinary"):
        require(policy.get(key) is (key == "sourceIsNotInstallableBinary"), "UNSAFE_" + key)
    for key in ("publicSourceForking", "noPrivateAssetsInPublicForks", "officialNameDoesNotAuthorizeImpersonation"):
        require(policy.get(key) is True, "UNSAFE_" + key)
    for key in ("publicationApproved", "securitySettingsLiveVerified", "deviceRuntimeVerified",
                "upstreamLicensesIndividuallyVerified", "providerEntitlementsVerified"):
        require(policy.get(key) is False, "FALSE_PROOF_" + key)
    require(policy.get("vendorForksCreated") == 0, "FAKE_FORKS")
    channels = policy.get("channels", [])
    require([c.get("id") for c in channels] == ["proposed", "beta", "stable"], "CHANNEL_ORDER")
    for channel in channels:
        require(channel.get("sourceForkable") is True, "NOT_FORKABLE")
        require(channel.get("publication") == ("SOURCE_ONLY" if channel.get("id") == "proposed" else "BLOCKED"),
                "RELEASE_LANE_BYPASS")
        require(channel.get("signedRuntimeProof") is False and channel.get("signerVerified") is False,
                "FALSE_SIGNING_PROOF")
    require(len(set(policy.get("forkRequirements", []))) >= 8, "INCOMPLETE_FORK_REVIEW")
    require("noPrivatePayload" in policy.get("forkRequirements", []), "PRIVATE_DATA_GATE_MISSING")
    for optional in policy.get("optionalVendors", []):
        require(optional.get("sourceProven") is False and optional.get("customNodeExecutionAllowed") is False,
                "OPTIONAL_UNTRUSTED_EXECUTION")
    pins = policy.get("vendorPins", [])
    require(len(pins) == 7, "PIN_COUNT_DRIFT")
    seen = set()
    for pin in pins:
        ident = (pin.get("manifest"), pin.get("name"), pin.get("ecosystem"))
        require(ident not in seen, "DUPLICATE_PIN")
        seen.add(ident)
        rel = pin.get("manifest", "")
        require(isinstance(rel, str) and rel and not Path(rel).is_absolute()
                and ".." not in Path(rel).parts, "MANIFEST_PATH_ESCAPE")
        p = (root / rel).resolve()
        require(p.is_relative_to(root.resolve()) and p.is_file(), "MISSING_MANIFEST:" + rel)
        ver = pin.get("version", "")
        require(isinstance(ver, str) and VERSION.fullmatch(ver) is not None, "NONEXACT_PIN:" + str(ident))
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf8")
        if pin.get("ecosystem") == "npm":
            package = json.loads(text)
            actual = package.get("dependencies", {}).get(pin["name"],
                       package.get("devDependencies", {}).get(pin["name"]))
            require(actual == ver, "NPM_PIN_DRIFT:" + pin["name"])
        elif pin.get("ecosystem") == "pip":
            require(re.search(r"(?m)^" + re.escape(pin["name"]) + r"==" +
                              re.escape(ver) + r"\s*$", text) is not None, "PIP_PIN_DRIFT")
        elif pin.get("ecosystem") == "gradle":
            require("implementation(\"" + pin["name"] + ":" + ver + "\")" in text, "GRADLE_PIN_DRIFT")
        else:
            errors.append("UNKNOWN_ECOSYSTEM")
    security = (root / "SECURITY.md").read_text(encoding="utf8")
    contributing = (root / "CONTRIBUTING.md").read_text(encoding="utf8")
    license_text = (root / "LICENSE").read_text(encoding="utf8")
    require("Security Advisories" in security and "private" in security.lower(), "SECURITY_CHANNEL_MISSING")
    require("fork" in contributing.lower() and "private" in contributing.lower(), "FORK_DOC_MISSING")
    require("GNU GENERAL PUBLIC LICENSE" in license_text, "LICENSE_DRIFT")
    return sorted(set(errors))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-ref", required=True)
    args = ap.parse_args()
    if not SHA.fullmatch(args.source_ref):
        raise SystemExit("EXACT_SOURCE_SHA_REQUIRED")
    current = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    if current.returncode != 0 or current.stdout.strip() != args.source_ref:
        raise SystemExit("EXACT_GIT_HEAD_MISMATCH")
    policy = json.loads((ROOT / POLICY).read_text(encoding="utf8"))
    errors = evaluate(policy)
    report = {"schema":"luhmOs.communityForkReceipt.v1","sourceRef":args.source_ref,
              "sourceAudit":"PASS" if not errors else "RED","errors":errors,
              "sourceForkable":True,"vendorForksCreated":0,"securitySettingsLiveVerified":False,
              "packagePublished":False,"runtimeProven":False,"releaseApproved":False,"crown":"STOP"}
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
