#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

root_path = Path(__file__).resolve().parents[1]
errors = []
lower_camel = re.compile(r"^[a-z][A-Za-z0-9]*$")
safe_workflow_name = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*\.ya?ml$")

semantic_id_keys = {
    "agentId",
    "providerId",
    "workerId",
    "machineIdentity",
    "capabilityId",
    "boss",
    "dispatcher",
    "reportsTo",
}

def add(kind: str, path: str, detail: str) -> None:
    errors.append({"kind": kind, "path": path, "detail": detail})

def git_lines(*args: str) -> list[str]:
    try:
        out = subprocess.check_output(
            ["git", *args],
            cwd=root_path,
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return [line.strip() for line in out.splitlines() if line.strip()]
    except Exception:
        return []

added = git_lines("diff", "--name-only", "--diff-filter=A", "origin/main...HEAD")
if not added:
    added = git_lines("diff-tree", "--no-commit-id", "--name-only", "--diff-filter=A", "-r", "HEAD")

for rel in added:
    path = Path(rel)

    # LuHm agent directories are semantic machine identities.
    if rel.startswith("agents/") and len(path.parts) > 1:
        agent_dir = path.parts[1]
        if not lower_camel.fullmatch(agent_dir):
            add("agentDirectorySemanticIdDrift", rel, agent_dir)

    # GitHub workflow filenames may use native kebab, camelHump, dots, or underscores.
    if rel.startswith(".github/workflows/"):
        if not safe_workflow_name.fullmatch(path.name):
            add("unsafeWorkflowFilename", rel, path.name)

    full = root_path / rel
    if not full.is_file() or full.suffix != ".json":
        continue

    try:
        doc = json.loads(full.read_text(encoding="utf-8"))
    except Exception as exc:
        add("invalidJson", rel, str(exc))
        continue

    def walk(value, key_path=""):
        if isinstance(value, dict):
            for key, item in value.items():
                here = f"{key_path}.{key}".lstrip(".")
                if key in semantic_id_keys and isinstance(item, str):
                    # External protocol-owned IDs are excluded by schema; these keys are LuHm-owned.
                    if not lower_camel.fullmatch(item):
                        add("semanticMachineIdNotCamelHump", rel, f"{here}={item}")
                walk(item, here)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, f"{key_path}[{index}]")

    walk(doc)

seal_path = root_path / "doctrine/namingPathSealV1.json"
if seal_path.is_file():
    seal = json.loads(seal_path.read_text(encoding="utf-8"))
    naming = seal.get("namingLaw", {})
    profiles = naming.get("conventionProfiles", {})
    monitoring = seal.get("monitoring", {})
    urd = monitoring.get("urdDoctorGoddess", {})
    belldandy = monitoring.get("belldandySecretary", {})

    if naming.get("semanticMachineIds") != "lowerCamelHumpPreferred":
        add("semanticNamingLawDrift", str(seal_path.relative_to(root_path)), str(naming.get("semanticMachineIds")))
    if profiles.get("pythonFunctionsAndLocals") != "snake_caseAllowed":
        add("pythonConventionMissing", str(seal_path.relative_to(root_path)), str(profiles.get("pythonFunctionsAndLocals")))
    if profiles.get("pythonConstants") != "UPPER_SNAKE_ALLOWED":
        add("pythonConstantConventionMissing", str(seal_path.relative_to(root_path)), str(profiles.get("pythonConstants")))
    if profiles.get("shellEnvironment") != "UPPER_SNAKE_ALLOWED":
        add("shellEnvironmentConventionMissing", str(seal_path.relative_to(root_path)), str(profiles.get("shellEnvironment")))
    if profiles.get("githubWorkflowFiles") != "kebab-case-or-camelHump-allowed":
        add("workflowConventionMissing", str(seal_path.relative_to(root_path)), str(profiles.get("githubWorkflowFiles")))
    if urd.get("role") != "structuralNamingPathology":
        add("urdMonitorMissing", str(seal_path.relative_to(root_path)), str(urd))
    if belldandy.get("role") != "canonicalNameLedger":
        add("belldandyMonitorMissing", str(seal_path.relative_to(root_path)), str(belldandy))

receipt = {
    "schema": "luhmOs.currentWritableNamingConventionAudit.v1",
    "status": "greenCurrentWritableNamingConventions" if not errors else "redCurrentWritableNamingConventions",
    "addedFilesChecked": added,
    "policy": {
        "semanticMachineIds": "lowerCamelHumpPreferred",
        "python": "languageNative",
        "shell": "languageNative",
        "githubWorkflows": "kebab-or-camel-allowed",
        "vendorSchemas": "preserveExternal",
    },
    "watchers": {
        "urdDoctorGoddess": "structuralNamingPathology",
        "belldandySecretary": "canonicalNameLedger",
    },
    "legacyAuditFilenameRetained": True,
    "cosmeticRenameChurnForbidden": True,
    "errors": errors,
    "crownStatus": "stop",
}
print(json.dumps(receipt, indent=2))
raise SystemExit(1 if errors else 0)
