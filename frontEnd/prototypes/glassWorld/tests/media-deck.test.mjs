import test from "node:test";
import assert from "node:assert/strict";
import { classifyLocalMedia } from "../src/media-deck.js";
test("local MP4 and audio files classify without network",()=>{
 assert.equal(classifyLocalMedia({name:"shot.mp4",size:1000,type:"video/mp4"}).kind,"video");
 assert.equal(classifyLocalMedia({name:"music.mp3",size:500,type:"audio/mpeg"}).kind,"audio");
});
test("bad URLs, unsupported types and oversized media rejected",()=>{
 for(const f of [
  {name:"remote.mp4",size:1e9,type:"video/mp4"},
  {name:"evil.svg",size:10,type:"image/svg+xml"},
  {name:"script.mp4",size:10,type:"text/html"},
  {name:"empty.mp4",size:0,type:"video/mp4"}
 ])assert.throws(()=>classifyLocalMedia(f));
});
test("the browser adapter never opens VLC or submits an upload",async()=>{
 const {readFile}=await import("node:fs/promises");
 const source=await readFile(new URL("../src/media-deck.js",import.meta.url),"utf8");
 assert.match(source,/URL.createObjectURL/);
 assert.match(source,/URL.revokeObjectURL/);
 assert.match(source,/luhm:media:preview/);
 assert.doesNotMatch(source,/fetch\s*\(/);
 assert.doesNotMatch(source,/https?:\/\//);
 assert.match(source,/crownGranted:false/);
});
