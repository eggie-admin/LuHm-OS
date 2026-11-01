import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { spawnSync } from "node:child_process";
import { resolve } from "node:path";
import { repoRoot } from "../src/index.mjs";
import { checkRegistry, encodePacket, decodePacket, initialCounts,
  sortActions, selectAction, platformIds, capabilityIds, hexIds } from "../src/device-registry.mjs";

const policyPath=resolve(repoRoot,"doctrine/deviceCapabilityRegistryV1.json");
const pyPath=resolve(repoRoot,"tools/deviceRegistrySqlReceipt.py");
const get=async()=>JSON.parse(await readFile(policyPath,"utf8"));
const clone=o=>structuredClone(o);
function sql(p){return spawnSync("python3",[pyPath],{cwd:repoRoot,input:JSON.stringify(p),
  encoding:"utf8",timeout:10000,maxBuffer:20000,env:{PATH:process.env.PATH||"/usr/bin:/bin",
    PYTHONDONTWRITEBYTECODE:"1"}});}
test("16 protected registry IDs agree with four device surfaces and typed capabilities",async()=>{
 const p=await get();assert.equal(checkRegistry(p),true);
 assert.deepEqual(p.platforms,platformIds);
 assert.deepEqual(p.capabilities,capabilityIds);
 assert.deepEqual(p.entries.map(x=>x.hex),Array.from(hexIds));
 for(let i=0;i<16;i++){assert.equal(p.entries[i].index,i);assert.equal(p.entries[i].deviceVerified,false);}
});
test("tampered hex, bypassed owner authority, SDK and protection gates fail closed",async()=>{
 const p=await get();
 for(const [kind,mutate] of [
  ["hex",x=>x.entries[2].hex="0xFF"],["deviceProof",x=>x.entries[5].deviceVerified=true],
  ["scope",x=>x.entries[0].namespace="windowsRegistry"],["sdk",x=>x.sdkGates.android.targetSdk=28],
  ["signer",x=>x.vendorUpdates.doNotChangeSigningIdentity=false],
  ["store",x=>x.safety.playStoreBuildUploaded=true],["merge",x=>x.crownStatus="GO"],
  ["gui",x=>x.gui.disableBackgroundRecording=false]]) {
   let c=clone(p);mutate(c);
   assert.throws(()=>checkRegistry(c),/^Error: RED_/,kind);
 }
});
test("UTF8 byte length differs from characters; canonical Base64 and SHA roundtrip",()=>{
 const text="LuHm ✦ 優先 3D";
 const p=encodePacket(text,{registryHex:"0x0B",kind:"artNote",rssBytes:8388608});
 assert.equal(p.byteCount,Buffer.byteLength(text,"utf8"));
 assert.ok(p.byteCount>text.length);
 assert.equal(p.rssBytes,8388608);
 assert.equal(decodePacket(p).value,text);
 assert.equal(Buffer.from(p.payloadBase64,"base64").toString("utf8"),text);
 assert.match(p.sha256,/^[a-f0-9]{64}$/);
 assert.equal(p.rightsState,"LOCAL_DRAFT");
});
test("reject forged hashes, altered size, invalid base64, remote rights and unknown hex",()=>{
 const p=encodePacket("safe");
 for(const [name,value] of [["sha256","0".repeat(64)],["byteCount",999],
  ["payloadBase64","eA==\n"],["rightsState","PUBLIC_APPROVED"],
  ["registryHex","0xFF"],["rssBytes",-1],["kind","executeShell"]]){
   let v={...p,[name]:value};
   assert.throws(()=>decodePacket(v),/^Error: RED_/,name);
 }
 assert.throws(()=>decodePacket({...p,privateKey:"not allowed"}),/^Error: RED_/);
 assert.throws(()=>encodePacket("🗲".repeat(2000)),/RED_TEXT_BYTES/);
 assert.throws(()=>encodePacket("e\u0301"),/RED_TEXT_CANONICAL/);
 assert.throws(()=>encodePacket("\ud800"),/RED_TEXT_CANONICAL/);
});
test("JS and Python SQLite STRICT parity on a safe fixture, never a real device proof",()=>{
 const p=encodePacket("LuHm ✦ 優先 3D",{registryHex:"0x0B",rssBytes:8388608});
 const run=sql(p);
 assert.equal(run.status,0,run.stderr);
 const r=JSON.parse(run.stdout);
 assert.equal(r.hex,p.registryHex);assert.equal(r.byteCount,p.byteCount);
 assert.equal(r.sha256,p.sha256);assert.equal(r.rssBytes,p.rssBytes);
 assert.equal(r.sqlite,"IN_MEMORY_STRICT");assert.equal(r.rows,1);
 assert.equal(r.sqlServiceStarted,false);assert.equal(r.kernelChanged,false);
 assert.equal(r.deviceVerified,false);assert.equal(r.crownStatus,"STOP");
 let forged=sql({...p,sha256:"f".repeat(64)});
 assert.equal(forged.status,2);
 assert.match(forged.stderr,/DEVICE_PACKET_REJECTED/);
});
test("SQLite rejects noncanonical and duplicate JSON keys, oversized input, bool RSS",()=>{
 const p=encodePacket("safe");
 assert.equal(sql({...p,rssBytes:true}).status,2);
 const raw=JSON.stringify(p).replace('"rssBytes":null','"rssBytes":null,"rssBytes":0');
 const dup=spawnSync("python3",[pyPath],{cwd:repoRoot,input:raw,encoding:"utf8"});
 assert.equal(dup.status,2);
 assert.equal(sql({...p,payloadBase64:"===="}).status,2);
});
test("GUI sorting uses session selections only; ties keep curated first-time order",()=>{
 let counts=initialCounts();
 assert.deepEqual(sortActions(counts),["play","edit","assets","build","audit","settings"]);
 counts=selectAction(counts,"build");
 counts=selectAction(counts,"assets");
 counts=selectAction(counts,"build");
 assert.deepEqual(sortActions(counts),["build","assets","play","edit","audit","settings"]);
 assert.deepEqual(sortActions(initialCounts()),["play","edit","assets","build","audit","settings"]);
 assert.throws(()=>selectAction(counts,"signAndroidRelease"),/RED_GUI_ACTION_UNKNOWN/);
 assert.throws(()=>sortActions({...counts,build:-3}),/RED_GUI_COUNT_SHAPE/);
});

