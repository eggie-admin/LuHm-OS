import test from "node:test";
import assert from "node:assert/strict";
import {validateUniversalRoute,renderUniversalRoute} from "../frontEnd/universalRouteProjection.mjs";
const sha="a".repeat(40);
function good() {return {
  schema:"luhmOs.universalRoutePlan.v1",sourceRef:sha,taskId:"source-task",
  lane:"lts",transport:"offlineFallback",capability:"sourceStatus",proposedRole:"skuldResearch",
  status:"SOURCE_ONLY",routeAvailable:false,workerExecuted:false,providerConnected:false,
  authorizedToMutate:false,crownStatus:"STOP",evidenceHash:"b".repeat(64)};}
test("all release lanes remain source-only",()=>{
 for(const lane of ["nightly","beta","lts","legacy"]) {
  const p=good();p.lane=lane;
  assert.equal(validateUniversalRoute(p,sha).lane,lane);
 }
});
test("all transport candidates are explicit",()=>{
 for(const transport of ["currentRenderDirect","candidateCloudflareTunnel","privateStudioLoopback","offlineFallback"]) {
  const p=good();p.transport=transport;
  assert.equal(validateUniversalRoute(p,sha).transport,transport);
 }
});
test("HTML is rendered with textContent only",()=>{
 const element={textContent:""};
 renderUniversalRoute(element,good(),sha);
 assert.match(element.textContent,/SOURCE ONLY; CROWN STOP/);
});
test("permission escalation fails closed",()=>{
 const p=good();p.workerExecuted=true;
 assert.throws(()=>validateUniversalRoute(p,sha),/NO_RUNTIME_AUTHORITY/);
});
test("route spoofing and extras fail closed",()=>{
 const p=good();p.transport="evilProxy";
 assert.throws(()=>validateUniversalRoute(p,sha),/ROUTE_PARAMETERS_INVALID/);
 p.transport="offlineFallback";p.extra="unreviewed";
 assert.throws(()=>validateUniversalRoute(p,sha),/UNEXPECTED_FIELDS/);
});
test("source and XSS task injection rejected",()=>{
 const p=good();p.taskId="<script>";
 assert.throws(()=>validateUniversalRoute(p,sha),/ROUTE_PARAMETERS_INVALID/);
 p.taskId="source-task";
 assert.throws(()=>validateUniversalRoute(p,"c".repeat(40)),/SOURCE_REF_INVALID/);
});
