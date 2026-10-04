(function ($) {
  "use strict";

  function postNative(type) {
    const bridge = window.LuHmNative;
    if (!bridge || typeof bridge.postMessage !== "function") return false;
    bridge.postMessage(JSON.stringify({ type: type }));
    return true;
  }

  $(function () {
    const $cockpit = $("[data-luhm-cockpit]");
    const $assetFactory = $cockpit.find("[data-luhm-asset-factory]");
    if (!$cockpit.length) return;

    $cockpit.luhmCockpit({ initialView: "chat" });

    $cockpit.on("click", "[data-luhm-factory-button]", function () {
      $cockpit.find("[data-luhm-menu]").prop("hidden", true);
      $assetFactory.prop("hidden", false);
    });
    $cockpit.on("click", "[data-luhm-factory-close]", function () {
      $assetFactory.prop("hidden", true);
    });

    $cockpit.on("luhm:magic:roleplay:activate", function (_event, detail) {
      if ($.codingRoleplay) {
        $.codingRoleplay.emit("workflowSummoned", {
          speaker: "Lum",
          expression: "working",
          lines: ["Old magic loaded.", "Roleplay is presentation; authority is unchanged."],
          machineState: "ROLEPLAY_ACTIVE",
          sourceRef: String((detail && detail.sourceRef) || "")
        });
      }
    });

    $cockpit.on("luhm:vendor:debug:request", function (_event, detail) {
      if ($.codingRoleplay) {
        $.codingRoleplay.emit("vendorCapabilityResult", {
          speaker: "Lum",
          expression: "working",
          lines: ["Vendor debug requested.", String((detail && detail.providerId) || "all")],
          machineState: "UNKNOWN_UNTIL_EXACT_EXECUTION_RECEIPT",
          evidenceRefs: []
        });
      }
    });

    // Android Web3 cockpit candidate boundary. Native Android System WebView
    // wrapper wiring remains separate and is intentionally not faked here.
    $cockpit.on("luhm:backend:open", function (_event, detail) {
      console.info("LuHm Godot/system boundary requested", detail);
      postNative("world_requested");
    });

    postNative("cockpit_ready");

    window.LuHmFrontEnd = Object.freeze({
      version: $.fn.luhmCockpit.version,
      jquery: $.fn.jquery,
      openBackend: function () { $cockpit.luhmCockpit("openBackend"); },
      closeBackend: function () { $cockpit.luhmCockpit("closeBackend"); },
      setView: function (view) { $cockpit.luhmCockpit("view", view); },
      openMediaFactory: function () { $assetFactory.prop("hidden", false); },
      closeMediaFactory: function () { $assetFactory.prop("hidden", true); },
      nativeBridgeAvailable: function () {
        return !!(window.LuHmNative && typeof window.LuHmNative.postMessage === "function");
      }
    });
  });
}(jQuery));
