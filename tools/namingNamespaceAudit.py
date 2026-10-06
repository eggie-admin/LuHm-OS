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

kebab_law=ns["kebabCase"]
need(kebab_law.get("repositoryAlignmentOnly") is True,"kebab must be repository-alignment only")
need(kebab_law.get("lowercaseRequired") is True,"kebab lowercase requirement missing")
need(kebab_law.get("uppercaseAllowed") is False,"kebab uppercase leak")
need(kebab_law.get("whitespaceAllowed") is False,"kebab whitespace leak")
need(kebab_law.get("nullAllowed") is False and kebab_law.get("emptyAllowed") is False,"kebab NULL/empty leak")
for bad_value in ("Foo-Bar","foo Bar","foo bar","FOO-BAR",""):
    need(not bool(kebab.fullmatch(bad_value)),f"kebab strictness leak: {bad_value!r}")

dragon_law=ns["dragonTail"]
need(dragon_law.get("machineLayer") is True,"DRAGONTAIL machine-layer flag missing")
need(dragon_law.get("uppercaseRequired") is True,"DRAGONTAIL uppercase requirement missing")
need(dragon_law.get("lowercaseAllowed") is False,"DRAGONTAIL lowercase leak")
need(dragon_law.get("whitespaceAllowed") is False,"DRAGONTAIL whitespace leak")
need(dragon_law.get("nullAllowed") is False and dragon_law.get("emptyAllowed") is False,"DRAGONTAIL NULL/empty leak")
for bad_value in ("green","Green","GREEN STATE","green_state",""):
    need(not bool(dragon.fullmatch(bad_value)),f"DRAGONTAIL strictness leak: {bad_value!r}")

projection=naming.get("strictProjectionLaw",{})
need(projection.get("canonicalLogic")=="camelHump","canonical logic projection drift")
need(projection.get("repositoryAlignment")=="kebabCase","repository projection drift")
need(projection.get("finalMachineToken")=="dragonTail","machine projection drift")
need(projection.get("linearAliasDegradation") is False,"namespace projection incorrectly treated as linear alias degradation")

dragon_scan_files=[
    "doctrine/luhmAiControlPlaneV1.json",
    "doctrine/escalationKernelV1.json",
    "doctrine/corporateEscalationProfileV1.json",
    "doctrine/magicEscalationProfileV1.json",
    "doctrine/founderEscalationLadderV1.json",
    "doctrine/yumeCreativeEscalationV1.json",
    "doctrine/operationTitan7ChatTriggerV2.json",
    "doctrine/escalationWorkflowRoomsV1.json",
]

def scan_dragon_values(value,path=""):
    if isinstance(value,dict):
        for key,item in value.items():
            item_path=f"{path}.{key}" if path else key
            if isinstance(item,str) and key in {"status","state","crownStatus","gate","receiptState","debugVerb"}:
                need(bool(dragon.fullmatch(item)),f"dragonTail field drift: {item_path}={item}")
            scan_dragon_values(item,item_path)
    elif isinstance(value,list):
        for index,item in enumerate(value):
            scan_dragon_values(item,f"{path}[{index}]")

for rel in dragon_scan_files:
    doc=json.loads((root/rel).read_text(encoding="utf-8"))
    scan_dragon_values(doc,rel)

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
