import test from "node:test";
import assert from "node:assert/strict";
import { classifyRuntime, collectRuntimeProbe, sampleAnimationFrameCadence,
  renderRuntimeReceipt, runtimeSchema } from "../src/runtime-diagnostics.mjs";

test("fail-closed static fallback without graphics", () => {
  const a = classifyRuntime({ webgl2: false, webAssembly: true, indexedDB: true, opfs: false });
  assert.equal(a.render, "STATIC_FALLBACK_REQUIRED");
  assert.equal(a.storage, "LIMITED_BEST_EFFORT_STORAGE");
  assert.equal(a.backgroundServiceCpu, "NOT_OBSERVABLE_FROM_BROWSER");
  assert.equal(a.crownStatus, "STOP");
});

test("browser diagnostics are capability hints with no consent escalation", async () => {
  const browser = { WebGL2RenderingContext: function GL2(){}, WebAssembly: {},
    isSecureContext: true, indexedDB: {}, caches: {}, crossOriginIsolated: false };
  const nav = { hardwareConcurrency: 4, deviceMemory: 2,
    storage: { getDirectory(){ throw Error("must not open files"); },
      async estimate(){ return {usage: 100, quota: 1000}; } }, serviceWorker: {} };
  const report = await collectRuntimeProbe({ browser, nav,
    canvas: {getContext(type){ assert.equal(type,"webgl2"); return {}; }} });
  assert.equal(report.schema, runtimeSchema);
  assert.equal(report.features.webgl2, true);
  assert.equal(report.assessment.render, "WEBGL2_WASM_CANDIDATE");
  assert.deepEqual(report.storageBytes, {usage:100, quota:1000});
  assert.equal(report.transmitted, false);
  assert.equal(report.features.localFilePicker, false);
});

test("blocked quota estimate never prevents the fallback receipt", async () => {
  const report = await collectRuntimeProbe({browser:{},nav:{storage:{estimate:async()=>{throw Error("blocked");}}},canvas:null});
  assert.equal(report.assessment.render, "STATIC_FALLBACK_REQUIRED");
  assert.equal(report.storageBytes, null);
  assert.equal(report.features.cpuThreadsHint, null);
});

test("frame sampling is bounded and hidden tabs never sampled", async () => {
  assert.equal(await sampleAnimationFrameCadence({ hidden:()=>true, raf:()=>{throw Error("must not execute");}}),null);
  let t=0;
  const result = await sampleAnimationFrameCadence({hidden:()=>false,frames:3,
    raf:cb=>queueMicrotask(()=>cb(t+=20))});
  assert.equal(result, 50);
});

test("receipt writes textContent, never executable HTML", () => {
  const element = { textContent:"" };
  renderRuntimeReceipt(element, {value:"<script>alert(1)</script>"});
  assert.match(element.textContent, /<script>/);
  assert.match(element.textContent, /"value"/);
});
