/* Minimal DOM-first kiosk entry. Babylon/Vue/jQuery load only on explicit activation. */
import { newScene, placeObject } from "./scene-state.mjs";
import { newKioskState, kioskTransition, maxFallbackObjects } from "./kiosk-core.mjs";

const byId = id => document.getElementById(id);
const entry = byId("kiosk-entry");
const world = byId("glass-world");
const objectList = byId("kiosk-objects");
const capabilityLabel = byId("kiosk-capability");
const message = byId("kiosk-message");
const enter3D = byId("kiosk-webgl");
let kiosk = newKioskState();
let scene = newScene();
let busy = false;
let launched = false;

function detectWebgl() {
  // Ephemeral probe only. Do not allocate a persistent second GPU context.
  for (const name of ["webgl2", "webgl"]) {
    try {
      const canvas = document.createElement("canvas");
      const gl = canvas.getContext(name, { antialias: false, powerPreference: "low-power" });
      if (!gl || gl.isContextLost()) continue;
      gl.getExtension("WEBGL_lose_context")?.loseContext();
      return { webgl2: name === "webgl2", webgl1: true };
    } catch { /* blocked GPU, software browser, or disabled canvas */ }
  }
  return { webgl2: false, webgl1: false };
}

function showObjects() {
  objectList.replaceChildren();
  for (const item of scene.objects) {
    const li = document.createElement("li");
    li.textContent = item.id + " · " + item.kind;
    objectList.appendChild(li);
  }
}
function safeFallback(reason) {
  if (!kiosk.stopped) kiosk = kioskTransition(kiosk, "RENDER_FAILURE");
  entry.hidden = false;
  world.hidden = true;
  enter3D.disabled = true;
  message.textContent = reason + " The DOM studio stays available; reload for a fresh GPU check.";
}
const probe = detectWebgl();
kiosk = kioskTransition(kiosk, "DETECT", probe);
capabilityLabel.textContent = kiosk.capability === "dom"
  ? "No usable WebGL context. DOM and SVG studio available."
  : ("Detected " + kiosk.capability.toUpperCase() + ". 3D loads only if you choose it.");
enter3D.disabled = kiosk.capability === "dom";

byId("kiosk-add").addEventListener("click", () => {
  if (scene.objects.length >= maxFallbackObjects) {
    message.textContent = "12-object lightweight stage limit reached. Clear the stage to continue.";
    return;
  }
  const kinds = ["box", "sphere", "cylinder", "torus"];
  scene = placeObject(scene, kinds[scene.objects.length % kinds.length]);
  showObjects();
  message.textContent = "Shape placed in safe DOM mode. Not a released art asset.";
});
byId("kiosk-clear").addEventListener("click", () => {
  scene = newScene();
  showObjects();
  message.textContent = "Local shapes cleared. No media files or master assets were modified.";
});
enter3D.addEventListener("click", async () => {
  if (busy || launched || kiosk.capability === "dom" || kiosk.stopped) return;
  busy = true;
  kiosk = kioskTransition(kiosk, "START");
  enter3D.disabled = true;
  world.hidden = false; // Canvas must be measurable before Babylon creates its engine.
  entry.hidden = true;
  byId("kiosk-render-status").textContent = "Starting local Babylon renderer…";
  try {
    // No dynamic 3D dependency is loaded until the user explicitly enters this mode.
    await import("./main.js");
    launched = true;
    kiosk = kioskTransition(kiosk, "READY");
    byId("kiosk-render-status").textContent =
      "WebGL local scene active. GPU budget: up to 30 rendered frames/second.";
  } catch {
    safeFallback("3D initialization failed.");
  } finally {
    busy = false;
  }
});
byId("kiosk-return").addEventListener("click", () => {
  if (launched) window.dispatchEvent(new Event("luhm:kiosk:exit"));
  if (!kiosk.stopped) kiosk = kioskTransition(kiosk, "CLOSE");
  launched = false;
  world.hidden = true;
  entry.hidden = false;
  enter3D.disabled = true;
  message.textContent = "WebGL session closed and GPU resources released. DOM mode remains available; reload to retry 3D.";
  byId("kiosk-add").focus();
});
byId("kiosk-fullscreen").addEventListener("click", async () => {
  if (!document.fullscreenEnabled || !document.documentElement.requestFullscreen) {
    message.textContent = "Fullscreen isn't available. The kiosk still works in this tab.";
    return;
  }
  try {
    if (document.fullscreenElement) await document.exitFullscreen();
    else await document.documentElement.requestFullscreen();
    message.textContent = document.fullscreenElement
      ? "Optional browser fullscreen. Escape exits; this does not lock the operating system."
      : "Returned to normal browser mode.";
  } catch {
    message.textContent = "Fullscreen request declined by the browser. Normal mode remains available.";
  }
});
window.addEventListener("luhm:kiosk:gpu-status", event => {
  const status = event.detail?.state;
  if (status === "lost") safeFallback("GPU context lost.");
  else if (status === "restored" && !kiosk.stopped) {
    message.textContent = "WebGL restored, but DOM mode remains safe. Reload to reactivate.";
  }
});
document.addEventListener("visibilitychange", () => {
  if (kiosk.stopped) return;
  kiosk = kioskTransition(kiosk, document.hidden ? "HIDE" : "SHOW");
});
showObjects();
