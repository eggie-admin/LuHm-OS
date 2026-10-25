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

# The brand is the sole project-owned case-sensitive human identity.
brand=naming.get("brandCaseLaw",{})
case=naming.get("caseResolutionLaw",{})
need(brand.get("canonicalBrand")=="LuHm-OS","brand exact spelling drift")
need(brand.get("exactSpellingRequired") is True,"brand-case exception missing")
need(brand.get("onlyProjectOwnedCaseSensitiveHumanIdentity") is True,"unexpected case-sensitive identity")
need(brand.get("automaticLowercaseBrandForbidden") is True,"brand cannot be lowercased")
need("LuHm-OS"!="LuHm-OS".lower(),"brand is not a lowercase slug")
need(case.get("caseSensitiveUserLookup") is False,"human command lookup must ignore case")
need(case.get("compareUsing")=="unicodeCasefoldThenRegisteredAliasLookup","casefold resolution law missing")
need(case.get("lowercaseKebabCaseOutput") is True,"lowercase kebab output required")
need(case.get("preserveCanonicalCamelHumpInternalSpelling") is True,"source identifier case changed")
need(case.get("normalizedAliasCollision")=="REJECT_AMBIGUOUS","casefold collisions must fail")
need(case.get("caseNormalizationMayNotTriggerCastBuildDeployOrPublication") is True,"alias granted authority")
need(case.get("externalProtocolFieldAndCodeIdentifierSpelling")=="preserveExactContractRequiredSpellingAtIntegrationBoundary","protocol compatibility contract missing")
for row in case.get("examples",[]):
    user=row["input"]
    canonical=row["canonical"]
    need(user.casefold()==canonical.casefold(),f"case-insensitive alias resolution drift: {user}")
    if row["kind"]=="kebabCase":
        need(bool(kebab.fullmatch(canonical)),f"non-lowercase kebab output: {canonical}")
    elif row["kind"]=="registeredCamelHumpAlias":
        need(bool(camel.fullmatch(canonical)),f"invalid preserved camelHump: {canonical}")
    elif row["kind"]=="dragonTail":
        need(bool(dragon.fullmatch(canonical)),f"invalid preserved DRAGONTAIL: {canonical}")
    else:
        need(False,f"unknown case resolution kind: {row['kind']}")

for value in ns["kebabCase"]["examples"]:
    need(bool(kebab.fullmatch(value)),f"kebab drift: {value}")
for value in ns["dragonTail"]["examples"]:
    need(bool(dragon.fullmatch(value)),f"dragonTail drift: {value}")
for value in ns["camelHump"]["examples"]:
    need(bool(camel.fullmatch(value)),f"camelHump drift: {value}")

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

ladder=naming.get("namespaceEscalation",{})
example=ladder.get("example",{})
need(ladder.get("orderedLayers")==["machineSqlDragonTail","repositoryKebabNamespace","vowelRippedStrictCamelHump","fullHumanCenteredCamelHump"],"namespace escalation order drift")
need(example.get("machineSqlDragonTail")=="OPERATION_TITAN","machine SQL token drift")
repoLayer=example.get("repositoryKebabNamespace",{})
need(repoLayer.get("slug")=="operation-titan","repository kebab slug drift")
need(repoLayer.get("namespacePattern")=="art.eggiebagelface.LuHmOS.*","repository namespace drift")
need(bool(kebab.fullmatch(repoLayer.get("slug",""))),"repository kebab slug invalid")
need(bool(camel.fullmatch(example.get("vowelRippedStrictCamelHump",""))),"vowel-ripped camelHump invalid")
need(example.get("vowelRippedStrictCamelHump")=="oprtTtn","Operation Titan vowel-ripped alias drift")
need(bool(camel.fullmatch(example.get("fullHumanCenteredCamelHump",""))),"full human-centered camelHump invalid")
need(example.get("fullHumanCenteredCamelHump")=="operationTitan","Operation Titan canonical identity drift")
need(ladder.get("identityLaw") and ladder.get("executionLaw"),"namespace identity/execution separation missing")

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
        prior=seen.get(value.casefold())
        if prior and prior!=canonical:
            errors.append(f"help alias collision: {value} -> {prior}/{canonical}")
        seen[value.casefold()]=canonical

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
        prior=seen.get(value.casefold())
        if prior and prior!=canonical:
            errors.append(f"precision alias collision: {value} -> {prior}/{canonical}")
        seen[value.casefold()]=canonical

binding=naming.get("codingRoleplayBinding",{})
roleplay=json.loads((root/"doctrine/codingRoleplayDirectorV2.json").read_text(encoding="utf-8"))
manual=json.loads((root/"doctrine/manualPluginVirginInstallV1.json").read_text(encoding="utf-8"))
source=json.loads((root/"doctrine/currentSourceTruthV3.json").read_text(encoding="utf-8"))
need(binding.get("canonicalMachineId")=="codingRoleplay","roleplay canonical camelHump drift")
need(bool(camel.fullmatch(binding.get("canonicalMachineId",""))),"roleplay camelHump syntax drift")
need(binding.get("transportSlug")=="coding-roleplay" and bool(kebab.fullmatch(binding.get("transportSlug",""))),"roleplay kebab slug drift")
need(binding.get("dragonTailState")=="PROPOSED_ONLY" and bool(dragon.fullmatch(binding.get("dragonTailState",""))),"roleplay state namespace drift")
need(binding.get("historicalTriggerAlias")=="mgcCdngRlplay" and binding.get("historicalTriggerAuthority")=="compatibilityAliasOnly","roleplay historic alias identity drift")
need(binding.get("resolvedIdentity")==binding.get("canonicalMachineId") and binding.get("aliasMayChangeAuthority") is False and binding.get("aliasMayActivateBuild") is False,"roleplay alias acquired authority")
need(roleplay.get("proposedLane",{}).get("id")=="proposed" and manual.get("firstBoot",{}).get("operatingLane")=="proposed","proposed roleplay first-boot lane drift")
need(source.get("pluginLayer",{}).get("proposedVirginInstall",{}).get("lane")=="proposed","source-truth proposed lane drift")

print(json.dumps({
  "schema":"luhmOs.namingNamespaceAudit.v1",
  "status":"GREEN_NAMING_NAMESPACE_CANDIDATE" if not errors else "RED_NAMING_NAMESPACE_CANDIDATE",
  "registeredIdentityCount":len(set(seen.values())),
  "errors":errors
},indent=2))
raise SystemExit(1 if errors else 0)
