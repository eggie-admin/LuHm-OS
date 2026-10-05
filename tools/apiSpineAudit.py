#!/usr/bin/env python3
import json
import re
from pathlib import Path

root=Path(__file__).resolve().parents[1]
errors=[]

def need(ok,msg):
    if not ok:
        errors.append(msg)

spine=json.loads((root/"doctrine/apiSpineV1.json").read_text(encoding="utf-8"))
traffic=json.loads((root/"doctrine/cloudflareAirTrafficControllerV1.json").read_text(encoding="utf-8"))
control=json.loads((root/"doctrine/luhmAiControlPlaneV1.json").read_text(encoding="utf-8"))
economy=json.loads((root/"doctrine/providerEconomyV1.json").read_text(encoding="utf-8"))
openai=json.loads((root/"doctrine/openAiDeploymentV3.json").read_text(encoding="utf-8"))
google=json.loads((root/"doctrine/bigBrotherCovenantV1.json").read_text(encoding="utf-8"))
truth=json.loads((root/"doctrine/currentSourceTruthV3.json").read_text(encoding="utf-8"))
mcp_scope=json.loads((root/"doctrine/mcpEnterpriseScopeV2.json").read_text(encoding="utf-8"))
opening=json.loads((root/"doctrine/openingDayStaffTrainingV1.json").read_text(encoding="utf-8"))
python_law=json.loads((root/"doctrine/python3ControlPlaneLawV1.json").read_text(encoding="utf-8"))
resolver=(root/"host/api/luhmApiSpine.py").read_text(encoding="utf-8")
server=(root/"host/mcp/luhmMcpServer.py").read_text(encoding="utf-8")
harness=(root/"host/mcp/luhmHarness.py").read_text(encoding="utf-8")
widget=(root/"host/harness/widget.html").read_text(encoding="utf-8")
dns=(root/"systemPortal/dns.example.yaml").read_text(encoding="utf-8")

need(spine.get("schema")=="luhmOs.apiSpine.v1","API spine schema drift")
need(spine.get("authority")=="Professor","API spine authority drift")
need(spine.get("boss")=="lum","API spine boss drift")
need(spine.get("routing",{}).get("principle")=="capabilityFirstProviderSecond","provider-first routing drift")
need(spine.get("publicInterface",{}).get("providerSpecificDetailsVisibleToEndUser") is False,"provider plumbing leaked to user")
need(spine.get("publicInterface",{}).get("providerSwapMayChangeUserWorkflow") is False,"provider swap may change UX")
need(spine.get("adapterContract",{}).get("providerNativePayloadMayEscapeAdapter") is False,"provider-native payload escape")
need(spine.get("adapterContract",{}).get("providerNativeErrorMayEscapeAdapter") is False,"provider-native error escape")
need(spine.get("secrets",{}).get("rotationShouldRequireProductCodeChange") is False,"secret rotation coupled to product code")
need(spine.get("authorityBoundary",{}).get("trafficControllerMayGrantAuthority") is False,"traffic controller authority leak")
need(spine.get("network",{}).get("cloudflareIsAiProvider") is False,"Cloudflare treated as AI provider")

providers=spine.get("providers",{})
need(set(providers)=={"openAi","googleAi","githubCopilot","huggingFace","edgeGallery"},"provider adapter registry drift")
for pid,p in providers.items():
    for key in ("providerId","adapterId","capabilityClasses","readiness","credentialSource","endpointSource","entitlementState","modelIdentityState","fallbackAdapters","receiptSchema"):
        need(key in p,f"provider adapter missing {pid}.{key}")
    need(p.get("receiptSchema")=="luhmOs.providerExecutionReceipt.v1",f"provider receipt schema drift {pid}")

need(traffic.get("schema")=="luhmOs.cloudflareAirTrafficController.v1","traffic-controller schema drift")
need(traffic.get("provider")=="cloudflare","traffic-controller provider drift")
need(traffic.get("role")=="networkAirTrafficController","traffic-controller role drift")
auth=traffic.get("authorityBoundary",{})
for key in ("aiProvider","agent","sourceTruthOwner","secretAuthority","mutationAuthority","greenAuthority","publicationAuthority","crownAuthority"):
    need(auth.get(key) is False,f"Cloudflare authority leak: {key}")
for key in ("liveDnsChangesRequireProfessor","tunnelChangesRequireProfessor","proxyModeChangesRequireProfessor"):
    need(auth.get(key) is True,f"Cloudflare Crown gate missing: {key}")

mcp_lane=traffic.get("lanes",{}).get("publicChatPluginMcp",{})
need(mcp_lane.get("currentEndpoint")=="https://luhm-os-harness-green.onrender.com/mcp","current MCP endpoint drift")
need(mcp_lane.get("cloudflareDependencyForCurrentEndpoint") is False,"current public plugin unexpectedly depends on Cloudflare")
need(mcp_lane.get("tunnelForThisLane") is False,"MCP tunnel drift")
need(mcp_lane.get("tlsTermination")=="RenderManagedTls","MCP TLS termination drift")
boot=mcp_lane.get("bootstrapRecord",{})
need(boot.get("type")=="CNAME" and boot.get("proxied") is False and boot.get("removeAaaa") is True,"Render custom-domain bootstrap drift")

