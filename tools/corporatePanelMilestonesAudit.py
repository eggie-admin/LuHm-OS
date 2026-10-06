#!/usr/bin/env python3
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
errors=[]

def need(ok,msg):
    if not ok:
        errors.append(msg)

d=json.loads((root/"doctrine/corporatePanelMilestonesV1.json").read_text(encoding="utf-8"))
need(d.get("schema")=="luhmOs.corporatePanelMilestones.v1","schema drift")
need(d.get("authority")=="Professor","authority drift")
need(len(d.get("milestones",[]))==3,"milestone count drift")

m={x["id"]:x for x in d.get("milestones",[])}
need(set(m)=={"corporateAuthorityMilestone","dualLaneOperatingMilestone","partnerEscalationMilestone"},"milestone ids drift")

a=m["corporateAuthorityMilestone"]["authorityMap"]
need(a["eggieFounder"]["displayTitle"]=="CEO and Founder","CEO/founder drift")
need(a["lum"]["displayTitle"]=="President","Lum president drift")
need(a["lum"]["mythicTitle"]=="Supreme Witch","Lum supreme-witch drift")
need(a["urdDoctorGoddess"]["displayTitle"]=="Vice President","Urd VP drift")
need(a["urdDoctorGoddess"]["practiceTitle"]=="Doctor","Urd doctor drift")
need(a["urdDoctorGoddess"]["corporateLogisticsOwner"] is False,"Urd logistics ownership leak")
need(a["belldandySecretary"]["displayTitle"]=="Secretary of State","Belldandy title drift")
need(a["skuldResearch"]["displayTitle"]=="Head of Research and Development","Skuld R&D title drift")

lanes=m["dualLaneOperatingMilestone"]["lanes"]
need(set(lanes)=={"commercialPublic","privateResearchDevelopment"},"lane split drift")
need(lanes["commercialPublic"]["lead"]=="lum","public lane Lum lead drift")
need(lanes["privateResearchDevelopment"]["researchLead"]=="skuldResearch","private R&D Skuld lead drift")
need(lanes["privateResearchDevelopment"]["healthAndRiskLead"]=="urdDoctorGoddess","private R&D Urd role drift")

p=m["partnerEscalationMilestone"]
need(p["defaultTier"]["tier"]==0 and p["defaultTier"]["member"]=="eggieFounder","default tier drift")
tiers=p["providerTiers"]
need([x["tier"] for x in tiers]==[1,2,3],"provider tier order drift")
need([x["providerId"] for x in tiers]==["googleAi","openAi","openSourceVendorCommunity"],"provider escalation order drift")
need(p["silentPatronSeats"]["antiDaddy"]["externalProviderMapping"]=="UNDEFINED_UNLESS_PROFESSOR_SEALS_ONE","Anti-Daddy mapping overclaim")

b=d["legalAndRoleplayBoundary"]
for k in ("providerInterestIsNotEquity","providerInterestIsNotStockOwnership","providerInterestIsNotLegalPartnership","providerInterestIsNotSponsorshipOrEndorsement"):
    need(b.get(k) is True,f"legal roleplay boundary missing: {k}")

for law in ("providerTierNeverGrantsCorporateAuthority","providerTierNeverGrantsGreen","providerTierNeverGrantsCrown"):
    need(law in p["escalationLaw"],f"provider authority guard missing: {law}")

print(json.dumps({
  "schema":"luhmOs.corporatePanelMilestonesAudit.v1",
  "status":"GREEN_CORPORATE_PANEL_MILESTONES_CANDIDATE" if not errors else "RED_CORPORATE_PANEL_MILESTONES_CANDIDATE",
  "milestones":3,
  "providerTierOrder":["FOUNDER_DEFAULT","GOOGLE","OPENAI","OPEN_SOURCE_VENDOR_COMMUNITY"],
  "errors":errors,
  "crownStatus":"STOP"
},indent=2))
raise SystemExit(1 if errors else 0)
