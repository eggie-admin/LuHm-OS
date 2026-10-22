#!/usr/bin/env python3
"""Offline audit of exact-source snapshot, dual compatibility, and quarantine."""
import copy, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FILES=["doctrine/currentCanonSnapshot20261022.json",
       "doctrine/currentSourceTruthV3.json",
       "doctrine/projectChatCanonV1.json",
       "doctrine/activeRepositorySetV1.json",
       "doctrine/worldHeadquartersOrchestrationV1.json",
       "doctrine/companyWideOperationalQuarantineV1.json"]
def read(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))
def check(s,t,c,r,h,q):
    errors=[]
    def need(ok,label):
        if not ok: errors.append(label)
    canonical=["chatGptOpenAi","github"]
    need(s.get("schema")=="luhmOs.currentCanonSnapshot.v1","schema")
    need(s.get("status")=="SOURCE_SNAPSHOT_VERIFIED_CANDIDATE_NOT_PROMOTED","status")
    need(s.get("compatibilityOrder")==canonical,"layers")
    need(t.get("activeCompatibilityOrder",{}).get("first")==canonical[0] and
         t.get("activeCompatibilityOrder",{}).get("second")==canonical[1],"truthOrder")
    need(t.get("worldHeadquarters",{}).get("contract")==FILES[4],"worldHQ")
    need(t.get("currentCanonSnapshot",{}).get("contract")==FILES[0],"truthPointer")
    need(c.get("alwaysLoadedCore",{}).get("canonSnapshot")==FILES[0],"chatPointer")
    need(all(f in c.get("loadOrder",[]) for f in [FILES[0],FILES[4],"doctrine/studioCompatibilityFastMeshV1.json"]),"chatLoad")
    need(c.get("chatRuntime",{}).get("compatibilityLayerOrder")==canonical,"chatOrder")
    need(c.get("chatRuntime",{}).get("codespacesSecondSourceOfTruthIsWorkingMirrorOnly") is True,"workingMirror")
    need(h.get("canonicalRepository")=="eggie-admin/LuHm-OS" and h.get("promotion") is False,"hqOwner")
    snapshots=s.get("snapshots",[])
    need(len(snapshots)==4 and len(set((x.get("repository"),x.get("kind")) for x in snapshots))==4,"snapshots")
    need(all(x.get("verified") is True and re.fullmatch("[0-9a-f]{40}",x.get("sha","")) and
         x.get("branch","").startswith("snapshot/") for x in snapshots),"snapshotIdentity")
    recorded={(x.get("repository"),x.get("sha"),x.get("branch")) for x in snapshots if x.get("kind")!="worldHeadquartersCandidatePreCanonUpdate"}
    tracked={(x.get("repository"),x.get("observedHead"),x.get("snapshotRef")) for x in r.get("activeRepositories",[])}
    need(recorded==tracked and len(tracked)==3,"repoSnapshotAlignment")
    drive=s.get("observedDriveIntake",{})
    need(drive.get("extractedFileCount")==164 and drive.get("fileTypeFolderCount")==18,"driveCount")
    need(drive.get("eligibleForCanonicalSourceOrPublishing") is False,"rights")
    need(drive.get("privateDriveIdsInPublicGit") is False,"privateRefs")
    need(s.get("runtime",{}).get("githubRsyncToGoogleDrive")=="NOT_VERIFIED_AUTHENTICATED","noFakeSync")
    need(q.get("state")=="QUARANTINED" and q.get("activeTaskWorkersAllowed") is False,"companyHold")
    need(t.get("crownStatus")=="STOP" and t.get("promotion") is False,"truthCrown")
    need(s.get("crownStatus")=="STOP" and s.get("promotion") is False,"snapshotCrown")
    need(all(s.get("authority",{}).get(x) is False for x in ["automaticMerge","automaticBuild",
         "automaticCast","automaticDeploy","automaticPublish","automaticAgentActivation","automaticCrown"]),"autoAuthority")
    return errors
def main():
    s,t,c,r,h,q=(read(x) for x in FILES)
    problems=check(s,t,c,r,h,q)
    if problems:
        print(json.dumps({"status":"RED_SNAPSHOT","errors":problems}));return 1
    cases=[(["compatibilityOrder",0],"github"),(["crownStatus"],"GREEN"),
           (["observedDriveIntake","eligibleForCanonicalSourceOrPublishing"],True),
           (["runtime","githubRsyncToGoogleDrive"],"VERIFIED"),
           (["authority","automaticMerge"],True),
           (["snapshots",0,"verified"],False),
           (["snapshots",1,"sha"],"not-a-sha")]
    for path,value in cases:
        changed=copy.deepcopy(s);obj=changed
        for key in path[:-1]:obj=obj[key]
        obj[path[-1]]=value
        if not check(changed,t,c,r,h,q):
            raise AssertionError("negative control did not fail: "+str(path))
    print(json.dumps({"status":"GREEN_SOURCE_ONLY","snapshots":4,"negativeControls":len(cases),
      "ciNotRuntime":True,"productionMerge":False,"crown":"STOP"}))
    return 0
if __name__=="__main__":
    raise SystemExit(main())
