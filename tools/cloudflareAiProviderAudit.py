#!/usr/bin/env python3
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
errors=[]

def need(ok,msg):
    if not ok: errors.append(msg)

p=root/"doctrine/cloudflareAiProviderV1.json"
ctlp=root/"doctrine/luhmAiControlPlaneV1.json"
cabp=root/"doctrine/lumGoddessCabinetV1.json"
truthp=root/"doctrine/SOURCE_OF_TRUTH.json"
skillp=root/"agents/cloudflareAiProvider/SKILL.md"

for path in (p,ctlp,cabp,truthp,skillp):
    need(path.is_file(),f"missing {path.relative_to(root)}")

if p.is_file():
    d=json.loads(p.read_text())
    need(d.get("providerId")=="cloudflareAiProvider","provider id drift")
    need(d.get("boss")=="lum","Lum boss drift")
    ac=d.get("acquaintance",{})
    need(ac.get("mayAddressLum") is True,"provider cannot address Lum")
    need(ac.get("mayAddressGoddessesDirectly") is False,"direct goddess control leak")
    need(ac.get("mayRecruitAgents") is False,"provider recruitment leak")
    need(ac.get("mayRouteWorkers") is False,"provider routing leak")
    need(ac.get("mayGrantGreen") is False,"provider GREEN authority leak")
    need(ac.get("mayGrantCrown") is False,"provider Crown authority leak")
    g=ac.get("knowsGoddesses",{})
    for ident in ("urdDoctorGoddess","belldandySecretary","skuldResearch"):
        need(ident in g,f"provider does not know {ident}")
    ev=d.get("evidence",{})
    need(ev.get("successIsGreen") is False,"provider success maps to GREEN")
    sec=d.get("security",{})
    need(sec.get("credentialsHostSideOnly") is True,"credential boundary drift")
    net=d.get("networkBoundary",{})
    for k in ("dnsMutation","tunnelMutation","publicExposure","cloudflareEdgeAuthority"):
        need(net.get(k) is False,f"network authority leak: {k}")
    need(d.get("crownStatus")=="stop","Crown must stop")

if ctlp.is_file():
    ctl=json.loads(ctlp.read_text())
    providers=ctl.get("providers",{})
    cf=providers.get("cloudflareAiProvider",{})
    need(cf.get("contract")=="doctrine/cloudflareAiProviderV1.json","control-plane provider contract missing")
    need(cf.get("speaksTo")=="lum","control-plane provider must speak to Lum")
    need(cf.get("cabinetAware") is True,"provider must be cabinet aware")
    need(cf.get("cabinetMember") is False,"provider must not be cabinet member")

if cabp.is_file():
    cab=json.loads(cabp.read_text())
    ext=cab.get("externalProviders",{})
    cf=ext.get("cloudflareAiProvider",{})
    need(cf.get("returnsTo")=="lum","cabinet provider must return to Lum")
    need(cf.get("directGoddessRouting") is False,"cabinet direct routing leak")

if truthp.is_file():
    truth=json.loads(truthp.read_text())
    cf=truth.get("aiProviders",{}).get("cloudflareAiProvider",{})
    need(cf.get("contract")=="doctrine/cloudflareAiProviderV1.json","source truth provider contract missing")
    need(cf.get("status")=="CANDIDATE_CONTRACT_ONLY","source truth must not claim live provider")

if skillp.is_file():
    txt=skillp.read_text()
    for token in ("Lum is the only conversational boss","Urd is the doctor goddess","Belldandy is the secretary goddess","Skuld is the research goddess","successful API response is `OBSERVED`, not GREEN"):
        need(token in txt,f"skill missing token: {token}")

print(json.dumps({
  "schema":"luhmOs.cloudflareAiProviderAudit.v1",
  "status":"greenCloudflareAiProviderCandidate" if not errors else "redCloudflareAiProviderCandidate",
  "cabinetAware":True,
  "cabinetMember":False,
  "providerAuthority":False,
  "crownStatus":"stop",
  "errors":errors
},indent=2))
raise SystemExit(1 if errors else 0)
