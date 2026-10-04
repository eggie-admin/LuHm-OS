#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

campaign = load("doctrine/patronageCampaignV1.json")
truth = load("doctrine/SOURCE_OF_TRUTH.json")

checks = [
    ("schema", campaign.get("schema") == "luhmOs.patronageCampaign.v1"),
    ("draftOnly", campaign.get("status") == "PROPOSED_OUTREACH_DRAFTS_ONLY"),
    ("professor", campaign.get("authority") == "Professor"),
    ("lumBoss", campaign.get("boss") == "lum"),
    ("noInsults", campaign.get("toneLaw", {}).get("insults") is False),
    ("noPutdowns", campaign.get("toneLaw", {}).get("negativePersonalPutdowns") is False),
    ("respectExpertise", campaign.get("toneLaw", {}).get("respectProfessorExpertise") is True),
    ("notRecognition", campaign.get("toneLaw", {}).get("recognitionOrTitleIsPrimaryGoal") is False),
    ("patronageGoal", campaign.get("toneLaw", {}).get("practicalPatronageIsPrimaryGoal") is True),
    ("noCredentialSeeking", campaign.get("professorPosition", {}).get("credentialSeeking") is False),
    ("unitApproach", "unitApproach" in campaign.get("projectEvidenceThemes", [])),
    ("razorScope", "razorSharpScope" in campaign.get("projectEvidenceThemes", [])),
    ("rapidWorkarounds", "rapidWorkaroundArchitecture" in campaign.get("projectEvidenceThemes", [])),
    ("phoneFirst", "phoneFirstConversationalEngineering" in campaign.get("projectEvidenceThemes", [])),
    ("noCode", "noCodeAndLowCodeAiAssistedDevelopment" in campaign.get("projectEvidenceThemes", [])),
    ("claimLaw", len(campaign.get("claimLaw", [])) >= 5),
    ("targets", set(campaign.get("targets", {})) == {"openAi","github","samsung","google","fDroid"}),
    ("targetsNoSend", all(v.get("sendAuthority") is False for v in campaign.get("targets", {}).values())),
    ("draftsAllowed", campaign.get("campaignState", {}).get("draftsMayBeCreated") is True),
    ("automaticSendFalse", campaign.get("campaignState", {}).get("automaticSend") is False),
    ("bulkSendFalse", campaign.get("campaignState", {}).get("bulkSend") is False),
    ("professorReview", campaign.get("campaignState", {}).get("professorReviewRequiredBeforeEachSend") is True),
    ("truthBound", truth.get("patronageCampaign", {}).get("contract") == "doctrine/patronageCampaignV1.json"),
    ("crownStop", campaign.get("crownStatus") == "STOP"),
]

failed=[name for name,ok in checks if not ok]
for idx,(name,ok) in enumerate(checks,1):
    print(f"{'PASS' if ok else 'FAIL'} {idx:02d}/{len(checks)} {name}")
if failed:
    raise SystemExit("PATRONAGE_CAMPAIGN_AUDIT=RED failed="+",".join(failed))
print("PATRONAGE_CAMPAIGN_AUDIT=GREEN")
print(f"passes={len(checks)}/{len(checks)}")
print("send=STOP")
print("crown=STOP")
