#!/usr/bin/env python3
import json
from pathlib import Path

reg=json.loads(Path("doctrine/workflowPluginRegistryV1.json").read_text())
esc=json.loads(Path("doctrine/operationTitan7EscalationV1.json").read_text())
js=Path("frontEnd/jquery/luhm.workflowPlugins.js").read_text()
skill=Path("agents/deepDungeon/SKILL.md").read_text()

assert reg["defaultRuntime"]=="luhmAgentMesh"
assert reg["pluginLaw"]["specialCaseOnly"] is True
assert reg["pluginLaw"]["mayNotBecomeDefaultWorkflow"] is True
assert reg["pluginLaw"]["recursiveRecruitment"] is False

titan=reg["plugins"]["operationTitan7"]
assert titan["entryPoint"]=="$.operationTitan7"
assert titan["releaseTo"]=="luhmAgentMesh"
assert titan["capabilityBroker"]=="aiApiBoss"
assert titan["directVendorApiAllowed"] is False
assert titan["escalationContract"]=="doctrine/operationTitan7EscalationV1.json"
assert titan["tiers"]==["ffs","scorchedEarth","finalForm"]
assert esc["tiers"]["ffs"]["hardPasses"]==25
assert esc["tiers"]["scorchedEarth"]["hardPasses"]==50
assert esc["tiers"]["finalForm"]["mode"]=="absoluteRipOutAndReplaceAudit"

deep=reg["plugins"]["deepDungeon"]
assert deep["entryPoint"]=="$.deepDungeon"
assert deep["agentMode"]=="oniMiniAgentOnly"
assert deep["oniSkill"]=="agents/deepDungeon/SKILL.md"
assert deep["capabilityBroker"]=="aiApiBoss"
assert deep["directVendorApiAllowed"] is False
assert deep["humanCenteredTrigger"]["naturalLanguageFirst"] is True

assert "$.operationTitan7 = function" in js
assert "$.operationTitan7Intent = operationTitan7Intent" in js
assert "$.deepDungeon = function" in js
assert "$.deepDungeonIntent = deepDungeonIntent" in js
assert 'trigger("luhm:workflow:operationTitan7"' in js
assert 'trigger("luhm:workflow:deepDungeon"' in js

assert "Oni mini-agent" in skill
assert "oniMiniAgentOnly" in skill
assert "AI API Boss" in skill
assert "No coding" in skill
assert "No recursive recruitment" in skill
assert "Memory is navigation context" in skill

print("WORKFLOW PLUGIN REGISTRY GREEN")
