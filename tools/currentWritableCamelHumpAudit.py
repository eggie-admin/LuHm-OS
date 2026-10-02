#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

rootPath=Path(__file__).resolve().parents[1]
errors=[]
lowerCamel=re.compile(r"^[a-z][A-Za-z0-9]*$")
upperInternal=re.compile(r"^[A-Z][A-Z0-9_]*$")
jsUpperDecl=re.compile(r"\b(?:const|let|var)\s+([A-Z][A-Z0-9_]*)\b")
pyUpperAssign=re.compile(r"^([A-Z][A-Z0-9_]*)\s*=",re.M)

def add(kind,path,detail):
    errors.append({"kind":kind,"path":path,"detail":detail})

def gitLines(*args):
    try:
        out=subprocess.check_output(["git",*args],cwd=rootPath,text=True,stderr=subprocess.DEVNULL)
        return [line.strip() for line in out.splitlines() if line.strip()]
    except Exception:
        return []

added=gitLines("diff","--name-only","--diff-filter=A","origin/main...HEAD")
if not added:
    added=gitLines("diff-tree","--no-commit-id","--name-only","--diff-filter=A","-r","HEAD")

controlledRoots=("doctrine/","tools/","agents/","frontEnd/jquery/",".github/workflows/")
externalFileNames={"SKILL.md","README.md","package.json","index.html","styles.css","app.js","plugin.json","mcp.json"}

for rel in added:
    if not rel.startswith(controlledRoots):
        continue
    path=Path(rel)
    name=path.name
    if name not in externalFileNames:
        stem=name.rsplit(".",1)[0]
        if not lowerCamel.fullmatch(stem):
            add("newWritableFileNotCamelHump",rel,stem)

    if rel.startswith("agents/") and len(path.parts)>1:
        agentDir=path.parts[1]
        if not lowerCamel.fullmatch(agentDir):
            add("newAgentDirectoryNotCamelHump",rel,agentDir)

    full=rootPath/rel
    if not full.is_file():
        continue
    text=full.read_text(encoding="utf-8")

    if full.suffix in {".js",".mjs"}:
        for match in jsUpperDecl.finditer(text):
            add("newJavascriptInternalNotCamelHump",rel,match.group(1))

    if full.suffix==".py":
        for match in pyUpperAssign.finditer(text):
            add("newPythonInternalNotCamelHump",rel,match.group(1))

    if full.suffix==".json":
        try:
            doc=json.loads(text)
        except Exception as exc:
            add("invalidJson",rel,str(exc))
            continue

        machineValueKeys={
            "status","providerId","workerId","machineIdentity","role","kind","boss",
            "implementationStatus","routingAuthority","classification","acceptsOrdersFrom",
            "providerResponseState","crownStatus","mode"
        }

        def walk(value,keyPath=""):
            if isinstance(value,dict):
                for key,item in value.items():
                    if not lowerCamel.fullmatch(key):
                        add("jsonKeyNotCamelHump",rel,f"{keyPath}.{key}".lstrip("."))
                    if key in machineValueKeys and isinstance(item,str):
                        if not lowerCamel.fullmatch(item):
                            add("machineValueNotCamelHump",rel,f"{keyPath}.{key}={item}".lstrip("."))
                    if (key.endswith("States") or key.endswith("Classes")) and isinstance(item,list):
                        for member in item:
                            if isinstance(member,str) and not lowerCamel.fullmatch(member):
                                add("machineEnumNotCamelHump",rel,f"{keyPath}.{key}={member}".lstrip("."))
                    walk(item,f"{keyPath}.{key}".strip("."))
            elif isinstance(value,list):
                for i,item in enumerate(value):
                    walk(item,f"{keyPath}[{i}]")
        walk(doc)

sealPath=rootPath/"doctrine/namingPathSealV1.json"
if sealPath.is_file():
    seal=json.loads(sealPath.read_text())
    monitoring=seal.get("monitoring",{})
    urd=monitoring.get("urdDoctorGoddess",{})
    belldandy=monitoring.get("belldandySecretary",{})
    if urd.get("role")!="structuralNamingPathology":
        add("urdMonitorMissing","doctrine/namingPathSealV1.json",str(urd))
    if belldandy.get("role")!="canonicalNameLedger":
        add("belldandyMonitorMissing","doctrine/namingPathSealV1.json",str(belldandy))

receipt={
    "schema":"luhmOs.currentWritableCamelHumpAudit.v1",
    "status":"greenCurrentWritableCamelHump" if not errors else "redCurrentWritableCamelHump",
    "addedFilesChecked":added,
    "watchers":{
        "urdDoctorGoddess":"structuralNamingPathology",
        "belldandySecretary":"canonicalNameLedger"
    },
    "historicalEvidenceRenamed":False,
    "errors":errors,
    "crownStatus":"stop"
}
print(json.dumps(receipt,indent=2))
raise SystemExit(1 if errors else 0)
