"use strict";
/* One monitor pane and one pet/chat pane. Two UI lanes, zero worker threads. */
(function () {
  const byId = id => document.getElementById(id);
  const monitor = byId("laneMonitorStatus");
  const detail = byId("laneMonitorReceipt");
  const workers = byId("laneWorkerState");
  const bubble = byId("lanePetBubble");
  const check = byId("laneCheckSource");
  const pet = byId("lanePetPreview");
  if (!monitor || !detail || !workers || !bubble || !check || !pet) return;
  const text = (el, value) => { el.textContent = value; };

  let currentController = null;
  check.addEventListener("click", async () => {
    if (currentController) return;
    const controller = new AbortController();
    currentController = controller;
    check.disabled = true;
    check.setAttribute("aria-busy", "true");
    text(monitor, "VERIFY · checking same-origin source");
    text(bubble, "Lum · VERIFY · Reading a public harness contract, not starting a worker.");
    const timeout = setTimeout(() => controller.abort(), 8000);
    try {
      const response = await fetch("/harness/config.json", {
        method: "GET", cache: "no-store", credentials: "same-origin",
        signal: controller.signal
      });
      if (!response.ok) throw Error("HTTP " + response.status);
      const type = response.headers.get("content-type") || "";
      if (!type.includes("application/json")) throw Error("unexpected content type");
      const size = Number(response.headers.get("content-length"));
      if (Number.isFinite(size) && size > 512 * 1024) throw Error("unexpected response size");
      const body = await response.text();
      if (body.length > 512 * 1024) throw Error("response too large");
      const data = JSON.parse(body);
      if (data.schema !== "luhmOs.harnessConfig.v2" ||
          data.experience?.schema !== "luhmOs.inChatExperience.v1" ||
          data.experience?.boss !== "lum") throw Error("source contract mismatch");
      const quarantine = data.embeddedStudio?.quarantine;
      const held = quarantine?.state === "QUARANTINED" && quarantine?.activeTaskWorkersAllowed === false;
      text(monitor, "OBSERVED · read-only source response");
      text(detail, "Harness config read succeeded. This does not prove current GitHub CI, device playback, ChatGPT host installation, or a running agent.");
      text(workers, held ? "Workers: QUARANTINED · 0 active" : "Workers: UNKNOWN · cannot infer agent release");
      text(bubble, held ?
        "Lum · IDLE · Source check succeeded. Our crew remains on standby." :
        "Lum · VERIFY · Source observed; worker execution unverified.");
    } catch (_) {
      text(monitor, "VERIFY · source unavailable");
      text(detail, "No compatible same-origin contract returned. Local media, pets, and other existing panels remain available.");
      text(workers, "Workers: UNKNOWN");
      text(bubble, "Lum · BLOCKED · No verified source response. No worker started.");
    } finally {
      clearTimeout(timeout);
      currentController = null;
      check.disabled = false;
      check.removeAttribute("aria-busy");
    }
  });
  pet.addEventListener("click", () => {
    text(bubble, "Lum · IDLE · I'm the on-screen pet. A real chat turn starts in ChatGPT, not inside this standalone preview.");
  });
  window.addEventListener("pagehide", () => { if (currentController) currentController.abort(); });
}());
