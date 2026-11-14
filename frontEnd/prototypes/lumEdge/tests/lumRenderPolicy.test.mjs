import test from "node:test";
import assert from "node:assert/strict";
import {chooseRenderPolicy} from "../src/lumRenderPolicy.mjs";

test("Chromium-capable desktop uses bounded WebGL2 shadow quality",()=>{
  const p=chooseRenderPolicy({webGlVersion:2});
  assert.equal(p.renderer,"WEBGL2");
  assert.equal(p.shadowMapSize,1024);
  assert.equal(p.defaultShadows,true);
  assert.equal(p.nativeVulkan,false);
});
test("coarse-pointer devices cap map size and pixel ratio",()=>{
  const p=chooseRenderPolicy({webGlVersion:2,coarsePointer:true});
  assert.equal(p.shadowMapSize,512);
  assert.equal(p.maxPixelRatio,1.25);
});
test("WebGL1 and reduced-motion pathways never silently claim full renderer",()=>{
  const fallback=chooseRenderPolicy({webGlVersion:1});
  assert.equal(fallback.shadowMapSize,0);
  assert.equal(fallback.defaultShadows,false);
  const reduced=chooseRenderPolicy({webGlVersion:2,reducedMotion:true});
  assert.equal(reduced.defaultShadows,false);
  assert.equal(reduced.shadowMapSize,512);
});
test("no editable renderer escalation state",()=>{
  assert.equal(Object.isFrozen(chooseRenderPolicy({webGlVersion:2})),true);
});
