import test from "node:test";
import assert from "node:assert/strict";
import {
 pinnedSourceRef,canonicalRoster,workflowStages,routing,observedServices,
 classifyAssetFile,assetSummary,createTaskEnvelope,inspectReceipt,canPromote
} from "../canonControlRoom.mjs";

test("retains the one canonical 15-member roster and eight stages",()=>{
 assert.equal(canonicalRoster.length,15);
 assert.equal(new Set(canonicalRoster).size,15);
 assert.equal(canonicalRoster[0],"lum");
 assert.deepEqual(workflowStages,["sanityCheck","audit","ingest","mutation","test","apply","continue","deploy"]);
 for(const workers of Object.values(routing)){
  assert.equal(workers[0],"lum");
  assert.ok(workers.length<=4);
  assert.ok(workers.every(w=>canonicalRoster.includes(w)));
 }
});
test("labels subscription separately from developer billing",()=>{
 assert.equal(observedServices.find(s=>s.id==="googleAiPro").state,"HISTORICALLY_CONFIRMED");
 assert.equal(observedServices.find(s=>s.id==="googleAi").state,"BLOCKED");
 assert.match(observedServices.find(s=>s.id==="googleAi").detail,/November 6/);
 assert.notEqual(observedServices.find(s=>s.id==="openAiMini").state,"LIVE");
});
test("does not unpack, execute or approve discovered local files",()=>{
 for(const [name,lane] of [["any.zip","archive"],["Eve.blend","models"],["walk.png","sprites"],["scene.mp4","video"],["code.py","quarantineScripts"],["voice.ogg","audio"],["file.xyz","unclassified"]]){
  assert.equal(classifyAssetFile(name),lane);
 }
 assert.deepEqual(assetSummary([{name:"a.png",size:1024},{name:"b.glb",size:2048}]),{
  count:2,totalBytes:3072,counts:{sprites:1,models:1},sizes:{sprites:1024,models:2048}
 });
});
test("task envelopes remain exact-source, planning-only, and human gated",()=>{
 const packet=createTaskEnvelope({lane:"architecture",intent:"audit Godot source",taskId:"ticket1",scopeId:"local",sourceRef:pinnedSourceRef});
 assert.equal(packet.schema,"luhmOs.aiTaskManifest.v2");
 assert.equal(packet.authorityClass,"PLAN_ONLY");
 assert.deepEqual(packet.authority,{mutation:false,green:false,crown:false});
 assert.equal(packet.providerPolicy.googleAi.startsWith("BLOCKED"),true);
 assert.equal(packet.crownStatus,"STOP");
 assert.equal(packet.budget.maxRequests,1);
 assert.deepEqual(packet.workerIds,["lum","skuldResearch","urdDoctorGoddess"]);
 assert.throws(()=>createTaskEnvelope({lane:"developer",intent:"x",taskId:"a",scopeId:"b",sourceRef:pinnedSourceRef}));
 assert.throws(()=>createTaskEnvelope({lane:"canon",intent:"x",taskId:"a",scopeId:"b",sourceRef:"abc"}));
});
test("received evidence shape never silently becomes runtime GREEN",()=>{
 const expected={taskId:"abc",scopeId:"local",sourceRef:pinnedSourceRef};
 const packet={...expected,evidenceRefs:["candidateReceipt"]};
 assert.deepEqual(inspectReceipt(packet,expected),{accepted:true,reason:"SHAPE_ACCEPTED_NOT_GREEN"});
 assert.equal(inspectReceipt({...packet,taskId:"wrong"},expected).accepted,false);
 assert.equal(inspectReceipt({...packet,evidenceRefs:[]},expected).accepted,false);
 assert.equal(inspectReceipt({taskId:"abc"}).accepted,false);
});
test("promotion requires release from quarantine and all approvals",()=>{
 assert.equal(canPromote({quarantine:true,rightsApproved:true,hostProof:true,deviceProof:true,humanApproval:true}),false);
 assert.equal(canPromote({quarantine:false,rightsApproved:true,hostProof:false,deviceProof:true,humanApproval:true}),false);
 assert.equal(canPromote({quarantine:false,rightsApproved:true,hostProof:true,deviceProof:true,humanApproval:true}),true);
});
