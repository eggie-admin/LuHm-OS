import assert from "node:assert/strict";
import test from "node:test";
import {decodeLuHmHexCommand,buildLuHmHexCastManifest,getLuHmHexCastIntent,luhmCastHexIdentity}
  from "../core/machineCastHexBridge.mjs";
import {installLuHmHexCastBridgePlugin} from "../jquery/luhm.hexCastBridge.mjs";

const sha="a".repeat(40);
const packet={sourceRef:sha,taskId:"machineCastReview",scopeId:"machineSql"};

test("CAST ASCII hex and candidate opcode are distinct from audit coordinates",()=>{
  assert.equal(Buffer.from("CAST").toString("hex").toUpperCase(),"43415354");
  assert.equal(luhmCastHexIdentity.displayName,"LuHm-OS");
  const d=decodeLuHmHexCommand("0xC1");
  assert.equal(d.command,"castIntent");
  assert.equal(d.effect,"INTENT_ONLY");
  assert.equal(d.dispatchAuthorized,false);
  for(const bad of ["0x43415354","0xC0","0x00","0x3F","0xc1","C1",0xC1,
                    "__proto__","../shell","CAST"]){
    assert.throws(()=>decodeLuHmHexCommand(bad),/RED_UNKNOWN_EXACT_HEX_OPCODE/);
  }
});

test("AI manifest is strict v2, bounded and incapable of granting authority",()=>{
  const m=buildLuHmHexCastManifest(packet);
  assert.equal(m.schema,"luhmOs.aiTaskManifest.v2");
  assert.equal(m.machineBridge.opcode,"0xC1");
  assert.equal(m.machineBridge.stage,"castBridge");
  assert.equal(m.machineBridge.fromStage,"castProposed");
  assert.deepEqual(m.authority,{mutation:false,green:false,crown:false});
  assert.deepEqual(m.budget,{maxRequests:1,maxParallel:1,maxPasses:1});
  assert.deepEqual(m.inputRefs,[]);
  assert.equal(m.machineBridge.machineSqlWritable,false);
  const x=getLuHmHexCastIntent(packet);
  assert.equal(x.status,"CANDIDATE_ONLY_PYTHON_REVALIDATION_REQUIRED");
  assert.equal(x.sourceBound,"NOT_SERVER_VALIDATED");
  assert.equal(x.dispatchAuthorized,false);
  assert.equal(x.crownGranted,false);
});

test("full source identity, camelHump scope and Canon tier rejects lookalikes",()=>{
  for(const bad of ["","a".repeat(39),"a".repeat(41),"A".repeat(40),"g".repeat(40),123,null]){
    assert.throws(()=>buildLuHmHexCastManifest({...packet,sourceRef:bad}),/RED_EXACT_SOURCE_REQUIRED/);
  }
  for(const bad of ["_x","A","my-task","../../secrets","",5,"0xC1"]){
    assert.throws(()=>buildLuHmHexCastManifest({...packet,taskId:bad}),/RED_BOUNDED_TASK_SCOPE_REQUIRED/);
  }
  assert.throws(()=>buildLuHmHexCastManifest({...packet,tier:"nuclearAdmin"}),/RED_CANON_COORDINATE_REQUIRED/);
  assert.throws(()=>getLuHmHexCastIntent({...packet,sql:"DROP TABLE"}),/RED_UNKNOWN_CAST_INPUT/);
  assert.throws(()=>getLuHmHexCastIntent(null),/RED_UNKNOWN_CAST_INPUT/);
});

test("optional $.fn only, chainable; does not replace cockpit nor contact network",()=>{
  const events=[];
  function $(element){return {trigger(name,args){events.push({element,name,args});}}}
  const existing=()=> "original cockpit";
  $.fn={each() {},luhmCockpit:existing,luhmParallax:existing};
  assert.equal(installLuHmHexCastBridgePlugin($),$);
  assert.equal($.fn.luhmCockpit,existing);
  assert.equal($.fn.luhmParallax,existing);
  const element={id:"safe"};
  const selection={each(fn){fn.call(element);return this;}};
  assert.equal($.fn.luhmHexCastBridge.call(selection,packet),selection);
  assert.equal(events.length,1);
  assert.equal(events[0].name,"luhm:cast:intent");
  assert.equal(events[0].args[0].opcode,"0xC1");
  assert.equal(events[0].args[0].dispatchAuthorized,false);
  assert.throws(()=>installLuHmHexCastBridgePlugin($),/RED_JQUERY_SLOT_COLLISION/);
  assert.throws(()=>$.fn.luhmHexCastBridge.call(selection,{...packet,sql:"DROP TABLE"}),/RED_UNKNOWN_CAST_INPUT/);
  assert.equal(events.length,1);
});
