#!/usr/bin/env node
/** Source-only apt/Netplan-inspired plan/try. Real apply intentionally disabled. */
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const SHA=/^[0-9a-f]{40}$/;
function check(value,message){if(!value)throw new Error(message);}
export function planThinPackages(sourceRef,policy,root=ROOT){
 check(SHA.test(sourceRef),'EXACT_40_SHA_REQUIRED');
 check(policy?.schema==='luhmOs.thinPackagePlan.v1'&&policy.status==='PROPOSED_SOURCE_ONLY'&&policy.crown==='STOP','POLICY_OR_CROWN_DRIFT');
 for(const key of ['autoApply','autoMerge','autoDeploy','autoPublish'])check(policy[key]===false,'UNSAFE_'+key);
 for(const key of ['neverExecuteVendorInstallScripts','neverAutoPurge','neverAssumeLicenseOrEntitlement','noEmbeddedProviderSecrets'])check(policy[key]===true,'UNSAFE_'+key);
 check(Array.isArray(policy.modules)&&policy.modules.length>0,'NO_MODULES');
 const byId=new Map();
 for(const m of policy.modules){
  check(/^[a-z][A-Za-z0-9]*$/.test(m.id)&&!byId.has(m.id),'DUPLICATE_OR_INVALID_ID');
  check(['client','service','studio','native','distribution','quarantine'].includes(m.surface),'INVALID_SURFACE');
  check(['retain','isolate','quarantine','replaceCandidate','retireCandidate'].includes(m.decision),'INVALID_DECISION');
  check(['npm','python','apiContract','blender','ffmpeg','godot','gradle','dpkg','none'].includes(m.manager),'INVALID_MANAGER');
  check(Array.isArray(m.requires),'INVALID_DEPS');
  check(typeof m.path==='string'&&!path.isAbsolute(m.path)&&!m.path.split(/[\\/]/).some(p=>['.','..',''].includes(p)),'UNSAFE_PATH');
  const dest=path.resolve(root,m.path);
  check(dest.startsWith(path.resolve(root)+path.sep),'PATH_ESCAPE');
  const stat=fs.lstatSync(dest,{throwIfNoEntry:false});
  check(stat&&!stat.isSymbolicLink(),'MISSING_OR_SYMLINK_'+m.id);
  if(m.surface==='quarantine')check(m.decision==='quarantine','QUARANTINE_DRIFT');
  byId.set(m.id,m);
 }
 const marks=new Map(),order=[];
 function walk(id){
  check(byId.has(id),'MISSING_DEP_'+id);
  check(marks.get(id)!==1,'CYCLE_'+id);
  if(marks.get(id)===2)return;
  marks.set(id,1);
  for(const dep of byId.get(id).requires){
    check(byId.get(dep)?.decision!=='quarantine','QUARANTINE_DEP_'+dep);
    walk(dep);
  }
  marks.set(id,2);order.push(id);
 }
 for(const m of policy.modules)walk(m.id);
 return {schema:'luhmOs.thinPackageReceipt.v1',sourceRef,mode:'plan',status:'GREEN_SOURCE_PLAN_ONLY',
  planOrder:order,decisions:order.map(id=>byId.get(id)),sourceIdentityVerified:false,
  vendorSourceExecuted:false,packageActionsExecuted:false,hostChanged:false,
  rightsCleared:false,deviceVerified:false,entitlementsProven:false,releaseAuthorized:false,crown:'STOP'};
}
export function tryThinPackages(plan,temporaryRoot=os.tmpdir()){
 check(plan?.status==='GREEN_SOURCE_PLAN_ONLY'&&SHA.test(plan.sourceRef),'PLAN_REQUIRED');
 const folder=fs.mkdtempSync(path.join(temporaryRoot,'luhm-plan-'));
 let ok=false;
 try{
  const receipt={sourceRef:plan.sourceRef,modules:plan.planOrder,install:false,delete:false};
  fs.writeFileSync(path.join(folder,'receipt.json'),JSON.stringify(receipt),{flag:'wx',mode:0o600});
  const got=JSON.parse(fs.readFileSync(path.join(folder,'receipt.json'),'utf8'));
  ok=got.sourceRef===plan.sourceRef&&got.modules.length===plan.planOrder.length;
 }finally{fs.rmSync(folder,{recursive:true,force:true});}
 check(ok&&!fs.existsSync(folder),'ROLLBACK_NOT_VERIFIED');
 return {...plan,mode:'try',status:'GREEN_TEMP_SIMULATION_ONLY',stagingRemoved:true,hostChanged:false};
}
export function applyThinPackages(){throw new Error('APPLY_BLOCKED_EXACT_CAST_DEVICE_SIGNER_AND_ROLLBACK_PROOF_REQUIRED');}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 try{
  const [mode,sha,...rest]=process.argv.slice(2);
  check(rest.length===0&&['plan','try','apply'].includes(mode),'USAGE: thin-package.mjs plan|try|apply EXACT_SHA');
  if(mode==='apply')applyThinPackages();
  const policy=JSON.parse(fs.readFileSync(path.join(ROOT,'doctrine/luhmThinPackagePlanV1.json'),'utf8'));
  const plan=planThinPackages(sha,policy);
  console.log(JSON.stringify(mode==='try'?tryThinPackages(plan):plan,null,2));
 }catch(error){console.error(error.message);process.exitCode=2;}
}
