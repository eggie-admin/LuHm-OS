(function ($) {
  "use strict";

  const registry = Object.freeze({
    operationTitan7: {
      trigger: "explicitOperationInvocation",
      mode: "specialCase",
      defaultWorkflow: false
    },
    deepDungeon: {
      trigger: "humanRecoveryIntent",
      mode: "oniMiniAgentOnly",
      defaultWorkflow: false
    }
  });

  function envelope(name, milestone, detail) {
    return Object.freeze({
      plugin: name,
      milestone: String(milestone || "").trim(),
      detail: Object.freeze(Object.assign({}, detail || {})),
      authority: "Professor",
      state: "invoked"
    });
  }

  const titan7TierPatterns = Object.freeze([
    Object.freeze({tier:"ffs", pattern:/^(?:ffs!|for fuck sake!)$/i}),
    Object.freeze({tier:"scorchedEarth", pattern:/^scorched earth$/i}),
    Object.freeze({tier:"finalForm", pattern:/^final form$/i})
  ]);

  function operationTitan7Intent(text) {
    const source = String(text || "").trim();
    for (const item of titan7TierPatterns) {
      if (item.pattern.test(source)) {
        return Object.freeze({matched:true, tier:item.tier, source});
      }
    }
    return Object.freeze({matched:false, tier:"", source});
  }

  $.operationTitan7Intent = operationTitan7Intent;

  $.operationTitan7 = function (milestone, detail) {
    const target = String(milestone || "").trim();
    if (!target) throw new Error("operationTitan7 requires a milestone");

    const payload = Object.assign({}, detail || {});
    if (payload.phrase && !payload.tier) {
      const intent = operationTitan7Intent(payload.phrase);
      if (intent.matched) payload.tier = intent.tier;
    }

    const packet = envelope("operationTitan7", target, payload);
    $(document).trigger("luhm:workflow:operationTitan7", [packet]);
    return packet;
  };

  const deepDungeonPatterns = Object.freeze([
    /where(?:'s| is) my\s+(.+)/i,
    /what happened (?:to|with) my\s+(.+)/i,
    /where did we leave\s+(.+)/i,
    /where were we with\s+(.+)/i,
    /what became of my\s+(.+)/i,
    /find my current\s+(.+)/i,
    /what(?:'s| is) the status of my\s+(.+)/i
  ]);

  function deepDungeonIntent(text) {
    const source = String(text || "").trim();
    for (const pattern of deepDungeonPatterns) {
      const match = source.match(pattern);
      if (match && String(match[1] || "").trim()) {
        return Object.freeze({
          matched:true,
          target:String(match[1]).trim(),
          source
        });
      }
    }
    return Object.freeze({matched:false, target:"", source});
  }

  $.deepDungeonIntent = deepDungeonIntent;

  $.deepDungeon = function (milestone, detail) {
    const target = String(milestone || "").trim();
    if (!target) throw new Error("deepDungeon requires the Professor milestone");
    const packet = envelope("deepDungeon", target, detail);
    $(document).trigger("luhm:workflow:deepDungeon", [packet]);
    return packet;
  };

  $.luhmWorkflowPlugins = Object.freeze({
    registry,
    release(name, receipt) {
      if (!registry[name]) throw new Error("unknown workflow plugin");
      const packet = Object.freeze({
        plugin:name,
        receipt:Object.freeze(Object.assign({}, receipt || {})),
        state:"released"
      });
      $(document).trigger("luhm:workflow:released", [packet]);
      return packet;
    }
  });
})(window.jQuery);
