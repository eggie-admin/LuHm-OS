#!/usr/bin/env python3
"""Offline, fail-closed Hydra capture/rotoscope/mocap/dating-sim CAST preflight.
No FFmpeg execution, network access, media uploads or cloud AI invocation.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
POLICY=ROOT/"doctrine/hydraCastMediaBridgeV1.json"
STORY=ROOT/"game/datingSimPilotV1.json"
HEX64=re.compile(r"[a-f0-9]{64}\Z")
SHA40=re.compile(r"[a-f0-9]{40}\Z")
NAME=re.compile(r"[a-zA-Z][a-zA-Z0-9_-]{0,63}\Z")
def verify_policy(p):
    errors=[]
    def need(condition,code):
        if not condition:errors.append(code)
    need(p.get("schema")=="luhmOs.hydraCastMediaBridge.v1" and p.get("status")=="PROPOSED_SOURCE_ONLY","POLICY_SCHEMA")
    need(p.get("authority")=="Professor" and p.get("crown")=="STOP","CROWN_GATE")
    e=p.get("existingSpine",{})
    need(e.get("source")=="eggie-admin/LuHm-OS" and e.get("godot")=="CURRENT_PLAYABLE_SPINE" and e.get("unrealStatus")=="TARGET_NOT_RUNTIME_PROVEN","ENGINE_PROOF")
    need(e.get("singleRuntimeAuthority")=="PER_BUILD_SELECTED_ENGINE","ENGINE_COMPETITION")
    light=p.get("lightOs",{})
    for k in ("videoComputeOnTabletRequired","unrealEditorOnTabletRequired"):
        need(light.get(k) is False,"TABLET_OVERLOAD_"+k)
    capture=p.get("capture",{})
    need(capture.get("minCameras")==1 and capture.get("maxCameras")==6 and capture.get("defaultFps") in capture.get("allowedFps",[]),"CAPTURE_CONTRACT")
    for k in ("referenceAudioClap","frameOffsetsRecorded","externalCameraConsentRequired"):
        need(capture.get(k) is True,"CAPTURE_SAFETY_"+k)
    for k in ("continuousBackgroundCameraCapture","multiCameraHardwareSyncVerified"):
        need(capture.get(k) is False,"FAKE_CAMERA_PROOF_"+k)
    roto=p.get("rotoscope",{})
    need(roto.get("defaultMode")=="luminanceMatte" and roto.get("luminanceIsNotChroma") is True,"LUMA_NOT_CHROMA")
    need(set(roto.get("modes",[]))=={"luminanceMatte","colorChromaKey","vectorRoto","trackedMask","aiSegmentationCandidate"},"ROTO_MODE_DRIFT")
    need(roto.get("originalColorFootagePreserved") is True and roto.get("editableMaskMaster")=="blender","LOSSY_ROTO")
    need(roto.get("remoteVideoUploadAllowed") is False and roto.get("untrustedScripts") is False,"UNSAFE_ROTO")
    mocap=p.get("motionCapture",{})
    need(mocap.get("calibrationRequired") is True and mocap.get("frameRateContinuityRequired") is True and mocap.get("facialConsentRequired") is True,"MOCAP_PROOF_GATE")
    for k in ("privateFaceDataToCloudAllowed","realTimeSixCamTriangulationProven","biometricRetentionReviewed"):
        need(mocap.get(k) is False,"MOCAP_PRIVACY_OR_FALSE_PROOF_"+k)
    vec=p.get("vector",{})
    need(vec.get("pathsEditable") is True and vec.get("closedSplineForAlphaRequired") is True and vec.get("artistApprovalRequired") is True,"VECTOR_REVIEW_GATE")
    ai=p.get("ai",{})
    need(ai.get("default")=="localDeterministic" and set(ai.get("providerRouting",[]))=={"localDeterministic","openAiOptional","googleGeminiOptional"},"PROVIDER_ROUTING")
    for k in ("requireTaskScopedConsent","requireEntitlementAndBudgetReceipt","requireModelOutputSchemaValidation","untrustedModelTextNotExecutable"):
        need(ai.get(k) is True,"AI_SAFETY_"+k)
    for k in ("automaticVideoUpload","automaticRemoteCalls","googleVertexLegacyFallback","cloudSecretsInCi","faceDataToProviderWithoutConsent"):
        need(ai.get(k) is False,"AI_AUTONOMY_"+k)
    need(type(ai.get("autoSpendUsd")) is int and ai.get("autoSpendUsd")==0,"AI_SPEND")
    need(p.get("story",{}).get("path")=="game/datingSimPilotV1.json" and p.get("story",{}).get("romanceParticipantsAdults") is True,"DATING_SIM_SCOPE")
    release=p.get("promotion",{})
    need(len(release.get("gates",[]))>=8 and "UnrealVerticalSliceProof" in release.get("gates",[]),"CAST_GATES")
    for k in ("automaticMerge","automaticDeploy","automaticAgentResume","automaticSign","automaticPublicRelease"):
        need(release.get(k) is False,"UNAUTHORIZED_RELEASE_"+k)
    return sorted(set(errors))
def verify_story(s):
    errors=[]
    def need(cond,msg):
        if not cond:errors.append(msg)
    need(s.get("schema")=="luhmOs.datingSimPilot.v1" and s.get("status")=="STORYBOARD_PROXY_ONLY","STORY_SCHEMA")
    need(s.get("allRomanceCharactersAdult") is True and len(s.get("characters",[]))>=2 and
         all(c.get("adult") is True and c.get("canonState")=="PROXY_UNAPPROVED" for c in s.get("characters",[])),"STORY_AGE_OR_CANON")
    nodes=s.get("nodes",[])
    ids=[n.get("id") for n in nodes if isinstance(n,dict)]
    need(len(nodes)>=3 and len(ids)==len(set(ids)) and s.get("entry") in ids,"STORY_GRAPH")
    referenced=set()
    for node in nodes:
        if not isinstance(node,dict):errors.append("INVALID_NODE");continue
        need(bool(NAME.fullmatch(str(node.get("id","")))),"UNSAFE_NODE_ID")
        need(node.get("kind") in ("dialogue","ending") and isinstance(node.get("line"),str) and len(node["line"])<=500,"UNSAFE_DIALOGUE")
        options=node.get("choices",[])
        need(isinstance(options,list) and len(options)<=3,"CHOICE_BUDGET")
        for choice in options if isinstance(options,list) else []:
            target=choice.get("next") if isinstance(choice,dict) else None
            if target is not None:referenced.add(target)
            need(isinstance(choice,dict) and target in ids and type(choice.get("affinityDelta")) is int and -2<=choice["affinityDelta"]<=2,"INVALID_CHOICE")
        if node.get("kind")=="ending":need(not options,"ENDING_HAS_CHOICES")
    need(referenced<=set(ids),"DANGLING_BRANCH")
    visited=set();stack=[s.get("entry")]
    while stack:
        key=stack.pop()
        if key in visited or key not in ids:continue
        visited.add(key)
        stack.extend(c.get("next") for c in nodes[ids.index(key)].get("choices",[]) if isinstance(c,dict))
    need(visited==set(ids),"UNREACHABLE_STORY_NODE")
    need(any(n.get("kind")=="ending" and n.get("id") in visited for n in nodes),"NO_REACHABLE_END")
    st=s.get("state",{})
    need(st.get("minAffinity")==0 and st.get("maxAffinity")==10 and st.get("defaultAffinity")==0,"AFFINITY_BOUNDS")
    need(s.get("dialogueVoiceCloningAllowed") is False and s.get("autoPublish") is False and s.get("crown")=="STOP","STORY_RIGHTS")
    need(s.get("exportAdapters",{}).get("unreal")=="FINAL_TARGET_UNVERIFIED","FALSE_UNREAL_BUILD")
    return sorted(set(errors))
def plan_shot(shot):
    """Return a no-execute, bounded FFmpeg argv for grayscale matte or chroma preview."""
    if not isinstance(shot,dict) or shot.get("schema")!="luhmOs.captureShot.v1":raise ValueError("SHOT_SCHEMA")
    name=shot.get("shotId")
    if not isinstance(name,str) or not NAME.fullmatch(name):raise ValueError("SHOT_ID")
    files=shot.get("cameras")
    if not isinstance(files,list) or not 1<=len(files)<=6:raise ValueError("CAMERA_COUNT")
    if len({c.get("cameraId") for c in files if isinstance(c,dict)})!=len(files):raise ValueError("DUPLICATE_CAMERA")
    fps=shot.get("fps")
    if fps not in ("24/1","25/1","30/1","30000/1001","60/1"):raise ValueError("FPS")
    if shot.get("sourceRightsCleared") is not True or shot.get("captureConsent") is not True:raise ValueError("RIGHTS_OR_CONSENT")
    if shot.get("audioClapFrame") is None or type(shot.get("audioClapFrame")) is not int or shot["audioClapFrame"]<0:raise ValueError("SYNC_CLAP")
    for c in files:
        if not isinstance(c,dict) or not isinstance(c.get("cameraId"),str) or not NAME.fullmatch(c["cameraId"]):raise ValueError("CAMERA_ID")
        file=c.get("file")
        if (not isinstance(file,str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]{0,127}",file)
            or Path(file).name!=file or Path(file).suffix.lower() not in (".mov",".mp4",".mkv",".webm")):
            raise ValueError("UNSAFE_FILE")
        if not isinstance(c.get("sha256"),str) or not HEX64.fullmatch(c["sha256"]):raise ValueError("SOURCE_SHA")
        if type(c.get("frameOffset")) is not int or abs(c["frameOffset"])>fps_to_frames(fps)*3:raise ValueError("SYNC_OFFSET")
    mode=shot.get("mode")
    if mode not in ("luminanceMatte","colorChromaKey","vectorRoto","trackedMask"):raise ValueError("MODE")
    if mode in ("vectorRoto","trackedMask"):return {"status":"ARTIST_EDIT_REQUIRED","source":files[0]["file"],"mode":mode,"execution":False,"required":["blenderEditMask","artistReview"],"crown":"STOP"}
    if mode=="luminanceMatte":
        threshold=shot.get("threshold",176)
        if type(threshold) is not int or not 1<=threshold<=254:raise ValueError("THRESHOLD")
        filt=f"fps={fps},format=yuv444p,lutyuv=y='if(gte(val\\,{threshold})\\,255\\,0)':u=128:v=128,format=gray"
        out=name+"-matte-%06d.png"
    else:
        if shot.get("keyColor") not in ("green","blue"):raise ValueError("KEY_COLOR")
        filt=f"fps={fps},format=rgba,colorkey={shot['keyColor']}:0.12:0.05"
        out=name+"-key-%06d.png"
    return {"status":"PLAN_ONLY_PRIVATE","mode":mode,"source":files[0]["file"],"command":["ffmpeg","-hide_banner","-nostdin","-n","-i",files[0]["file"],"-vf",filt,"-an","-frames:v","240",out],"execution":False,"sourceHash":files[0]["sha256"],"manualMaskReviewRequired":True,"crown":"STOP"}
def fps_to_frames(fps):
    num,den=map(int,fps.split("/"));return (num+den-1)//den
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-ref",required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--shot",type=Path)
    a=ap.parse_args()
    if not SHA40.fullmatch(a.source_ref):raise SystemExit("EXACT_SHA_REQUIRED")
    git=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True)
    if git.returncode or git.stdout.strip()!=a.source_ref:raise SystemExit("EXACT_CHECKOUT_MISMATCH")
    policy=json.loads(POLICY.read_text(encoding="utf-8"))
    story=json.loads(STORY.read_text(encoding="utf-8"))
    errors=verify_policy(policy)+verify_story(story)
    receipt={"sourceRef":a.source_ref,"status":"PASS_SOURCE_ONLY_CROWN_STOP" if not errors else "FAIL_SOURCE","errors":sorted(set(errors)),"ffmpegExecuted":False,"providerCalled":False,"engineBuilt":False,"biometricDataTransferred":False,"crown":"STOP","policySha256":hashlib.sha256(POLICY.read_bytes()).hexdigest(),"storySha256":hashlib.sha256(STORY.read_bytes()).hexdigest()}
    if a.shot:
        try:receipt["plannedShot"]=plan_shot(json.loads(a.shot.read_text(encoding="utf-8")))
        except (ValueError,OSError,TypeError) as exc:receipt["errors"].append(str(exc));receipt["status"]="FAIL_SOURCE"
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:receipt[k] for k in ("status","errors","sourceRef","crown")},indent=2))
    if receipt["errors"]:raise SystemExit(2)
if __name__=="__main__":main()
