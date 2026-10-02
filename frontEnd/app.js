(function ($) {
  "use strict";

  $(function () {
    const $cockpit = $("[data-luhm-cockpit]");
    if (!$cockpit.length) return;

    $cockpit.luhmCockpit({ initialView: "chat" });

    // Android Web3 cockpit candidate boundary. Native Android System WebView
    // wrapper wiring remains separate and is intentionally not faked here.
    $cockpit.on("luhm:backend:open", function (_event, detail) {
      console.info("LuHm Godot/system boundary requested", detail);
    });

    window.LuHmFrontEnd = Object.freeze({
      version: $.fn.luhmCockpit.version,
      jquery: $.fn.jquery,
      openBackend: function () { $cockpit.luhmCockpit("openBackend"); },
      closeBackend: function () { $cockpit.luhmCockpit("closeBackend"); },
      setView: function (view) { $cockpit.luhmCockpit("view", view); }
    });
  });
}(jQuery));
