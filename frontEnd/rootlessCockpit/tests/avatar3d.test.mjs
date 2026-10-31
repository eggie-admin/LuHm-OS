import test from "node:test";
import assert from "node:assert/strict";
import {createAvatarGeometry,mountAvatarPreview,AVATAR_INFO} from "../avatar3d.mjs";
test("original adult character is a real indexed triangle mesh with no downloaded assets",()=>{
  const mesh=createAvatarGeometry();
  assert.equal(AVATAR_INFO.adult,true);
  assert.equal(AVATAR_INFO.rigged,false);
  assert.equal(mesh.rigged,false);
  assert.equal(mesh.modelDownloaded,false);
  assert.ok(mesh.triangles>1500&&mesh.triangles<=AVATAR_INFO.maxTriangles);
  assert.ok(mesh.vertexCount>2500);
  assert.equal(mesh.indices.length,mesh.triangles*3);
  assert.equal(mesh.positions.length,mesh.normals.length);
  assert.equal(mesh.positions.length,mesh.colors.length);
  assert.ok(mesh.parts.includes("opaque-bust-panel-1"));
  assert.ok(mesh.parts.includes("pleated-velvet-skirt"));
  assert.ok(mesh.parts.includes("curved-oni-horn-1"));
  assert.ok(mesh.parts.includes("eyeball-1"));
});
test("topology and color coordinates have bounded finite values",()=>{
  const mesh=createAvatarGeometry();
  assert.ok([...mesh.positions].every(Number.isFinite));
  assert.ok([...mesh.normals].every(x=>Number.isFinite(x)&&Math.abs(x)<=1.001));
  assert.ok([...mesh.colors].every(x=>Number.isFinite(x)&&x>=0&&x<=1));
  assert.ok([...mesh.indices].every(i=>i>=0&&i<mesh.vertexCount));
  assert.ok(Math.max(...mesh.positions)<5&&Math.min(...mesh.positions)>-5);
});
test("no GPU gracefully keeps the 2D original artwork",()=>{
  const fallback={hidden:false},report={textContent:""};
  assert.equal(mountAvatarPreview(null,fallback,report).status,"FALLBACK");
  assert.equal(mountAvatarPreview({getContext:()=>null},fallback,report).status,"FALLBACK");
  assert.equal(fallback.hidden,false);
  assert.match(report.textContent,/2D artwork/);
});
test("no external CDN, model loads, eval, or auto asset downloads",async()=>{
  const fs=await import("node:fs/promises");
  const source=await fs.readFile(new URL("../avatar3d.mjs",import.meta.url),"utf8");
  for(const forbidden of [/fetch\s*\(/,/eval\s*\(/,/XMLHttpRequest/,/import\(/,/https?:\/\//])assert.doesNotMatch(source,forbidden);
  assert.match(source,/getContext\("webgl2"/);
  assert.match(source,/prefers-reduced-motion/);
  assert.match(source,/webglcontextlost/);
});
