import test from "node:test";
import assert from "node:assert/strict";
import {buildCrownLayout,crownModes,crownLayoutSchema} from "../src/crown-cathedral-layout.mjs";
test("all three branded environment modes are bounded and have an original 3D proxy",()=>{
 for(const mode of crownModes){
   const one=buildCrownLayout(mode),two=buildCrownLayout(mode);
   assert.equal(one.schema,crownLayoutSchema);assert.equal(one.mode,mode);
   assert.ok(one.parts.length>20&&one.parts.length<=128);
   assert.deepEqual(one,two);
   assert.equal(new Set(one.parts.map(x=>x.id)).size,one.parts.length);
   assert.equal(one.runtimeAuthority,false);assert.equal(one.publicationAuthority,false);
   assert.ok(one.parts.some(x=>x.id==="proxy-head"));
   assert.ok(one.attribution.includes("NOT the approved"));
 }
});
test("3D layout coordinates, colors, sizes and kinds are all within strict bounds",()=>{
 for(const mode of crownModes){
  for(const x of buildCrownLayout(mode).parts){
   assert.match(x.id,/^[a-z0-9-]+$/);assert.match(x.color,/^#[0-9a-f]{6}$/);
   assert.ok(["box","sphere","cylinder","torus"].includes(x.kind));
   for(const value of Object.values(x.position))assert.ok(Number.isFinite(value)&&Math.abs(value)<=18);
   for(const value of Object.values(x.size))assert.ok(Number.isFinite(value)&&value>0&&value<=18);
  }
 }
});
test("unknown world cannot activate remote models or provider routes",()=>{
 for(const mode of ["__proto__","remote","https://host.invalid/model.glb","",42,null])
  assert.throws(()=>buildCrownLayout(mode),/RED_CROWN_MODE/);
});
