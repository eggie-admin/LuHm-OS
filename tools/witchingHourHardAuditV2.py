#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "doctrine" / "WITCHING_HOUR_HARD_AUDIT_V2.json"

errors: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    require(CONTRACT.is_file(), "missing Witching Hour hard-audit v2 contract")
    if errors:
        return finish()

    data = json.loads(CONTRACT.read_text(encoding="utf-8"))

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

    secretary = data.get("secretaryOni", {})
    require(secretary.get("mustPreserveContradictions") is True, "Secretary must preserve contradictions")
    require(secretary.get("mustSeparateEnvironmentFromIntegration") is True, "Secretary must separate environment from integration")

    forge = data.get("forge", {})
    require(forge.get("law") == "PROTECT != INGEST != MUTATE != CAST != JANITOR", "Forge operation separation drift")
    require(forge.get("compileRequiresProfessorCast") is True, "compile must require Professor CAST")
    require(forge.get("castPresent") is False, "candidate must not claim CAST present")

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
        "BUILD_WITHOUT_EXACT_PROFESSOR_CAST",
        "UNSCOPED_GREEN",
    ):
        require(required_stop in hard_stops, f"missing hard stop: {required_stop}")

    return finish()


def finish() -> int:
    if errors:
        print("WITCHING_HOUR_HARD_AUDIT_V2=RED")
        for error in errors:
            print(f"ERROR={error}")
        print("crown=STOP")
        return 1

    print("WITCHING_HOUR_HARD_AUDIT_V2=GREEN")
    print("scope=static-policy-contract-only")
    print("edgeGalleryEnvironment=SOURCE_DERIVED_GREEN")
    print("galleryToLuhmIntegration=UNKNOWN")
    print("modelRuntime=UNKNOWN")
    print("entitlementProgram=UNKNOWN")
    print("cast=NOT_ISSUED")
    print("build=NOT_AUTHORIZED")
    print("crown=STOP")
    return 0


if __name__ == "__main__":
    sys.exit(main())
