(function ($) {
  "use strict";
  const rooms = Object.freeze(["surface","sourceTruth","doctrine","receipts","memoryCrypt","contradictionVault","dependencyDepth","dungeonMap"]);
  const allowed = new Set(["professorIntent","workflowSummoned","oniEntered","vendorCapabilityResult","evidenceFound","memoryRecovered","contradictionFound","repairProposed","checkpoint","professorNeeded","workflowReleased","goalGap","boundedMutation","proofReceipt","softwareCandidate","professorGate","castReached","postCastPhysicalProof"]);
  function freezeList(value) { return Object.freeze(Array.isArray(value) ? value.slice() : []); }
  const roleplay = {
    emit(type, input) {
      if (!allowed.has(type)) throw new Error("unknown roleplay event");
      const data = input || {};
      const packet = Object.freeze({
        type,
        speaker:String(data.speaker || "System"),
        expression:String(data.expression || "neutral"),
        lines:freezeList(data.lines).slice(0,3),
        evidenceRefs:freezeList(data.evidenceRefs),
        machineState:String(data.machineState || "UNKNOWN"),
        authority:"presentationOnly",
        sourceRef:String(data.sourceRef || ""),
        gate:String(data.gate || "")
      });
      $(document).trigger("luhm:roleplay:event", [packet]);
      return packet;
    },
    dungeon(target) {
      const name=String(target || "").trim();
      if(!name) throw new Error("dungeon target required");
      return Object.freeze({target:name,rooms,depth:0,machineState:"UNKNOWN",presentationState:"entering"});
    }
  };
  $.codingRoleplay = Object.freeze(roleplay);
})(window.jQuery);
