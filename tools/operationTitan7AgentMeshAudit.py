#!/usr/bin/env python3
import json, pathlib, sys, tomllib

root = pathlib.Path(__file__).resolve().parents[1]
errors=[]

def load_json(path):
    try:
        return json.loads((root/path).read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path}: {exc}")
        return {}

def require(cond,msg):
    if not cond: errors.append(msg)

titan=load_json("doctrine/operationTitan7AgentMeshV1.json")
plane=load_json("doctrine/luhmAiControlPlaneV1.json")
cabinet=load_json("doctrine/lumGoddessCabinetV1.json")

expected=["urdDoctorGoddess","belldandySecretary","skuldResearch","yume"]
require(titan.get("authority")=="Professor","Professor authority missing")
require(titan.get("boss")=="lum","Lum must remain sole boss")
require(titan.get("residentCustomAgents")==expected,"resident custom agent set mismatch")
require(titan.get("residentLaw",{}).get("presenceIsNotInference") is True,"presenceIsNotInference must be true")
require(titan.get("lumMustNotDuplicateGoddessSpecialties") is True,"Lum delegation firewall missing")
require(titan.get("belldandyRetention",{}).get("hardMaximumCommitAudit")==50,"commit audit ceiling must be 50")
require(titan.get("belldandyRetention",{}).get("generatedWorkingMaterialMaxDays")<=30,"generated TTL exceeds 30 days")
require(titan.get("crownStatus")=="STOP","Titan7 candidate must Crown STOP")

agents=plane.get("agents",{})
for agent_id, spec in agents.items():
    skill=spec.get("skillPath")
    require(bool(skill),f"{agent_id} missing skillPath")
    if skill:
        require((root/skill).is_file(),f"{agent_id} skill missing: {skill}")

contract=plane.get("customAgentContract",{})
require(contract.get("defaultSet")==expected,"control-plane default set mismatch")
require(contract.get("presenceIsNotInference") is True,"control-plane presenceIsNotInference missing")
require(contract.get("residentAgentMesh")=="doctrine/operationTitan7AgentMeshV1.json","control-plane Titan7 binding missing")

profiles=sorted((root/".codex/agents").glob("*.toml"))
require([p.stem for p in profiles]==sorted(expected),f"resident profiles must be exactly four: {[p.stem for p in profiles]}")
for p in profiles:
    try:
        data=tomllib.loads(p.read_text(encoding="utf-8"))
        require(data.get("sandbox_mode")=="read-only",f"{p} must be read-only")
        require(data.get("name")==p.stem,f"{p} name mismatch")
    except Exception as exc:
        errors.append(f"{p}: {exc}")

config=tomllib.loads((root/".codex/config.toml").read_text(encoding="utf-8"))
require(config.get("agents",{}).get("max_concurrent_threads_per_session")==4,"custom-agent concurrency must equal four")

routes=plane.get("routeProfiles",{})
require(routes.get("records")==["lum","belldandySecretary"],"records route still duplicates Belldandy")
require(routes.get("external")==["lum","skuldResearch"],"external route still duplicates Skuld")
require("fumi" not in routes.get("records",[]),"Fumi must be fallback, not default records route")
require("momo" not in routes.get("external",[]),"Momo must be fallback, not default external route")

lum=(root/"agents/lum/SKILL.md").read_text(encoding="utf-8")
require("Delegation firewall" in lum,"Lum delegation firewall missing")
require("presenceIsNotInference" in lum,"Lum presence/inference distinction missing")
require(len(lum.encode("utf-8")) < 6500,"Lum skill still too fat")
for token in ["urdDoctorGoddess","belldandySecretary","skuldResearch","yume","exact sourceRef","Professor retains Crown"]:
    require(token in lum,f"Lum skill missing {token}")

bell=(root/"agents/belldandyQualityOni/SKILL.md").read_text(encoding="utf-8")
for token in ["10 commits","25 commits","50 commits","maximum 30 days","snapshot before legacy prune"]:
    require(token in bell,f"Belldandy retention law missing {token}")

skuld=(root/"agents/skuldResearchOni/SKILL.md").read_text(encoding="utf-8")
for token in ["vendorSecurityUpdates","android16Canary","Cloudflare","Google AI Edge Gallery"]:
    require(token in skuld,f"Skuld watch law missing {token}")

urd=(root/"agents/urdMutationOni/SKILL.md").read_text(encoding="utf-8")
require("crossLayerDriftPathology" in urd,"Urd drift pathology ownership missing")

require(cabinet.get("delegationFirewall",{}).get("lumDoesNotReimplementOwnedSpecialties") is True,"cabinet delegation firewall missing")

status="GREEN_OPERATION_TITAN7_AGENT_MESH" if not errors else "RED_OPERATION_TITAN7_AGENT_MESH"
print(json.dumps({
    "schema":"luhmOs.operationTitan7AgentMeshAudit.v1",
    "status":status,
    "residentCustomAgents":expected,
    "declaredAgentRoles":len(agents),
    "lumSkillBytes":len(lum.encode("utf-8")),
    "errors":errors,
    "crownStatus":"STOP"
},indent=2))
sys.exit(1 if errors else 0)
