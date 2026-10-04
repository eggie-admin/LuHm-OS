#!/usr/bin/env python3
import json
import pathlib
import sys

root = pathlib.Path(__file__).resolve().parents[1]
errors = []
path = root / "doctrine/tourniquetGuardrailV1.json"
doc = json.loads(path.read_text(encoding="utf-8"))
require = lambda condition, message: errors.append(message) if not condition else None
require(doc.get("schema") == "luhmOs.tourniquetGuardrail.v1", "schema mismatch")
require(doc.get("kind") == "taskBoundInterruptAndScopeClamp", "Tourniquet must remain an interrupt/scope clamp")
require(doc.get("notAnAutonomousAgent") is True and doc.get("notARepairEngine") is True, "Tourniquet must not become an autonomous agent or repair engine")
interrupt = doc.get("interruptSemantics", {})
require("userCorrectsAssistant" in interrupt.get("triggers", []), "user correction must interrupt")
require(interrupt.get("effect") == "immediatelyPauseActivePlanAndMutation", "correction must pause stale plan before mutation")
require(interrupt.get("rebindTo") == "latestUserInstruction", "resume must rebind to latest user instruction")
clamp = doc.get("clamp", {})
require(clamp.get("routineIntermediateGreen") == "continueAutomaticallyWithinAuthorizedTaskManifest", "routine GREEN must continue within existing authority")
require(clamp.get("reAskOnRoutineGreen") is False, "do not re-ask on routine GREEN")
require("sourceRefDrift" in clamp.get("stopOn", []) and "scopeExpansion" in clamp.get("stopOn", []), "source drift and scope expansion must stop")
require("professorCrownDecision" in clamp.get("stopOn", []), "Professor Crown boundary must stop")
require(doc.get("memory", {}).get("currentSourceBeatsChatMemory") is True, "repo source must outrank chat memory")
canon = json.loads((root / "doctrine/projectChatCanonV1.json").read_text(encoding="utf-8"))
require(canon.get("alwaysLoadedCore", {}).get("tourniquetGuardrail") == "doctrine/tourniquetGuardrailV1.json", "canon must always load Tourniquet doctrine")
require(canon.get("alwaysLoadedCore", {}).get("tourniquetSkill") == "agents/tourniquetGuardrail/SKILL.md", "canon must always load Tourniquet skill")
control = json.loads((root / "doctrine/luhmAiControlPlaneV1.json").read_text(encoding="utf-8"))
require(control.get("tourniquetGuardrailContract") == "doctrine/tourniquetGuardrailV1.json", "control plane binding missing")
truth = json.loads((root / "doctrine/SOURCE_OF_TRUTH.json").read_text(encoding="utf-8"))
require(truth.get("tourniquetGuardrail", {}).get("contract") == "doctrine/tourniquetGuardrailV1.json", "source truth pointer missing")
for rel in ("agents/tourniquetGuardrail/SKILL.md", "agents/lum/SKILL.md", "agents/urdMutationOni/SKILL.md", "agents/belldandyQualityOni/SKILL.md", "agents/witchingHourCoding/SKILL.md", "agents/projectChatBootstrap/SKILL.md"):
    content = (root / rel).read_text(encoding="utf-8")
    require("tourniquetGuardrailV1.json" in content, f"{rel} must bind to Tourniquet contract")
if errors:
    print(json.dumps({"status":"red","errors":errors},indent=2))
    sys.exit(1)
print(json.dumps({"status":"greenTourniquetContract","interrupts":len(interrupt.get("triggers",[])),"stopConditions":len(clamp.get("stopOn",[])),"autonomousAgent":False},indent=2))
