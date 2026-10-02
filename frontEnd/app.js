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
    const $yumeBooth = $cockpit.find("[data-yume-booth]");
    if (!$cockpit.length) return;

    $cockpit.luhmCockpit({ initialView: "chat" });
    $yumeBooth.luhmYumeBooth({ mode: "artDirectionJam", sceneId: "betaScene001" });

    $cockpit.on("click", "[data-luhm-factory-button]", function () {
      $cockpit.find("[data-luhm-menu]").prop("hidden", true);
      $assetFactory.prop("hidden", false);
    });
    $cockpit.on("click", "[data-luhm-factory-close]", function () {
      $assetFactory.prop("hidden", true);
    });

    $cockpit.on("click", "[data-yume-open]", function () {
      $cockpit.find("[data-luhm-menu]").prop("hidden", true);
      $yumeBooth.prop("hidden", false);
    });

    $cockpit.on("click", "[data-yume-close]", function () {
      $yumeBooth.prop("hidden", true);
    });

    $yumeBooth.on("luhm:yume:cutsceneRequested", function (_event, detail) {
      console.info("Yume cutscene packet", detail);
      postNative("yume_cutscene_requested");
    });

    $yumeBooth.on("luhm:yume:proofRejected", function (_event, detail) {
      console.info("Yume rejected proof", detail);
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
      openYumeBooth: function () { $yumeBooth.prop("hidden", false); },
      closeYumeBooth: function () { $yumeBooth.prop("hidden", true); },
      nativeBridgeAvailable: function () {
        return !!(window.LuHmNative && typeof window.LuHmNative.postMessage === "function");
      }
    });
  });
}(jQuery));
