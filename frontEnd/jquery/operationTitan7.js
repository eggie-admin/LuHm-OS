(function ($) {
  "use strict";
  const pluginName = "operationTitan7";
  const invokeEvent = "luhm:operationTitan7:invoke";
  const commands = new Set(["saneApproach","dryRun","update","upgrade","distro","apply","continue","continueAll","exit","quit"]);
  const tiers = new Set(["forFuckSake","scorchedEarth","finalForm"]);

  function normalize(value) {
    return String(value || "").toLocaleLowerCase("en-US").replace(/[^a-z0-9]+/g, " ").trim();
  }

  function parse(text) {
    const n = normalize(text);
    if (!/(^| )operation titan (7|seven)( |$)|(^| )operationtitan7( |$)/.test(n)) return null;

    let escalation = "forFuckSake";
    if (n.includes("final form")) escalation = "finalForm";
    else if (n.includes("scorched earth")) escalation = "scorchedEarth";
    else if (n.includes("ffs") || n.includes("for fuck s sake") || n.includes("for fucks sake")) escalation = "forFuckSake";

    let command = "dryRun";
    if (n.includes("continue all")) command = "continueAll";
    else if (n.includes("dry run")) command = "dryRun";
    else for (const candidate of ["saneApproach","update","upgrade","distro","apply","continue","exit","quit"]) {
      if (n.includes(normalize(candidate))) { command = candidate; break; }
    }
    return { command, options:{ escalation } };
  }

  function invoke($root, command, options) {
    if (!commands.has(command)) $.error("Unknown operationTitan7 command: " + command);
    const settings = $.extend({ escalation:"forFuckSake", dryRun:command === "dryRun" }, options || {});
    if (!tiers.has(settings.escalation)) $.error("Unknown operationTitan7 escalation: " + settings.escalation);
    const manifest = {
      schema:"luhmOs.operationTitan7Invocation.v1",
      command,
      escalation:settings.escalation,
      authorityClass:settings.dryRun ? "READ_ONLY" : "PLAN_ONLY",
      stopConditions:["RED","UNKNOWN","CROWN_STOP"],
      requiredOutputs:["receipt","inspiredMutation"]
    };
    const wire = $.luhmManifestMin ? $.luhmManifestMin.compact(manifest) : manifest;
    $root.trigger(invokeEvent, [{ manifest, wire }]);
    return true;
  }

  $.fn[pluginName] = function (command, options) {
    return this.each(function () { invoke($(this), command, options); });
  };
  $.fn[pluginName].parse = parse;
  $.fn[pluginName].commands = Object.freeze(Array.from(commands));
  $.fn[pluginName].tiers = Object.freeze(Array.from(tiers));
}(jQuery));
