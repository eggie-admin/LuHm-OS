import test from "node:test";
import assert from "node:assert/strict";
import { classifyLocalMedia } from "../src/media-deck.js";
import { sceneSignal } from "../src/jquery-bridge.js";
test("local MP4, audio, and WebP or PNG images classify without network", () => {
  assert.equal(classifyLocalMedia({name:"shot.mp4",size:1000,type:"video/mp4"}).kind,"video");
  assert.equal(classifyLocalMedia({name:"music.mp3",size:500,type:"audio/mpeg"}).kind,"audio");
  assert.equal(classifyLocalMedia({name:"hero.webp",size:3000,type:"image/webp"}).kind,"image");
  assert.equal(classifyLocalMedia({name:"matte.png",size:1200,type:"image/png"}).kind,"image");
  assert.equal(classifyLocalMedia({name:"poster.avif",size:1700,type:"image/avif"}).kind,"image");
});
test("SVG, remote path, oversized WebP, mismatched MIME and unsupported media rejected", () => {
  for (const f of [
    {name:"remote.mp4",size:1e9,type:"video/mp4"},
    {name:"evil.svg",size:10,type:"image/svg+xml"},
    {name:"script.mp4",size:10,type:"text/html"},
    {name:"empty.mp4",size:0,type:"video/mp4"},
    {name:"too-large.webp",size:25*1024*1024,type:"image/webp"},
    {name:"https://attacker/image.webp",size:10,type:"image/webp"},
    {name:"fake.png",size:10,type:"image/webp"}
  ]) assert.throws(()=>classifyLocalMedia(f));
});
test("isolated Glass World uses native events without importing jQuery", async () => {
  const {readFile}=await import("node:fs/promises");
  for (const name of ["src/media-deck.js","src/jquery-bridge.js"]) {
    const source=await readFile(new URL("../"+name,import.meta.url),"utf8");
    assert.doesNotMatch(source,/from\s*["']jquery["']/);
    assert.match(source,/new CustomEvent\(/);
    assert.doesNotMatch(source,/fetch\s*\(/);
  }
  assert.equal(sceneSignal(null,"placed"),false);
  assert.equal(sceneSignal({dispatchEvent(){}}, "invalid"),false);
});
test("native scene events preserve data and prevent authority upgrades", () => {
  const saved=globalThis.CustomEvent;
  globalThis.CustomEvent=class {constructor(type,options){this.type=type;this.detail=options.detail;}};
  try {
    const received=[];
    assert.equal(sceneSignal({dispatchEvent(e){received.push(e);}},"placed",{objectId:"obj-001",revision:7}),true);
    assert.equal(received[0].type,"luhm:scene:placed");
    assert.equal(received[0].detail.crownGranted,false);
    assert.equal(received[0].detail.revision,7);
  } finally { if(saved===undefined)delete globalThis.CustomEvent; else globalThis.CustomEvent=saved; }
});
test("media preview revokes blob URLs and does not offer VLC NPAPI or upload",async()=>{
  const {readFile}=await import("node:fs/promises");
  const source=await readFile(new URL("../src/media-deck.js",import.meta.url),"utf8");
  assert.match(source,/URL.createObjectURL/);
  assert.match(source,/URL.revokeObjectURL/);
  assert.match(source,/luhm:media:preview/);
  assert.doesNotMatch(source,/https?:\/\//);
  assert.match(source,/crownGranted: false/);
  assert.match(source,/nativeVlcRunning: false/);
});
