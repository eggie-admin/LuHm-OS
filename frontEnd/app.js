(function ($, window) {
  "use strict";

  $(function () {
    const $cockpit = $("[data-luhm-cockpit]");
    if (!$cockpit.length) return;

    $cockpit.luhmCockpit({ initialView: "chat" });

    function boundary(name, detail) {
      const packet = $.extend({ source: "frontEnd", observed: false }, detail || {});
      $cockpit.trigger(name, [packet]);
      return packet;
    }

    $cockpit.on("luhm:backend:open", function (_event, detail) {
      console.info("LuHm backend boundary requested", detail);
    });

    $cockpit.on("luhm:chat:workbench-submit", function (_event, detail) {
      boundary("luhm:transport:send", detail);
    });

    $cockpit.on("luhm:chat:attach", function (_event, detail) {
      boundary("luhm:transport:attach", detail);
    });

    $cockpit.on("luhm:chat:voice", function (_event, detail) {
      boundary("luhm:transport:voice", detail);
    });

    $cockpit.on("luhm:chat:stop", function (_event, detail) {
      boundary("luhm:transport:stop", detail);
    });

    function requireWorkbench() {
      if (!window.luhmChatWorkbench) throw new Error("LuHm chat workbench not initialized");
      return window.luhmChatWorkbench;
    }

    window.LuHmFrontEnd = Object.freeze({
      version: $.fn.luhmCockpit.version,
      jquery: $.fn.jquery,
      openBackend: function () { $cockpit.luhmCockpit("openBackend"); },
      closeBackend: function () { $cockpit.luhmCockpit("closeBackend"); },
      setView: function (view) { $cockpit.luhmCockpit("view", view); },
      setChatContext: function (detail) { requireWorkbench().setContext(detail); },
      setChatState: function (detail) { requireWorkbench().state(detail); },
      appendAssistant: function (detail) { requireWorkbench().assistant(detail); },
      appendReceipt: function (detail) { requireWorkbench().receipt(detail); },
      setOniActivity: function (detail) {
        if (!window.luhmOniActivity) throw new Error("LuHm Oni activity dock not initialized");
        return window.luhmOniActivity.set(detail);
      }
    });
  });
}(jQuery, window));
