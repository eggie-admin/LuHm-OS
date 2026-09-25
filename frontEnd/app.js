(function ($) {
  "use strict";

  $(function () {
    const $cockpit = $("[data-luhm-cockpit]");
    if (!$cockpit.length) return;

    $cockpit.luhmCockpit({ initialView: "chat" });

    // Temporary dry-run bridge surface. Native backend launch/wrapper wiring
    // belongs to the Android/Godot shell and is intentionally not faked here.
    $cockpit.on("luhm:backend:open", function (_event, detail) {
      console.info("LuHm backend boundary requested", detail);
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
