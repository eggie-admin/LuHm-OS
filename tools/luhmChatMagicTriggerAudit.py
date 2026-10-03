#!/usr/bin/env python3
import json
import pathlib
import re
import sys
import tomllib

root = pathlib.Path(__file__).resolve().parents[1]
errors = []
contract = json.loads((root / "doctrine/luhmChatMagicTriggerV1.json").read_text())
expected_phrases = ["I invoke the old magic", "so let it be written, so let it be done"]
if contract.get("trigger", {}).get("operator") != "AND":
    errors.append("magic trigger must use AND")
if contract.get("trigger", {}).get("allOf") != expected_phrases:
    errors.append("both canonical trigger phrases must match")
if contract.get("trigger", {}).get("eitherPhraseAloneActivates") is not False:
    errors.append("single-phrase activation must be disabled")
if contract.get("trigger", {}).get("authorityEffect") != "none":
    errors.append("trigger must not grant authority")
if contract.get("projectLibrary", {}).get("workingDevelopmentTitle") != "Project Hydra":
    errors.append("Project Hydra working title missing")
if contract.get("projectLibrary", {}).get("acronym", {}).get("expansion") != ["Linux", "Unix", "Hydra", "Manifest"]:
    errors.append("LuHm OS acronym expansion mismatch")
expected_agents = ["urdDoctorGoddess", "belldandySecretary", "skuldResearch", "yume"]
if contract.get("defaults", {}).get("projectAgentSet") != expected_agents:
    errors.append("default custom-agent set mismatch")
for alias, agent in contract.get("agentAliases", {}).get("nicknameRouting", {}).items():
    if agent != "yume":
        errors.append(f"Yume nickname routes outside canonical identity: {alias}")
for name in expected_agents:
    path = root / ".codex/agents" / f"{name}.toml"
    try:
        profile = tomllib.loads(path.read_text())
        if profile.get("name") != name:
            errors.append(f"custom-agent name mismatch: {path}")
        if "canonical skill" not in profile.get("developer_instructions", "").lower():
            errors.append(f"missing canonical skill binding: {path}")
    except Exception as exc:
        errors.append(f"invalid custom-agent TOML {path}: {exc}")
config = tomllib.loads((root / ".codex/config.toml").read_text())
if config.get("agents", {}).get("max_concurrent_threads_per_session") != 4:
    errors.append("custom-agent concurrency must fit four defaults")
if errors:
    print(json.dumps({"status": "red", "errors": errors}, indent=2))
    sys.exit(1)
print(json.dumps({"status": "greenChatMagicTriggerContract", "defaultCustomAgentCount": len(expected_agents), "triggerPhraseCount": len(expected_phrases)}, indent=2))
