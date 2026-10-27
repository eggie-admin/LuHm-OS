"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const root=path.resolve(__dirname,"..");
const desk=require(path.join(root,"host/harness/samsung-art-desk.js"));
const good=desk.fresh();
assert.equal(good.shots.length,7);
assert.deepEqual(good.shots.map(s=>s.slot),["100","200","300","401","402","403","500"]);
good.shots[0].notes="Lum opens the seven-shot Riverwalk storyboard.";
good.shots[0].speaker="lum";
good.shots[0].strokes=[{color:"#ff2277",width:5,erase:false,points:[[0,0],[720,405]]}];
const roundTrip=desk.cleanPacket(JSON.parse(JSON.stringify(good)));
assert.deepEqual(roundTrip,good);
assert.equal(roundTrip.approved,false);
assert.equal(roundTrip.serverWrites,false);
for(const bad of [
  {...good,approved:true},
  {...good,serverWrites:true},
  {...good,shots:[...good.shots].slice(0,6)},
  {...good,shots:good.shots.map((x,i)=>i===0?{...x,speaker:"root"}:x)},
  {...good,shots:good.shots.map((x,i)=>i===0?{...x,strokes:[{color:"#ff2277",width:2,erase:false,points:[[900,0]]}]}:x)},
  {...good,project:"x".repeat(90)}
])assert.throws(()=>desk.cleanPacket(bad));
const malicious={...good,cloudUpload:true,apiKey:"NEVER_COMMIT"};
const projected=desk.cleanPacket(malicious);
assert.equal("apiKey" in projected,false);
assert.equal("cloudUpload" in projected,false);
const server=fs.readFileSync(path.join(root,"host/mcp/luhmHarness.py"),"utf8");
const html=fs.readFileSync(path.join(root,"host/harness/index.html"),"utf8");
assert.match(server,/"samsung-art-desk.js"/);
assert.match(server,/"samsung-art-desk.css"/);
assert.match(html,/id="samsung-canvas"/);
assert.match(html,/id="samsung-import"/);
assert.match(html,/id="samsung-save"/);
assert.match(html,/\/harness\/assets\/samsung-art-desk.js/);
const source=fs.readFileSync(path.join(root,"host/harness/samsung-art-desk.js"),"utf8");
assert.doesNotMatch(source,/\bfetch\s*\(|XMLHttpRequest|sendBeacon|new WebSocket/);
assert.doesNotMatch(source,/\binnerHTML\b/);
const yaml=fs.readFileSync(path.join(root,"infrastructure/samsung-art-desk/runtime.yaml"),"utf8");
for(const s of ["git-owner: eggie-admin","linux-admin-expected: eggie","codespace-user-existing: codespace","requires-live-host-proof: true","sql-column: sourceRef","no-plaintext-passwords: true"])assert.ok(yaml.includes(s),s);
console.log("PASS_SAMSUNG_ART_DESK_SEVEN_SHOT_TOUCH_HANOFF_SOURCE_ONLY");
