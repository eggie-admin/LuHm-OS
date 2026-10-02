#!/usr/bin/env python3
import pathlib,re,sys
root=pathlib.Path(__file__).resolve().parents[1]
path=root/"agents/yumeArtOni/SKILL.md"
text=path.read_text()
bad=[]
for lineNo,line in enumerate(text.splitlines(),1):
    if line.startswith("#") and re.search(r"\b[A-Z]{2,}_[A-Z0-9_]+\b",line):
        bad.append([lineNo,"screamingSnakeTitle",line])
    for token in re.findall(r"`([A-Za-z][A-Za-z0-9_]*)`",line):
        if "_" in token:
            bad.append([lineNo,"controlledSnakeToken",token])
required=["protectedReference","visualVocabulary","canonLock","layeredMutation","candidateAsset","approvedArt","runtimeImport","cast","contaminationAudit","professorReview"]
for token in required:
    if token not in text:
        bad.append([0,"missingCamelHumpToken",token])
if bad:
    print({"status":"red","violations":bad}); sys.exit(1)
print({"status":"greenSourceLint","camelHumpRequired":True,"path":str(path.relative_to(root))})
