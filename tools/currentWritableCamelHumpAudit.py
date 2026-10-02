#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

rootPath = Path(__file__).resolve().parents[1]
violations = []
camelHumpRx = re.compile(r"^[a-z][A-Za-z0-9]*$")
snakeNameRx = re.compile(r"\b[a-z][a-z0-9]*_[a-zA-Z0-9_]+\b")
pyDefRx = re.compile(r"^def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", re.M)
pyAssignRx = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=", re.M)
jsDeclRx = re.compile(r"\b(?:const|let|var)\s+([A-Za-z_$][A-Za-z0-9_$]*)")
shAssignRx = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=", re.M)

semanticIdKeys = {
    "agentId",
    "providerId",
    "workerId",
    "machineIdentity",
    "capabilityId",
    "taskId",
    "scopeId",
    "artifactId",
    "deploymentId",
    "boss",
    "dispatcher",
    "reportsTo",
}

externalUpperNames = {
    "GITHUB_ACTIONS",
    "DEBIAN_FRONTEND",
    "CMAKE_GENERATOR",
    "NINJA_STATUS",
    "GITHUB_ENV",
    "RUNNER_TEMP",
    "GITHUB_REPOSITORY",
    "GITHUB_ACTOR",
    "GH_TOKEN",
    "ANDROID_HOME",
    "JAVA_HOME",
}

def addViolation(kind: str, path: str, detail: str) -> None:
    violations.append({"kind": kind, "path": path, "detail": detail})

