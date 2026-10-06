#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine" / "WITCHING_HOUR_HARD_AUDIT_V2.json"
RECEIPT = ROOT / "doctrine" / "WITCHING_HOUR_HARD_AUDIT_RECEIPT_20261001.json"

errors: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def load(path: Path, label: str) -> dict:
    require(path.is_file(), f"missing {label}")
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid {label}: {exc}")
        return {}
    require(isinstance(value, dict), f"{label} must be a JSON object")
    return value if isinstance(value, dict) else {}


def main() -> int:
    data = load(CONTRACT, "Witching Hour hard-audit v2 contract")
    receipt = load(RECEIPT, "Witching Hour hard-audit receipt")
    if errors:
        return finish()

    require(data.get("schema") == "luhm.witching-hour.hard-audit.v2", "schema mismatch")
    require(data.get("status") == "PROPOSED_CANDIDATE", "candidate status required")
    require(data.get("crownStatus") == "STOP", "Crown must remain STOP")
    require(data.get("authority") == "Professor", "Professor authority required")
    require(data.get("projectGoal") == "LuHm OS", "LuHm OS project goal required")
    require(data.get("workingTitle") == "Project Hydra", "Project Hydra working title required")
    require(data.get("openAiAgent") == "Lum", "Lum OpenAI agent identity required")
    require(data.get("codingRoleplaySystem") == "Witching Hour", "Witching Hour coding-roleplay identity required")
    require(data.get("castIssued") is False, "CAST must not be pre-issued")
    require(data.get("buildAuthority") is False, "hard audit must not carry build authority")

    enterprise = data.get("enterpriseDefault", {})
    require(enterprise.get("mode") == "ENTERPRISE_DEFAULT_UNLESS_RED", "enterprise default mode drift")
    require(enterprise.get("defaultEnabled") is True, "enterprise mode must default on")
    require(enterprise.get("readinessClaimRequiresEvidence") is True, "enterprise readiness must remain evidence-gated")
    require(enterprise.get("amberBehavior") == "CONTINUE_ENTERPRISE_DESIGN_WITHOUT_CLAIMING_PROOF", "AMBER enterprise behavior drift")
    require(enterprise.get("unknownBehavior") == "CONTINUE_ENTERPRISE_DESIGN_AND_OPEN_EVIDENCE_GATE", "UNKNOWN enterprise behavior drift")
    require(enterprise.get("redBehavior") == "BLOCK_AFFECTED_CAPABILITY_AND_REQUIRE_REMEDIATION", "RED enterprise behavior drift")
    require(enterprise.get("automaticFallbackToNonEnterprise") is False, "non-enterprise fallback cannot be automatic")
    require(enterprise.get("nonEnterpriseFallbackRequiresProfessorAuthorization") is True, "non-enterprise fallback must require Professor authorization")
    require(enterprise.get("redDoesNotEraseUnrelatedEnterpriseControls") is True, "one RED gate cannot disable unrelated enterprise controls")
    required_enterprise_domains = {
        "architecture", "security", "identity_and_permissions", "source_governance",
        "ci_and_build_governance", "signing_design", "distribution_design",
        "managed_install_design", "update_and_rollback_design", "device_enrollment_design",
        "audit_and_evidence", "supply_chain", "backup_and_restore", "secrets_management",
        "least_privilege",
    }
    require(set(enterprise.get("appliesTo", [])) == required_enterprise_domains, "enterprise default domain set drift")

    bb = data.get("bigBrother", {})
    require(bb.get("surface") == "GOOGLE_AI_EDGE_GALLERY_IN_SAMSUNG_SECURE_FOLDER", "Big Brother must be Edge Gallery Secure Folder lane")
    require(bb.get("environmentState") == "SOURCE_DERIVED_GREEN", "Secure Folder Edge Gallery environment must preserve source-derived GREEN scope")
    require(bb.get("modelRuntime") == "UNKNOWN_UNTIL_EXACT_DEVICE_RECEIPT", "model/runtime must remain UNKNOWN until receipted")
    require(bb.get("entitlementProgram") == "UNKNOWN_UNTIL_EXACT_RECEIPT", "entitlement must remain UNKNOWN until receipted")
    require(bb.get("galleryToLuhmIntegration") == "UNKNOWN_UNTIL_DEVICE_SIDE_TOOL_RESULT_RECEIPT", "Gallery→LuHm integration must remain separately receipted")
    require(bb.get("auditOutput") == "UNKNOWN_UNTIL_ACTUAL_EDGE_GALLERY_REVIEW_RECEIPT", "review output must require its own receipt")
    require(bb.get("secureFolderIsolationMustRemain") is True, "Secure Folder isolation must remain mandatory")

    for reviewer in (bb, data.get("copilot", {})):
        for field in ("approvalAuthority", "mergeAuthority", "publishAuthority", "deployAuthority", "signAuthority", "crownAuthority"):
            require(reviewer.get(field) is False, f"reviewer authority leak: {field}")

    doctor = data.get("doctorOni", {})
    require(doctor.get("role") == "ANTI_HALLUCINATION_TRUTH_ADJUDICATOR", "Dr. Nao role drift")
    require(doctor.get("reviewPrestigeIsEvidence") is False, "reviewer prestige cannot become evidence")
    require(doctor.get("memoryIsMutableStateProof") is False, "memory cannot prove mutable state")
    require(doctor.get("enterpriseDefaultIsEnterpriseReadyProof") is False, "enterprise default cannot be treated as readiness proof")

    secretary = data.get("secretaryOni", {})
    require(secretary.get("mustPreserveContradictions") is True, "Secretary must preserve contradictions")
    require(secretary.get("mustSeparateEnvironmentFromIntegration") is True, "Secretary must separate environment from integration")
    require(secretary.get("mustTrackEnterpriseGateStateSeparately") is True, "Secretary must track enterprise gate states separately")

    forge = data.get("forge", {})
    require(forge.get("law") == "PROTECT != INGEST != MUTATE != CAST != JANITOR", "Forge operation separation drift")
    require(forge.get("compileRequiresProfessorCast") is True, "compile must require Professor CAST")
    require(forge.get("castPresent") is False, "candidate must not claim CAST present")
    require(forge.get("enterpriseBuildControlsDefault") is True, "Forge enterprise build controls must default on")

    passes = data.get("tenPasses", [])
    require(isinstance(passes, list) and len(passes) == 10, "exactly ten audit passes required")
    require(len(set(passes)) == 10, "audit passes must be unique")

    separation = data.get("pass5RequiredSeparation", [])
    expected = {
        "SECURE_FOLDER_EDGE_GALLERY_ENVIRONMENT",
        "EDGE_GALLERY_MODEL_RUNTIME",
        "EDGE_GALLERY_ENTITLEMENTS",
        "EDGE_GALLERY_TO_LUHM_INTEGRATION",
        "BIG_BROTHER_AUDIT_OUTPUT",
    }
    require(set(separation) == expected, "Edge Gallery proof boundaries collapsed")

    target = data.get("enterpriseTarget", {})
    require(target.get("device") == "Samsung Galaxy S24 FE", "enterprise device target drift")
    require(target.get("os") == "Android 16", "enterprise OS target drift")
    require(target.get("root") is False, "enterprise target must remain unrooted")
    require(target.get("endUserDeveloperToolDependency") is False, "final target cannot depend on end-user developer tooling")
    require(target.get("architectureDefault") == "ENTERPRISE", "enterprise architecture must be the default target")

    automation = data.get("automation", {})
    require(automation.get("staticAuditAllowed") is True, "static audit should be allowed")
    for field in ("repoMutationAllowed", "buildAllowed", "artifactProductionAllowed", "deploymentAllowed", "publicationAllowed", "signingAllowed", "crownAllowed"):
        require(automation.get(field) is False, f"hard-audit automation authority leak: {field}")

    hard_stops = set(data.get("hardStops", []))
    for required_stop in (
        "BIG_BROTHER_ENVIRONMENT_TREATED_AS_COMPLETED_AUDIT",
        "EDGE_GALLERY_INSTALL_TREATED_AS_LUHM_INTEGRATION",
        "UNKNOWN_MODEL_OR_ENTITLEMENT_INVENTED",
        "SECURE_FOLDER_ISOLATION_WEAKENED",
        "ENTERPRISE_DEFAULT_TREATED_AS_ENTERPRISE_READY_PROOF",
        "AMBER_OR_UNKNOWN_USED_TO_SILENTLY_FALL_BACK_TO_NON_ENTERPRISE",
        "RED_ENTERPRISE_GATE_IGNORED",
        "BUILD_WITHOUT_EXACT_PROFESSOR_CAST",
        "UNSCOPED_GREEN",
    ):
        require(required_stop in hard_stops, f"missing hard stop: {required_stop}")

    require(receipt.get("schema") == "luhm.witching-hour.hard-audit-receipt.v2", "receipt schema mismatch")
    require(receipt.get("status") == "AMBER_HARD_AUDIT_BLOCKERS_REMAIN", "receipt must preserve broader AMBER state")
    require(receipt.get("crownStatus") == "STOP", "receipt Crown must remain STOP")
    require(receipt.get("authority") == "Professor", "receipt Professor authority required")
    require(receipt.get("baseCanonicalMain") == data.get("baseCanonicalMain"), "contract/receipt canonical main mismatch")
    require(receipt.get("castPresent") is False, "receipt cannot claim CAST")
    require(receipt.get("buildExecutedByThisAudit") is False, "static audit cannot claim build execution")

    receipt_enterprise = receipt.get("enterprisePolicy", {})
    require(receipt_enterprise.get("mode") == "ENTERPRISE_DEFAULT_UNLESS_RED", "receipt enterprise mode drift")
    require(receipt_enterprise.get("defaultEnabled") is True, "receipt must keep enterprise default on")
    require(receipt_enterprise.get("currentEnterpriseReadiness") == "AMBER_NOT_PROVEN", "enterprise readiness should remain AMBER, not default GREEN")
    require(receipt_enterprise.get("automaticFallbackToNonEnterprise") is False, "receipt cannot authorize automatic non-enterprise fallback")

    rb = receipt.get("reviewers", {}).get("bigBrother", {})
    require(rb.get("surface") == "GOOGLE_AI_EDGE_GALLERY_IN_SAMSUNG_SECURE_FOLDER", "receipt Big Brother surface drift")
    require(rb.get("environment") == "SOURCE_DERIVED_GREEN", "receipt must preserve source-derived environment scope")
    for field in ("modelRuntime", "entitlementProgram", "galleryToLuhmIntegration", "currentAuditOutput"):
        require(rb.get(field) == "UNKNOWN", f"receipt must keep {field} UNKNOWN until direct receipt")
    require(rb.get("signoff") == "NOT_CLAIMED", "Big Brother signoff cannot be invented")

    result_passes = receipt.get("passes", [])
    require(isinstance(result_passes, list) and len(result_passes) == 10, "receipt must contain ten pass results")
    ids = [item.get("id") for item in result_passes if isinstance(item, dict)]
    require(ids == list(range(1, 11)), "receipt pass IDs must be 1..10 in order")
    statuses = {item.get("id"): item.get("status") for item in result_passes if isinstance(item, dict)}
    require(statuses.get(7) == "RED", "canonical Forge/CAST mismatch must remain RED")
    require(statuses.get(9) == "AMBER", "enterprise path should remain default under incomplete evidence, not be marked RED")
    require(all(value in {"GREEN", "AMBER", "RED", "UNKNOWN"} for value in statuses.values()), "invalid pass status")

    require(receipt.get("verdict") == "WITCHING_HOUR_ENTERPRISE_DEFAULT_STATIC_GREEN_BROADER_MILESTONE_AMBER_WITH_RED_FORGE_GATE", "receipt verdict drift")

    return finish()


def finish() -> int:
    if errors:
        print("WITCHING_HOUR_HARD_AUDIT_V2=RED")
        for error in errors:
            print(f"ERROR={error}")
        print("crown=STOP")
        return 1

    print("WITCHING_HOUR_HARD_AUDIT_V2=GREEN")
    print("scope=static-policy-and-receipt-consistency-only")
    print("enterpriseDefault=ON_UNLESS_RED")
    print("enterpriseReadiness=AMBER_NOT_PROVEN")
    print("edgeGalleryEnvironment=SOURCE_DERIVED_GREEN")
    print("galleryToLuhmIntegration=UNKNOWN")
    print("modelRuntime=UNKNOWN")
    print("entitlementProgram=UNKNOWN")
    print("bigBrotherAuditOutput=UNKNOWN")
    print("canonicalForgeCastGate=RED")
    print("cast=NOT_ISSUED")
    print("build=NOT_AUTHORIZED")
    print("crown=STOP")
    return 0


if __name__ == "__main__":
    sys.exit(main())
