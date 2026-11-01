import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { capabilityTier, kioskLayers, kioskSchema, maxFallbackObjects,
  newKioskState, kioskTransition, safeFrameRate } from "../src/kiosk-core.mjs";

const read = async file => readFile(new URL("../" + file, import.meta.url), "utf8");

test("four layers are independent; Unreal cannot self-start on a phone", () => {
  assert.deepEqual(kioskLayers, ["dom", "illustrated2d", "babylonWebgl", "remoteUnrealCandidate"]);
  const state = newKioskState();
  assert.equal(state.schema, kioskSchema);
  assert.equal(state.phase, "idle");
  assert.equal(state.layer, "dom");
  assert.ok(maxFallbackObjects <= 16);
});
test("GPU feature probes are strict, with explicit DOM fallback", () => {
  assert.equal(capabilityTier({ webgl1: false, webgl2: false }), "dom");
  assert.equal(capabilityTier({ webgl1: true, webgl2: false }), "webgl1");
  assert.equal(capabilityTier({ webgl1: true, webgl2: true }), "webgl2");
  for (const bad of [null, 3, {}, { webgl1: "true", webgl2: false }])
    assert.throws(() => capabilityTier(bad), /RED_INVALID_CAPABILITY_RECEIPT/);
});
test("no GPU, no crash: DOM mode stays independently operable", () => {
  let state = kioskTransition(newKioskState(), "DETECT", { webgl1: false, webgl2: false });
  assert.equal(state.phase, "fallback");
  state = kioskTransition(state, "START");
  assert.equal(state.phase, "fallback");
  assert.equal(state.layer, "dom");
});
test("full lifecycle supports pause, recovery, fault fallback and permanent close", () => {
  let state = kioskTransition(newKioskState(), "DETECT", { webgl1: true, webgl2: true });
  state = kioskTransition(state, "START");
  assert.equal(state.phase, "loading");
  state = kioskTransition(state, "HIDE");
  state = kioskTransition(state, "READY");
  assert.equal(state.phase, "paused");
  state = kioskTransition(state, "SHOW");
  assert.equal(state.phase, "active");
  state = kioskTransition(state, "CONTEXT_LOST");
  assert.equal(state.layer, "dom");
  assert.equal(state.phase, "fallback");
  state = kioskTransition(state, "CLOSE");
  assert.equal(state.stopped, true);
  assert.equal(kioskTransition(state, "START"), state);
  assert.throws(() => kioskTransition(newKioskState(), "READY"), /RED_KIOSK_EARLY_READY/);
  assert.throws(() => kioskTransition(newKioskState(), "EXECUTE_PRIVILEGED"), /RED_KIOSK_UNKNOWN_EVENT/);
});
test("frame-rate target clamps negative/unbounded knobs, no higher-than-30 default", () => {
  assert.equal(safeFrameRate(144), 30);
  assert.equal(safeFrameRate(-20), 15);
  assert.equal(safeFrameRate(25), 25);
  for (const v of [Infinity, NaN, "30", 24.5])
    assert.throws(() => safeFrameRate(v), /RED_FRAME_BUDGET/);
});
test("CSP-bounded kiosk is offline-first, DOM-first and defers 3D dependencies", async () => {
  const [html, entry, renderer, vue, vite] = await Promise.all(
    ["kiosk.html", "src/kiosk-entry.mjs", "src/babylon-world.js", "src/main.js", "vite.config.js"].map(read)
  );
  assert.match(html, /default-src 'none'/);
  assert.match(html, /script-src 'self'/);
  assert.match(html, /connect-src 'none'/);
  assert.match(html, /object-src 'none'/);
  assert.match(html, /<main>/);
  assert.match(html, /id="kiosk-add"/);
  assert.match(html, /id="kiosk-return"/);
  assert.match(html, /tabindex="0"/);
  assert.match(html, /prefers-reduced-motion|kiosk\.css/);
  assert.doesNotMatch(html, /<script[^>]*https?:|<iframe|onload=|onclick=|unsafe-eval|unsafe-inline/i);
  assert.match(entry, /await import\("\.\/main\.js"\)/);
  assert.match(entry, /document\.createElement\("li"\)/);
  assert.match(entry, /textContent/);
  assert.match(entry, /requestFullscreen/);
  assert.match(renderer, /onContextLostObservable/);
  assert.match(renderer, /onContextRestoredObservable/);
  assert.match(renderer, /engine\.stopRenderLoop/);
  assert.match(renderer, /scene\.dispose\(\)/);
  assert.match(renderer, /mesh\.dispose\(false, true\)/);
  assert.match(renderer, /1000 \/ 30/);
  assert.match(vue, /window\.addEventListener\("luhm:kiosk:exit", cleanup/);
  assert.match(vite, /kiosk\.html/);
  assert.doesNotMatch(entry, /fetch\s*\(|eval\s*\(|innerHTML\s*=|location\.href\s*=|postMessage\s*\(/);
});
