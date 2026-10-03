#!/usr/bin/env python3
import json, pathlib, sys

root = pathlib.Path(__file__).resolve().parents[1]
path = root / "doctrine/luhmSubsidiaryAiMeshV1.json"
errors = []

try:
    data = json.loads(path.read_text(encoding="utf-8"))
except Exception as exc:
    print(json.dumps({"status":"red","errors":[f"invalid json: {exc}"]}, indent=2))
    raise SystemExit(1)

def require(cond, msg):
    if not cond:
        errors.append(msg)

require(data.get("schema") == "luhmOs.subsidiaryAiMesh.v1", "schema mismatch")
require(data.get("boss") == "lum", "Lum must remain boss")
require(data.get("authority") == "Professor", "Professor authority missing")
agents = data.get("canonicalAgents", {}).get("alwaysRegisteredForProjectTask", [])
require(agents == ["urdDoctorGoddess","belldandySecretary","skuldResearch","yume"], "default custom-agent set mismatch")
require(data.get("canonicalAgents", {}).get("vendorInstancesAre") == "roleMirrorsNotNewAgents", "vendors must mirror roles, not create new canonical agents")
require(data.get("concurrency", {}).get("maxGlobalSupportInference") <= 4, "support inference cap exceeds 4")
require(data.get("concurrency", {}).get("duplicateContextFanoutForbidden") is True, "duplicate context fanout must be forbidden")
require(data.get("retentionPolicy", {}).get("generatedWorkingMaterialMaxDays") <= 30, "generated working material TTL exceeds 30 days")
depth = data.get("goddessRoles", {}).get("belldandySecretary", {}).get("auditCommitDepth", {})
require(max(depth.values() or [999]) <= 50, "audit commit depth exceeds 50")
edge = data.get("edgeGallerySafety", {})
require(edge.get("toolsDefault") == "deny", "Edge Gallery tools must default deny")
require(edge.get("mutationToolsExposed") is False, "Edge Gallery mutation tools exposed")
require(edge.get("signingToolsExposed") is False, "Edge Gallery signing tools exposed")
require(edge.get("crownToolsExposed") is False, "Edge Gallery Crown tools exposed")
rss = data.get("wireProtocol", {}).get("rssAtom", {})
require(rss.get("mayCarryAuthority") is False and rss.get("mayTriggerMutation") is False, "RSS/Atom must remain status-only")
mini = data.get("wireProtocol", {}).get("minifier", {})
require(mini.get("deterministicOnly") is True and mini.get("authority") is False, "minifier must be deterministic and non-authoritative")
subs = data.get("corporateTopology", {}).get("subsidiaries", {})
for name, obj in subs.items():
    require(obj.get("mayGrantCrown") is False, f"{name} mayGrantCrown must be false")

status = "greenSubsidiaryAiMeshSource" if not errors else "redSubsidiaryAiMeshSource"
print(json.dumps({"status":status,"errors":errors,"agentCount":len(agents),"maxAuditCommits":max(depth.values() or [0])}, indent=2))
sys.exit(1 if errors else 0)
