/* LuHm OS Oni Summoner. Presentation/routing UI only; authority remains backend/doctrine owned. */
(function ($) {
  "use strict";

  const PLUGIN = "luhmOniSummoner";
  const DATA_KEY = PLUGIN;
  const EVENT_NS = "." + PLUGIN;
  const VALID_ACTIVITY = new Set(["PARKED", "QUEUED", "ACTIVE", "WAITING", "VERIFYING", "SUCCESS", "ERROR"]);

  const roster = [
    { name: "Lum", glyph: "L", kind: "boss-router-integrator", skillPath: "agents/lum/SKILL.md", defaultAuthority: "NONE", tagline: "Routes the smallest useful crew and keeps the Professor-facing thread coherent." },
    { name: "Kiri", glyph: "K", kind: "context-resolver", skillPath: "agents/kiriContextOni/SKILL.md", defaultAuthority: "READ_ONLY", tagline: "Resolves source identity, scope, context, and evidence references." },
    { name: "Tetsu", glyph: "T", kind: "fast-builder", skillPath: "agents/buildOnis/SKILL.md", defaultAuthority: "READ_ONLY", tagline: "Runs the fast exact-source build lane." },
    { name: "Kaji", glyph: "J", kind: "clean-room-builder", skillPath: "agents/buildOnis/SKILL.md", defaultAuthority: "READ_ONLY", tagline: "Independently rebuilds the same immutable source for cross-checking." },
    { name: "Momo", glyph: "M", kind: "bounded-researcher", skillPath: "agents/momoResearchOni/SKILL.md", defaultAuthority: "READ_ONLY", tagline: "Researches only the bounded external/current fact Lum asks for." },
    { name: "Shiori", glyph: "S", kind: "critic-contradiction-checker", skillPath: "agents/shioriCriticOni/SKILL.md", defaultAuthority: "READ_ONLY", tagline: "Challenges contradictions, stale evidence, scope drift, and fake GREEN." },
    { name: "DrNao", glyph: "N", kind: "deterministic-source-truth-adjudicator", skillPath: "agents/doctorOni/SKILL.md", defaultAuthority: "READ_ONLY", tagline: "Adjudicates exact-source evidence without repairing what she diagnoses." },
    { name: "Kugi", glyph: "G", kind: "deterministic-tool-executor", skillPath: "agents/kugiToolOni/SKILL.md", defaultAuthority: "PLAN_ONLY", tagline: "Executes only the exact bounded mutation packet already authorized." },
    { name: "Fumi", glyph: "F", kind: "records-registrar-helper", skillPath: "agents/fumiSecretaryOni/SKILL.md", defaultAuthority: "READ_ONLY", tagline: "Normalizes records, Drive/API/repo naming, and receipt indexes." },
    { name: "Sumi", glyph: "U", kind: "asset-curator", skillPath: "agents/sumiAssetOni/SKILL.md", defaultAuthority: "READ_ONLY", tagline: "Checks asset identity, rights, provenance, and importability." },
    { name: "Koe", glyph: "O", kind: "dictation-scribe", skillPath: "agents/koeDictationOni/SKILL.md", defaultAuthority: "READ_ONLY", tagline: "Turns dictation into faithful notes and bounded task packets." },
    { name: "Yume", glyph: "Y", kind: "art-media-helper", skillPath: "agents/yumeArtOni/SKILL.md", defaultAuthority: "PLAN_ONLY", tagline: "Plans original visual and audiovisual work inside the bounded creative lane." },
    { name: "Urd", glyph: "R", kind: "doctor-goddess-system-diagnostician", skillPath: "agents/urdMutationOni/SKILL.md", defaultAuthority: "READ_ONLY", tagline: "Diagnoses failures, evidence gaps, rollback risk, and repair sanity without taking authority." },
    { name: "Belldandy", glyph: "B", kind: "secretary-goddess-state-records-keeper", skillPath: "agents/belldandyQualityOni/SKILL.md", defaultAuthority: "READ_ONLY", tagline: "Keeps state, names, paths, receipts, handoffs, and milestone continuity from drifting." },
    { name: "Skuld", glyph: "S", kind: "research-goddess-compatibility-scout", skillPath: "agents/skuldResearchOni/SKILL.md", defaultAuthority: "READ_ONLY", tagline: "Scouts current technical compatibility, dependencies, vendor behavior, and licensing." }
  ];

  const defaults = {
    roster: roster,
    maxActivity: 80,
    maxSummaryLength: 220,
    summonEvent: "luhm:oni:summon",
    activityEvent: "luhm:oni:activity",
    routeEvent: "luhm:oni:route",
    bubbleEvent: "luhm:oni:bubble",
    selected: "Lum"
  };

  function clampText(value, max) {
    const text = String(value == null ? "" : value).replace(/\s+/g, " ").trim();
    return text.length <= max ? text : text.slice(0, Math.max(0, max - 1)) + "…";
  }

  function normalizeActivity(input, settings) {
    const raw = input && typeof input === "object" ? input : {};
    const state = VALID_ACTIVITY.has(String(raw.state || "").toUpperCase()) ? String(raw.state).toUpperCase() : "PARKED";
    const progress = Number(raw.progress);
    return {
      oni: clampText(raw.oni || "Lum", 32),
      state: state,
      summary: clampText(raw.summary || "No observed activity summary yet.", settings.maxSummaryLength),
      processLabel: clampText(raw.processLabel || "", 96),
      taskId: clampText(raw.taskId || "UNKNOWN", 120),
      sourceRef: clampText(raw.sourceRef || "UNKNOWN", 160),
      receiptRef: clampText(raw.receiptRef || "", 180),
      progress: Number.isFinite(progress) ? Math.max(0, Math.min(100, progress)) : null,
      updatedAt: clampText(raw.updatedAt || new Date().toISOString(), 64)
    };
  }

  function stateClass(state) {
    return "state-" + String(state || "PARKED").toLowerCase();
  }

  function findRole(state, name) {
    return state.settings.roster.find(function (role) { return role.name === name; }) || null;
  }

  function emit($root, name, detail) {
    $root.trigger(name, [detail || {}]);
  }

  function makePet(role) {
    const $pet = $("<span>", { class: "luhmOniPet", "aria-hidden": "true" });
    $("<span>", { class: "luhmOniHorn hornLeft" }).appendTo($pet);
    $("<span>", { class: "luhmOniHorn hornRight" }).appendTo($pet);
    $("<span>", { class: "luhmOniGlyph", text: role.glyph }).appendTo($pet);
    return $pet;
  }

  function renderShell($root, settings) {
    $root.empty().addClass("luhmOniSummoner");

    const $header = $("<header>", { class: "luhmOniHeader" }).appendTo($root);
    const $title = $("<div>", { class: "luhmOniTitle" }).appendTo($header);
    $("<strong>", { text: "Oni Summoner" }).appendTo($title);
    $("<span>", { text: "Lum routes. Oni report observed work. Professor keeps Crown." }).appendTo($title);
    $("<span>", { class: "luhmOniTruthChip", text: "ACTIVITY ≠ AUTHORITY" }).appendTo($header);

    const $layout = $("<div>", { class: "luhmOniLayout" }).appendTo($root);
    const $roster = $("<section>", { class: "luhmOniRoster", "aria-label": "Oni roster" }).appendTo($layout);
    const $inspector = $("<section>", { class: "luhmOniInspector", "aria-live": "polite" }).appendTo($layout);
    const $activity = $("<section>", { class: "luhmOniActivity" }).appendTo($root);
    $("<div>", { class: "luhmOniSectionTitle", text: "Observed background activity" }).appendTo($activity);
    const $feed = $("<div>", { class: "luhmOniFeed", role: "log", "aria-live": "polite", "aria-relevant": "additions text" }).appendTo($activity);

    settings.roster.forEach(function (role) {
      const $button = $("<button>", {
        type: "button",
        class: "luhmOniCard " + (role.name === settings.selected ? "isSelected" : ""),
        "data-oni": role.name,
        title: role.kind
      }).appendTo($roster);
      makePet(role).appendTo($button);
      const $copy = $("<span>", { class: "luhmOniCardCopy" }).appendTo($button);
      $("<strong>", { text: role.name }).appendTo($copy);
      $("<span>", { text: role.kind }).appendTo($copy);
      $("<span>", { class: "luhmOniState state-parked", "data-oni-state": role.name, text: "PARKED" }).appendTo($button);
    });

    $root.data(DATA_KEY, {
      settings: settings,
      selected: settings.selected,
      activities: [],
      lastByOni: Object.create(null),
      $roster: $roster,
      $inspector: $inspector,
      $feed: $feed
    });
    renderInspector($root, settings.selected);

    if ($.fn.tooltip) {
      $root.find("[title]").tooltip({ track: true });
    }
  }

  function renderInspector($root, name) {
    const state = $root.data(DATA_KEY);
    if (!state) return;
    const role = findRole(state, name) || findRole(state, "Lum") || state.settings.roster[0];
    if (!role) return;
    state.selected = role.name;
    state.$roster.find(".luhmOniCard").toggleClass("isSelected", false);
    state.$roster.find('[data-oni="' + role.name + '"]').addClass("isSelected");
    state.$inspector.empty();

    const $hero = $("<div>", { class: "luhmOniInspectorHero" }).appendTo(state.$inspector);
    makePet(role).appendTo($hero);
    const $heroCopy = $("<div>").appendTo($hero);
    $("<h3>", { text: role.name }).appendTo($heroCopy);
    $("<p>", { text: role.tagline }).appendTo($heroCopy);

    const last = state.lastByOni[role.name] || normalizeActivity({ oni: role.name, state: "PARKED", summary: "No observed task packet is active." }, state.settings);
    const $bubble = $("<div>", { class: "luhmOniBubble " + stateClass(last.state) }).appendTo(state.$inspector);
    $("<div>", { class: "luhmOniBubbleMeta", text: last.state + " · " + last.taskId }).appendTo($bubble);
    $("<p>", { text: last.summary }).appendTo($bubble);
    if (last.processLabel) $("<div>", { class: "luhmOniProcess", text: last.processLabel }).appendTo($bubble);
    if (last.progress !== null) {
      const $meter = $("<div>", { class: "luhmOniProgress", role: "progressbar", "aria-valuemin": "0", "aria-valuemax": "100", "aria-valuenow": String(last.progress) }).appendTo($bubble);
      $("<span>").css("width", last.progress + "%").appendTo($meter);
    }

    const $facts = $("<dl>", { class: "luhmOniFacts" }).appendTo(state.$inspector);
    [["Skill", role.skillPath], ["Default authority", role.defaultAuthority], ["Source", last.sourceRef]].forEach(function (pair) {
      $("<dt>", { text: pair[0] }).appendTo($facts);
      $("<dd>", { text: pair[1] }).appendTo($facts);
    });

    $("<button>", { type: "button", class: "luhmSummonButton", "data-luhm-summon": role.name, text: role.name === "Lum" ? "Call Lum" : "Summon " + role.name }).appendTo(state.$inspector);
    $("<p>", { class: "luhmOniFinePrint", text: "Summon requests routing only. It does not execute, approve, merge, sign, publish, or invent background work." }).appendTo(state.$inspector);
  }

  function pushActivity($root, raw) {
    const state = $root.data(DATA_KEY);
    if (!state) return;
    const item = normalizeActivity(raw, state.settings);
    const role = findRole(state, item.oni);
    if (!role) return;
    state.lastByOni[item.oni] = item;
    state.activities.unshift(item);
    state.activities = state.activities.slice(0, state.settings.maxActivity);

    const $chip = state.$roster.find('[data-oni-state="' + item.oni + '"]');
    $chip.attr("class", "luhmOniState " + stateClass(item.state)).text(item.state);

    const $entry = $("<article>", { class: "luhmOniFeedEntry " + stateClass(item.state) });
    makePet(role).appendTo($entry);
    const $body = $("<div>", { class: "luhmOniFeedBody" }).appendTo($entry);
    const $meta = $("<div>", { class: "luhmOniFeedMeta" }).appendTo($body);
    $("<strong>", { text: item.oni }).appendTo($meta);
    $("<span>", { text: item.state }).appendTo($meta);
    $("<span>", { text: item.taskId }).appendTo($meta);
    $("<p>", { text: item.summary }).appendTo($body);
    if (item.receiptRef) $("<code>", { text: item.receiptRef }).appendTo($body);
    state.$feed.prepend($entry);
    state.$feed.children().slice(state.settings.maxActivity).remove();

    if (state.selected === item.oni) renderInspector($root, item.oni);
  }

  function applyRoute($root, result) {
    const state = $root.data(DATA_KEY);
    if (!state) return;
    const workers = Array.isArray(result && result.workers) ? result.workers : [];
    const taskId = result && result.requestScope ? result.requestScope.taskId : "UNKNOWN";
    const sourceRef = result && result.requestScope ? result.requestScope.sourceRef : "UNKNOWN";
    state.settings.roster.forEach(function (role) {
      if (workers.includes(role.name)) {
        pushActivity($root, { oni: role.name, state: "QUEUED", taskId: taskId, sourceRef: sourceRef, summary: role.name === "Lum" ? "Route accepted. Lum is coordinating the observed worker plan." : "Queued by the deterministic route. Waiting for an observed task/process receipt." });
      }
    });
    emit($root, state.settings.routeEvent, { workers: workers.slice(), taskId: taskId, sourceRef: sourceRef });
  }

  function initElement(element, options) {
    const $root = $(element);
    if ($root.data(DATA_KEY)) return;
    const settings = $.extend(true, {}, $.fn[PLUGIN].defaults, options || {});
    renderShell($root, settings);

    $root.on("click" + EVENT_NS, "[data-oni]", function () {
      renderInspector($root, String($(this).data("oni") || "Lum"));
    });
    $root.on("click" + EVENT_NS, "[data-luhm-summon]", function () {
      const state = $root.data(DATA_KEY);
      const name = String($(this).data("luhm-summon") || "Lum");
      const role = findRole(state, name);
      if (!role) return;
      emit($root, state.settings.summonEvent, {
        name: role.name,
        kind: role.kind,
        skillPath: role.skillPath,
        defaultAuthority: role.defaultAuthority,
        mutationAuthority: false,
        greenAuthority: false
      });
      pushActivity($root, { oni: "Lum", state: "QUEUED", taskId: "LOCAL_SUMMON_REQUEST", sourceRef: "UNKNOWN", summary: "Summon request emitted for " + role.name + ". Waiting for the host/router to accept or reject it." });
    });
    $root.on(settings.activityEvent + EVENT_NS, function (_event, detail) { pushActivity($root, detail); });
    $root.on(settings.bubbleEvent + EVENT_NS, function (_event, detail) { pushActivity($root, detail); });
  }

  const methods = {
    init: function (options) { return this.each(function () { initElement(this, options); }); },
    select: function (name) { return this.each(function () { renderInspector($(this), name); }); },
    activity: function (detail) { return this.each(function () { pushActivity($(this), detail); }); },
    route: function (result) { return this.each(function () { applyRoute($(this), result); }); },
    snapshot: function () {
      const state = this.first().data(DATA_KEY);
      if (!state) return null;
      return { selected: state.selected, activities: state.activities.slice(), lastByOni: $.extend(true, {}, state.lastByOni) };
    },
    destroy: function () {
      return this.each(function () {
        const $root = $(this);
        if ($.fn.tooltip) {
          try { $root.find("[title]").tooltip("destroy"); } catch (_error) { /* optional enhancer */ }
        }
        $root.off(EVENT_NS).empty().removeClass("luhmOniSummoner").removeData(DATA_KEY);
      });
    }
  };

  $.fn[PLUGIN] = function (methodOrOptions) {
    if (methods[methodOrOptions]) return methods[methodOrOptions].apply(this, Array.prototype.slice.call(arguments, 1));
    if (typeof methodOrOptions === "object" || methodOrOptions == null) return methods.init.apply(this, arguments);
    $.error("Unknown " + PLUGIN + " method: " + methodOrOptions);
    return this;
  };

  $.fn[PLUGIN].defaults = defaults;
  $.fn[PLUGIN].version = "1.0.0-candidate.1";
}(jQuery));
