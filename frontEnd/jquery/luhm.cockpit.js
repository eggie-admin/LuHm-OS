/* LuHm OS jQuery front-end shell. UI only; privileged actions remain backend-owned. */
(function ($) {
  "use strict";

  const PLUGIN = "luhmCockpit";
  const DATA_KEY = PLUGIN;
  const EVENT_NS = "." + PLUGIN;

  const defaults = {
    initialView: "chat",
    clockIntervalMs: 30000,
    backendEvent: "luhm:backend:open",
    backendCloseEvent: "luhm:backend:close",
    chatSubmitEvent: "luhm:chat:submit",
    viewChangeEvent: "luhm:view:change"
  };

  function getState($root) {
    return $root.data(DATA_KEY);
  }

  function emit($root, name, detail) {
    $root.trigger(name, [detail || {}]);
  }

  function setView($root, view) {
    const state = getState($root);
    if (!state) return;
    state.view = view;
    $root.find("[data-view]").each(function () {
      $(this).toggleClass("isActive", $(this).data("view") === view);
    });
    state.$menu.prop("hidden", true);
    emit($root, state.settings.viewChangeEvent, { view: view });
  }

  function openBackend($root) {
    const state = getState($root);
    if (!state) return;
    state.$menu.prop("hidden", true);
    state.$systemLayer.prop("hidden", false);
    emit($root, state.settings.backendEvent, { source: "frontEnd" });
  }

  function closeBackend($root) {
    const state = getState($root);
    if (!state) return;
    state.$systemLayer.prop("hidden", true);
    emit($root, state.settings.backendCloseEvent, { source: "frontEnd" });
  }

  function updateClock($root) {
    const state = getState($root);
    if (!state) return;
    state.$clock.text(new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" }));
  }

  function appendUserMessage($root, text) {
    const state = getState($root);
    if (!state) return;
    const time = new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
    const $article = $("<article>", { class: "message messageUser" });
    $("<div>", { class: "avatar", "aria-hidden": "true", text: "Y" }).appendTo($article);
    const $body = $("<div>").appendTo($article);
    const $meta = $("<div>", { class: "messageMeta" }).appendTo($body);
    $("<strong>", { text: "You" }).appendTo($meta);
    $("<time>", { text: time }).appendTo($meta);
    $("<p>", { text: text }).appendTo($body);
    state.$messageStream.append($article);
    state.$messageStream.scrollTop(state.$messageStream.prop("scrollHeight"));
  }

  function initElement(element, options) {
    const $root = $(element);
    if (getState($root)) return;

    const settings = $.extend({}, $.fn[PLUGIN].defaults, options || {});
    const state = {
      settings: settings,
      view: settings.initialView,
      $systemLayer: $root.find("[data-luhm-system-layer]"),
      $menu: $root.find("[data-luhm-menu]"),
      $messageStream: $root.find("[data-luhm-message-stream]"),
      $composer: $root.find("[data-luhm-composer]"),
      $input: $root.find("[data-luhm-input]"),
      $clock: $root.find("[data-luhm-clock]"),
      clockTimer: null
    };
    $root.data(DATA_KEY, state);

    $root.on("click" + EVENT_NS, "[data-view]", function () {
      setView($root, $(this).data("view"));
    });
    $root.on("click" + EVENT_NS, "[data-luhm-backend-button]", function () {
      openBackend($root);
    });
    $root.on("click" + EVENT_NS, "[data-luhm-backend-close]", function () {
      closeBackend($root);
    });
    $root.on("click" + EVENT_NS, "[data-luhm-menu-button]", function () {
      state.$menu.prop("hidden", !state.$menu.prop("hidden"));
    });
    state.$composer.on("submit" + EVENT_NS, function (event) {
      event.preventDefault();
      const text = String(state.$input.val() || "").trim();
      if (!text) return;
      appendUserMessage($root, text);
      state.$input.val("");
      emit($root, settings.chatSubmitEvent, { text: text });
    });

    setView($root, settings.initialView);
    updateClock($root);
    state.clockTimer = window.setInterval(function () { updateClock($root); }, settings.clockIntervalMs);
    emit($root, "luhm:frontend:ready", { version: $.fn[PLUGIN].version, jquery: $.fn.jquery });
  }

  const methods = {
    init: function (options) {
      return this.each(function () { initElement(this, options); });
    },
    view: function (view) {
      return this.each(function () { setView($(this), view); });
    },
    openBackend: function () {
      return this.each(function () { openBackend($(this)); });
    },
    closeBackend: function () {
      return this.each(function () { closeBackend($(this)); });
    },
    destroy: function () {
      return this.each(function () {
        const $root = $(this);
        const state = getState($root);
        if (!state) return;
        if (state.clockTimer) window.clearInterval(state.clockTimer);
        state.$composer.off(EVENT_NS);
        $root.off(EVENT_NS);
        $root.removeData(DATA_KEY);
      });
    }
  };

  $.fn[PLUGIN] = function (methodOrOptions) {
    if (methods[methodOrOptions]) {
      return methods[methodOrOptions].apply(this, Array.prototype.slice.call(arguments, 1));
    }
    if (typeof methodOrOptions === "object" || methodOrOptions == null) {
      return methods.init.apply(this, arguments);
    }
    $.error("Unknown " + PLUGIN + " method: " + methodOrOptions);
    return this;
  };

  $.fn[PLUGIN].defaults = defaults;
  $.fn[PLUGIN].version = "0.2.0-dryrun.1";
}(jQuery));
