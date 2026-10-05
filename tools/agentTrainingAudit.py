#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_json(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

seal = load_json("doctrine/agentTrainingSealV1.json")
control = load_json("doctrine/luhmAiControlPlaneV1.json")
canon = load_json("doctrine/projectChatCanonV1.json")
covenant = load_json("doctrine/everlastingCovenantV1.json")

errors = []
agents = control.get("agents", {})
required = seal.get("requiredAgents", [])
expected_count = seal.get("expectedAgentCount")

if control.get("boss") != "lum":
    errors.append("controlPlane.boss must be lum")
if control.get("authority") != "Professor":
    errors.append("controlPlane.authority must be Professor")
if control.get("crownStatus") != "STOP":
    errors.append("controlPlane.crownStatus must be STOP")
if control.get("invariants", {}).get("lumOnlyConversationalBoss") is not True:
    errors.append("lumOnlyConversationalBoss must be true")
if control.get("invariants", {}).get("professorFinalAuthority") is not True:
    errors.append("professorFinalAuthority must be true")
if control.get("invariants", {}).get("unknownIsNotGreen") is not True:
    errors.append("unknownIsNotGreen must be true")
if control.get("invariants", {}).get("providerOutputIsNotProofUntilReconciled") is not True:
    errors.append("providerOutputIsNotProofUntilReconciled must be true")

if len(agents) != expected_count:
    errors.append(f"agent count mismatch: expected {expected_count}, got {len(agents)}")

missing = [agent_id for agent_id in required if agent_id not in agents]
extra = [agent_id for agent_id in agents if agent_id not in required]
if missing:
    errors.append("missing required agents: " + ", ".join(missing))
if extra:
    errors.append("unsealed extra agents: " + ", ".join(extra))

required_fields = [
    "displayName",
    "kind",
    "skillPath",
    "defaultAuthority",
    "capabilities",
    "forbidden",
    "parallelClass",
    "speaksTo",
    "mayRecruit",
    "maySelfApprove",
]

for agent_id in required:
    agent = agents.get(agent_id)
    if not isinstance(agent, dict):
        continue
    absent = [field for field in required_fields if field not in agent]
    if absent:
        errors.append(f"{agent_id}: missing fields {', '.join(absent)}")
        continue
    if not isinstance(agent["capabilities"], list) or not agent["capabilities"]:
        errors.append(f"{agent_id}: capabilities must be a non-empty list")
    if not isinstance(agent["forbidden"], list) or not agent["forbidden"]:
        errors.append(f"{agent_id}: forbidden must be a non-empty list")
    if agent["mayRecruit"] is not False:
        errors.append(f"{agent_id}: mayRecruit must be false")
    if agent["maySelfApprove"] is not False:
        errors.append(f"{agent_id}: maySelfApprove must be false")
    skill = ROOT / agent["skillPath"]
    if not skill.is_file():
        errors.append(f"{agent_id}: skill path missing: {agent['skillPath']}")
    if agent_id == "lum":
        if agent["speaksTo"] != "Professor":
            errors.append("lum: speaksTo must be Professor")
    elif agent["speaksTo"] != "lum":
        errors.append(f"{agent_id}: speaksTo must be lum")

resident = seal.get("residentCore", [])
cabinet = control.get("goddessCabinet", {}).get("members", [])
if resident != cabinet:
    errors.append(f"residentCore mismatch: seal={resident} controlPlane={cabinet}")

expected_guardrail = [
    "sanityCheck",
    "audit",
    "ingest",
    "mutation",
    "test",
    "apply",
    "continue",
    "deploy",
]
if control.get("covenant", {}).get("guardRail") != expected_guardrail:
    errors.append("controlPlane covenant guardRail mismatch")
if covenant.get("guardRail", {}).get("orderedStates") != expected_guardrail:
    errors.append("everlasting covenant orderedStates mismatch")
if canon.get("boss") != "lum":
    errors.append("projectChatCanon boss must be lum")
if canon.get("crownStatus") != "stop":
    errors.append("projectChatCanon crownStatus must be stop")

if errors:
    print("AGENT_TRAINING_CONTRACT=RED")
    for item in errors:
        print(f"ERROR: {item}")
    raise SystemExit(1)

print("AGENT_TRAINING_CONTRACT=GREEN")
print(f"trainedAgents={len(required)}")
print("scope=behavioralContractsAndRouting")
print("modelWeightFineTuning=false")
print("crownStatus=STOP")
