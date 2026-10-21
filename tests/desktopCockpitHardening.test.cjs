"use strict";
const fs = require("node:fs");
const vm = require("node:vm");
const assert = require("node:assert/strict");

const js = fs.readFileSync("host/harness/cockpit.js", "utf8");
const bootMarker = "\nboot().catch(";
assert.equal(js.split(bootMarker).length,2,"missing fail-closed boot handler");
const script = js.split(bootMarker)[0] +
  "\nglobalThis.testApi = { classify, addFiles, clearAssets, state, fetchJson, MAX_DESK_FILES, MAX_ASSET_BYTES, MAX_DESK_BYTES };";
let made=0, revoked=0, paused=0, networkRequests=0;
class Node {
  constructor(){this.style={};this.children=[];this.attributes=new Set();this.textContent="";this.classList={add(){},remove(){}};}
  append(...nodes){this.children.push(...nodes)}
  appendChild(n){this.children.push(n)}
  removeAttribute(a){this.attributes.delete(a)}
  setAttribute(a,b){this.attributes.add(a)}
  addEventListener(){}
  pause(){paused++}
}
const nodeMap=new Map();
const doc={
 getElementById(id){if(!nodeMap.has(id))nodeMap.set(id,new Node());return nodeMap.get(id)},
 createElement(){return new Node()}
};
let response={ok:true,text:async()=>JSON.stringify({safe:true})};
const context={
 document:doc,window:{},crypto:{randomUUID:()=>"desk-"+String(made)},
 URL:{createObjectURL:()=>{made++;return "blob:local/"+made},revokeObjectURL:()=>{revoked++}},
 fetch:async()=>{networkRequests++;return response},
 AbortSignal:{timeout:ms=>({timeoutMs:ms})},
 console:{error:()=>{}},
 requestAnimationFrame:()=>0,
 location:{hostname:"localhost",protocol:"http:",host:"localhost"}
};
vm.runInNewContext(script,context,{timeout:5000});
const x=context.testApi;
function file(name,type,size=100){return{name,type,size}}
assert.equal(x.classify(file("photo.png","image/png")),"image");
assert.equal(x.classify(file("photo.JPG","image/jpeg")),"image");
assert.equal(x.classify(file("scene.mp4","video/mp4")),"video");
assert.equal(x.classify(file("docs.pdf","application/pdf")),"pdf");
for(const bad of [file("evil.svg","image/svg+xml"),file("bad.pdf","text/html"),
                  file("wrong.jpg","image/png"),file("script.html","text/html")])
  assert.equal(x.classify(bad),"other","allowed disallowed preview "+bad.name);
x.addFiles([
 file("good.png","image/png",150),
 file("fake.png","text/html",200),
 file("too-big.mp4","video/mp4",33*1024*1024),
 file("empty.jpg","image/jpeg",0),
 file("unsafe.svg","image/svg+xml",160)
]);
assert.equal(x.state.assets.length,1);
assert.equal(made,1);
assert.match(doc.getElementById("deskStatus").textContent,/1 added, 4 skipped/);
x.addFiles(Array.from({length:45},(_,i)=>file("img-"+i+".jpg","image/jpeg",1000)));
assert.equal(x.state.assets.length,24);
assert.equal(made,24);
x.clearAssets();
assert.equal(x.state.assets.length,0);
assert.equal(revoked,24,"blob URLs must be revoked");
assert.equal(doc.getElementById("deskStatus").textContent,"Local media cleared and preview URLs revoked.");
assert.ok(paused>0);
x.addFiles(Array.from({length:5},(_,i)=>file("movie-"+i+".mp4","video/mp4",32*1024*1024)));
assert.equal(x.state.assets.length,4,"128MiB total cap required");
x.clearAssets();

(async()=>{
  assert.equal((await x.fetchJson("/harness/config.json")).safe,true);
  assert.equal(networkRequests,1);
  response={ok:false,text:async()=>""};
  await assert.rejects(x.fetchJson("/harness/config.json"),/Desktop dependency not available/);
  response={ok:true,text:async()=> "x".repeat(512*1024+1)};
  await assert.rejects(x.fetchJson("/harness/config.json"),/Oversized desktop config/);
  console.log("GREEN_DESKTOP_JS_BEHAVIOR_14_NEGATIVE_AND_POSITIVE_CONTROLS");
})().catch(error=>{console.error(error);process.exitCode=1;});
