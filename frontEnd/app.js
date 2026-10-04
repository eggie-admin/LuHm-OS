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

    // Android Web3 cockpit candidate boundary. Native Android System WebView
    // wrapper wiring remains separate and is intentionally not faked here.
    $cockpit.on("luhm:backend:open", function (_event, detail) {
      console.info("LuHm Godot/system boundary requested", detail);
      postNative("world_requested");
    });

    $cockpit.on("luhm:operationTitan7:invoke", function (_event, detail) {
      console.info("operationTitan7 invocation requested", detail.wire || detail.manifest);
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
      operationTitan7: function (command, options) { return $cockpit.operationTitan7(command, options); },
      nativeBridgeAvailable: function () {
        return !!(window.LuHmNative && typeof window.LuHmNative.postMessage === "function");
      }
    });
  });
}(jQuery));
