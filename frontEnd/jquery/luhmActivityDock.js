/* LuHm OS receipt-driven comic activity dock. UI only; no execution authority. */
(function ($) {
  "use strict";

  const pluginName = "luhmActivityDock";
  const dataKey = pluginName;
  const eventNs = "." + pluginName;
  const states = new Set(["parked", "queued", "active", "waiting", "observed", "verifying", "success", "error", "unknown", "crownStop"]);
  const claims = new Set(["unknown", "observed", "amber", "green", "red"]);

  const defaults = {
    updateEvent: "luhm:activity:update",
    clearEvent: "luhm:activity:clear"
  };

  function text(value, fallback) {
    const out = String(value == null ? "" : value).trim();
    return out || fallback;
  }

  function stateValue(value) {
    const out = text(value, "unknown");
    return states.has(out) ? out : "unknown";
  }

  function claimValue(value) {
    const out = text(value, "unknown").toLowerCase();
    return claims.has(out) ? out : "unknown";
  }

  function getState($root) {
    return $root.data(dataKey);
  }

  function setStateClass($el, value) {
    const state = stateValue(value);
    $el.attr("data-state", state).text(state);
  }

  function renderLane($root, lane) {
    const id = text(lane && lane.id, "");
    if (!id) return;
    const $lane = $root.find('[data-luhm-agent-lane="' + id.replace(/"/g, "") + '"]');
    if (!$lane.length) return;
    setStateClass($lane.find("[data-lane-state]"), lane.state);
    $lane.find("[data-lane-note]").text(text(lane.note, "no observed receipt"));
  }

  function render($root, packet) {
    const state = getState($root);
    if (!state) return;
    const p = packet && typeof packet === "object" ? packet : {};

    $root.attr("data-task-id", text(p.taskId, "UNKNOWN"));
    $root.attr("data-source-ref", text(p.sourceRef, "UNKNOWN"));
    $root.attr("data-scope-id", text(p.scopeId, "UNKNOWN"));

    $root.find("[data-activity-headline]").text(text(p.headline, "No active observed task"));
    setStateClass($root.find("[data-activity-phase]"), p.phase);

    const claim = claimValue(p.claimState);
    $root.find("[data-activity-claim]").attr("data-claim", claim).text(claim.toUpperCase());
    $root.find("[data-activity-check]").text(text(p.checkSummary, "No deterministic check observed"));
    $root.find("[data-activity-receipt]").text(text(p.evidenceRef, "none"));
    $root.find("[data-activity-crown]").text(text(p.crownStatus, "stop").toUpperCase());

    const lanes = Array.isArray(p.lanes) ? p.lanes : [];
    lanes.forEach(function (lane) { renderLane($root, lane); });

    state.lastPacket = $.extend(true, {}, p);
    $root.trigger("luhm:activity:rendered", [{
      taskId: text(p.taskId, "unknown"),
      sourceRef: text(p.sourceRef, "unknown"),
      scopeId: text(p.scopeId, "unknown"),
      claimState: claim
    }]);
  }

  function clear($root) {
    render($root, {
      taskId: "unknown",
      sourceRef: "unknown",
      scopeId: "unknown",
      headline: "PARKED · no active task receipt",
      phase: "parked",
      claimState: "unknown",
      checkSummary: "No deterministic check observed",
      evidenceRef: "none",
      crownStatus: "stop",
      lanes: [
        { id: "lum", state: "parked", note: "waiting for task" },
        { id: "urdDoctorGoddess", state: "parked", note: "no diagnosis packet" },
        { id: "belldandySecretary", state: "parked", note: "no state packet" },
        { id: "skuldResearch", state: "parked", note: "no research packet" }
      ]
    });
  }

  function initElement(element, options) {
    const $root = $(element);
    if (getState($root)) return;

    const settings = $.extend({}, $.fn[pluginName].defaults, options || {});
    $root.data(dataKey, { settings: settings, lastPacket: null, raf: 0, px: 0, py: 0 });

    const motionOkay = !(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
    if (motionOkay) {
      $root.on("pointermove" + eventNs, function (event) {
        const state = getState($root);
        if (!state) return;
        const rect = this.getBoundingClientRect();
        state.px = ((event.clientX - rect.left) / Math.max(rect.width, 1) - 0.5) * 2;
        state.py = ((event.clientY - rect.top) / Math.max(rect.height, 1) - 0.5) * 2;
        if (state.raf) return;
        state.raf = window.requestAnimationFrame(function () {
          state.raf = 0;
          const x = Math.max(-1, Math.min(1, state.px));
          const y = Math.max(-1, Math.min(1, state.py));
          $root.css({"--comicX": x.toFixed(3), "--comicY": y.toFixed(3)});
        });
      });
      $root.on("pointerleave" + eventNs, function () {
        const state = getState($root);
        if (!state) return;
        state.px = 0;
        state.py = 0;
        $root.css({"--comicX": "0", "--comicY": "0"});
      });
    }

    $root.on(settings.updateEvent + eventNs, function (_event, packet) {
      render($root, packet);
    });
    $root.on(settings.clearEvent + eventNs, function () {
      clear($root);
    });

    clear($root);
  }

  const methods = {
    init: function (options) {
      return this.each(function () { initElement(this, options); });
    },
    render: function (packet) {
      return this.each(function () { render($(this), packet); });
    },
    clear: function () {
      return this.each(function () { clear($(this)); });
    },
    snapshot: function () {
      const state = getState(this.first());
      return state ? $.extend(true, {}, state.lastPacket) : null;
    },
    destroy: function () {
      return this.each(function () {
        const $root = $(this);
        const state = getState($root);
        if (!state) return;
        if (state.raf) window.cancelAnimationFrame(state.raf);
        $root.off(eventNs);
        $root.removeData(dataKey);
      });
    }
  };

  $.fn[pluginName] = function (methodOrOptions) {
    if (methods[methodOrOptions]) {
      return methods[methodOrOptions].apply(this, Array.prototype.slice.call(arguments, 1));
    }
    if (typeof methodOrOptions === "object" || methodOrOptions == null) {
      return methods.init.apply(this, arguments);
    }
    $.error("Unknown " + pluginName + " method: " + methodOrOptions);
    return this;
  };

  $.fn[pluginName].defaults = defaults;
  $.fn[pluginName].version = "1.0.0-candidate.1";
}(jQuery));
