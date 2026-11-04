"use strict";
const STATUS_URL = "http://127.0.0.1:8765/antenna/v1/status";
const byId = (id) => document.getElementById(id);
const button = byId("check");

function setText(id, value) { byId(id).textContent = String(value); }
function reset() {
  setText("connection", "OFFLINE / NOT VERIFIED");
  setText("source", "Unknown");
  setText("shellSize", "Not measured");
  setText("patchState", "Not checked");
  setText("authority", "CROWN STOP");
}
function validateStatus(s) {
  return s && s.schema === "luhmOs.firefoxAntennaStatus.v1"
    && s.mode === "READ_ONLY"
    && s.crownStatus === "STOP"
    && s.updateState === "CHECK_ONLY_NO_INSTALL"
    && Number.isInteger(s.shellBytes)
    && s.shellBytes >= 0 && s.shellBytes <= 100000000
    && typeof s.sourceRef === "string"
    && (/^[0-9a-f]{40}$/.test(s.sourceRef) || s.sourceRef === "UNVERIFIED");
}
async function checkLocal() {
  button.disabled = true;
  reset();
  setText("message", "Checking 127.0.0.1 only…");
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 2500);
  try {
    const response = await fetch(STATUS_URL, {
      method: "GET", cache: "no-store", credentials: "omit", signal: controller.signal
    });
    if (!response.ok || !(response.headers.get("content-type") || "").startsWith("application/json")) {
      throw new Error("Local status unavailable");
    }
    const raw = await response.text();
    if (raw.length > 8192) throw new Error("Status too large");
    const status = JSON.parse(raw);
    if (!validateStatus(status)) throw new Error("Unrecognized or unsafe antenna status");
    setText("connection", "LOCAL ANTENNA / SOURCE ONLY");
    setText("source", status.sourceRef === "UNVERIFIED" ? "UNVERIFIED" : status.sourceRef.slice(0, 12));
    setText("shellSize", String(status.shellBytes) + " bytes (source assets only)");
    setText("patchState", status.updateState);
    setText("authority", status.crownStatus);
    setText("message", "Read-only handshake confirmed. No patch downloaded or installed.");
  } catch (_) {
    reset();
    setText("message", "Antenna unavailable or unverified. Start the local service to test.");
  } finally {
    clearTimeout(timer);
    button.disabled = false;
  }
}
button.addEventListener("click", checkLocal);
