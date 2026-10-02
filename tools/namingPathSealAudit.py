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
 "tools/artOniCamelHumpAudit.py","tools/namingPathSealAudit.py"
]
snake=re.compile(r"^[A-Za-z0-9.-]*_[A-Za-z0-9_.-]+$")
scream=re.compile(r"^[A-Z0-9]+(?:_[A-Z0-9]+)+")
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
if bad:
    print(json.dumps({"status":"red","violations":bad},indent=2)); sys.exit(1)
print(json.dumps({"status":"greenNamingPathSeal","sealedPathCount":len(seal["sealedPaths"]),"legacyEvidenceRenamed":False},indent=2))
