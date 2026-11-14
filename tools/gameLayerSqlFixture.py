#!/usr/bin/env python3
"""Rebuild a disposable populated game-layer SQLite projection from source Canon.
Never connects to production SQL, external hosts, ChatGPT, or local device APIs.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3

ROOT=Path(__file__).resolve().parents[1]
SCHEMA=ROOT/"host/api/machineRegistrySqliteV1.sql"
INVENTORY=ROOT/"game/demo/gameLayerBuildInventoryV1.json"
POLICY=ROOT/"doctrine/machineSqlHex512EscalationV1.json"
HEX40=re.compile(r"^[0-9a-f]{40}$")
ALLOWED={"cpu","gpu","memory","os","kernel","bios","uefi","bootloader","firmware",
         "driver","storage","filesystem","partition","network","dns","certificate",
         "process","service","package","library","plugin","api","model","runtime",
         "container","vm","display","sensor","media"}
KEY_NAMES={"id","componentClass","path","localSource"}
RELATIONS={"dependsOn","contains","runsOn","exposes","compatibleWith"}

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))

def key(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:32]

def sha256(value):
    return hashlib.sha256(value).hexdigest()

def insist(condition,reason):
    if not condition: raise ValueError("RED_GAME_LAYER_"+reason)

def normalize(inventory):
    insist(inventory.get("schema")=="luhmOs.gameLayerBuildInventory.v1","inventorySchema")
    insist(inventory.get("status")=="SOURCE_ONLY_RESEARCH_BUILD","inventoryState")
    canon=inventory.get("canon",{})
    insist(canon.get("repository")=="eggie-admin/LuHm-OS"
           and canon.get("crown")=="STOP","sourceAuthority")
    rules=inventory.get("rules",{})
    for name in ("singleExistingSqlSchema","sqlSyntheticFixtureOnly","professorFinalApprovalRequired"):
        insist(rules.get(name) is True,"policy"+name)
    for name in ("productionSqlMutation","externalModsDownloaded","sourceFilesNeverExecutedBySql",
                 "privateKeysInSql","backendPluginEdited","automaticAgentActivation",
                 "mergeToMain","astraHardeningNotExecuted"):
        # sourceFilesNeverExecutedBySql is True: source text is never executed through the SQL.
        expected=name in ("sourceFilesNeverExecutedBySql","astraHardeningNotExecuted")
        insist(rules.get(name) is expected,"nonExecution"+name)
    items=inventory.get("components",[])
    insist(isinstance(items,list) and len(items)>=18,"componentCount")
    ids=set()
    files={}
    for row in items:
        insist(type(row) is dict and set(row)==KEY_NAMES,"componentFields")
        ident,typ,path=row["id"],row["componentClass"],row["path"]
        insist(isinstance(ident,str) and re.fullmatch(r"[a-z][A-Za-z0-9]{2,55}",ident)
               and ident not in ids and typ in ALLOWED and row["localSource"] is True,"componentIdentity")
        insist(isinstance(path,str) and ".." not in Path(path).parts
               and not path.startswith("/") and "\\x00" not in path,"sourcePath")
        full=(ROOT/path).resolve()
        insist(full.is_relative_to(ROOT) and full.is_file() and not (ROOT/path).is_symlink(),"sourceMissingOrEscaped")
        ids.add(ident)
        files[ident]=(path,full.read_bytes())
    relations=inventory.get("links",[])
    insist(isinstance(relations,list) and len(relations)>=12,"relationCount")
    seen=set()
    for row in relations:
        insist(type(row) is dict and set(row)=={"from","to","relation"}
               and row["from"] in ids and row["to"] in ids
               and row["from"]!=row["to"] and row["relation"] in RELATIONS,"linkIdentity")
        triple=(row["from"],row["to"],row["relation"])
        insist(triple not in seen,"duplicateLink")
        seen.add(triple)
    insist({"sqlRegistry","npmLock","htmlAtelier","cssAtelier","jsAtelier",
            "jqueryDock","castIntent","portablePlugin","godotProject",
            "godotCompanionScene","originalProfiles","relationshipRules",
            "modReferenceShelf"}.issubset(ids),"requiredLayers")
    profiles=load(ROOT/inventory["originalCharactersSource"])
    mod=load(ROOT/inventory["modResearchSource"])
    rules_doc=load(ROOT/inventory["relationshipRulesSource"])
    insist(profiles.get("schema")=="luhmOs.originalCompanionProfiles.v1"
           and len(profiles.get("companions",[]))==3
           and all(row.get("adult") is True for row in profiles["companions"]),"originalAdultRoster")
    insist(mod.get("schema")=="luhmOs.modInspirationCatalog.v1"
           and len(mod.get("sources",[]))>=8
           and all(row.get("fileReuse") is False for row in mod["sources"]),"referenceShelfNotBundled")
    insist(rules_doc.get("schema")=="luhmOs.relationshipRules.v2"
           and len(rules_doc.get("events",{}))==7,"gameplayRules")
    insist(inventory.get("modResearchMode")=="INDEX_AND_DESIGN_REFERENCE_ONLY_NO_BINARY_IMPORT","researchBoundary")
    return files,relations,profiles,mod

def populate(source_ref):
    insist(type(source_ref) is str and HEX40.fullmatch(source_ref) is not None,"exactGit40")
    inventory=load(INVENTORY)
    files,relations,profiles,mod=normalize(inventory)
    sql=SCHEMA.read_text(encoding="utf-8")
    db=sqlite3.connect(":memory:")
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript(sql)
    observed=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    inventory_digest=sha256(INVENTORY.read_bytes())
    machine_key=key("syntheticLuHmGameLayer")
    db.execute("INSERT INTO sourceRevision VALUES(?,?,?,?,?)",
               (source_ref,inventory_digest,"eggie-admin/LuHm-OS","SOURCE_CANDIDATE",observed))
    db.execute("INSERT INTO machineIdentity VALUES(?,?,?,?,?,?)",
               (machine_key,"SYNTHETIC_GAME_LAYER","synthetic",source_ref,None,1))
    for row in inventory["components"]:
        name=row["id"]
        path,blob=files[name]
        digest=sha256(blob)
        db.execute("INSERT INTO machineComponent VALUES(?,?,?,?,?,?,?,?)",
                   (key("component:"+name),machine_key,row["componentClass"],
                    name,None,digest,"SOURCE_ONLY",source_ref))
        db.execute("INSERT INTO artifactPointer VALUES(?,?,?,?,?,?,?)",
                   ("sourceAsset"+name,digest,len(blob),"githubSource",path,source_ref,"HASH_OBSERVED"))
    for row in relations:
        db.execute("INSERT INTO machineComponentLink VALUES(?,?,?,?)",
                   (key("component:"+row["from"]),key("component:"+row["to"]),
                    row["relation"],source_ref))
    db.execute("INSERT INTO namespaceRegistry VALUES(?,?,?,?,?)",
               ("gamePlugin","plugin","LuHm-OS",source_ref,"SOURCE_ONLY"))
    db.execute("INSERT INTO namespaceRegistry VALUES(?,?,?,?,?)",
               ("gameNpmPackage","package","luhm-os-frontend-dryrun",source_ref,"SOURCE_ONLY"))
    db.execute("INSERT INTO machineApi VALUES(?,?,?,?,?,?,?)",
               ("gameConsoleRead",machine_key,"GET","ui",
                "/frontEnd/prototypes/gameLayerConsole/","READ_ONLY",source_ref))
    db.execute("INSERT INTO machineApi VALUES(?,?,?,?,?,?,?)",
               ("candidateMcpRead",machine_key,"MCP_TOOL","mcp",
                "luhm_open_cockpit","READ_ONLY",source_ref))
    db.execute("INSERT INTO castOpcodeRegistry VALUES(?,?,?,?,?,?)",
               ("0xC1","43415354","castIntent","INTENT_ONLY",0,source_ref))
    db.execute("INSERT INTO evidenceReceipt VALUES(?,?,?,?,?,?)",
               ("gameLayersSourceProjection",source_ref,inventory_digest,observed,
                "SOURCE_CI","SOURCE_ONLY"))
    # Populate the SAME canonical 512-coordinate table as review-state metadata.
    # HOLD is intentional: merely populating logical coordinates proves no runtime or gameplay.
    p=load(POLICY)
    stages=p["coordinates"]["stages"]
    beats=p["coordinates"]["beats"]
    tiers=p["coordinates"]["tiers"]
    for domain in p["surfaces"]:
        for i,stage in enumerate(stages):
            for j,beat in enumerate(beats):
                for k,tier in enumerate(tiers):
                    coordinate=f"0x{16*i+4*j+k:02X}"
                    db.execute("INSERT INTO auditCoordinate VALUES(?,?,?,?,?,?,?)",
                               (domain,coordinate,stage,beat,tier,source_ref,"HOLD"))
    db.commit()
    receipt={
        "schema":"luhmOs.gameLayerSqlFixtureReceipt.v1",
        "sourceRef":source_ref,
        "state":"SYNTHETIC_IN_MEMORY_ONLY",
        "database":"existingMachineRegistrySqliteV1",
        "sourceInventorySha256":inventory_digest,
        "componentRecords":db.execute("SELECT count(*) FROM machineComponent").fetchone()[0],
        "dependencyLinks":db.execute("SELECT count(*) FROM machineComponentLink").fetchone()[0],
        "artifactPointers":db.execute("SELECT count(*) FROM artifactPointer").fetchone()[0],
        "auditCoordinatesHeld":db.execute("SELECT count(*) FROM auditCoordinate WHERE evaluation='HOLD'").fetchone()[0],
        "originalAdultCompanions":len(profiles["companions"]),
        "modReferenceEntries":len(mod["sources"]),
        "sqlForeignKeyViolations":len(db.execute("PRAGMA foreign_key_check").fetchall()),
        "castOpcode":"0xC1",
        "castEffect":"INTENT_ONLY",
        "livePluginUpdated":False,
        "sqlProductionChanged":False,
        "crown":"STOP"
    }
    insist(receipt["componentRecords"]==len(files)
           and receipt["dependencyLinks"]==len(relations)
           and receipt["artifactPointers"]==len(files)
           and receipt["auditCoordinatesHeld"]==512
           and receipt["sqlForeignKeyViolations"]==0,"sqlProjection")
    for bad,params in [
        ("INSERT INTO machineComponentLink VALUES(?,?,?,?)",
         (key("component:missing"),key("component:godotProject"),"dependsOn",source_ref)),
        ("INSERT INTO machineComponent VALUES(?,?,?,?,?,?,?,?)",
         (key("badClass"),machine_key,"executeCode","badClass",None,"a"*64,"SOURCE_ONLY",source_ref)),
        ("INSERT INTO artifactPointer VALUES(?,?,?,?,?,?,?)",
         ("badArtifact","x"*64,0,"githubSource","bad",source_ref,"SOURCE_ONLY")),
        ("UPDATE castOpcodeRegistry SET grantsAuthority=1 WHERE opcode='0xC1'",()),
    ]:
        db.execute("SAVEPOINT rejectCase")
        try:
            db.execute(bad,params)
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("RED_SQL_NEGATIVE_CONTROL")
        finally:
            db.execute("ROLLBACK TO rejectCase")
            db.execute("RELEASE rejectCase")
    db.close()
    return receipt

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--source-ref")
    a=ap.parse_args()
    if a.self_test == bool(a.source_ref):
        ap.error("pass exactly one of --self-test or --source-ref")
    result=populate("f"*40 if a.self_test else a.source_ref)
    print(json.dumps(result,sort_keys=True,indent=2))

if __name__=="__main__":
    main()