def getGitLines(*args: str) -> list[str]:
    try:
        out = subprocess.check_output(
            ["git", *args],
            cwd=rootPath,
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return [line.strip() for line in out.splitlines() if line.strip()]
    except Exception:
        return []

def isCamelHump(name: str) -> bool:
    return bool(camelHumpRx.fullmatch(name))

def isExternalBoundaryName(name: str) -> bool:
    return name in externalUpperNames or name.startswith("__")

def auditPython(relPath: str, text: str) -> None:
    for match in pyDefRx.finditer(text):
        fnName = match.group(1)
        if not isExternalBoundaryName(fnName) and not isCamelHump(fnName):
            addViolation("pythonFunctionNotCamelHump", relPath, fnName)

    for match in pyAssignRx.finditer(text):
        varName = match.group(1)
        if not isExternalBoundaryName(varName) and not isCamelHump(varName):
            addViolation("pythonVariableNotCamelHump", relPath, varName)

def auditJavascript(relPath: str, text: str) -> None:
    for match in jsDeclRx.finditer(text):
        varName = match.group(1)
        if not isCamelHump(varName):
            addViolation("javascriptVariableNotCamelHump", relPath, varName)

def auditShell(relPath: str, text: str) -> None:
    for match in shAssignRx.finditer(text):
        varName = match.group(1)
        if isExternalBoundaryName(varName):
            continue
        if not isCamelHump(varName):
            addViolation("shellVariableNotCamelHump", relPath, varName)

def auditJson(relPath: str, text: str) -> None:
    try:
        doc = json.loads(text)
    except Exception as exc:
        addViolation("invalidJson", relPath, str(exc))
        return

    def walk(value, keyPath=""):
        if isinstance(value, dict):
            for key, item in value.items():
                here = f"{keyPath}.{key}".lstrip(".")
                if key in semanticIdKeys and isinstance(item, str) and not isCamelHump(item):
                    addViolation("semanticMachineIdNotCamelHump", relPath, f"{here}={item}")
                walk(item, here)
        elif isinstance(value, list):
            for idx, item in enumerate(value):
                walk(item, f"{keyPath}[{idx}]")

    walk(doc)

addedFiles = getGitLines("diff", "--name-only", "--diff-filter=A", "origin/main...HEAD")
if not addedFiles:
    addedFiles = getGitLines("diff-tree", "--no-commit-id", "--name-only", "--diff-filter=A", "-r", "HEAD")

for relPath in addedFiles:
    fullPath = rootPath / relPath
    if not fullPath.is_file():
        continue

    fileStem = fullPath.name.rsplit(".", 1)[0]
    if relPath.startswith(("doctrine/", "tools/", "agents/", "frontEnd/jquery/")):
        if fullPath.name not in {"SKILL.md", "README.md"} and not isCamelHump(fileStem):
            addViolation("newWritableFileNotCamelHump", relPath, fileStem)

    if relPath.startswith("agents/") and len(fullPath.parts) > 1:
        agentDir = Path(relPath).parts[1]
        if not isCamelHump(agentDir):
            addViolation("agentDirectoryNotCamelHump", relPath, agentDir)

    text = fullPath.read_text(encoding="utf-8")
    if fullPath.suffix == ".py":
        auditPython(relPath, text)
    elif fullPath.suffix in {".js", ".mjs"}:
        auditJavascript(relPath, text)
    elif fullPath.suffix == ".sh":
        auditShell(relPath, text)
    elif fullPath.suffix == ".json":
        auditJson(relPath, text)

sealPath = rootPath / "doctrine/namingPathSealV1.json"
if sealPath.is_file():
    seal = json.loads(sealPath.read_text(encoding="utf-8"))
    namingLaw = seal.get("namingLaw", {})
    humanLaw = namingLaw.get("humanCenteredNaming", {})
    vowelLaw = namingLaw.get("vowelRip", {})
    boolLaw = namingLaw.get("booleanPhraseLaw", {})
    fnLaw = namingLaw.get("functionPhraseLaw", {})
    breadcrumbLaw = namingLaw.get("breadcrumbLaw", {})
    monitoring = seal.get("monitoring", {})

    if namingLaw.get("controlledNames") != "camelHump":
        addViolation("camelHumpLawMissing", "doctrine/namingPathSealV1.json", str(namingLaw.get("controlledNames")))
    if humanLaw.get("phraseFirst") is not True:
        addViolation("humanPhraseFirstLawMissing", "doctrine/namingPathSealV1.json", str(humanLaw))
    if vowelLaw.get("enabled") is not True or vowelLaw.get("readabilityWins") is not True:
        addViolation("vowelRipLawMissing", "doctrine/namingPathSealV1.json", str(vowelLaw))
    if boolLaw.get("required") is not True:
        addViolation("booleanPhraseLawMissing", "doctrine/namingPathSealV1.json", str(boolLaw))
    if fnLaw.get("required") is not True:
        addViolation("functionPhraseLawMissing", "doctrine/namingPathSealV1.json", str(fnLaw))
    if breadcrumbLaw.get("requiredWhenCompressed") is not True:
        addViolation("breadcrumbLawMissing", "doctrine/namingPathSealV1.json", str(breadcrumbLaw))
    if monitoring.get("urdDoctorGoddess", {}).get("role") != "structuralNamingPathology":
        addViolation("urdNamingMonitorMissing", "doctrine/namingPathSealV1.json", "urdDoctorGoddess")
    if monitoring.get("belldandySecretary", {}).get("role") != "canonicalNameLedger":
        addViolation("belldandyNamingMonitorMissing", "doctrine/namingPathSealV1.json", "belldandySecretary")

receipt = {
    "schema": "luhmOs.currentWritableCamelHumpAudit.v2",
    "status": "greenHumanCenteredCamelHump" if not violations else "redHumanCenteredCamelHump",
    "law": "humanPhrase -> readableVowelRip -> camelHump -> booleanPredicates -> actionFunctions -> breadcrumbs",
    "addedFilesChecked": addedFiles,
    "watchers": {
        "urdDoctorGoddess": "structuralNamingPathology",
        "belldandySecretary": "canonicalNameLedger",
    },
    "violations": violations,
    "crownStatus": "stop",
}
print(json.dumps(receipt, indent=2))
raise SystemExit(1 if violations else 0)
