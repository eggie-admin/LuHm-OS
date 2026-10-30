#!/usr/bin/env python3
"""Four-lane namespace/edge/forge contract audit. Never reaches a network."""
import json
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]

def inspect(root=ROOT,policy_override=None):
    def read(p):return (root/p).read_text(encoding="utf-8")
    def obj(p):return json.loads(read(p))
    p=policy_override or obj("doctrine/universalFourLaneV1.json")
    cloud=obj("doctrine/cloudflareEdgeHardeningV1.json")
    net=obj("doctrine/networkSpineV1.json")
    pins=obj("frontEnd/prototypes/glassWorld/package.json")
    lock=obj("frontEnd/prototypes/glassWorld/package-lock.json")
    quarantined=obj("doctrine/companyWideOperationalQuarantineV1.json")
    pkg=obj("doctrine/fourPackageTrainV1.json")
    kernel=obj("doctrine/samsungCast500V1.json")
    c={}
    def ck(k,ok):c[k]=bool(ok)
    ck("rootSchema",p.get("schema")=="luhmOs.universalFourLaneV1")
    n=p["namespace"]
    ck("sourceCanonical",n["repo"]=="eggie-admin/LuHm-OS" and n["package"]=="luhm-os" and n["projectHydra"]=="project-hydra")
    ck("publicZoneStable",n["publicZone"]==cloud["canonicalZone"]=="eggiebagelface.art")
    ck("mcpCandidate",n["publicCandidates"][0]=="mcp.eggiebagelface.art")
    ck("networkMcpCandidate",net["identityChain"]["forwardFqdn"]["publicMcp"]==n["publicCandidates"][0])
    ck("privateDnsNotPublic",n["privateTestZone"]=="vm.luhm.test" and n["dnsAuthority"]=="CLOUDFLARE_UNCHANGED")
    f=p["fourByFour"]
    ck("fourSoftwareLayers",len(f["layers"])==4 and len(set(f["layers"]))==4)
    ck("canonicalComposition",f["composition"]==["coreLibrary","pluginExtension","classWidgetOrganization","stubAdapterBoundary"])
    ck("releaseFour",f["releaseLanes"]==["nightly","beta","lts","legacy"])
    ck("packagesUntouched",f["packageFormats"]==pkg["order"]==["dev","npm","dmg","apk"])
    ck("fourBeatFourTier",f["beats"]==["hear","resolve","act","verify"] and f["escalation"]==[0,1,2,3])
    ck("noExperimentalDriverUpgrade",all(p["release"][x]["driverUpgrade"] is False for x in f["releaseLanes"]))
    ck("noTrackAutoupgrade",all(p["release"][x]["upgradeByDefault"] is False for x in f["releaseLanes"]))
    ck("noUnverifiedDeploy",p["release"]["nightly"]["runtime"]=="NONE")
    ck("noFalseSamsungProof",kernel["samsung"]["installedBuilds"]=="UNVERIFIED")
    t=p["transport"]
    ck("preserveRenderDirect",t["existingPublicMcp"]["id"]=="currentRenderDirect" and t["existingPublicMcp"]["cloudflareProxy"] is False and t["existingPublicMcp"]["tunnel"] is False)
    ck("mcpCurrentRenderDoctrine",cloud["lanes"]["chatGptMcp"]["activeTransport"]=="directRenderManagedTls")
    ck("tunnelNotDeployed",t["candidateVm"]["deployed"] is False and t["candidateVm"]["dnsChanged"] is False)
    ck("fourSecurityStages",t["edgeFourStages"]==["edgeDdosAndWaf","authenticatedIdentityAndAccess","privateLoopbackProxy","capabilityAuthorizationAndAudit"])
    ck("privateOrigin",t["noPublicOriginPort"] is True and t["noPublicSqlRoute"] is True)
    ck("doNotTreatGeoAsLogin",t["noClientGeolocationWithoutConsent"] is True and t["noLocationCollection"] is True and t["ipGeoNotAuthProof"] is True)
    ck("paidBotScoreNotRequired",t["paidBotScoreRequired"] is False)
    ck("oneProxyOnly",t["nginx"].startswith("OPTIONAL_") and t["apacheHttpd"]=="ALTERNATIVE_NOT_STACKED")
    ck("noOpenVpn",t["noOpenVpnByDefault"] is True)
    r=p["runtime"]
    ck("noUnverifiedUv",r["uv"]=="OPTIONAL_LOCKED_ONLY_NOT_INSTALLED")
    ck("unresolvedAliasesNotInvented",r["lightningScript"]=="UNRESOLVED_UNMAPPED_NAMESPACE" and r["piForge"]=="UNRESOLVED_NAME_NO_RENAME")
    ck("noUnreviewedCdn",r["cdn"]=="SELF_HOSTED_HASHED_PUBLIC_ASSETS_ONLY")
    ck("noFakeGoogleSentry",r["googleSentry"]=="UNRESOLVED_PRODUCT_ID_NO_ASSUME_PROVIDES_SECURITY")
    ck("npmLockVersion",lock["lockfileVersion"]==3 and pins["dependencies"]=={"@babylonjs/core":"9.32.0","jquery":"3.7.1","vue":"3.5.44"})
    ck("npmBuildOnly",r["npm"].startswith("Node22 build-time"))
    ck("studioSixCamerasUnproven",p["hardware"]["sixWebcams"].endswith("0/6 proven"))
    ck("noEngineBundling",p["engines"]["canonicalRuntime"]=="Godot 4" and p["engines"]["optionalDoNotBundle"] is True)
    ck("sixRolesNotWorkers",len(p["agents"]["proposalSix"])==6 and len(set(p["agents"]["proposalSix"]))==6 and p["agents"]["workersActive"]==0)
    ck("quarantineOriginalFifteen",quarantined["registeredCount"]==15 and quarantined["activeTaskWorkersAllowed"] is False)
    ck("noPrivilegeInheritance",p["agents"]["noBackgroundAgents"] is True and p["agents"]["modelWeightsBundled"] is False)
    ck("base64NotCrypto",p["agents"]["base44"]=="SEPARATE_EXTERNAL_PLATFORM_NOT_A_CODEC")
    ck("safetyAllFalse",all(v is False for k,v in p["safety"].items() if k!="crownStatus"))
    ck("stop",p["safety"]["crownStatus"]=="STOP")
    yaml=read("infra/universal-four-lane/four-lane.yaml")
    ck("yamlFourChannels",all("  "+x+":" in yaml for x in f["releaseLanes"]))
    ck("yamlNotDeploy",yaml.count("    release: false")==4 and "deployment: DENY" in yaml)
    ck("projectionNoInnerHtml","innerHTML" not in read("frontEnd/universalRouteProjection.mjs"))
    ck("oneK9000Present",(root/"frontEnd/k9000.html").is_file())
    errors=sorted(x for x,ok in c.items() if not ok)
    return {"schema":"luhmOs.universalFourLaneAudit.v1","checks":len(c),"passed":len(c)-len(errors),
        "errors":errors,"verdict":"SOURCE_GREEN_RUNTIME_AMBER" if not errors else "RED_SOURCE",
        "vmRunning":False,"tunnelConnected":False,"systemShellEnabled":False,
        "motionCaptured":False,"agentWorkersActive":0,"crownStatus":"STOP"}

if __name__=="__main__":
    result=inspect()
    print(json.dumps(result,indent=2))
    if result["errors"]:raise SystemExit(1)
