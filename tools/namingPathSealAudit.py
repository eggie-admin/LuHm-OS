#!/usr/bin/env python3
import json
import pathlib
import re
import sys

rootPath = pathlib.Path(__file__).resolve().parents[1]
sealPath = rootPath / "doctrine/namingPathSealV1.json"
sealDoc = json.loads(sealPath.read_text())
violations = []

def addViolation(kind, path, detail=None):
    row = {"kind": kind, "path": path}
    if detail is not None:
        row["detail"] = detail
    violations.append(row)

for relPath in sealDoc["sealedPaths"]:
    if not (rootPath / relPath).exists():
        addViolation("missingSealedPath", relPath)

controlledPaths = [
    "agents/yumeArtOni",
    "agents/sumiAssetOni",
    "agents/belldandyQualityOni",
    "agents/shioriCriticOni",
    "doctrine/artOniLayeredMutationV3.json",
    "doctrine/namingPathSealV1.json",
    "doctrine/rootedTermuxGitHubReleaseInstallV1.json",
    "doctrine/smX400OneBashInstallSealV1.json",
    "tools/artOniCamelHumpAudit.py",
    "tools/namingPathSealAudit.py",
    "tools/smX400OneBashInstall.sh",
    "tools/smX400OneBashInstallAudit.py",
]

snakeStemRx = re.compile(r"^[A-Za-z0-9.-]*_[A-Za-z0-9_.-]+$")
screamStemRx = re.compile(r"^[A-Z0-9]+(?:_[A-Z0-9]+)+")
camelHumpRx = re.compile(r"^[a-z][A-Za-z0-9]*$")

for relPath in controlledPaths:
    fileName = pathlib.PurePosixPath(relPath).name
    fileStem = fileName.rsplit(".", 1)[0]
    if snakeStemRx.match(fileStem) or screamStemRx.match(fileStem):
        addViolation("nonCamelHumpControlledName", relPath)

agentsPath = rootPath / "agents"
seenAgentNames = {}
for agentPath in agentsPath.iterdir():
    if not agentPath.is_dir():
        continue
    foldedName = agentPath.name.lower()
    if foldedName in seenAgentNames:
        addViolation("duplicateAgentPath", str(agentPath), [seenAgentNames[foldedName], agentPath.name])
    seenAgentNames[foldedName] = agentPath.name

for relPath in ("doctrine/rootedTermuxGitHubReleaseInstallV1.json", "doctrine/smX400OneBashInstallSealV1.json"):
    doc = json.loads((rootPath / relPath).read_text())
    for fieldName in ("status", "nextGate", "crownStatus"):
        fieldValue = doc.get(fieldName)
        if isinstance(fieldValue, str) and not camelHumpRx.fullmatch(fieldValue):
            addViolation("nonCamelHumpMachineValue", relPath, f"{fieldName}={fieldValue}")

    if relPath.endswith("rootedTermuxGitHubReleaseInstallV1.json"):
        portalStatus = doc.get("priorLanPortal", {}).get("status")
        if isinstance(portalStatus, str) and not camelHumpRx.fullmatch(portalStatus):
            addViolation("nonCamelHumpMachineValue", relPath, f"priorLanPortal.status={portalStatus}")
    else:
        for fieldName, fieldValue in doc.get("deviceProof", {}).items():
            if isinstance(fieldValue, str) and not camelHumpRx.fullmatch(fieldValue):
                addViolation("nonCamelHumpMachineValue", relPath, f"deviceProof.{fieldName}={fieldValue}")

wrapperText = (rootPath / "tools/smX400OneBashInstall.sh").read_text()
for lineText in wrapperText.splitlines():
    if re.match(r"^[A-Z][A-Z0-9_]*=", lineText):
        addViolation("nonCamelHumpInternalShellVariable", "tools/smX400OneBashInstall.sh", lineText.split("=", 1)[0])

namingLaw = sealDoc.get("namingLaw", {})
humanLaw = namingLaw.get("humanCenteredNaming", {})
vowelLaw = namingLaw.get("vowelRip", {})
booleanLaw = namingLaw.get("booleanPhraseLaw", {})
functionLaw = namingLaw.get("functionPhraseLaw", {})
breadcrumbLaw = namingLaw.get("breadcrumbLaw", {})

if namingLaw.get("controlledNames") != "camelHump":
    addViolation("camelHumpLawMissing", "doctrine/namingPathSealV1.json")
if humanLaw.get("phraseFirst") is not True:
    addViolation("humanPhraseFirstMissing", "doctrine/namingPathSealV1.json")
if vowelLaw.get("enabled") is not True or vowelLaw.get("readabilityWins") is not True:
    addViolation("readableVowelRipMissing", "doctrine/namingPathSealV1.json")
if booleanLaw.get("required") is not True:
    addViolation("booleanPhraseLawMissing", "doctrine/namingPathSealV1.json")
if functionLaw.get("required") is not True:
    addViolation("functionPhraseLawMissing", "doctrine/namingPathSealV1.json")
if breadcrumbLaw.get("requiredWhenCompressed") is not True:
    addViolation("breadcrumbLawMissing", "doctrine/namingPathSealV1.json")

if violations:
    print(json.dumps({"status": "redNamingPathSeal", "violations": violations}, indent=2))
    sys.exit(1)

print(json.dumps({
    "status": "greenNamingPathSeal",
    "sealedPathCount": len(sealDoc["sealedPaths"]),
    "humanCenteredNaming": True,
    "readableVowelRip": True,
    "booleanPhraseLaw": True,
    "functionPhraseLaw": True,
    "legacyEvidenceRenamed": False,
}, indent=2))
