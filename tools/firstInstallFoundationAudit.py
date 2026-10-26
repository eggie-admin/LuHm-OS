#!/usr/bin/env python3
"""Four-foundation first-install source gate. Offline, no installs or privileged writes."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = "doctrine/firstInstallFoundationV1.json"

def validate_policy(p: dict) -> list[str]:
    errors: list[str] = []
    def need(ok: bool, code: str) -> None:
        if not ok:
            errors.append(code)
    need(p.get("schema") == "luhmOs.firstInstallFoundation.v1", "schema")
    need(p.get("status") == "SOURCE_AUDIT_CANDIDATE_NOT_INSTALLED", "notInstalled")
    groups = p.get("foundations", [])
    need([g.get("id") for g in groups] ==
         ["identity", "plugins", "architecture", "legalDocumentation"], "fourFoundations")
    need(all(g.get("source") and g.get("runtimeState") != "GREEN"
             for g in groups), "noFalseRuntimeGreen")
    topology = p.get("pluginTopology", {})
    need(topology.get("githubPackage", {}).get("sourceVersion") == "0.5.2", "packageVersion")
    need(topology.get("separateSite", {}).get("name") == "Project Hydra", "keepSeparateSite")
    need(topology.get("privateProviderDataStoredInPublicRepo") is False, "noPrivateData")
    legal = p.get("legal", {})
    need(legal.get("repoCodeLicense") == "GPL-3.0-only" and
         legal.get("preserveExistingLicense") is True, "preserveGpl")
    need(legal.get("doNotAssumeAllAssetsApproved") is True and
         legal.get("publicReleaseRequiresFileByFileClearance") is True, "rights")
    quality = p.get("quality", {})
    need(quality.get("sourceProofNotRuntimeProof") is True and
         quality.get("exactHeadRequired") is True, "proofBoundary")
    release = p.get("release", {})
    need(all(release.get(key) is False for key in (
         "automatedPluginPublish", "gitHubMainMutation", "cloudflareDnsChange",
         "renderDeploy", "secretWrite", "publicArtPublication")), "noPublicMutation")
    need(release.get("ownerApprovalRequiredForPromotion") is True and
         release.get("companyQuarantinePreserved") is True and
         release.get("crownStatus") == "STOP", "crownStop")
    return errors

def audit(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        policy = json.loads((root / CONTRACT).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return ["missingOrInvalidPolicy:" + type(exc).__name__]
    errors.extend(validate_policy(policy))
    for group in policy.get("foundations", []):
        for name in group.get("source", []):
            f = root / name
            if f.is_symlink() or not f.is_file() or f.stat().st_size == 0:
                errors.append("missingSource:" + name)
    extra = ["host/harness/jquery-LICENSE.txt",
             "host/harness/jquery-ui-LICENSE.txt",
             "plugins/luhm-os/assets/assetCatalog.json",
             ".github/workflows/frontend-jquery-dryrun.yml",
             ".github/workflows/in-chat-widget-evidence-gate.yml",
             ".github/workflows/manual-plugin-virgin-install-audit.yml",
             ".github/workflows/first-install-foundation-audit.yml",
             "tests/testFirstInstallFoundationAudit.py"]
    for name in extra:
        if not (root / name).is_file():
            errors.append("missingRequired:" + name)
    try:
        license_text = (root / "LICENSE").read_text(encoding="utf-8")
        manifest = json.loads((root / "plugins/luhm-os/plugin.json").read_text(encoding="utf-8"))
        npm = json.loads((root / "frontEnd/package.json").read_text(encoding="utf-8"))
        library = json.loads((root / "host/harness/libraryPolicy.json").read_text(encoding="utf-8"))
        art = json.loads((root / "plugins/luhm-os/assets/assetCatalog.json").read_text(encoding="utf-8"))
        if "GNU GENERAL PUBLIC LICENSE" not in license_text or "Version 3" not in license_text:
            errors.append("gplBody")
        if manifest.get("license") != "GPL-3.0-only" or manifest.get("version") != "0.5.2":
            errors.append("pluginLicenseVersion")
        if npm.get("dependencies", {}).get("jquery") != "3.7.1":
            errors.append("unpinnedJquery")
        if library.get("chatWidgetExternalCdnAllowed") is not False:
            errors.append("unreviewedRemoteScript")
        if not any(row.get("publicApproved") is False for row in art.get("files", [])):
            errors.append("unapprovedArtVisibility")
        for name in ("host/harness/jquery-LICENSE.txt", "host/harness/jquery-ui-LICENSE.txt"):
            if "OpenJS Foundation" not in (root / name).read_text(encoding="utf-8"):
                errors.append("missingVendoredNotice:" + name)
        if not (root / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8").startswith("# Third-party notices"):
            errors.append("noticeIndex")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append("dependencyInspection:" + type(exc).__name__)
    return sorted(set(errors))

if __name__ == "__main__":
    problems = audit()
    if problems:
        for problem in problems:
            print("RED_FIRST_INSTALL_SOURCE " + problem)
        raise SystemExit(1)
    print("GREEN_FIRST_INSTALL_SOURCE_ONLY fourFoundations=4")
    print("LIVE_PLUGIN_RENDER_CLOUDFLARE_ART_RIGHTS=UNVERIFIED")
    print("CROWN=STOP")