test("unified local CLI uses synthetic JS Python SQLite registry receipt",()=>{
 const cli=resolve(repoRoot,"tools/luhm-machine-agent/bin/luhm-machine-audit.mjs");
 const res=spawnSync(process.execPath,[cli,"audit","--with-python","--with-device"],{
    cwd:repoRoot,encoding:"utf8",timeout:20000,maxBuffer:256000});
 assert.equal(res.status,0,res.stderr);
 const out=JSON.parse(res.stdout);
 assert.equal(out.deviceRegistryInterop,"SYNTHETIC_4X4_JS_PYTHON_SQL_VERIFIED");
 assert.equal(out.deviceRegistryHex,"0x0B");
 assert.equal(out.deviceRssSample,"SYNTHETIC_NOT_MEASURED");
 assert.equal(out.pythonSqlInterop,"SOURCE_ONLY_VERIFIED");
 assert.equal(out.hardwareVerified,false);
 assert.equal(out.remoteInvocation,"DISABLED");
});
test("phone UI exposes no fake Play links, no scripts from CDN and no analytics",async()=>{
 const base=resolve(repoRoot,"tools/luhm-machine-agent/demo");
 const [html,css,js]=await Promise.all(["index.html","style.css","app.mjs"]
   .map(x=>readFile(resolve(base,x),"utf8")));
 assert.match(html,/default-src 'none'/);
 assert.match(html,/connect-src 'none'/);
 assert.match(html,/No apps, GPUs, private assets, or agents have been started/);
 assert.match(html,/Not a live Godot or Unreal scene/);
 assert.match(html,/script type="module" src="\.\/app\.mjs"/);
 assert.match(js,/replaceChildren/);
 assert.match(js,/selectAction\(counts,id\)/);
 assert.match(js,/noopener noreferrer/);
 assert.doesNotMatch(js,/fetch\(|XMLHttpRequest|localStorage|innerHTML\s*=/);
 assert.match(css,/prefers-reduced-motion/);
});
