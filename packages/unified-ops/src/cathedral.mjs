#!/usr/bin/env node
// Read-only candidate inventory. Never builds, signs, publishes or activates agents.
import fs from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"../../..");
const REQUIRED=[
 "project.godot","scenes/Main.tscn","game/assets/ASSET_MANIFEST_V1.json",
 "media/godot4-asset-reconciliation-v1.json","tools/yumeGodotAssetPrep.py",
 "tools/buildGodotWebHarness.sh","host/api/typedLanesV1.sql","tools/typedSqlStub.py",
 "frontEnd/package.json","frontEnd/package-lock.json",
 "frontEnd/prototypes/glassWorld/package.json","frontEnd/prototypes/glassWorld/package-lock.json",
 "packages/unified-ops/package.json","packages/unified-ops/package-lock.json",
 "doctrine/currentSourceTruthV3.json","doctrine/featureMutationPipelineV1.json",
 "doctrine/codingRoleplayDirectorV2.json","doctrine/vendorProvenanceBoundaryV1.json"
];
function load(root,p){return JSON.parse(fs.readFileSync(path.join(root,p),"utf8"));}
export function packageErrors(pkg,lock,id){
 const errors=[];
 if(pkg?.private!==true)errors.push(id+":notPrivate");
 if(lock?.lockfileVersion!==3||!lock.packages?.[""])errors.push(id+":badLockfile");
 for(const kind of ["dependencies","devDependencies"]){
  const declared=pkg?.[kind]||{}, locked=lock?.packages?.[""]?.[kind]||{};
  if(JSON.stringify(declared)!==JSON.stringify(locked))errors.push(id+":"+kind+"Drift");
  for(const [name,version] of Object.entries(declared)){
   if(typeof version!=="string"||!/^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?$/.test(version))
    errors.push(id+":notExact:"+name);
   const entry=lock?.packages?.["node_modules/"+name];
   if(!entry||entry.version!==version||!entry.integrity)errors.push(id+":unverified:"+name);
  }
 }
 return errors;
}
export function proposedPlan(sha){
 if(typeof sha!=="string"||!/^[a-f0-9]{40}$/.test(sha))throw new Error("EXACT_SOURCE_SHA_REQUIRED");
 return {schema:"luhmOs.cathedralProposedPreflight.v1",sourceRef:sha,lane:"PROPOSED_SOURCE_ONLY",
  actors:{tetsu:"sourceForgeLabelOnly",kaji:"compileForgeLabelOnly",lum:"supervisorLabelOnly"},
  steps:[
   {id:"inventory",needs:[],surface:"3D-and-custom-resources",proof:"assetId/hash/rights"},
   {id:"rights",needs:["inventory"],surface:"licenses-and-provenance",proof:"upstream/NOTICE/permission"},
   {id:"blender",needs:["rights"],surface:"private-sandbox-GLB-export",proof:"real-blender-export"},
   {id:"godot",needs:["blender"],surface:"headless-import-and-play",proof:"real-scene-runtime"},
   {id:"npm",needs:["rights"],surface:"locked-static-bundle",proof:"npm-ci-and-hashed-output"},
   {id:"sql",needs:["godot","npm"],surface:"typed-SQLite-receipt",proof:"transaction-and-rollback"},
   {id:"dpkgOptional",needs:["sql"],surface:"Linux-only-package",proof:"dpkg-content-licenses-install-smoke"},
   {id:"review",needs:["sql"],surface:"exact-SHA-PR",proof:"independent-code-and-privacy-review"},
   {id:"cast",needs:["review"],surface:"separately-authorized-build",proof:"owner-current-main-and-device"},
   {id:"crown",needs:["cast"],surface:"beta-public-release",proof:"signer-rights-privacy-host"}
  ],executor:"NONE",sourceChecksAreRuntimeProof:false,autoMerge:false,autoDeploy:false,
  automaticCast:false,releaseAuthorized:false,crown:"STOP"};
}
export function auditProposed(sha,root=ROOT){
 const plan=proposedPlan(sha),errors=[];
 for(const p of REQUIRED)try{
  const s=fs.lstatSync(path.join(root,p));
  if(!s.isFile()||s.isSymbolicLink())errors.push("unsafe:"+p);
 }catch{errors.push("missing:"+p);}
 if(!errors.length)try{
  for(const dir of ["frontEnd","frontEnd/prototypes/glassWorld","packages/unified-ops"])
   errors.push(...packageErrors(load(root,dir+"/package.json"),load(root,dir+"/package-lock.json"),dir));
  const truth=load(root,"doctrine/currentSourceTruthV3.json");
  const pipeline=load(root,"doctrine/featureMutationPipelineV1.json");
  const assets=load(root,"media/godot4-asset-reconciliation-v1.json");
  const roleplay=load(root,"doctrine/codingRoleplayDirectorV2.json");
  if(truth.promotion!==false||pipeline.lanes?.proposed?.publish!==false)errors.push("promotionDrift");
  if(pipeline.mutationControls?.autoMerge!==false||pipeline.mutationControls?.automaticReleasePromotion!==false)errors.push("autoMergeDrift");
  if(assets.publicationAuthority!==false||assets.crownStatus!=="STOP")errors.push("assetRightsGateDrift");
  if(roleplay.promotion!==false||roleplay.crownStatus!=="STOP")errors.push("roleplayAuthorityDrift");
 }catch{errors.push("unreadableManifest");}
 return {...plan,sourcePreflight:errors.length?"RED":"PASS_SOURCE_ONLY",errors,
  blenderExecuted:false,godotDeviceVerified:false,sqlMigrationExecuted:false,debBuilt:false,
  assetRightsAllCleared:false,privateDriveAclVerified:false,ownerCastObserved:false,
  blockers:["asset-rights-and-import","independent-PR-review","device-and-signer",
   "host-and-private-ACL","owner-Cast-and-Crown"]};
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 try{
  if(process.argv.length!==3)throw new Error("USAGE: npm run plan:cathedral -- EXACT_40_SHA");
  const report=auditProposed(process.argv[2]);
  console.log(JSON.stringify(report,null,2));
  if(report.sourcePreflight==="RED")process.exitCode=1;
 }catch(e){console.error(e.message);process.exitCode=2;}
}
