/* LuHm-OS: Project Premonition · typed CAST intent adapter only.
 * Built alongside the accepted luhm.cockpit.js without modifying its fingerprint.
 * Python fnCastMatrix is the authority for the 4x4x4 request and release gates.
 */
(function ($) {
  "use strict";
  const stages = Object.freeze(["castTesting", "castProposed", "castBridge", "cast"]);
  const beats = Object.freeze(["hear", "resolve", "act", "verify"]);
  const tiers = Object.freeze(["technologyFastPath", "forFuckSake", "scorchedEarth", "finalForm"]);
  const aliases = Object.freeze({ castDev: "castTesting", devCast: "castTesting" });
  const canonicalStage = (value) =>
    Object.prototype.hasOwnProperty.call(aliases, value) ? aliases[value] : value;
  const validIdentity = (value) => typeof value === "string" && /^[a-z][A-Za-z0-9]{0,79}$/.test(value);

  $.fn.luhmCastIntent = function (request) {
    if (!request || typeof request !== "object") return this;
    const stage = canonicalStage(request.stage);
    const fromStage = request.fromStage == null ? null : canonicalStage(request.fromStage);
    const current = stages.indexOf(stage);
    const previous = fromStage == null ? -1 : stages.indexOf(fromStage);
    const validTransition = fromStage == null
      ? current === 0 : previous !== -1 && (current === previous || current === previous + 1);
    const validRequest = request.armed === true &&
      typeof request.sourceRef === "string" && /^[a-f0-9]{40}$/.test(request.sourceRef) &&
      validIdentity(request.taskId) && validIdentity(request.scopeId) &&
      validTransition && beats.includes(request.beat) && tiers.includes(request.tier);
    if (!validRequest) return this;
    return this.each(function () {
      const $root = $(this);
      if (!$root.data("luhmCockpit")) return;
      $root.trigger("luhm:cast:intent", [{
        schema: "luhmOs.castMatrixRequest.v1",
        product: "LuHm-OS", project: "Project Premonition",
        stage: stage, fromStage: fromStage,
        beat: request.beat, tier: request.tier,
        sourceRef: request.sourceRef, taskId: request.taskId, scopeId: request.scopeId,
        armed: true, authorityEffect: "none", pythonValidationRequired: true,
        buildDispatched: false, releasePublished: false, crownGranted: false
      }]);
    });
  };
  $.fn.luhmCastIntent.matrixSize = stages.length * beats.length * tiers.length;
}(jQuery));
