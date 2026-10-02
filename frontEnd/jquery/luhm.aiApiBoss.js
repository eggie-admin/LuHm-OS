(function ($) {
  "use strict";

  const providers = Object.freeze({
    openAi: ["reasoning","responses","toolUse","remoteMcp"],
    googleBigBrother: ["research","realtime","creativeTooling","review"],
    huggingFace: ["modelResearch","conditionalCritic","modelCompatibility"],
    ollamaLocal: ["privateInference","planDrafting"]
  });

  function requireText(value, name) {
    const out = String(value || "").trim();
    if (!out) throw new Error("aiApiBoss requires " + name);
    return out;
  }

  $.aiApiBoss = Object.freeze({
    providers,
    request(input) {
      const packet = Object.freeze({
        requestId: requireText(input && input.requestId, "requestId"),
        workflowPlugin: requireText(input && input.workflowPlugin, "workflowPlugin"),
        agentSkill: requireText(input && input.agentSkill, "agentSkill"),
        capability: requireText(input && input.capability, "capability"),
        sourceRef: requireText(input && input.sourceRef, "sourceRef"),
        scope: Object.freeze((input && input.scope) || {}),
        authorityClass: requireText(input && input.authorityClass, "authorityClass"),
        evidenceRequired: Object.freeze((input && input.evidenceRequired) || []),
        stopConditions: Object.freeze((input && input.stopConditions) || [])
      });
      $(document).trigger("luhm:boss:capabilityRequest", [packet]);
      return packet;
    },
    receive(result) {
      if (!result || !result.requestId || !result.provider || !result.capability) {
        throw new Error("aiApiBoss rejects malformed provider result");
      }
      const packet = Object.freeze({
        requestId:String(result.requestId),
        provider:String(result.provider),
        capability:String(result.capability),
        state:String(result.state || "UNKNOWN"),
        evidenceRefs:Object.freeze(result.evidenceRefs || []),
        unknowns:Object.freeze(result.unknowns || []),
        resultRef:result.resultRef ? String(result.resultRef) : ""
      });
      $(document).trigger("luhm:boss:capabilityResult", [packet]);
      return packet;
    }
  });
})(window.jQuery);
