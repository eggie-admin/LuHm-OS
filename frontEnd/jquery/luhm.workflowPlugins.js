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

  $.operationTitan7 = function (milestone, detail) {
    if (!String(milestone || "").trim()) throw new Error("operationTitan7 requires a milestone");
    const packet = envelope("operationTitan7", milestone, detail);
    $(document).trigger("luhm:workflow:operationTitan7", [packet]);
    return packet;
  };

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
