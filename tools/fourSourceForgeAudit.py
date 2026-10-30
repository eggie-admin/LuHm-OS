#!/usr/bin/env python3
"""Four-source VM/kiosk/app/CI infrastructure and plugin boundary audit."""
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]

def inspect(root=ROOT):
    read=lambda x:(root/x).read_text(encoding="utf-8")
    j=lambda x:json.loads(read(x))
    p=j("doctrine/fourSourceForgeV1.json")
    q=j("doctrine/companyWideOperationalQuarantineV1.json")
    checks={}
    def ck(k,v):checks[k]=bool(v)
    ck("fourSources",p.get("sources")==["vmHeadless","deviceKiosk","webUi","githubBuild"])
    ck("fourColumns",p.get("columns")==["coreLibrary","pluginExtension","classWidgetOrganization","stubAdapterBoundary"])
    ck("fourBeats",p.get("beats")==["hear","resolve","act","verify"])
    ck("fourTiers",p.get("tiers")==[0,1,2,3])
    ck("fourProfiles",p.get("profiles")==["headless","witchingHour","corporate","githubDevelopment"])
    ck("canonicalEscalation",p.get("canonicalEscalation")=="doctrine/escalationKernelV1.json")
    ck("agentQuarantine",p.get("runtimeAgents")==0 and q.get("activeTaskWorkersAllowed") is False)
    ck("base64NotEncryption",p["encoding"]["format"]=="base64url-json" and p["encoding"]["base44IsEncoding"] is False and p["encoding"]["encryption"] is False)
    ck("max44KiB",p["encoding"]["maxDecodedBytes"]==45056)
    ck("sqliteReused",p.get("sqlite")=="host/api/typedLanesV1.sql")
    ck("mariaDbOptional",p.get("mariaDb")=="OPTIONAL_SEPARATE_DB_REVIEW")
    ck("fourLoginMethods",p["identity"]["options"]==["github","google","apple","luhmNative"] and p["identity"]["connected"]==[])
    ck("loginNotRoles",p["identity"]["roleAuthorizationSeparate"] is True)
    ck("mailNotRunning",p["mail"]["configured"] is False and p["mail"]["remotePollEnabled"] is False)
    ck("sixUvcUnverified",p["hardware"]["webcamTargetCount"]==6 and p["hardware"]["webcamsVerified"]==0)
    ck("btVirtualNotReal","btvirt" in p["hardware"]["bluetoothEmulation"])
    ck("blenderNotRunning",p["hardware"]["remoteBlender"]=="HEADLESS_JOB_NOT_RUNNING")
    ck("dnsUnchanged","Cloudflare" in p["network"]["dns"] and p["network"]["autoApply"] is False)
    ck("noAuthority",p["safety"]["crownStatus"]=="STOP" and not any(v for k,v in p["safety"].items() if k!="crownStatus"))
    for name in p["plugins"]["manifestPaths"]:
        manifest=j(name)
        ck("pluginSyntax:"+name, bool(manifest.get("name")) and bool(manifest.get("license")))
    ck("incomingNotExecutable",p["plugins"]["incomingExecutable"] is False)
    netplan=read("infra/four-source/netplan/99-luhm-networkd.example.yaml")
    ck("netplanNetworkdExample","renderer: networkd" in netplan and "dhcp4: true" in netplan and "enp1s0" in netplan)
    ck("netplanNeverApplied","netplan apply" not in netplan)
    kiosk=read("infra/four-source/systemd/kiosk-preview.service.example")
    ck("kioskPhysicalOnly","/usr/bin/cage" in kiosk and "file:///opt/luhmos/frontEnd/k9000.html" in kiosk)
    ck("noVMKiosk","127.0.0.1:8789/" not in kiosk)
    acme=read("infra/four-source/certbot/README.md")
    ck("certbotNoTokens","Cloudflare" in acme and "API token" in acme and "never" in acme.lower())
    code=read("tools/ownerImapUnreadCheck.py")
    ck("imapReadOnly",'readonly=True' in code and '.search(None,"UNSEEN")' in code)
    ck("imapNoFetch",'.fetch(' not in code and '.store(' not in code)
    ck("noAutomaticMail","if not args.check:" in code)
    pipeline=read("tools/unifiedForgePipeline.py")
    ck("manifestUsesStrictSql",'host/api/typedLanesV1.sql' in pipeline and '":memory:"' in pipeline and "aiManifestStream" in pipeline)
    ck("manifestNoProviderCalls", "subprocess.run" not in pipeline and "requests." not in pipeline and "urllib." not in pipeline)
    frontend=read("frontEnd/forgeSourceProjection.mjs")
    ck("jsSafeUi","textContent=" in frontend and "innerHTML" not in frontend and "fetch(" not in frontend)
    failures=sorted(k for k,v in checks.items() if not v)
    return {"schema":"luhmOs.fourSourceForgeAudit.v1","sourceChecks":len(checks),
      "sourcePass":len(checks)-len(failures),"failures":failures,
      "verdict":"SOURCE_GREEN_RUNTIME_AMBER" if not failures else "RED_SOURCE",
      "vmLive":False,"cameraFrames":False,"identityProvidersConnected":0,
      "emailRemoteRunning":False,"blenderRenderProven":False,"crownStatus":"STOP"}

if __name__=="__main__":
    result=inspect()
    print(json.dumps(result,indent=2))
    if result["failures"]:raise SystemExit(1)
