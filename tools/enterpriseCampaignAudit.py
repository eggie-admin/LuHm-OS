#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def load(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))

orientation=load("doctrine/enterpriseOrientationBridgeV1.json")
launch=load("doctrine/campaignLaunchKitV1.json")
truth=load("doctrine/currentSourceTruthV3.json")
workbench=load("doctrine/unifiedCampaignWorkbenchV1.json")
roadmap=load("doctrine/chatDeploymentRoadmapV1.json")
patronage=load("doctrine/patronageCampaignV1.json")

checks=[
("orientationSchema",orientation.get("schema")=="luhmOs.enterpriseOrientationBridge.v1"),
("orientationProfessor",orientation.get("authority")=="Professor"),
("orientationLum",orientation.get("president")=="lum"),
("orientationRoleplayNoAuthority",orientation.get("roleplayLaw",{}).get("roleplayMayNotChangeAuthority") is True),
("orientationNoFakeGreen",orientation.get("roleplayLaw",{}).get("roleplayMayNotUpgradeUnknownToGreen") is True),
("openDaddyPrimary",orientation.get("headquarters",{}).get("primaryConversationalHeadquarters",{}).get("nickname")=="openDaddy"),
("bigBrotherSecondary",orientation.get("headquarters",{}).get("secondaryCapacityHeadquarters",{}).get("nickname")=="bigBrother"),
("gitDaddySource",orientation.get("headquarters",{}).get("sourceForge",{}).get("nickname")=="gitDaddy"),
("cloudflareCrown",orientation.get("headquarters",{}).get("trafficController",{}).get("publicActivationRequiresCrown") is True),
("samsungAntennaBound",orientation.get("headquarters",{}).get("fieldSubsidiary",{}).get("antennaContract")=="doctrine/samsungAntennaV1.json"),
("skuldItLead",orientation.get("cabinetIntroductions",{}).get("skuldResearch",{}).get("title")=="headOfItResearchAndCompatibility"),
("urdDoctor",orientation.get("cabinetIntroductions",{}).get("urdDoctorGoddess",{}).get("title")=="doctorLogisticsAndEvidenceAdjudication"),
("belldandySecretary",orientation.get("cabinetIntroductions",{}).get("belldandySecretary",{}).get("title")=="secretaryStateAndEnterpriseReadiness"),
("yumeCampaignLead",orientation.get("cabinetIntroductions",{}).get("yume",{}).get("title")=="creativeCampaignAndArtProductionLead"),
("icebreakerNoLegacy",orientation.get("employeeIcebreaker",{}).get("legacyAgentsParticipate") is False),
("launchSchema",launch.get("schema")=="luhmOs.campaignLaunchKit.v1"),
("launchMilestone",launch.get("milestoneId")=="letsMakeMoneyForCorporations"),
("launchYume",launch.get("creativeLead")=="yume"),
("launchUrd",launch.get("evidenceLead")=="urdDoctorGoddess"),
("launchBelldandy",launch.get("recordsLead")=="belldandySecretary"),
("launchSkuld",launch.get("researchLead")=="skuldResearch"),
("launchBigBrother",launch.get("providerAssist")=="bigBrother"),
("launchUnits",len(launch.get("firstWaveUnits",[]))>=7),
("launchNoSend",launch.get("automaticSend") is False),
("launchNoPublish",launch.get("automaticPublication") is False),
("launchNoCrossPost",launch.get("automaticCrossPost") is False),
("toneNoPutdowns",launch.get("toneLaw",{}).get("negativePersonalPutdowns") is False),
("tonePatronage",launch.get("toneLaw",{}).get("practicalPatronageNotRecognition") is True),
("truthOrientation",truth.get("enterpriseOrientation",{}).get("contract")=="doctrine/enterpriseOrientationBridgeV1.json"),
("truthCampaign",truth.get("campaignLayer",{}).get("campaignLaunchKit")=="doctrine/campaignLaunchKitV1.json"),
("workbenchLaunch",workbench.get("launchKit")=="doctrine/campaignLaunchKitV1.json"),
("roadmapOrientation",roadmap.get("orientationBridge")=="doctrine/enterpriseOrientationBridgeV1.json"),
("patronageNoSend",patronage.get("campaignState",{}).get("automaticSend") is False),
("campaignDraftPresent",(ROOT/"campaign/first-campaign-wave.md").is_file()),
("crownStop",orientation.get("crownStatus")=="STOP" and launch.get("crownStatus")=="STOP")
]
failed=[n for n,o in checks if not o]
for i,(n,o) in enumerate(checks,1): print(f"{'PASS' if o else 'FAIL'} {i:02d}/{len(checks)} {n}")
if failed: raise SystemExit("ENTERPRISE_CAMPAIGN_AUDIT=RED failed="+",".join(failed))
print("ENTERPRISE_CAMPAIGN_AUDIT=GREEN")
print(f"passes={len(checks)}/{len(checks)}")
print("send=STOP")
print("publication=STOP")
print("crown=STOP")
