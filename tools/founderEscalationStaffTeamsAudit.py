#!/usr/bin/env python3
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
errors=[]

def need(ok,msg):
    if not ok:
        errors.append(msg)

ladder=json.loads((root/"doctrine/founderEscalationLadderV1.json").read_text(encoding="utf-8"))
teams=json.loads((root/"doctrine/staffIntentTeamsV1.json").read_text(encoding="utf-8"))
deployment=json.loads((root/"doctrine/agentSystemDeploymentV1.json").read_text(encoding="utf-8"))

need(ladder.get("schema")=="luhmOs.founderEscalationLadder.v1","ladder schema drift")
tiers=ladder.get("tiers",[])
need([x.get("tier") for x in tiers]==[0,1,2,3],"tier numbering drift")
need([x.get("id") for x in tiers]==[
  "professorGarageLab",
  "lumCorporateHandling",
  "researchAndDevelopmentEscalation",
  "witchingHourCastClosure"
],"tier order drift")
need(tiers[0].get("lead")=="Professor","garage lead drift")
need(tiers[1].get("lead")=="lum","Lum handling drift")
need(tiers[2].get("lead")=="skuldResearch","R&D lead drift")
need(tiers[2].get("executiveLead")=="lum","R&D executive lead drift")
need(tiers[3].get("presidingOfficer")=="lum","final closure presiding officer drift")
need("CAST" in tiers[3].get("closureFlow",[]),"CAST missing from final tier")
need(tiers[3].get("physicalBoundary")=="installedOrLaunchedClaimsStillRequirePhysicalReceipt","physical proof boundary drift")

need(teams.get("schema")=="luhmOs.staffIntentTeams.v1","team schema drift")
matrix=teams.get("teams",{})
expected={
  "ritualSupport":["kiri","momo","shiori"],
  "officeSupport":["koe","fumi","kugi"],
  "studioSupport":["sumi","mediaAssetFactory","kaji"]
}
for name,members in expected.items():
    need(matrix.get(name,{}).get("members")==members,f"{name} membership drift")
    need(len(matrix.get(name,{}).get("members",[]))==3,f"{name} must contain three workers")

roster=set(deployment.get("requiredAgents",[]))
assigned=[]
for row in matrix.values():
    assigned.extend(row.get("members",[]))
need(set(assigned).issubset(roster),"team member outside canonical roster")
need(len(assigned)==len(set(assigned)),"worker assigned to multiple intent teams")
need(teams.get("independentForgeWorker",{}).get("id")=="tetsu","independent forge worker drift")
need(teams.get("leadership",{}).get("studioLead")=="yume","Yume studio lead drift")

print(json.dumps({
  "schema":"luhmOs.founderEscalationStaffTeamsAudit.v1",
  "status":"GREEN_FOUNDER_ESCALATION_STAFF_TEAMS_CANDIDATE" if not errors else "RED_FOUNDER_ESCALATION_STAFF_TEAMS_CANDIDATE",
  "tierCount":len(tiers),
  "intentTeamCount":len(matrix),
  "assignedWorkerCount":len(assigned),
  "errors":errors,
  "crownStatus":"STOP"
},indent=2))
raise SystemExit(1 if errors else 0)
