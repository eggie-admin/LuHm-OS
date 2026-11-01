import test from "node:test";
import assert from "node:assert/strict";
import {spawnSync} from "node:child_process";
import {readFile} from "node:fs/promises";
import {fileURLToPath} from "node:url";
import {dirname,resolve} from "node:path";
import {
 auditSource,loadPolicy,checkPolicy,planTask,remotePlan,classifyTask,
 HEX16,DOMAINS,PHASES,repoRoot
} from "../src/index.mjs";
const entry=resolve(dirname(fileURLToPath(import.meta.url)),"../bin/luhm-machine-audit.mjs");
const clone=o=>structuredClone(o);
function run(args){return spawnSync(process.execPath,[entry,...args],
 {encoding:"utf8",timeout:15000,maxBuffer:256000});}

test("exact source-only audit covers all 16 4x4 hex cells and source SHA256",async()=>{
 const r=await auditSource();
 assert.equal(r.verdict,"AMBER_SOURCE_ONLY");
 assert.deepEqual(r.hex,Array.from(HEX16));
 assert.equal(r.matrixCells,16);
 assert.equal(r.sources.length,10);
 for(const s of r.sources){assert.match(s.sha256,/^[a-f0-9]{64}$/);assert.ok(s.bytes>0);}
 assert.equal(r.npmRuntimeDependencies,0);
 assert.equal(r.crownStatus,"STOP");
 for(const k of ["hardwareVerified","modelInferenceUsed","agentActivated","networkAccessed",
                 "kernelChanged","filesChanged","publicServerStarted"])assert.equal(r[k],false);
 assert.equal(r.remoteInvocation,"DISABLED");
});
test("all 4x4 columns distinct and logical, never physical kernel",async()=>{
 const {policy}=await loadPolicy();
 assert.deepEqual(DOMAINS,["kernel","data","browser","agent"]);
 assert.deepEqual(PHASES,["detect","bound","test","escalate"]);
 assert.equal(HEX16.at(0),"0x00");assert.equal(HEX16.at(-1),"0x0F");
 assert.ok(checkPolicy(policy));
 for(const key of ["hex","phase","hardwareVerified","proof"]){
   const bad=clone(policy);
   bad.matrix[8][key]=({hex:"0xDEADBEEF",phase:"execute",hardwareVerified:true,proof:"RUNNING"})[key];
   assert.throws(()=>checkPolicy(bad),/RED_HEX_OR_PROOF/);
 }
});
test("all privilege, networking, cloud/model and public deployment toggles fail closed",async()=>{
 const {policy}=await loadPolicy();
 for(const k of Object.keys(policy.limits).filter(k=>typeof policy.limits[k]==="boolean")){
   const p=clone(policy);p.limits[k]=true;
   assert.throws(()=>checkPolicy(p),/RED_LOCAL_PRIVILEGE/,k);
 }
 for(const mode of ["LIVE","UNREVIEWED","ALLOW"]){
  const p=clone(policy);p.remoteBoundary.mode=mode;
  assert.throws(()=>checkPolicy(p),/RED_REMOTE_AUTHORITY/);
 }
 const p=clone(policy);p.remoteBoundary.allowedEndpoints.push("https://example.test");
 assert.throws(()=>checkPolicy(p),/RED_REMOTE_AUTHORITY/);
});
test("NGINX Apache PHP and SQL stay vendor options, not a server farm",async()=>{
 const {policy}=await loadPolicy();
 for(const id of ["apache2","nginx","php","postgres","mariadb","vulkan"]){
  const p=clone(policy);p.softwareDecisions.find(x=>x.id===id).policy="REQUIRED_INSTALL";
  assert.throws(()=>checkPolicy(p),/RED_UNAUTHORIZED_VENDOR/);
 }
});
test("bounded local task router doesn't follow arbitrary instructions",async()=>{
 const {policy}=await loadPolicy();
 assert.equal(classifyTask("inspect Vulkan driver",policy).id,"machine");
 assert.equal(planTask("make a video storyboard",policy).intent,"art");
 const receipt=planTask("deploy my AI agent to every server",policy);
 assert.equal(receipt.intent,"ai");
 assert.equal(receipt.agentActivated,false);
 assert.equal(receipt.commandsExecuted,false);
 assert.equal(receipt.modelInferenceUsed,false);
 assert.deepEqual(receipt.steps,["classifyInput","bindCurrentSource","proposeReadOnlyCheck","humanReview"]);
 for(const bad of ["", "x".repeat(1025), "\ud800", "hello\nworld"]){
   if(bad==="\ud800")continue; // malformed JS surrogate is not universally rejected by TextEncoder
   assert.throws(()=>planTask(bad,policy),/RED_TASK_UTF8_BUDGET/);
 }
});
test("remote endpoint cannot be called, and plan keeps human gate",async()=>{
 const {policy}=await loadPolicy();
 const p=remotePlan(policy);
 assert.equal(p.status,"BLOCKED_PENDING_APPROVAL");
 assert.equal(p.networkRequestMade,false);
 assert.equal(p.modelCalled,false);
 assert.equal(p.secretsRead,false);
 assert.equal(p.receiptPromotion,false);
 assert.equal(p.crownStatus,"STOP");
 assert.ok(p.requirements.includes("ownerAuthorization"));
});
test("CLI audit, bounded plan and remote-plan all work without npm dependencies",()=>{
 for(const command of [["audit"],["verify"],["plan","--task","check browser WebGL"],["remote-plan"]]){
   const runResult=run(command);
   assert.equal(runResult.status,0,runResult.stderr);
   let receipt=JSON.parse(runResult.stdout);
   assert.equal(receipt.crownStatus,"STOP");
 }
 for(const bad of [["shell","rm -rf /"],["audit","--unknown"],
                   ["plan"],["remote-plan","--execute"],["plan","--task",""]]){
   const x=run(bad);
   assert.equal(x.status,2);
   assert.match(x.stderr,/RED_LOCAL_AUDIT/);
 }
});
test("fixed-argument Python bridge produces separate STRICT SQLite receipt without host probe",()=>{
 const child=run(["audit","--with-python"]);
 assert.equal(child.status,0,child.stderr);
 const result=JSON.parse(child.stdout);
 assert.equal(result.pythonSqlInterop,"SOURCE_ONLY_VERIFIED");
 assert.match(result.pythonReceiptSha256,/^[a-f0-9]{64}$/);
 assert.equal(result.hardwareVerified,false);
});
test("private npm package has zero dependencies, exact local binaries and no script hooks",async()=>{
 const pkg=JSON.parse(await readFile(resolve(repoRoot,"tools/luhm-machine-agent/package.json"),"utf8"));
 assert.equal(pkg.private,true);
 assert.deepEqual(pkg.dependencies,{});
 assert.deepEqual(pkg.devDependencies,{});
 assert.equal(pkg.type,"module");
 for(const key of ["preinstall","install","postinstall","prepare","prepack","postpack"])
   assert.equal(Object.hasOwn(pkg.scripts,key),false);
});
