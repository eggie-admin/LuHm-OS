import test from "node:test";
import assert from "node:assert/strict";
import {validateForgeProjection,showForgeProjection} from "../frontEnd/forgeSourceProjection.mjs";
const sha="a".repeat(40);
function sample(){return {schema:"luhmOs.forgeSourceProjection.v1",sourceRef:sha,
 taskId:"task-1",scopeId:"source-only",mode:"headless",tier:0,
 sql:"SQLITE_STRICT_JSON1_GREEN",workerExecuted:false,providerConnected:false,
 authorityEffect:"none",crownStatus:"STOP",evidenceHash:"b".repeat(64)};}
test("four-source view projection is read only",()=>{
  for(const m of ["headless","witchingHour","corporate","githubDevelopment"]){
    const data=sample();data.mode=m;
    assert.equal(validateForgeProjection(data,sha).mode,m);
  }
});
test("safe rendering uses textContent only",()=>{
 const el={textContent:""};
 showForgeProjection(el,sample(),sha);
 assert.match(el.textContent,/CROWN STOP/);
});
test("source mismatch or fake worker fails closed",()=>{
 assert.throws(()=>validateForgeProjection(sample(),"c".repeat(40)),/SOURCE_MISMATCH/);
 const data=sample();data.workerExecuted=true;
 assert.throws(()=>validateForgeProjection(data,sha),/AUTHORITY/);
});
test("injected HTML in taskId is refused",()=>{
 const data=sample();data.taskId="<img src=x onerror=alert(1)>";
 assert.throws(()=>validateForgeProjection(data,sha),/INVALID_ID/);
});
test("extra keys are never trusted",()=>{
 const data=sample();data.token="private";
 assert.throws(()=>validateForgeProjection(data,sha),/FIELDS/);
});
