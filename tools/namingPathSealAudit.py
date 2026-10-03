#!/usr/bin/env python3
import json,pathlib,re,sys
root=pathlib.Path(__file__).resolve().parents[1]
sealPath=root/"doctrine/namingPathSealV1.json"
seal=json.loads(sealPath.read_text())
bad=[]
for rel in seal["sealedPaths"]:
    if not (root/rel).exists():
        bad.append({"kind":"missingSealedPath","path":rel})
controlled=[
 "agents/yumeArtOni","agents/sumiAssetOni","agents/belldandyQualityOni","agents/shioriCriticOni",
 "doctrine/artOniLayeredMutationV3.json","doctrine/namingPathSealV1.json",
 "doctrine/rootedTermuxGitHubReleaseInstallV1.json","doctrine/smX400OneBashInstallSealV1.json",
 "tools/artOniCamelHumpAudit.py","tools/namingPathSealAudit.py",
 "tools/smX400OneBashInstall.sh","tools/smX400OneBashInstallAudit.py",
 ".codex/agents/urdDoctorGoddess.toml",".codex/agents/belldandySecretary.toml",
 ".codex/agents/skuldResearch.toml",".codex/agents/yume.toml",
 "doctrine/luhmChatMagicTriggerV1.json","tools/luhmChatMagicTriggerAudit.py"
]
snake=re.compile(r"^[A-Za-z0-9.-]*_[A-Za-z0-9_.-]+$")
scream=re.compile(r"^[A-Z0-9]+(?:_[A-Z0-9]+)+")
lowerCamel=re.compile(r"^[a-z][A-Za-z0-9]*$")
for rel in controlled:
    name=pathlib.PurePosixPath(rel).name
    stem=name.rsplit(".",1)[0]
    if snake.match(stem) or scream.match(stem):
        bad.append({"kind":"nonCamelHumpControlledName","path":rel})
agents=root/"agents"
seen={}
for p in agents.iterdir():
    if not p.is_dir(): continue
    key=p.name.lower()
    if key in seen: bad.append({"kind":"duplicateAgentPath","paths":[seen[key],p.name]})
    seen[key]=p.name

for rel in ("doctrine/rootedTermuxGitHubReleaseInstallV1.json","doctrine/smX400OneBashInstallSealV1.json"):
    doc=json.loads((root/rel).read_text())
    for field in ("status","nextGate","crownStatus"):
        value=doc.get(field)
        if isinstance(value,str) and not lowerCamel.fullmatch(value):
            bad.append({"kind":"nonCamelHumpMachineValue","path":rel,"field":field,"value":value})
    if rel.endswith("rootedTermuxGitHubReleaseInstallV1.json"):
        value=doc.get("priorLanPortal",{}).get("status")
        if isinstance(value,str) and not lowerCamel.fullmatch(value):
            bad.append({"kind":"nonCamelHumpMachineValue","path":rel,"field":"priorLanPortal.status","value":value})
    else:
        for field,value in doc.get("deviceProof",{}).items():
            if isinstance(value,str) and not lowerCamel.fullmatch(value):
                bad.append({"kind":"nonCamelHumpMachineValue","path":rel,"field":"deviceProof."+field,"value":value})

wrapper=(root/"tools/smX400OneBashInstall.sh").read_text()
for line in wrapper.splitlines():
    if re.match(r"^[A-Z][A-Z0-9_]*=",line):
        bad.append({"kind":"nonCamelHumpInternalShellVariable","path":"tools/smX400OneBashInstall.sh","line":line.split("=",1)[0]})

if bad:
    print(json.dumps({"status":"red","violations":bad},indent=2)); sys.exit(1)
print(json.dumps({"status":"greenNamingPathSeal","sealedPathCount":len(seal["sealedPaths"]),"legacyEvidenceRenamed":False},indent=2))
