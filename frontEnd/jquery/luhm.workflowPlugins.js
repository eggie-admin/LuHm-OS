(function ($) {
  "use strict";

  const registry = Object.freeze({
    operationTitan7: {
      trigger: "explicitOperationInvocation",
      mode: "specialCase",
      defaultWorkflow: false
    },
    deepDungeon: {
      trigger: "whereIsMyMilestonePhrase",
      mode: "miniAgentOnly",
      defaultWorkflow: false
    }
  });

  function envelope(name, milestone, detail) {
    return Object.freeze({
      plugin: name,
      milestone: String(milestone || "").trim(),
      detail: detail || {},
      authority: "Professor",
      state: "invoked"
    });
  }

  const titan7TierPatterns = Object.freeze([
    {tier:"ffs", pattern:/^(?:ffs!|for fuck sake!)$/i},
    {tier:"scorchedEarth", pattern:/^scorched earth$/i},
    {tier:"finalForm", pattern:/^final form$/i}
  ]);

  function operationTitan7Intent(text) {
    const source=String(text || "").trim();
    for (const item of titan7TierPatterns) {
      if (item.pattern.test(source)) return Object.freeze({matched:true,tier:item.tier,source});
    }
    return Object.freeze({matched:false,tier:"",source});
  }

  $.operationTitan7Intent = operationTitan7Intent;

  $.operationTitan7 = function (milestone, detail) {
    if (!String(milestone || "").trim()) throw new Error("operationTitan7 requires a milestone");
    const payload=Object.assign({}, detail || {});\n    if (payload.phrase && !payload.tier) {\n      const intent=operationTitan7Intent(payload.phrase);\n      if (intent.matched) payload.tier=intent.tier;\n    }\n    const packet = envelope("operationTitan7", milestone, payload);
    $(document).trigger("luhm:workflow:operationTitan7", [packet]);
    return packet;
  };

  const deepDungeonPatterns = [
    /where(?:'s| is) my\s+(.+)/i,
    /what happened (?:to|with) my\s+(.+)/i,
    /where did we leave\s+(.+)/i,
    /where were we with\s+(.+)/i,
    /what became of my\s+(.+)/i,
    /find my current\s+(.+)/i,
    /what(?:'s| is) the status of my\s+(.+)/i
  ];

  function deepDungeonIntent(text) {
    const source = String(text || "").trim();
    for (const pattern of deepDungeonPatterns) {
      const match = source.match(pattern);
      if (match && String(match[1] || "").trim()) {
        return Object.freeze({matched:true, target:String(match[1]).trim(), source});
      }
    }
    return Object.freeze({matched:false, target:"", source});
  }

  $.deepDungeonIntent = deepDungeonIntent;

  $.deepDungeon = function (milestone, detail) {
    if (!String(milestone || "").trim()) throw new Error("deepDungeon requires the Professor milestone");
    const packet = envelope("deepDungeon", milestone, detail);
    $(document).trigger("luhm:workflow:deepDungeon", [packet]);
    return packet;
  };

  $.luhmWorkflowPlugins = Object.freeze({
    registry,
    release(name, receipt) {
      if (!registry[name]) throw new Error("unknown workflow plugin");
      const packet = Object.freeze({plugin:name, receipt:receipt || {}, state:"released"});
      $(document).trigger("luhm:workflow:released", [packet]);
      return packet;
    }
  });
})(window.jQuery);
