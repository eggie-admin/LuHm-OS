/* LuHm-OS: browser boundary state without UI, GPU, network, or privilege. */
export const kioskSchema = "luhmOs.webKioskBoundary.v1";
export const kioskLayers = Object.freeze(["dom", "illustrated2d", "babylonWebgl", "remoteUnrealCandidate"]);
export const maxFallbackObjects = 12;
export function capabilityTier(probe) {
  if (!probe || typeof probe !== "object" || Array.isArray(probe) ||
      typeof probe.webgl2 !== "boolean" || typeof probe.webgl1 !== "boolean") {
    throw new Error("RED_INVALID_CAPABILITY_RECEIPT");
  }
  return probe.webgl2 ? "webgl2" : probe.webgl1 ? "webgl1" : "dom";
}
export function safeFrameRate(value) {
  if (typeof value !== "number" || !Number.isInteger(value)) throw new Error("RED_FRAME_BUDGET");
  return Math.max(15, Math.min(30, value));
}
export function newKioskState() {
  return { schema: kioskSchema, layer: "dom", capability: "unknown", phase: "idle",
    visible: true, stopped: false, revision: 0 };
}
export function kioskTransition(state, type, detail = {}) {
  if (!state || state.schema !== kioskSchema ||
      !["idle", "loading", "active", "paused", "fallback"].includes(state.phase) ||
      typeof type !== "string") throw new Error("RED_KIOSK_STATE");
  if (state.stopped) return state;
  const next = { ...state, revision: state.revision + 1 };
  if (type === "DETECT") {
    const tier = capabilityTier(detail);
    next.capability = tier;
    next.phase = tier === "dom" ? "fallback" : "idle";
  } else if (type === "START") {
    next.phase = next.capability === "dom" ? "fallback" : "loading";
    next.layer = next.capability === "dom" ? "dom" : "babylonWebgl";
  } else if (type === "READY") {
    if (state.phase !== "loading") throw new Error("RED_KIOSK_EARLY_READY");
    next.phase = state.visible ? "active" : "paused";
  } else if (type === "HIDE") {
    next.visible = false;
    next.phase = state.phase === "active" ? "paused" : state.phase;
  } else if (type === "SHOW") {
    next.visible = true;
    next.phase = state.phase === "paused" ? "active" : state.phase;
  } else if (type === "CONTEXT_LOST" || type === "RENDER_FAILURE") {
    next.phase = "fallback";
    next.layer = "dom";
    next.capability = "dom";
  } else if (type === "CLOSE") {
    next.phase = "idle";
    next.layer = "dom";
    next.stopped = true;
  } else {
    throw new Error("RED_KIOSK_UNKNOWN_EVENT");
  }
  return next;
}
