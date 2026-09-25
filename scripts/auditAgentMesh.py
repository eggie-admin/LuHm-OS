#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
roles = json.loads((ROOT / "agents/luhm-agent-mesh/roles.json").read_text())
integrations = json.loads((ROOT / "agents/luhm-agent-mesh/integrations.json").read_text())
doctrine = json.loads((ROOT / "doctrine/agentMesh-20260925.json").read_text())
roleplay = json.loads((ROOT / "doctrine/lumCodingRoleplay-20260925.json").read_text())
skill = (ROOT / "skills/luhm-agent-mesh/SKILL.md").read_text()
reference = (ROOT / "skills/luhm-agent-mesh/references/coding-roleplay.md").read_text()

helper_ids = {h["role_id"] for h in roles["helpers"]}
assert roles["boss"]["role_id"] == "Lum"
assert helper_ids == {"Context", "Build", "Research", "Critic"}
assert roles["limits"]["max_parallel_helpers"] <= 3
assert roles["limits"]["max_delegation_depth"] == 1
assert roles["limits"]["recursive_recruitment"] is False
assert roles["limits"]["parallel_writes"] is False
assert roles["limits"]["evidence_by_reference"] is True
assert roles["executor"]["agent"] is False
assert roles["executor"]["kind"] == "DETERMINISTIC_EDGE"

assert doctrine["roles"]["boss"] == "Lum"
assert doctrine["status"] == "CANDIDATE_NOT_PROMOTED"
assert doctrine["production_actions_authorized_by_this_manifest"] is False
assert doctrine["boot_contract"]["auto_load_for_luhm_project_work"] is True
assert doctrine["boot_contract"]["coding_roleplay_doctrine"] == "doctrine/lumCodingRoleplay-20260925.json"
assert doctrine["boot_contract"]["presentation_authority"] == "PRESENTATION_ONLY"

assert integrations["integrations"]["github"]["role"] == "CANONICAL_CODE_SOURCE"
assert integrations["integrations"]["google_drive"]["canonical_code"] is False
assert integrations["integrations"]["fastapi_cloud"]["android_runtime_authority"] is False
assert integrations["integrations"]["modal"]["policy_authority"] is False
assert integrations["integrations"]["mixpanel"]["deny_payloads"]
assert integrations["integrations"]["gmail"]["default_action"] == "DRAFT"

assert roleplay["status"] == "CANDIDATE_NOT_PROMOTED"
assert roleplay["authority"] == "Professor"
assert roleplay["agent"] == "Lum"
assert roleplay["presentation_layer"]["authority"] == "PRESENTATION_ONLY"
assert roleplay["risk_model"]["green_requires_evidence"] is True
assert roleplay["risk_model"]["user_saying_green_is_not_evidence"] is True
assert roleplay["production_actions_authorized_by_this_manifest"] is False

commands = roleplay["commands"]
for green in ("SYSTEM", "AUDIT", "SANITY", "APPROACH"):
    assert commands[green]["risk"] == "GREEN"
for amber in ("INGEST", "MUTATE", "REROLL", "SEAL"):
    assert commands[amber]["risk"] == "AMBER"
for red in ("PROMOTE", "DEPLOY", "PURGE"):
    assert commands[red]["risk"] == "RED"
assert commands["GREEN"]["risk"] == "VERDICT_ONLY"
assert commands["CROWN"]["risk"] == "AUTHORIZATION"
assert commands["MUTATE"]["never_implies"] == ["main_merge", "production_deploy", "publication"]
assert commands["SEAL"]["never_implies"] == ["promotion", "merge", "release"]
assert "Crown never overrides BLACK" in commands["CROWN"]["rules"]
assert "authorization expires when target identity changes" in commands["CROWN"]["rules"]
assert "proprietary_or_unlicensed_donor_code" in commands["INGEST"]["black_conditions"]

locks = roleplay["locks"]
assert locks["secret_print"] == "BLACK_FORBIDDEN"
assert locks["false_green"] == "BLACK_FORBIDDEN"
assert locks["authority_bypass"] == "BLACK_FORBIDDEN"
assert locks["main_merge"] == "RED_LOCKED_CROWN_REQUIRED"
assert locks["production_deploy"] == "RED_LOCKED_CROWN_REQUIRED"

assert "AI proposes. Policy authorizes. CI proves. Human promotes." in skill
assert "PHANTOM_CODING_MODE" in skill
assert "is a verdict, never an authorization token." in skill and "`GREEN`" in skill
assert "continue until green" in skill
assert "Kanabo Gate" in skill
assert "Oni-Kumo" in skill and "Oni-Tetsu" in skill and "Oni-Sumi" in skill and "Oni-Ibara" in skill
assert "A good reply can feel like a heist briefing and still read like an audit log." in reference

print("LUHM AGENT MESH AUDIT GREEN")
print({
    "boss": roles["boss"]["role_id"],
    "helpers": sorted(helper_ids),
    "max_parallel_helpers": roles["limits"]["max_parallel_helpers"],
    "delegation_depth": roles["limits"]["max_delegation_depth"],
    "executor": roles["executor"]["display_name"],
    "source_authority": integrations["integrations"]["github"]["role"],
    "coding_roleplay": roleplay["presentation_layer"]["name"],
    "green_is_verdict_only": commands["GREEN"]["risk"] == "VERDICT_ONLY",
})
