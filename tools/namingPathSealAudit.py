#!/usr/bin/env python3
import json
import pathlib
import re
import sys

root=pathlib.Path(__file__).resolve().parents[1]
seal=json.loads((root/"doctrine/namingPathSealV1.json").read_text(encoding="utf-8"))
naming=json.loads((root/"doctrine/namingNamespaceCanonV1.json").read_text(encoding="utf-8"))
bad=[]

camel=re.compile(naming["namespaces"]["camelHump"]["regex"])
kebab=re.compile(naming["namespaces"]["kebabCase"]["regex"])
dragon=re.compile(naming["namespaces"]["dragonTail"]["regex"])

for rel in seal["sealedPaths"]:
    if not (root/rel).exists():
        bad.append({"kind":"missingSealedPath","path":rel})

controlledCamel=[
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
    "tools/smX400OneBashInstallAudit.py"
]
for rel in controlledCamel:
    name=pathlib.PurePosixPath(rel).name
    stem=name.rsplit(".",1)[0]
    if not camel.fullmatch(stem):
        bad.append({"kind":"nonCamelHumpControlledName","path":rel})

law=seal.get("namingLaw",{})
if law.get("machineIdentifiers")!="camelHump":
    bad.append({"kind":"machineNamespaceDrift"})
if law.get("transportSlugs")!="kebab-case-lowercase":
    bad.append({"kind":"kebabNamespaceDrift"})
if law.get("stateAndSentinels")!="DRAGONTAIL":
    bad.append({"kind":"dragonTailNamespaceDrift"})
if law.get("compressedAliasMustResolveThroughHelp") is not True:
    bad.append({"kind":"helpRecoveryMissing"})
if law.get("kebabCaseMustBeLowercase") is not True or law.get("kebabCaseWhitespaceAllowed") is not False or law.get("kebabCaseNullAllowed") is not False:
    bad.append({"kind":"kebabStrictTokenLawDrift"})
if law.get("kebabCaseRepositoryAlignmentOnly") is not True:
    bad.append({"kind":"kebabRepositoryAlignmentDrift"})
if law.get("dragonTailMustBeUppercase") is not True or law.get("dragonTailWhitespaceAllowed") is not False or law.get("dragonTailNullAllowed") is not False:
    bad.append({"kind":"dragonTailStrictTokenLawDrift"})
if law.get("strictCaseSensitiveTokens") is not True:
    bad.append({"kind":"strictCaseSensitiveTokenLawMissing"})

agents=root/"agents"
seen={}
for p in agents.iterdir():
    if not p.is_dir():
        continue
    key=p.name.lower()
    if key in seen:
        bad.append({"kind":"duplicateAgentPath","paths":[seen[key],p.name]})
    seen[key]=p.name

wrapper=(root/"tools/smX400OneBashInstall.sh").read_text(encoding="utf-8")
for line in wrapper.splitlines():
    if re.match(r"^[A-Z][A-Z0-9_]*=",line):
        bad.append({"kind":"undeclaredDragonTailShellVariable","path":"tools/smX400OneBashInstall.sh","line":line.split("=",1)[0]})

if bad:
    print(json.dumps({"status":"RED_NAMING_PATH_SEAL","violations":bad},indent=2))
    sys.exit(1)

print(json.dumps({
    "status":"GREEN_NAMING_PATH_SEAL_CANDIDATE",
    "sealedPathCount":len(seal["sealedPaths"]),
    "namespaces":["camelHump","kebab-case","DRAGONTAIL"],
    "helpRecovery":True,
    "legacyEvidenceRenamed":False
},indent=2))
