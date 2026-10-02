#!/usr/bin/env python3
import json,re
from pathlib import Path
reg=json.loads(Path("doctrine/workflowPluginRegistryV1.json").read_text())
js=Path("frontEnd/jquery/luhm.workflowPlugins.js").read_text()
skill=Path("agents/deepDungeon/SKILL.md").read_text()
assert reg["defaultRuntime"]=="luhmAgentMesh"
assert reg["pluginLaw"]["specialCaseOnly"] is True
assert reg["pluginLaw"]["mayNotBecomeDefaultWorkflow"] is True
assert reg["plugins"]["operationTitan7"]["entryPoint"]=="$.operationTitan7"
assert reg["plugins"]["operationTitan7"]["releaseTo"]=="luhmAgentMesh"
assert reg["plugins"]["deepDungeon"]["entryPoint"]=="$.deepDungeon"
assert reg["plugins"]["deepDungeon"]["agentMode"]=="miniAgentOnly"
assert "$.operationTitan7 = function" in js
assert "$.deepDungeon = function" in js
assert 'trigger("luhm:workflow:operationTitan7"' in js
assert 'trigger("luhm:workflow:deepDungeon"' in js
assert "miniAgentOnly" in skill
for forbidden in ("No coding","No recursive recruitment"):
    assert forbidden in skill
assert "Memory is navigation context" in skill
print("WORKFLOW PLUGIN REGISTRY GREEN")
