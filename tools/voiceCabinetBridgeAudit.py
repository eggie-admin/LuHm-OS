#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
errors = []

def need(ok, message):
    if not ok:
        errors.append(message)

bridge_path = root / "doctrine/voiceCabinetBridgeV1.json"
deploy_path = root / "doctrine/agentSystemDeploymentV1.json"
lum_path = root / "agents/lum/SKILL.md"

for path in (bridge_path, deploy_path, lum_path):
    need(path.is_file(), f"missing {path.relative_to(root)}")

if bridge_path.is_file():
    bridge = json.loads(bridge_path.read_text(encoding="utf-8"))
    need(bridge.get("schema") == "luhmOs.voiceCabinetBridge.v1", "voice bridge schema drift")
    need(bridge.get("boss") == "lum", "Lum must remain voice cabinet boss")
    need(bridge.get("authority") == "Professor", "Professor authority drift")
    need(bridge.get("routingLaw", {}).get("explicitNamedWorkersAreHonored") is True, "named-worker voice routing missing")
    example = bridge.get("routingLaw", {}).get("exampleExplicitRoute", {})
    need(example.get("workers") == ["skuldResearch", "urdDoctorGoddess"], "Skuld/Urd explicit route drift")
    projection = bridge.get("voiceProjection", {})
    need(projection.get("independentPerAgentTtsVoicesProven") is False, "unproven independent voice claim")
    need(projection.get("mayClaimDistinctAudibleAgentVoices") is False, "distinct audible voice claim must fail closed")
    gate = bridge.get("hostCapabilityGate", {})
    need(gate.get("ifUnavailable") == "PLATFORM_CAPABILITY_UNPROVEN", "platform capability fallback drift")
    need(gate.get("mustNotFabricateToolCalls") is True, "tool-call fabrication guard missing")
    need(gate.get("mustNotFabricateBackgroundWorkers") is True, "background-worker fabrication guard missing")
    need(bridge.get("promotion") is False and bridge.get("crownStatus") == "STOP", "voice bridge authority leak")

if deploy_path.is_file():
    deploy = json.loads(deploy_path.read_text(encoding="utf-8"))
    surface = deploy.get("deploymentSurfaces", {}).get("voiceConversation", {})
    need(surface.get("adapter") == "doctrine/voiceCabinetBridgeV1.json", "deployment registry missing voice bridge")
    need(surface.get("mode") == "lumMediatedCabinetTurn", "voice deployment mode drift")
    need(surface.get("roster") == "residentCore", "voice surface should use resident core by default")
    need(surface.get("livePlatformCapabilityProven") is False, "live platform capability must remain unproven")
    need(surface.get("independentPerAgentAudioVoicesProven") is False, "independent agent audio must remain unproven")

if lum_path.is_file():
    text = lum_path.read_text(encoding="utf-8")
    need("doctrine/voiceCabinetBridgeV1.json" in text, "Lum skill missing voice bridge binding")
    need("PLATFORM_CAPABILITY_UNPROVEN" in text, "Lum skill missing fail-closed platform state")
    need("named speaker segments" in text.lower(), "Lum skill missing named speaker projection")

print(json.dumps({
    "schema": "luhmOs.voiceCabinetBridgeAudit.v1",
    "status": "greenVoiceCabinetBridgeCandidate" if not errors else "redVoiceCabinetBridgeCandidate",
    "livePlatformCapabilityProven": False,
    "independentPerAgentAudioVoicesProven": False,
    "crownStatus": "STOP",
    "errors": errors
}, indent=2))
raise SystemExit(1 if errors else 0)
