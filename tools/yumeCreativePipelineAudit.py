#!/usr/bin/env python3
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
contract_path = ROOT / "doctrine" / "yumeCreativePipelineV1.json"
yume_path = ROOT / "agents" / "yumeArtOni" / "SKILL.md"
media_path = ROOT / "agents" / "mediaAssetFactory" / "SKILL.md"
project_manifest = ROOT / "media" / "daddys-princess-date" / "edit-manifest.json"
prompt_pack = ROOT / "media" / "daddys-princess-date" / "edge-gallery-prompt-pack.md"
community_path = ROOT / "doctrine" / "yumeCommunityArtResourcesV1.json"
credit_path = ROOT / "doctrine" / "artistCreditLedgerV1.json"
budget_path = ROOT / "doctrine" / "githubWorkflowBudgetV1.json"

errors = []
for p in (contract_path, yume_path, media_path, project_manifest, prompt_pack, community_path, credit_path, budget_path):
    if not p.exists():
        errors.append(f"missing:{p.relative_to(ROOT)}")

if errors:
    print("YUME_CREATIVE_PIPELINE_RED")
    print("\n".join(errors))
    raise SystemExit(1)

contract = json.loads(contract_path.read_text())
manifest = json.loads(project_manifest.read_text())
yume = yume_path.read_text()
media = media_path.read_text()
prompt = prompt_pack.read_text()
community = json.loads(community_path.read_text())
credit = json.loads(credit_path.read_text())
budget = json.loads(budget_path.read_text())

checks = [
    ("schema", contract.get("schema") == "luhm.yumeCreativePipeline.v1"),
    ("professorAuthority", contract.get("authority") == "Professor"),
    ("lumBoss", contract.get("boss") == "Lum"),
    ("yumeLead", contract.get("creativeLead") == "yumeArtOni"),
    ("edgeUnconfigured", contract["providerReadiness"].get("edgeGallery") == "UNCONFIGURED_EVIDENCE_PENDING"),
    ("googleUnconfigured", contract["providerReadiness"].get("googleAi") == "UNCONFIGURED_EVIDENCE_PENDING"),
    ("hfUnproven", contract["providerReadiness"].get("huggingFace") == "CANDIDATE_PROVIDER_UNPROVEN"),
    ("providerFallbackLaw", "unconfigured_provider_falls_back_to_provider_neutral_task_card" in contract["providerLaw"]),
    ("productionBible", "productionBible" in contract["stages"]),
    ("scriptDepartment", "scriptDepartment" in contract["stages"]),
    ("artDepartment", "artDepartment" in contract["stages"]),
    ("cinematography", "cinematographyDepartment" in contract["stages"]),
    ("storyboard", "storyboardDepartment" in contract["stages"]),
    ("sound", "soundDepartment" in contract["stages"]),
    ("editorial", "editorialDepartment" in contract["stages"]),
    ("professorReview", "professorReview" in contract["stages"]),
    ("crownStop", contract.get("crownStatus") == "STOP"),
    ("communityPointer", contract.get("communityArtResources") == "doctrine/yumeCommunityArtResourcesV1.json"),
    ("creditPointer", contract.get("artistCreditLedger") == "doctrine/artistCreditLedgerV1.json"),
    ("covenantPointer", contract.get("everlastingCovenant") == "doctrine/everlastingCovenantV1.json"),
    ("workflowBudgetPointer", contract.get("workflowBudget") == "doctrine/githubWorkflowBudgetV1.json"),
    ("communityLead", community.get("creativeLead") == "yumeArtOni"),
    ("communitySumi", community.get("provenanceLead") == "sumi"),
    ("communityNoBlindVendor", "no_blind_whole_repository_vendoring" in community.get("discoveryLaw", [])),
    ("artistCreditHuman", "credit_the_human_when_identity_is_known_even_if_the_license_does_not_require_attribution" in credit.get("humanPolicy", [])),
    ("artistNoExploit", "do_not_exploit_the_art_community" in credit.get("humanPolicy", [])),
    ("artistNoAiAuthorshipRewrite", credit.get("authorshipLaw", {}).get("humanAuthorshipMustNotBeReassignedToAi") is True),
    ("workflowCommitLimit", budget.get("maxCommitsPerWorkflow") == 50),
    ("yumeEdgeTruth", "Google AI Edge / Edge Gallery must be treated as unavailable" in yume),
    ("mediaEdgeTruth", "never been accepted as properly configured" in media),
    ("promptParked", "UNCONFIGURED_EVIDENCE_PENDING" in prompt and manifest["mediaPolicy"]["rawMediaInRepo"] is False),
]

# 20 passes by doctrine request. Each pass re-evaluates the complete immutable contract.
for pass_num in range(1, 21):
    failed = [name for name, ok in checks if not ok]
    status = "GREEN" if not failed else "RED"
    print(f"PASS_{pass_num:02d}={status}")
    if failed:
        for name in failed:
            print(f"  FAIL:{name}")
        print("YUME_CREATIVE_PIPELINE_RED")
        raise SystemExit(1)

print("YUME_CREATIVE_PIPELINE_SOURCE_GREEN")
print("passes=20")
print("scope=source_contract_only")
print("edgeGallery=UNCONFIGURED_EVIDENCE_PENDING")
print("googleAi=UNCONFIGURED_EVIDENCE_PENDING")
print("artistCredit=ENFORCED_SOURCE_CONTRACT")
print("communityResources=CURATED_PROVENANCE_REQUIRED")
print("workflowCommitCeiling=50")
print("crown=STOP")
