import test from "node:test";
import assert from "node:assert/strict";
import { createModule, validateModule, rollDice, step } from "../src/engine.mjs";

test("original RPG module template passes validation without vendor content",()=>{
 const m=createModule("moonlit-archive","a".repeat(40));
 const v=validateModule(m);
 assert.equal(v.moduleId,"moonlit-archive");
 assert.equal(v.nodeCount,4);
 assert.equal(v.rights,"originalOwned");
 assert.equal(v.distributionApproved,false);
 assert.equal(v.externalArtApproved,false);
 assert.equal(m.start,"gate");
});
test("deterministic bounded dice replay, not crypto or public gambling",()=>{
 const a=rollDice("2d6+2",2026),b=rollDice("2d6+2",2026);
 assert.deepEqual(a,b);assert.equal(a.faces.length,2);
 assert.equal(a.total,a.faces[0]+a.faces[1]+2);
 assert.match(a.status,/SYNTHETIC/);
 for(const expression of ["1d20+2","20d100","3d8-5","1d4"]){
  const x=rollDice(expression,77);
  assert.ok(Number.isInteger(x.total));
 }
 for(const bad of ["100d20","21d6","1d200","d6","1d6+999",
   "1d20;eval","2D6","0d6","1d20 + 1","1d6**2",null]) {
  assert.throws(()=>rollDice(bad,1));
 }
});
test("bounded character action transition and granted resource are only data",()=>{
 const m=createModule("candle-hall","b".repeat(40));
 const a=step(m,"gate",0,2026);
 assert.equal(a.from,"gate");assert.equal(a.to,"vault");
 assert.equal(a.networkCalls,0);assert.equal(a.pluginCalls,0);
 assert.equal(a.productionGameProven,false);
 const b=step(m,"gate",1,2026);
 assert.deepEqual(b.effect,{type:"grant",resource:"focus",amount:1});
 assert.throws(()=>step(m,"ending",0));
 assert.throws(()=>step(m,"gate",10));
});
test("hostile graph cannot inject imports, shell commands or reach nonexistent node",()=>{
 const base=createModule("moonlit-archive","f".repeat(40));
 const inject=structuredClone(base);
 inject.nodes[0].choices[0].shell="rm -rf /";
 assert.throws(()=>validateModule(inject),/RED_RPG_CHOICE_FIELDS/);
 const dangling=structuredClone(base);
 dangling.nodes[0].choices[0].target="missing";
 assert.throws(()=>validateModule(dangling),/RED_RPG_MISSING_TARGET/);
 const evalNode=structuredClone(base);
 evalNode.nodes[0].type="script";
 assert.throws(()=>validateModule(evalNode),/RED_RPG_NODE_TYPE/);
 const oversized=structuredClone(base);
 oversized.nodes[0].text="a".repeat(1000);
 assert.throws(()=>validateModule(oversized),/RED_RPG_TEXT/);
 const privileges=structuredClone(base);
 privileges.rights="NexusAutoImported";
 assert.throws(()=>validateModule(privileges),/RED_RPG_RIGHTS/);
});
test("collision, bad slug, unknown dice and out-of-scope effects denied",()=>{
 for(const name of ["../evil","evil/path","UPPER","", "a".repeat(49),"constructor"]){
   assert.throws(()=>createModule(name),/RED_RPG_SLUG/);
 }
 const dupe=createModule();
 dupe.nodes[1].id="gate";
 assert.throws(()=>validateModule(dupe),/RED_RPG_DUPLICATE_NODE/);
 const effect=createModule();
 effect.nodes[0].choices[0].effect={type:"execute",resource:"shell",amount:1};
 assert.throws(()=>validateModule(effect),/RED_RPG_EFFECT_TYPE/);
 const badRights=createModule();
 badRights.sourceRef="main";
 assert.throws(()=>validateModule(badRights),/RED_RPG_SOURCE_ID/);
});
