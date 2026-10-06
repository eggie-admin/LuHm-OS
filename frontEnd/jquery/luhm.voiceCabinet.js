(function ($) {
  "use strict";

  const pluginName = "luhmVoiceCabinet";
  const dataKey = pluginName;
  const eventNamespace = ".luhmVoiceCabinet";
  const preferenceKey = "luhmVoiceCabinet.voiceMap.v1";
  const states = Object.freeze(["OUTSIDE", "ACTIVE", "PAUSED"]);
  const speakers = Object.freeze({
    lum: "Lum",
    urdDoctorGoddess: "Urd",
    belldandySecretary: "Belldandy",
    skuldResearch: "Skuld",
    yume: "Yume"
  });

  function normalizeCommand(value) {
    return String(value || "").normalize("NFC").trim().toLocaleUpperCase("en-US");
  }

  function parseCommand(value, state) {
    const command = normalizeCommand(value);
    const mode = states.includes(state) ? state : "OUTSIDE";

    if (command === "AFTER HOURS" && mode === "OUTSIDE") return "enter";
    if (command === "EXIT" && mode !== "OUTSIDE") return "exit";
    if ((command === "PAUSE" || command === "OOC") && mode === "ACTIVE") return "pause";
    if (command === "RESUME" && mode === "PAUSED") return "resume";
    if (command === "C" && mode === "ACTIVE") return "continue";
    if (command === "C" && mode === "PAUSED") return "continueWhilePaused";
    return null;
  }

  function normalizeTurn(turn) {
    if (!turn || turn.kind !== "namedEnsembleTurn" || !Array.isArray(turn.speakerSegments)) return null;
    const segments = turn.speakerSegments.slice(0, 8).map(function (segment) {
      if (!segment || !Object.prototype.hasOwnProperty.call(speakers, segment.speakerId)) return null;
      const text = String(segment.utterance || segment.text || "").trim().slice(0, 900);
      if (!text) return null;
      return Object.freeze({ speakerId: segment.speakerId, text: text });
    }).filter(Boolean);
    if (!segments.length) return null;
    return Object.freeze({ kind: "namedEnsembleTurn", speakerSegments: Object.freeze(segments) });
  }

  function readVoiceMap() {
    try {
      const raw = window.localStorage && window.localStorage.getItem(preferenceKey);
      const value = raw ? JSON.parse(raw) : {};
      return value && typeof value === "object" && !Array.isArray(value) ? value : {};
    } catch (_error) {
      return {};
    }
  }

  function saveVoiceMap(value) {
    try {
      if (window.localStorage) window.localStorage.setItem(preferenceKey, JSON.stringify(value));
    } catch (_error) {
      // Voice preferences are optional; private-mode storage may be unavailable.
    }
  }

  function stateFor($root) {
    return $root.data(dataKey);
  }

  function emit($root, eventName, payload) {
    $root.trigger(eventName, [payload]);
  }

  function appendStatus(state, title, text) {
    const $article = $("<article>", { class: "message messageLum voiceStatus" });
    const $body = $("<div>").appendTo($article);
    const $meta = $("<div>", { class: "messageMeta" }).appendTo($body);
    $("<strong>", { text: title }).appendTo($meta);
    $("<p>", { text: text }).appendTo($body);
    state.$messageStream.append($article);
    state.$messageStream.scrollTop(state.$messageStream.prop("scrollHeight"));
  }

  function availableVoices(state) {
    const speech = window.speechSynthesis;
    if (!speech || typeof speech.getVoices !== "function") return [];
    return speech.getVoices() || [];
  }

  function buildVoiceSelectors(state) {
    const voices = availableVoices(state);
    const $host = state.$voiceSelectors.empty();
    const $status = $("<p>", { class: "voiceCabinetStatus", "aria-live": "polite" })
      .text(voices.length ? "Choose an installed device voice for each speaker." : "Device voices will appear here when the browser provides them.")
      .appendTo($host);

    Object.keys(speakers).forEach(function (speakerId) {
      const selectorId = "voice-" + speakerId;
      const $label = $("<label>", { class: "voiceSelector", for: selectorId });
      $("<span>", { text: speakers[speakerId] }).appendTo($label);
      const $select = $("<select>", { id: selectorId, "data-luhm-speaker-voice": speakerId });
      $("<option>", { value: "", text: "Device default" }).appendTo($select);
      voices.forEach(function (voice) {
        $("<option>", { value: voice.voiceURI, text: voice.name + " · " + voice.lang }).appendTo($select);
      });
      const saved = state.voiceMap[speakerId] || "";
      if (saved && voices.some(function (voice) { return voice.voiceURI === saved; })) $select.val(saved);
      $select.prop("disabled", !voices.length);
      $label.append($select).appendTo($host);
    });
    return $status;
  }

  function selectedVoice(state, speakerId) {
    const uri = state.voiceMap[speakerId];
    if (!uri) return null;
    return availableVoices(state).find(function (voice) { return voice.voiceURI === uri; }) || null;
  }

  function speakTurn(state, rawTurn) {
    const turn = normalizeTurn(rawTurn);
    if (!turn) {
      appendStatus(state, "VOICE CABINET", "The response did not match the named-speaker format; no audio was played.");
      return false;
    }

    turn.speakerSegments.forEach(function (segment) {
      const label = speakers[segment.speakerId];
      const $article = $("<article>", { class: "message messageLum voiceSegment" });
      const $body = $("<div>").appendTo($article);
      const $meta = $("<div>", { class: "messageMeta" }).appendTo($body);
      $("<strong>", { text: label }).appendTo($meta);
      $("<p>", { text: segment.text }).appendTo($body);
      state.$messageStream.append($article);
    });
    state.$messageStream.scrollTop(state.$messageStream.prop("scrollHeight"));

    const speech = window.speechSynthesis;
    const Utterance = window.SpeechSynthesisUtterance;
    if (!speech || typeof speech.speak !== "function" || typeof Utterance !== "function") {
      appendStatus(state, "VOICE CABINET", "Named dialogue is visible; speech synthesis is unavailable in this host.");
      return false;
    }
    speech.cancel();
    turn.speakerSegments.forEach(function (segment) {
      const utterance = new Utterance(segment.text);
      utterance.voice = selectedVoice(state, segment.speakerId);
      utterance.rate = 1;
      utterance.pitch = 1;
      speech.speak(utterance);
    });
    return true;
  }

  function updateControls(state) {
    state.$enter.prop("hidden", state.mode !== "OUTSIDE");
    state.$continue.prop("hidden", state.mode !== "ACTIVE");
    state.$pause.prop("hidden", state.mode !== "ACTIVE");
    state.$resume.prop("hidden", state.mode !== "PAUSED");
    state.$exit.prop("hidden", state.mode === "OUTSIDE");
    state.$mode.text(state.mode === "OUTSIDE" ? "NORMAL CHAT" : "AFTER HOURS · " + state.mode);
    state.$root.toggleClass("afterHoursActive", state.mode === "ACTIVE");
  }

  function processCommand(state, command, source) {
    if (!command) return false;
    if (command === "continueWhilePaused") {
      appendStatus(state, "AFTER HOURS · PAUSED", "Say RESUME before continuing the scene.");
      return true;
    }
    if (command === "enter") {
      state.mode = "ACTIVE";
      updateControls(state);
      appendStatus(state, "AFTER HOURS", "The read-only scene is open. C advances it; OOC pauses it.");
      emit(state.$root, "luhm:after-hours:enter", { mode: state.mode, authorityEffect: "none", source: source });
      return true;
    }
    if (command === "pause") {
      state.mode = "PAUSED";
      if (window.speechSynthesis) window.speechSynthesis.cancel();
      updateControls(state);
      appendStatus(state, "OOC · PAUSED", "The scene is paused. Real-world requests stay out of the fiction.");
      emit(state.$root, "luhm:after-hours:pause", { mode: state.mode, authorityEffect: "none", source: source });
      return true;
    }
    if (command === "resume") {
      state.mode = "ACTIVE";
      updateControls(state);
      appendStatus(state, "AFTER HOURS", "Back in the scene.");
      emit(state.$root, "luhm:after-hours:resume", { mode: state.mode, authorityEffect: "none", source: source });
      return true;
    }
    if (command === "exit") {
      state.mode = "OUTSIDE";
      if (window.speechSynthesis) window.speechSynthesis.cancel();
      updateControls(state);
      appendStatus(state, "NORMAL CHAT", "After Hours closed.");
      emit(state.$root, "luhm:after-hours:exit", { mode: state.mode, authorityEffect: "none", source: source });
      return true;
    }
    if (command === "continue") {
      appendStatus(state, "VOICE CABINET", "C reached Lum’s cabinet event bridge. This front-end candidate has no agent runtime attached yet.");
      emit(state.$root, "luhm:voice:continue", {
        mode: "afterHours",
        modeState: state.mode,
        utterance: "C",
        source: source,
        authorityEffect: "none"
      });
      return true;
    }
    return false;
  }

  function routeText(state, rawText) {
    const text = String(rawText || "").trim();
    const command = parseCommand(text, state.mode);
    if (command) return processCommand(state, command, "text");
    if (state.mode === "ACTIVE" && /^OOC\s*:/i.test(text)) {
      processCommand(state, "pause", "text");
      const outOfCharacterText = text.replace(/^OOC\s*:\s*/i, "").trim();
      if (outOfCharacterText) {
        emit(state.$root, "luhm:chat:submit", { text: outOfCharacterText, mode: "ooc" });
      }
      return true;
    }
    if (state.mode === "ACTIVE") {
      appendStatus(state, "AFTER HOURS INPUT", "The scene input reached the cabinet event bridge. No agent runtime is attached by this front-end candidate.");
      emit(state.$root, "luhm:after-hours:input", { mode: state.mode, text: text, authorityEffect: "none" });
      return true;
    }
    return false;
  }

  function init(element) {
    const $root = $(element);
    if (stateFor($root)) return;
    const state = {
      $root: $root,
      mode: "OUTSIDE",
      voiceMap: readVoiceMap(),
      $messageStream: $root.find("[data-luhm-message-stream]"),
      $voiceSelectors: $root.find("[data-luhm-voice-selectors]"),
      $enter: $root.find("[data-luhm-after-hours-enter]"),
      $continue: $root.find("[data-luhm-continue]"),
      $pause: $root.find("[data-luhm-pause]"),
      $resume: $root.find("[data-luhm-resume]"),
      $exit: $root.find("[data-luhm-exit]"),
      $mode: $root.find("[data-luhm-after-hours-mode]")
    };
    $root.data(dataKey, state);
    buildVoiceSelectors(state);
    updateControls(state);

    $root.on("luhm:chat:route" + eventNamespace, function (_event, detail) {
      return routeText(state, detail && detail.text);
    });
    $root.on("luhm:voice:ensemble" + eventNamespace, function (_event, turn) {
      if (state.mode === "ACTIVE") speakTurn(state, turn);
    });
    $root.on("click" + eventNamespace, "[data-luhm-continue]", function () {
      processCommand(state, "continue", "button");
    });
    $root.on("click" + eventNamespace, "[data-luhm-after-hours-enter]", function () {
      processCommand(state, "enter", "button");
    });
    $root.on("click" + eventNamespace, "[data-luhm-pause]", function () {
      processCommand(state, "pause", "button");
    });
    $root.on("click" + eventNamespace, "[data-luhm-resume]", function () {
      processCommand(state, "resume", "button");
    });
    $root.on("click" + eventNamespace, "[data-luhm-exit]", function () {
      processCommand(state, "exit", "button");
    });
    $root.on("change" + eventNamespace, "[data-luhm-speaker-voice]", function () {
      const speakerId = String($(this).attr("data-luhm-speaker-voice") || "");
      if (!Object.prototype.hasOwnProperty.call(speakers, speakerId)) return;
      state.voiceMap[speakerId] = String($(this).val() || "");
      saveVoiceMap(state.voiceMap);
    });
    state.onVoicesChanged = function () { buildVoiceSelectors(state); };
    if (window.speechSynthesis && typeof window.speechSynthesis.addEventListener === "function") {
      window.speechSynthesis.addEventListener("voiceschanged", state.onVoicesChanged);
    }
  }

  const methods = {
    init: function () {
      return this.each(function () { init(this); });
    },
    state: function () {
      return this.length ? ((stateFor($(this[0])) || {}).mode || "OUTSIDE") : "OUTSIDE";
    },
    speak: function (turn) {
      return this.each(function () {
        const state = stateFor($(this));
        if (state && state.mode === "ACTIVE") speakTurn(state, turn);
      });
    },
    destroy: function () {
      return this.each(function () {
        const $root = $(this);
        const state = stateFor($root);
        if (!state) return;
        if (window.speechSynthesis) window.speechSynthesis.cancel();
        if (window.speechSynthesis && state.onVoicesChanged && typeof window.speechSynthesis.removeEventListener === "function") {
          window.speechSynthesis.removeEventListener("voiceschanged", state.onVoicesChanged);
        }
        $root.off(eventNamespace);
        $root.removeData(dataKey);
      });
    }
  };

  $.fn[pluginName] = function (method) {
    if (methods[method]) return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
    if (method == null || typeof method === "object") return methods.init.apply(this, arguments);
    $.error("Unknown " + pluginName + " method: " + method);
    return this;
  };
  $.fn[pluginName].version = "0.1.0-candidate";
  $.luhmVoiceCabinet = Object.freeze({
    parseCommand: parseCommand,
    normalizeTurn: normalizeTurn,
    speakers: speakers
  });
}(window.jQuery));
