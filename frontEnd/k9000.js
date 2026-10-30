(function () {
  "use strict";
  const headings = Object.freeze({
    studio: ["THE CREATOR'S COCKPIT", "One canvas. A whole universe of tools. Powered by your ideas."],
    cameras: ["THE CAMERA MATRIX", "Discover hardware first. Preview and recording need separate consent."],
    hardware: ["THE HARDWARE LAB", "Canonical roles, read-only diagnostics and no invented driver support."],
    screens: ["THE SCREEN MATRIX", "Local display detection first. Pairing and mirroring require consent."],
    models: ["HEADLESS AI LAB", "One cockpit, optional local inference, no invented provider access."],
    vault: ["THE CREATOR VAULT", "Private assets stay private until intentionally exported."],
    world: ["THE WORLD PORTAL", "Enter the shared Godot world engine."]
  });
  const status = document.querySelector("[data-native-status]");
  const deviceCount = document.querySelector("[data-camera-count]");
  const deviceDetail = document.querySelector("[data-camera-detail]");
  const deviceList = document.querySelector("[data-camera-list]");
  const worldStatus = document.querySelector("[data-world-status]");
  const hardwareCount = document.querySelector("[data-hardware-count]");
  const hardwareDetail = document.querySelector("[data-hardware-detail]");
  const hardwareList = document.querySelector("[data-hardware-list]");
  const screenCount = document.querySelector("[data-screen-count]");
  const screenDetail = document.querySelector("[data-screen-detail]");
  let ready = false;

  function nativeMessage(type) {
    if (!ready || !window.LuHmNative || typeof window.LuHmNative.postMessage !== "function") return false;
    window.LuHmNative.postMessage(JSON.stringify({ type: type }));
    return true;
  }
  function show(view) {
    if (!Object.prototype.hasOwnProperty.call(headings, view)) return;
    document.querySelectorAll("[data-panel]").forEach(function (node) {
      node.classList.toggle("active", node.dataset.panel === view);
    });
    document.querySelectorAll(".rail-button").forEach(function (node) {
      const selected = node.dataset.view === view;
      node.classList.toggle("current", selected);
      if (selected) node.setAttribute("aria-current", "page");
      else node.removeAttribute("aria-current");
    });
    document.querySelector("[data-heading]").textContent = headings[view][0];
    document.querySelector("[data-subheading]").textContent = headings[view][1];
  }
  function updateClock() {
    const clock = document.querySelector("[data-clock]");
    if (clock && !document.hidden) clock.textContent = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }
  function receiveNative(message) {
    if (!message || typeof message !== "object") return;
    if (message.type === "screen_inventory") {
      const count = Number(message.externalDisplayCount);
      screenCount.textContent = Number.isInteger(count) && count >= 0 && count < 32
        ? count + " EXTERNAL DISPLAY(S) REPORTED" : "UNVERIFIED";
      screenDetail.textContent = "Android display inventory only. Mirroring, multi-window and casting have not been tested.";
      return;
    }
    if (!Array.isArray(message.devices)) return;
    if (message.type === "hardware_inventory") {
      const devices = message.devices.slice(0, 32);
      hardwareCount.textContent = devices.length + " USB DEVICE(S) PRESENT";
      hardwareDetail.textContent = "Descriptors only. Vendor identification does not confirm an exact scanner or camera model.";
      hardwareList.replaceChildren();
      if (!devices.length) {
        const p = document.createElement("p");
        p.textContent = "No connected USB devices enumerated by Android.";
        hardwareList.append(p);
      }
      devices.forEach(function (device) {
        const vid = Number(device.vendorId), pid = Number(device.productId);
        const vendor = vid === 0x04b8 ? "Epson vendor candidate" :
          vid === 0x04b0 ? "Nikon vendor candidate" :
          vid === 0x046d ? "Logitech vendor candidate" : "Other USB vendor";
        const p = document.createElement("p");
        p.textContent = vendor + " · VID " + (Number.isInteger(vid) ? vid : "?") +
          " · PID " + (Number.isInteger(pid) ? pid : "?") + " · DETECTED, NOT OPENED";
        hardwareList.append(p);
      });
      return;
    }
    if (message.type !== "camera_inventory") return;
    const devices = message.devices.slice(0, 32);
    deviceCount.textContent = devices.length + " UVC CANDIDATE" + (devices.length === 1 ? "" : "S");
    deviceDetail.textContent = "USB device inventory only. No feed has been opened and no capture permission granted.";
    deviceList.replaceChildren();
    if (!devices.length) {
      const p = document.createElement("p"); p.textContent = "No USB video-class interfaces detected. Test USB OTG, power and Android USB permissions."; deviceList.append(p);
    }
    devices.forEach(function (device, index) {
      const p = document.createElement("p");
      const vid = Number(device.vendorId);
      const pid = Number(device.productId);
      p.textContent = "UVC " + (index + 1) + " · VID " + (Number.isInteger(vid) ? vid : "?") + " · PID " + (Number.isInteger(pid) ? pid : "?") + " · DETECTED / NOT STREAMING";
      deviceList.append(p);
    });
  }
  document.querySelectorAll("[data-view]").forEach(function (button) {
    button.addEventListener("click", function () {
      const view = button.dataset.view;
      if (view === "world" && button.classList.contains("action")) show("world");
      else show(view);
    });
  });
  document.querySelector("[data-camera-probe]").addEventListener("click", function () {
    if (!nativeMessage("camera_probe_requested")) {
      deviceCount.textContent = "BRIDGE UNAVAILABLE";
      deviceDetail.textContent = "Android native USB enumeration is unavailable in this preview. No devices were scanned.";
    } else {
      deviceCount.textContent = "SCANNING...";
      deviceDetail.textContent = "Waiting for native USB inventory (no camera access requested).";
    }
  });
  document.querySelector("[data-hardware-probe]").addEventListener("click", function () {
    if (!nativeMessage("hardware_probe_requested")) {
      hardwareCount.textContent = "BRIDGE UNAVAILABLE";
      hardwareDetail.textContent = "Native hardware probe unavailable in this preview. No scan performed.";
    } else {
      hardwareCount.textContent = "CHECKING...";
      hardwareDetail.textContent = "Waiting for read-only USB inventory. No hardware access or permission requested.";
    }
  });
  document.querySelector("[data-screen-probe]").addEventListener("click", function () {
    if (!nativeMessage("screen_probe_requested")) {
      screenCount.textContent = "BRIDGE UNAVAILABLE";
      screenDetail.textContent = "DisplayManager status only exists in the native Android K9000 app.";
    } else {
      screenCount.textContent = "CHECKING...";
      screenDetail.textContent = "Waiting for native display inventory, without screen capture.";
    }
  });
  document.querySelector("[data-native-world]").addEventListener("click", function () {
    worldStatus.textContent = nativeMessage("world_requested") ? "Native world requested." : "Open the installed Android K9000 application to enter the Godot world.";
  });
  window.K9000 = Object.freeze({ receiveNative: receiveNative });
  ready = !!(window.LuHmNative && typeof window.LuHmNative.postMessage === "function");
  status.textContent = ready ? "ANDROID LOCAL BRIDGE · DETECTED" : "LOCAL UI · NATIVE BRIDGE UNAVAILABLE";
  if (ready) {
    document.querySelector(".status-dot").classList.add("online");
    nativeMessage("cockpit_ready");
  }
  updateClock();
  setInterval(updateClock, 30000);
  document.addEventListener("visibilitychange", updateClock);
}());