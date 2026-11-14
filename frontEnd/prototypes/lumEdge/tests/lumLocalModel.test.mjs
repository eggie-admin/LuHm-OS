import test from "node:test";
import assert from "node:assert/strict";
import { inspectLocalGlb, maxLumGlbBytes } from "../src/lumLocalModel.mjs";

function fakeGlb(json, name="LuHm-OS.glb") {
  const raw = Buffer.from(JSON.stringify(json));
  const pad = (4 - raw.length % 4) % 4;
  const jsonChunk = Buffer.concat([raw,Buffer.alloc(pad,32)]);
  const bytes = Buffer.alloc(20+jsonChunk.length);
  bytes.write("glTF",0,4,"ascii");
  bytes.writeUInt32LE(2,4);
  bytes.writeUInt32LE(bytes.length,8);
  bytes.writeUInt32LE(jsonChunk.length,12);
  bytes.write("JSON",16,4,"ascii");
  jsonChunk.copy(bytes,20);
  return Object.assign(new Blob([bytes]),{name});
}
const model = {asset:{version:"2.0"},nodes:[{}],meshes:[{}],
  buffers:[{byteLength:4}],images:[{bufferView:1,mimeType:"image/png"}],
  animations:[{name:"Lum Running"}]};
test("embedded GLB is inspected locally and exposes bounded metadata",async()=>{
  const r=await inspectLocalGlb(fakeGlb(model));
  assert.equal(r.embeddedOnly,true);
  assert.equal(r.animations,1);
  assert.deepEqual(r.animationNames,["Lum Running"]);
});
test("remote image URI fails closed",async()=>{
  await assert.rejects(inspectLocalGlb(fakeGlb({...model,images:[{uri:"https://bad.example/track.png"}]})),/RED_EXTERNAL_GLB_URI/);
});
test("relative external texture URI fails closed too",async()=>{
  await assert.rejects(inspectLocalGlb(fakeGlb({...model,images:[{uri:"texture.png"}]})),/RED_EXTERNAL_GLB_URI/);
});
test("non-GLB filename, corrupt magic and excessive file size are rejected",async()=>{
  await assert.rejects(inspectLocalGlb(fakeGlb(model,"malicious.gltf")),/RED_GLB_SIZE_OR_TYPE/);
  const wrong = fakeGlb(model);const b=Buffer.from(await wrong.arrayBuffer());b.write("BAD!",0);
  await assert.rejects(inspectLocalGlb(Object.assign(new Blob([b]),{name:"bad.glb"})),/RED_GLB_HEADER/);
  const tooBig=Object.assign({name:"huge.glb",size:maxLumGlbBytes+1,slice:()=>{throw Error("should not read")}} ,{});
  await assert.rejects(inspectLocalGlb(tooBig),/RED_GLB_SIZE_OR_TYPE/);
});
test("unsupported codec and high node count are rejected",async()=>{
  await assert.rejects(inspectLocalGlb(fakeGlb({...model,extensionsRequired:["KHR_draco_mesh_compression"]})),/RED_GLB_UNSUPPORTED_CODEC/);
  await assert.rejects(inspectLocalGlb(fakeGlb({...model,nodes:Array.from({length:1001},()=>({}))})),/RED_GLB_COMPLEXITY/);
});

test("embedded normal and ORM maps are counted without claiming GPU visual proof",async()=>{
  const source={...model,textures:[{source:0}],materials:[
    {normalTexture:{index:0},pbrMetallicRoughness:{metallicRoughnessTexture:{index:0}}}
  ]};
  const r=await inspectLocalGlb(fakeGlb(source));
  assert.equal(r.normalMaps,1);
  assert.equal(r.roughnessMaps,1);
  assert.equal(r.surfaceProof,"METADATA_ONLY");
});
test("out-of-range normal map texture references fail closed",async()=>{
  await assert.rejects(inspectLocalGlb(fakeGlb({...model,materials:[{normalTexture:{index:99}}],textures:[{source:0}]})),/RED_GLB_TEXTURE_INDEX/);
  await assert.rejects(inspectLocalGlb(fakeGlb({...model,materials:[{}],textures:[{source:99}]})),/RED_GLB_TEXTURE_IMAGE/);
});
