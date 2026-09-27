(function ($, window, document) {
  "use strict";

  var MAX_STREAM_NODES = 120;
  var MAX_DRAFT_CHARS = 12000;
  var CONTEXT_STALE_MS = 5 * 60 * 1000;
  var DRAFT_KEY = "luhm.chat.draft.v1";
  var contextTouchedAt = 0;
  var contextTimer = 0;

  function installHardeningStyles() {
    if (document.querySelector('link[data-luhm-ui-hardening]')) return;
    var link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "./ui-hardening.css";
    link.setAttribute("data-luhm-ui-hardening", "true");
    document.head.appendChild(link);
  }

  function safeSessionGet(key) {
    try { return window.sessionStorage.getItem(key); } catch (_error) { return null; }
  }

  function safeSessionSet(key, value) {
    try { window.sessionStorage.setItem(key, value); } catch (_error) { /* app stays usable */ }
  }

  function safeSessionRemove(key) {
    try { window.sessionStorage.removeItem(key); } catch (_error) { /* app stays usable */ }
  }

  installHardeningStyles();

  $(function () {
    var $cockpit = $("[data-luhm-cockpit]").first();
    if (!$cockpit.length) return;

    $cockpit.luhmCockpit({ initialView: "chat" });

    var $chat = $cockpit.find("[data-luhm-chat]").first();
    var $input = $cockpit.find("[data-luhm-input]").first();
    var $stream = $cockpit.find("[data-luhm-message-stream]").first();

    function boundary(name, detail) {
      var packet = $.extend({ source: "frontEnd", observed: false }, detail || {});
      $cockpit.trigger(name, [packet]);
      return packet;
    }

    function trimMessageStream() {
      var nodes = $stream.children();
      var excess = nodes.length - MAX_STREAM_NODES;
      if (excess > 0) nodes.slice(0, excess).remove();
    }

    function persistDraft() {
      var value = String($input.val() || "").slice(0, MAX_DRAFT_CHARS);
      if (value) safeSessionSet(DRAFT_KEY, value);
      else safeSessionRemove(DRAFT_KEY);
    }

    function restoreDraft() {
      var value = safeSessionGet(DRAFT_KEY);
      if (!value || String($input.val() || "").trim()) return;
      $input.val(String(value).slice(0, MAX_DRAFT_CHARS)).trigger("input");
    }

    function updateRuntimeFlags() {
      var reducedMotion = false;
      try { reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches; } catch (_error) { reducedMotion = false; }
      $cockpit.attr("data-page-visible", document.visibilityState === "visible" ? "true" : "false");
      $cockpit.attr("data-network-state", window.navigator.onLine === false ? "offline" : "online");
      $cockpit.attr("data-reduced-motion", reducedMotion ? "true" : "false");
    }

    function updateBusyState(detail) {
      var mode = String((detail && detail.mode) || $chat.attr("data-chat-state") || "ready").toLowerCase();
      var busy = /^(queued|active|working|verifying|building|researching)$/.test(mode);
      $chat.attr("aria-busy", busy ? "true" : "false");
    }

    function updateContextFreshness() {
      var source = String($cockpit.find('[data-chat-context="sourceRef"] strong').text() || "UNKNOWN").trim();
      var stale = source !== "UNKNOWN" && contextTouchedAt > 0 && (Date.now() - contextTouchedAt) > CONTEXT_STALE_MS;
      $cockpit.attr("data-context-freshness", stale ? "stale" : "fresh");
    }

    function recordContextTouch(detail) {
      detail = detail || {};
      if (Object.prototype.hasOwnProperty.call(detail, "sourceRef") || Object.prototype.hasOwnProperty.call(detail, "branch")) {
        contextTouchedAt = Date.now();
        updateContextFreshness();
      }
    }

    function startContextClock() {
      if (contextTimer) window.clearInterval(contextTimer);
      contextTimer = window.setInterval(function () {
        if (document.visibilityState === "visible") updateContextFreshness();
      }, 30000);
    }

    $cockpit.on("luhm:backend:open", function (_event, detail) {
      console.info("LuHm backend boundary requested", detail);
    });

    $cockpit.on("luhm:chat:workbench-submit", function (_event, detail) {
      boundary("luhm:transport:send", detail);
      safeSessionRemove(DRAFT_KEY);
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

    $cockpit.on("luhm:proof:pin-request", function (_event, detail) {
      boundary("luhm:transport:proof-pin", detail);
    });

    $input.on("input.luhmUiRuntime", persistDraft);
    $(window).on("pagehide.luhmUiRuntime", persistDraft);
    $(window).on("online.luhmUiRuntime offline.luhmUiRuntime", updateRuntimeFlags);
    $(document).on("visibilitychange.luhmUiRuntime", updateRuntimeFlags);

    window.addEventListener("luhm:chat:context", function (event) {
      recordContextTouch(event.detail || {});
    });

    window.addEventListener("luhm:chat:state", function (event) {
      updateBusyState(event.detail || {});
    });

    if (window.MutationObserver && $stream.length) {
      new MutationObserver(function () {
        window.requestAnimationFrame(trimMessageStream);
      }).observe($stream.get(0), { childList: true });
    }

    function requireWorkbench() {
      if (!window.luhmChatWorkbench) throw new Error("LuHm chat workbench not initialized");
      return window.luhmChatWorkbench;
    }

    function requireProofViewer() {
      if (!window.luhmProofViewer) throw new Error("LuHm proof viewer not initialized");
      return window.luhmProofViewer;
    }

    updateRuntimeFlags();
    updateBusyState({ mode: $chat.attr("data-chat-state") || "ready" });
    restoreDraft();
    startContextClock();

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
      openProof: function (detail) { return requireProofViewer().open(detail); },
      closeProof: function () { return requireProofViewer().close(); },
      currentProof: function () { return requireProofViewer().current(); },
      setOniActivity: function (detail) {
        if (!window.luhmOniActivity) throw new Error("LuHm Oni activity dock not initialized");
        return window.luhmOniActivity.set(detail);
      },
      runtimeSnapshot: function () {
        return Object.freeze({
          pageVisible: document.visibilityState === "visible",
          networkState: window.navigator.onLine === false ? "offline" : "online",
          contextFreshness: $cockpit.attr("data-context-freshness") || "fresh",
          messageNodes: $stream.children().length,
          messageNodeCap: MAX_STREAM_NODES,
          providerNetworkTelemetry: false
        });
      }
    });
  });
}(jQuery, window, document));
