#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
roles = json.loads((ROOT / "agents/luhm-agent-mesh/roles.json").read_text())
integrations = json.loads((ROOT / "agents/luhm-agent-mesh/integrations.json").read_text())
doctrine = json.loads((ROOT / "doctrine/agentMesh-20260925.json").read_text())
skill = (ROOT / "skills/luhm-agent-mesh/SKILL.md").read_text()

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
assert integrations["integrations"]["github"]["role"] == "CANONICAL_CODE_SOURCE"
assert integrations["integrations"]["google_drive"]["canonical_code"] is False
assert integrations["integrations"]["fastapi_cloud"]["android_runtime_authority"] is False
assert integrations["integrations"]["modal"]["policy_authority"] is False
assert integrations["integrations"]["mixpanel"]["deny_payloads"]
assert integrations["integrations"]["gmail"]["default_action"] == "DRAFT"
assert "AI proposes. Policy authorizes. CI proves. Human promotes." in skill
assert "Kanabo Gate" in skill
assert "Oni-Kumo" in skill and "Oni-Tetsu" in skill and "Oni-Sumi" in skill and "Oni-Ibara" in skill

print("LUHM AGENT MESH AUDIT GREEN")
print({
    "boss": roles["boss"]["role_id"],
    "helpers": sorted(helper_ids),
    "max_parallel_helpers": roles["limits"]["max_parallel_helpers"],
    "delegation_depth": roles["limits"]["max_delegation_depth"],
    "executor": roles["executor"]["display_name"],
    "source_authority": integrations["integrations"]["github"]["role"],
})