portal_lane=traffic.get("lanes",{}).get("systemPortal",{})
need(portal_lane.get("mode")=="optionalCloudflareTunnel","System Portal tunnel lane drift")
need(portal_lane.get("tunnelRecord",{}).get("target")=="<cloudflare-tunnel-uuid>.cfargotunnel.com","Tunnel CNAME drift")

need(control.get("inherits",{}).get("apiSpine")=="doctrine/apiSpineV1.json","control plane missing API spine")
need(control.get("inherits",{}).get("cloudflareAirTrafficController")=="doctrine/cloudflareAirTrafficControllerV1.json","control plane missing traffic controller")
need(control.get("providerBoundary",{}).get("cloudflareIsProviderAdapter") is False,"control plane treats Cloudflare as provider adapter")
need(economy.get("routingLaw",{}).get("capabilityFirst") is True,"provider economy not capability-first")
need(openai.get("openAi",{}).get("adapterContract")=="doctrine/apiSpineV1.json#providers.openAi","OpenAI adapter contract drift")
need(google.get("adapter",{}).get("contract")=="doctrine/apiSpineV1.json#providers.googleAi","Google adapter contract drift")
need(mcp_scope.get("apiSpine")=="doctrine/apiSpineV1.json","MCP scope missing API spine")
need(mcp_scope.get("transport",{}).get("currentPublishedPluginDependsOnCustomFqdn") is False,"published plugin depends on custom FQDN")
need(opening.get("installModel",{}).get("apiSpineHiddenFromEndUser") is True,"opening-day leaks API spine")
need(opening.get("installModel",{}).get("providerSwapMayChangeInstallFlow") is False,"provider swap may change install flow")
need("host/api/luhmApiSpine.py" in python_law.get("currentAuthorityFiles",[]),"Python control-plane law missing API spine resolver")
need("capability-first provider routing" in python_law.get("currentPython3Scopes",[]),"Python control-plane scope missing capability routing")
need("def resolve_capability(" in resolver,"API spine resolver missing capability resolver")
need("def validate_receipt(" in resolver,"API spine resolver missing receipt validator")

need(truth.get("providerLayer",{}).get("apiSpine")=="doctrine/apiSpineV1.json","source truth missing API spine")
need(truth.get("networkLayer",{}).get("trafficController")=="doctrine/cloudflareAirTrafficControllerV1.json","source truth missing traffic controller")
need(truth.get("networkLayer",{}).get("aiProvider") is False,"source truth calls Cloudflare AI provider")

need('API_SPINE = ROOT / "doctrine" / "apiSpineV1.json"' in server,"MCP runtime missing API spine")
need('TRAFFIC_CONTROLLER = ROOT / "doctrine" / "cloudflareAirTrafficControllerV1.json"' in server,"MCP runtime missing traffic controller")
need("def luhm_api_spine()" in server,"MCP API-spine tool missing")
need("def luhm_resolve_capability(" in server,"MCP capability resolver tool missing")
need('"apiSpine": api_spine' in harness and '"trafficController": traffic_controller' in harness,"cockpit payload missing spine/controller")
need('id="apiSpine"' in widget and 'id="airTraffic"' in widget,"cockpit UI missing spine/controller")

need("name: mcp" in dns and "target: '<render-service>.onrender.com'" in dns and "proxied: false" in dns,"DNS example still tunnels/proxies MCP")
need("name: system" in dns and "target: '<cloudflare-tunnel-uuid>.cfargotunnel.com'" in dns,"System Portal tunnel example missing")
need("The mcp lane is deliberately not a Tunnel example" in dns,"lane separation note missing")

secret_patterns=[
    r"sk-proj-[A-Za-z0-9_-]{10,}",
    r"gh[pousr]_[A-Za-z0-9]{20,}",
    r"AIza[0-9A-Za-z_-]{20,}",
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
]
combined="\n".join([
    (root/"doctrine/apiSpineV1.json").read_text(encoding="utf-8"),
    (root/"doctrine/cloudflareAirTrafficControllerV1.json").read_text(encoding="utf-8"),
    dns,
])
for pattern in secret_patterns:
    need(re.search(pattern,combined) is None,f"secret-like material matched: {pattern}")

print(json.dumps({
  "schema":"luhmOs.apiSpineAudit.v1",
  "status":"GREEN_API_SPINE_SOURCE" if not errors else "RED_API_SPINE_SOURCE",
  "routing":"capabilityFirstProviderSecond",
  "providerAdapters":len(providers),
  "publicPluginEndpoint":mcp_lane.get("currentEndpoint"),
  "cloudflareRole":traffic.get("role"),
  "cloudflareAiProvider":auth.get("aiProvider"),
  "liveDnsMutation":"CROWN_GATED",
  "crownStatus":"STOP",
  "errors":errors
},indent=2))
raise SystemExit(1 if errors else 0)
