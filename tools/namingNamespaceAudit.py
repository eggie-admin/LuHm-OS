#!/usr/bin/env python3
import json
import pathlib
import re
import sys

root=pathlib.Path(__file__).resolve().parents[1]
naming=json.loads((root/"doctrine/namingNamespaceCanonV1.json").read_text(encoding="utf-8"))
help_doc=json.loads((root/"doctrine/commandHelpV1.json").read_text(encoding="utf-8"))
precision=json.loads((root/"doctrine/chatPrecisionCommandV1.json").read_text(encoding="utf-8"))
errors=[]

def need(ok,msg):
    if not ok:
        errors.append(msg)

ns=naming["namespaces"]
kebab=re.compile(ns["kebabCase"]["regex"])
dragon=re.compile(ns["dragonTail"]["regex"])
camel=re.compile(ns["camelHump"]["regex"])
short=re.compile(naming["personCenteredDegradation"]["shorthandLayer"]["regex"])

for value in ns["kebabCase"]["examples"]:
    need(bool(kebab.fullmatch(value)),f"kebab drift: {value}")
for value in ns["dragonTail"]["examples"]:
    need(bool(dragon.fullmatch(value)),f"dragonTail drift: {value}")
for value in ns["camelHump"]["examples"]:
    need(bool(camel.fullmatch(value)),f"camelHump drift: {value}")
for row in naming["personCenteredDegradation"]["shorthandLayer"]["examples"]:
    need(bool(short.fullmatch(row["shorthand"])),f"shorthand drift: {row['shorthand']}")

recovery=naming["personCenteredDegradation"]["recoveryLaw"]
need(recovery.get("canonicalIdentityNeverDiscarded") is True,"canonical identity may be discarded")
need(recovery.get("helpMustResolveEveryRegisteredAlias") is True,"help recovery missing")
need(help_doc.get("behavior",{}).get("helpMayMutate") is False,"help mutation leak")
need(help_doc.get("behavior",{}).get("allAliasesResolveToCanonical") is True,"help alias recovery missing")
need("luhm -h" in help_doc.get("entryPoints",[]),"apt-like -h missing")

for row in precision.get("examples",[]):
    need(bool(kebab.fullmatch(row["kebab"])),f"precision kebab drift: {row['kebab']}")
    need(bool(dragon.fullmatch(row["debugVerb"])),f"precision dragonTail drift: {row['debugVerb']}")
    need(bool(camel.fullmatch(row["camelHump"])),f"precision camelHump drift: {row['camelHump']}")

print(json.dumps({
  "schema":"luhmOs.namingNamespaceAudit.v1",
  "status":"GREEN_NAMING_NAMESPACE_CANDIDATE" if not errors else "RED_NAMING_NAMESPACE_CANDIDATE",
  "errors":errors
},indent=2))
raise SystemExit(1 if errors else 0)
