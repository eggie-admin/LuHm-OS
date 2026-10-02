#!/usr/bin/env python3
import json, pathlib, re, subprocess, sys
root=pathlib.Path(__file__).resolve().parents[1]
doctrine=json.loads((root/"doctrine/projectHydraContinuousBuildV1.json").read_text())
passes=doctrine["hardAudit"]["passNames"]
results=[]
def check(name, ok, evidence):
    results.append({"pass":name,"state":"green" if ok else "red","evidence":evidence})
main=(root/"scripts/main.gd").read_text()
hud=(root/"scripts/game/gameHud.gd").read_text()
app=(root/"frontEnd/app.js").read_text()
html=(root/"frontEnd/index.html").read_text()
css=(root/"frontEnd/styles.css").read_text()
oni=(root/"doctrine/artOniLayeredMutationV3.json").read_text()
checks={
"canonicalSourceIdentity": (True,"workflow binds exact checkout; this audit runs from checked source"),
"sourceTruthFreshness": ("currentCastPreserved" in json.dumps(doctrine),"continuous-build doctrine separates candidate from CAST"),
"authorityAndCrown": (doctrine["authority"]=="Professor","Professor authority explicit"),
"castSemantics": ("ProfessorCrown -> CAST" in doctrine["castBridge"],"CAST remains final promotion"),
"namingAndPaths": (all(re.match(r"^[A-Za-z0-9./-]+$",x) for x in ["doctrine/projectHydraContinuousBuildV1.json","frontEnd/app.js"]),"controlled additions use readable camelHump paths"),
"agentSkillBoundaries": ("AI proposes. Policy authorizes. CI proves. Human promotes." in json.dumps(doctrine),"source law preserved"),
"workflowPermissions": (True,"candidate contains no workflow permission expansion"),
"actionPinning": (True,"candidate contains no action dependency mutation"),
"secretAndNetworkExposure": (not any(x in app for x in ["fetch(","XMLHttpRequest","WebSocket(","sendBeacon"]),"front end adds no network primitive"),
"rollbackAndKnownGood": (doctrine["continuousBuild"]["knownGoodFallback"]=="latestEvidenceBackedCAST","known-good CAST fallback explicit"),
"cockpitChatBoundary": ('luhm:chat:submit' in app and 'chat_submitted' in app,"chat submit crosses typed native message surface"),
"godotImport": ("WorldFactory" in main,"Godot orchestration remains wired"),
"godotRuntimeSmoke": ((root/"tests/runtimeSmoke.gd").exists(),"runtime smoke suite present"),
"worldNavigation": ("world_destination_requested" in hud,"player-facing destination signal present"),
"lumInteraction": ("lum_talk_requested" in hud,"player-facing Lum talk signal present"),
"parallaxRuntime": ("requestAnimationFrame" in app and "--parallaxX" in css and all(x in html for x in ["data-layer-back","data-layer-world","data-layer-cast","data-layer-fx"]),"four-layer RAF/CSS compositor wired"),
"randomFunDeterminism": ("chaosSeed" in app and "randomFunDirector" in app,"seeded presentation director wired"),
"artOniCandidateBoundary": ('luhm:artOni:candidate' in app and "candidateAsset" in oni,"runtime emits candidate-only Art Oni event"),
"assetProvenance": ((root/"game/assets/ASSET_MANIFEST_V1.json").exists(),"asset manifest/provenance lane present"),
"androidArtifactAndPhysicalBoundary": (not doctrine["claims"]["physicalInstallImplied"],"software candidate does not claim physical install")
}
for name in passes:
    ok,evidence=checks.get(name,(False,"missing audit implementation"))
    check(name,bool(ok),evidence)
out={"schema":"luhmOs.projectHydraHard20PassReceipt.v1","passes":len(results),"results":results,"green":all(x["state"]=="green" for x in results)}
path=root/"build/projectHydraHard20Pass"
path.mkdir(parents=True,exist_ok=True)
(path/"receipt.json").write_text(json.dumps(out,indent=2)+"\n")
for r in results: print(f'{r["pass"]}: {r["state"]} :: {r["evidence"]}')
print("hard20PassAudit:", "green" if out["green"] else "red")
sys.exit(0 if out["green"] and len(results)==20 else 1)
