#!/usr/bin/env python3
import json
import pathlib
import re
import sys
import tomllib

root = pathlib.Path(__file__).resolve().parents[1]
errors = []
network = json.loads((root / "doctrine/luhmNetworkTransportV1.json").read_text())
intent = network.get("intendedArchitecture", {})
local = intent.get("localIPv4ControllerSocket", {})
tunnel = intent.get("cloudflareTunnel", {})
remote = intent.get("remoteServiceSockets", {})
public = intent.get("inboundPublicClient", {})
current = network.get("currentDocumentedState", {})
server_source = (root / "host/mcp/luhmMcpServer.py").read_text()
deployment = (root / "plugins/luhm-os/DEPLOYMENT.md").read_text()

checks = [
    (network.get("status") == "candidateReview", "network contract must remain candidate review"),
    (local.get("address") == "127.0.0.1", "local HTTP must bind to IPv4 loopback"),
    (local.get("protocol") == "http" and local.get("encrypted") is False, "local HTTP hop must be labeled plaintext"),
    (local.get("scope") == "sameHostLoopbackOnly", "local HTTP must be loopback scoped"),
    ("0.0.0.0" in local.get("bindAddressesForbidden", []), "all-interface bind must be forbidden"),
    (tunnel.get("connectorToCloudflare") == "outboundEncryptedTunnel", "Cloudflare tunnel hop must be encrypted"),
    (tunnel.get("automaticallyUpgradesLocalHttpToTls") is False, "local HTTP must not be described as auto-upgraded"),
    (tunnel.get("localOriginHopEncrypted") is False, "HTTP origin hop must remain explicitly plaintext"),
    (public.get("requiredProtocol") == "https", "public client transport must require HTTPS"),
    (public.get("redirectProtectsInitialHttpRequest") is False, "redirect must not be treated as encryption"),
    (remote.get("requiredProtocol") == "https" and remote.get("peerCertificateValidation") is True, "remote service clients must validate TLS"),
    (current.get("cloudflareRole") == "authoritativeDnsOnlyForCurrentRenderEndpoint", "current Render/DNS-only state must remain distinct"),
    (current.get("cloudflareTunnel") == "notConfiguredOrProvenInCurrentSource", "do not claim a tunnel is deployed"),
    ('LOCAL_HOST = "127.0.0.1"' in server_source and "host=LOCAL_HOST" in server_source, "local MCP profile must bind IPv4 loopback"),
    ("The workstation is never an origin for the public endpoint." in deployment, "current runbook must keep workstation unpublished"),
    ("DNS only" in deployment, "current runbook must preserve DNS-only Render state"),
    (network.get("statusClaims", {}).get("tunnelRuntime") == "unknownNotRunningClaimed", "runtime status must remain unknown"),
]
for ok, message in checks:
    if not ok:
        errors.append(message)

magic = json.loads((root / "doctrine/luhmChatMagicTriggerV1.json").read_text())
voice = magic.get("voiceDictationAliases", {})
if voice.get("scope") != "chatVoiceDictationOnly" or voice.get("nickname") != "DreamChan":
    errors.append("DreamChan must be scoped to chat voice dictation")
if voice.get("canonicalTarget") != "yume" or voice.get("canonicalAgentIdentityCreated") is not False:
    errors.append("DreamChan must target the existing Yume identity")
if voice.get("typedTextBehavior") != "noSpecialNormalizationOrDispatch":
    errors.append("typed text must not activate the DreamChan alias")
if "agentAliases" in magic:
    errors.append("broad legacy agent alias map must be absent")
canon = json.loads((root / "doctrine/projectChatCanonV1.json").read_text())
if canon.get("alwaysLoadedCore", {}).get("networkTransport") != "doctrine/luhmNetworkTransportV1.json":
    errors.append("network doctrine must be part of the always-loaded core")
source = json.loads((root / "doctrine/SOURCE_OF_TRUTH.json").read_text())
if source.get("networkTransport", {}).get("noRuntimeProofClaim") is not True:
    errors.append("source truth must preserve candidate/runtime separation")

for name in ("urdDoctorGoddess", "belldandySecretary", "skuldResearch", "yume"):
    path = root / ".codex/agents" / f"{name}.toml"
    try:
        agent = tomllib.loads(path.read_text())
        if "doctrine/luhmNetworkTransportV1.json" not in agent.get("developer_instructions", ""):
            errors.append(f"{name} profile omits network doctrine")
    except Exception as exc:
        errors.append(f"invalid custom-agent TOML {path}: {exc}")

if errors:
    print(json.dumps({"status": "red", "runtimeVerified": False, "errors": errors}, indent=2))
    sys.exit(1)
print(json.dumps({"status": "candidateContractValid", "runtimeVerified": False, "checks": len(checks), "activeTunnelClaim": False}, indent=2))
