/* CAST runtime diagnostics: user-triggered, read-only, same-origin, no upload. */
export const runtimeSchema = "luhmOs.browserRuntimeProbe.v1";

export function classifyRuntime(features) {
  const render = features.webgl2 && features.webAssembly
    ? "WEBGL2_WASM_CANDIDATE" : "STATIC_FALLBACK_REQUIRED";
  const storage = features.indexedDB && features.opfs
    ? "BROWSER_SANDBOX_AVAILABLE" : "LIMITED_BEST_EFFORT_STORAGE";
  return { render, storage, hostKernel: "UNVERIFIED", nativeSdl: "UNVERIFIED",
    backgroundServiceCpu: "NOT_OBSERVABLE_FROM_BROWSER", samsungDeviceProof: "UNVERIFIED",
    crownStatus: "STOP" };
}

export function boundedCount(value) {
  return Number.isInteger(value) && value > 0 && value < 1024 ? value : null;
}

export async function collectRuntimeProbe({ browser = globalThis, nav = globalThis.navigator,
  canvas = globalThis.document?.getElementById("babylon-stage") } = {}) {
  const f = {
    webgl2: Boolean(browser.WebGL2RenderingContext && canvas?.getContext?.("webgl2")),
    webAssembly: typeof browser.WebAssembly === "object",
    secureContext: browser.isSecureContext === true,
    indexedDB: Boolean(browser.indexedDB),
    opfs: typeof nav?.storage?.getDirectory === "function",
    cacheStorage: Boolean(browser.caches),
    serviceWorker: Boolean(nav?.serviceWorker),
    localFilePicker: typeof browser.showOpenFilePicker === "function",
    crossOriginIsolated: browser.crossOriginIsolated === true,
    cpuThreadsHint: boundedCount(nav?.hardwareConcurrency),
    deviceMemoryGiBHint: typeof nav?.deviceMemory === "number" &&
      Number.isFinite(nav.deviceMemory) && nav.deviceMemory > 0 ? nav.deviceMemory : null
  };
  // Estimate only: do not create files, enumerate browser cache, or request permissions.
  let storageBytes = null;
  if (typeof nav?.storage?.estimate === "function") {
    try {
      const estimate = await nav.storage.estimate();
      storageBytes = {
        usage: Number.isSafeInteger(estimate.usage) && estimate.usage >= 0 ? estimate.usage : null,
        quota: Number.isSafeInteger(estimate.quota) && estimate.quota >= 0 ? estimate.quota : null
      };
    } catch { /* unsupported, blocked, or privacy restriction */ }
  }
  return { schema: runtimeSchema, features: f, storageBytes,
    assessment: classifyRuntime(f),
    measurementScope: "READ_ONLY_BROWSER_HINTS_NOT_OS_BENCHMARKS",
    transmitted: false };
}

export async function sampleAnimationFrameCadence({ raf = globalThis.requestAnimationFrame,
  hidden = () => globalThis.document?.hidden, frames = 30 } = {}) {
  if (typeof raf !== "function" || hidden() || !Number.isInteger(frames) || frames < 2 || frames > 120)
    return null;
  const times = [];
  return await new Promise(resolve => {
    const onFrame = time => {
      if (hidden()) { resolve(null); return; }
      times.push(time);
      if (times.length < frames) { raf(onFrame); return; }
      const elapsed = times.at(-1) - times[0];
      resolve(elapsed > 0 ? Math.round(1000 * (times.length - 1) / elapsed) : null);
    };
    raf(onFrame);
  });
}

export function renderRuntimeReceipt(node, report) {
  if (!node) return;
  node.textContent = JSON.stringify(report, null, 2);
}

export function mountRuntimeDiagnostics(doc = globalThis.document) {
  const button = doc?.getElementById("runtime-probe");
  const output = doc?.getElementById("runtime-receipt");
  if (!button || !output) return;
  let active = false;
  button.addEventListener("click", async () => {
    if (active) return;
    active = true; button.disabled = true;
    output.textContent = "Inspecting this browser locally...";
    try {
      const report = await collectRuntimeProbe();
      report.frameCadenceHzEstimate = await sampleAnimationFrameCadence();
      report.frameNote = "JS animation callback cadence; not GPU frame rate or an OS CPU benchmark";
      renderRuntimeReceipt(output, report);
    } catch {
      output.textContent = "Browser probe unavailable; static fallback remains valid.";
    } finally { active = false; button.disabled = false; }
  });
}

if (typeof document !== "undefined") mountRuntimeDiagnostics();
