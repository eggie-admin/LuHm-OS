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

def vowel_rip(name):
    parts=re.findall(r"[a-z]+|[A-Z][a-z0-9]*|[A-Z]+(?![a-z])|[0-9]+",name)
    out=[]
    for part in parts:
        if not part:
            continue
        out.append(part[0]+"".join(ch for ch in part[1:] if ch.lower() not in "aeiou"))
    return "".join(out)

def shorthand(name):
    return "".join(word[0] for word in re.findall(r"[a-z]+|[A-Z][a-z0-9]*",name)).lower()

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

degrade=naming["personCenteredDegradation"]
need(degrade.get("canonicalHumanLayer",{}).get("form")=="camelHump","person-centered canonical layer drift")
need(degrade.get("vowelRippedLayer",{}).get("form")=="vowelRippedCamel","vowel-ripped layer drift")
need(degrade.get("shorthandLayer",{}).get("form")=="lowercaseShorthand","shorthand layer drift")
for row in degrade["shorthandLayer"]["examples"]:
    need(bool(short.fullmatch(row["shorthand"])),f"shorthand drift: {row['shorthand']}")

recovery=degrade["recoveryLaw"]
need(recovery.get("canonicalIdentityNeverDiscarded") is True,"canonical identity may be discarded")
need(recovery.get("aliasMustResolveToCanonical") is True,"alias canonical recovery missing")
need(recovery.get("helpMustResolveEveryRegisteredAlias") is True,"help recovery missing")
need(recovery.get("compressedAliasMayCreateAuthority") is False,"compressed alias authority leak")

behavior=help_doc.get("behavior",{})
need(behavior.get("helpMayMutate") is False,"help mutation leak")
need(behavior.get("helpMayGrantAuthority") is False,"help authority leak")
need(behavior.get("allAliasesResolveToCanonical") is True,"help alias recovery missing")
need("luhm -h" in help_doc.get("entryPoints",[]),"apt-like -h missing")
need("luhm <command> -h" in help_doc.get("entryPoints",[]),"per-command -h missing")

seen={}
required=set(help_doc.get("requiredHelpFields",[]))
for row in help_doc.get("builtins",[]):
    canonical=row.get("canonicalName","")
    need(bool(camel.fullmatch(canonical)),f"help canonical camelHump drift: {canonical}")
    need(required.issubset(row),f"help entry fields missing: {canonical}")
    aliases=row.get("aliases",{})
    if "kebab" in aliases:
        need(bool(kebab.fullmatch(aliases["kebab"])),f"help kebab drift: {aliases['kebab']}")
    if "dragonTail" in aliases:
        need(bool(dragon.fullmatch(aliases["dragonTail"])),f"help dragonTail drift: {aliases['dragonTail']}")
    if "vowelRipped" in aliases:
        need(bool(camel.fullmatch(aliases["vowelRipped"])),f"help vowelRipped drift: {aliases['vowelRipped']}")
    if "shorthand" in aliases:
        need(bool(short.fullmatch(aliases["shorthand"])),f"help shorthand drift: {aliases['shorthand']}")
    for value in [canonical,*aliases.values()]:
        prior=seen.get(value)
        if prior and prior!=canonical:
            errors.append(f"help alias collision: {value} -> {prior}/{canonical}")
        seen[value]=canonical

for row in precision.get("examples",[]):
    canonical=row["camelHump"]
    need(bool(kebab.fullmatch(row["kebab"])),f"precision kebab drift: {row['kebab']}")
    need(bool(dragon.fullmatch(row["debugVerb"])),f"precision dragonTail drift: {row['debugVerb']}")
    need(bool(camel.fullmatch(canonical)),f"precision camelHump drift: {canonical}")
    generated={
        "kebab":row["kebab"],
        "dragonTail":row["debugVerb"],
        "vowelRipped":vowel_rip(canonical),
        "shorthand":shorthand(canonical)
    }
    for value in [canonical,*generated.values()]:
        prior=seen.get(value)
        if prior and prior!=canonical:
            errors.append(f"precision alias collision: {value} -> {prior}/{canonical}")
        seen[value]=canonical

print(json.dumps({
  "schema":"luhmOs.namingNamespaceAudit.v1",
  "status":"GREEN_NAMING_NAMESPACE_CANDIDATE" if not errors else "RED_NAMING_NAMESPACE_CANDIDATE",
  "registeredIdentityCount":len(set(seen.values())),
  "errors":errors
},indent=2))
raise SystemExit(1 if errors else 0)
