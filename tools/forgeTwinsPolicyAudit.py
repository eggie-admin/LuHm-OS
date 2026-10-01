#!/usr/bin/env python3
import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []
warnings = []


def require(value, message):
    if not value:
        errors.append(message)


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"cannot parse {path.relative_to(ROOT)}: {exc}")
        return {}


contract_path = ROOT / "doctrine" / "FORGE_TWINS_V3.json"
ttl_path = ROOT / "doctrine" / "FORGE_TTL_POLICY_V1.json"
shared_skill_path = ROOT / "agents" / "buildOnis" / "SKILL.md"
source_skill_path = ROOT / "agents" / "buildOnis" / "sourceForge" / "SKILL.md"
compile_skill_path = ROOT / "agents" / "buildOnis" / "compileForge" / "SKILL.md"
cast_gate_path = ROOT / "tools" / "forgeCastGate.py"
janitor_path = ROOT / "tools" / "forgeWorkspaceJanitor.py"

for path in [contract_path, ttl_path, shared_skill_path, source_skill_path, compile_skill_path, cast_gate_path, janitor_path]:
    require(path.is_file(), f"missing required Forge file: {path.relative_to(ROOT)}")

contract = load_json(contract_path) if contract_path.exists() else {}
ttl = load_json(ttl_path) if ttl_path.exists() else {}
shared = shared_skill_path.read_text(encoding="utf-8") if shared_skill_path.exists() else ""
source_skill = source_skill_path.read_text(encoding="utf-8") if source_skill_path.exists() else ""
compile_skill = compile_skill_path.read_text(encoding="utf-8") if compile_skill_path.exists() else ""
cast_gate = cast_gate_path.read_text(encoding="utf-8") if cast_gate_path.exists() else ""
janitor = janitor_path.read_text(encoding="utf-8") if janitor_path.exists() else ""

require(contract.get("status") == "PROPOSED_CANDIDATE", "Forge contract must remain PROPOSED_CANDIDATE")
require(contract.get("crownStatus") == "STOP", "Forge contract must remain CROWN=STOP")
require(contract.get("authority") == "Professor", "Professor must remain final authority")
require(contract.get("operationLaw") == "PROTECT != INGEST != MUTATE != CAST != JANITOR", "Forge operation separation law drift")

cast = contract.get("castEnvelope", {})
require(cast.get("castWord") == "cast", "CAST word must be exact 'cast'")
require(cast.get("authorizedBy") == "Professor", "CAST authority must remain Professor")
require(cast.get("persistentAuthorizationAllowed") is False, "standing CAST authorization is forbidden")
require(cast.get("consumedOnAttempt") is True, "CAST must be consumed on build attempt")
require(int(cast.get("defaultTtlMinutes", 0)) <= 30, "CAST envelope TTL may not exceed 30 minutes by default")
require(bool(cast.get("authorizedGitHubActors")), "authorizedGitHubActors must be explicit")

for phrase in [
    "PROTECT != INGEST != MUTATE != CAST != JANITOR",
    "The word `cast` is the only Professor phrase that authorizes a build milestone.",
    "A failed build consumes the Cast Envelope.",
    "Automatic PR/push workflows may perform read-only/static protection audits, but they must not compile/export/package before CAST.",
    "Dr. Nao remains the anti-hallucination truth guard.",
]:
    require(phrase in shared, f"shared Forge skill missing required law: {phrase}")

require("buildAuthority: `NONE`" in source_skill, "Source Forge must have zero build authority")
require("preCastBuildAuthority: `NONE`" in compile_skill, "Compile Forge must have zero pre-CAST build authority")
require("Synonyms and implied approval are invalid." in compile_skill, "Compile Forge must reject implied CAST")

for path, text in [(cast_gate_path, cast_gate), (janitor_path, janitor)]:
    try:
        ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        errors.append(f"Python syntax error in {path.relative_to(ROOT)}: {exc}")

require("FORGE_CAST_GATE=DENIED" in cast_gate, "CAST gate must fail closed")
require("args.source_ref != args.actual_source_ref" in cast_gate, "CAST gate must bind exact sourceRef")
require("authorizedGitHubActors" in cast_gate, "CAST gate must enforce explicit GitHub actor allowlist")

require(ttl.get("janitorAuthority") == "TEMPORARY_FORGE_PATHS_ONLY", "janitor authority drift")
never = set(ttl.get("neverAutoDeleteClasses", []))
for cls in ["source", "canonical", "evidenceReceipt", "backup", "snapshot", "release", "promotedArtifact", "signingMaterial"]:
    require(cls in never, f"TTL policy must protect class {cls}")
require(ttl.get("sentinelName") == ".luhm-forge-root.json", "Forge sentinel drift")
for phrase in ["is_symlink", "missing Forge root sentinel", "filesystem/home/repository root is forbidden", "REFUSED_PATH_ESCAPE"]:
    require(phrase in janitor, f"janitor missing safety control: {phrase}")

cast_workflows = {
    ".github/workflows/android-testing-build.yml": "android-testing-apk",
    ".github/workflows/godot-web-harness.yml": "godot-web-harness",
    ".github/workflows/lumrigv2-phase1.yml": "lumrigv2-phase1",
}
for rel, scope in cast_workflows.items():
    path = ROOT / rel
    require(path.is_file(), f"missing CAST-gated workflow: {rel}")
    if not path.is_file():
        continue
    text = path.read_text(encoding="utf-8")
    require("workflow_dispatch:" in text, f"{rel} must be manual workflow_dispatch")
    require("pull_request:" not in text, f"{rel} must not auto-build on pull_request")
    require(re.search(r"(?m)^\s*push:\s*$", text) is None, f"{rel} must not auto-build on push")
    require("forgeCastGate.py" in text, f"{rel} must invoke Forge CAST gate")
    require("${{ inputs.cast }}" in text, f"{rel} must bind explicit CAST input")
    require("${{ inputs.sourceRef }}" in text, f"{rel} must bind exact sourceRef input")
    require(scope in text, f"{rel} CAST scope mismatch")
    for match in re.finditer(r"retention-days:\s*(\d+)", text):
        require(int(match.group(1)) <= 3, f"{rel} remote build artifact retention exceeds 72h")

# Search all workflows for obvious build-producing primitives. Any matching workflow must be CAST gated.
patterns = [
    "--export-debug",
    "--export-release",
    "buildGodotWebHarness.sh",
    "gradlew assemble",
    "gradlew bundle",
    "npm run build",
    "pnpm build",
    "yarn build",
    "cargo build",
    "cmake --build",
    "docker build",
]
for path in sorted((ROOT / ".github" / "workflows").glob("*.y*ml")):
    text = path.read_text(encoding="utf-8")
    if any(pattern.lower() in text.lower() for pattern in patterns):
        rel = str(path.relative_to(ROOT))
        require("forgeCastGate.py" in text, f"build-producing workflow lacks CAST gate: {rel}")
        require("pull_request:" not in text, f"build-producing workflow has pull_request trigger: {rel}")
        require(re.search(r"(?m)^\s*push:\s*$", text) is None, f"build-producing workflow has push trigger: {rel}")

status = "GREEN" if not errors else "RED"
print(f"FORGE_TWINS_POLICY_AUDIT={status}")
print(f"errors={len(errors)} warnings={len(warnings)}")
for error in errors:
    print("ERROR:", error)
for warning in warnings:
    print("WARN:", warning)
print("NOTE: GREEN proves only static Forge policy separation and CAST-gating. It does not authorize or execute a build, mutate main, or grant release/deploy/Crown authority.")
sys.exit(0 if not errors else 2)
