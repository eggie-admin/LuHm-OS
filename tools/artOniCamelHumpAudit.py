#!/usr/bin/env python3
import pathlib,re,sys,json
root=pathlib.Path(__file__).resolve().parents[1]
targets=[
 root/"agents/yumeArtOni/SKILL.md",
 root/"agents/sumiAssetOni/SKILL.md",
 root/"doctrine/artOniLayeredMutationV3.json",
 root/"game/assets/ASSET_MANIFEST_V1.json",
]
bad=[]
for path in targets:
    text=path.read_text()
    for lineNo,line in enumerate(text.splitlines(),1):
        if line.startswith("#") and re.search(r"\b[A-Z]{2,}_[A-Z0-9_]+\b",line):
            bad.append([str(path.relative_to(root)),lineNo,"screamingSnakeTitle",line])
        for token in re.findall(r"`([A-Za-z][A-Za-z0-9_]*)`",line):
            if "_" in token:
                bad.append([str(path.relative_to(root)),lineNo,"controlledSnakeToken",token])
for path in [root/"doctrine/artOniLayeredMutationV3.json",root/"game/assets/ASSET_MANIFEST_V1.json"]:
    data=json.loads(path.read_text())
    def walk(v,p=""):
        if isinstance(v,dict):
            for k,val in v.items():
                if "_" in k: bad.append([str(path.relative_to(root)),0,"snakeJsonKey",p+k])
                walk(val,p+k+".")
        elif isinstance(v,list):
            for i,val in enumerate(v): walk(val,p+str(i)+".")
    walk(data)
required=["protectedReference","visualVocabulary","canonLock","layeredMutation","candidateAsset","approvedArt","runtimeImport","cast","contaminationAudit","professorReview"]
joined="\n".join(p.read_text() for p in targets)
for token in required:
    if token not in joined: bad.append(["all",0,"missingCamelHumpToken",token])
if bad:
    print(json.dumps({"status":"red","violations":bad},indent=2)); sys.exit(1)
print(json.dumps({"status":"greenSourceLint","camelHumpRequired":True,"targets":[str(p.relative_to(root)) for p in targets]},indent=2))
