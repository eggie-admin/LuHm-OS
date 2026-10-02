(function ($) {
  "use strict";

  const rooms = Object.freeze(["surface","sourceTruth","doctrine","receipts","memoryCrypt","contradictionVault","dependencyDepth","dungeonMap"]);
  const allowed = new Set(["professorIntent","workflowSummoned","oniEntered","bossCapabilityRequest","vendorCapabilityResult","evidenceFound","memoryRecovered","contradictionFound","repairProposed","checkpoint","professorNeeded","workflowReleased","goalLoaded","goalGap","boundedMutation","proofReceipt","softwareCandidate","professorGate","castReached","postCastPhysicalProof"]);

  function freezeList(value) { return Object.freeze(Array.isArray(value) ? value.slice() : []); }

  $.codingRoleplay = Object.freeze({
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
        authority:String(data.authority || "presentationOnly"),
        goalState:String(data.goalState || "UNKNOWN"),
        proofClass:String(data.proofClass || ""),
        sourceRef:String(data.sourceRef || ""),
        gate:String(data.gate || ""),
        chaosSeed:String(data.chaosSeed || "0")
      });
      $(document).trigger("luhm:roleplay:event", [packet]);
      return packet;
    },
    dungeon(target) {
      const name=String(target || "").trim();
      if(!name) throw new Error("dungeon target required");
      return Object.freeze({
        target:name,
        rooms,
        depth:0,
        machineState:"UNKNOWN",
        presentationState:"entering"
      });
    },
    room(target, depth, state) {
      const index=Math.max(0,Math.min(rooms.length-1,Number(depth)||0));
      const packet=Object.freeze({
        target:String(target || ""),
        room:rooms[index],
        depth:index,
        depthMax:rooms.length-1,
        machineState:String(state || "UNKNOWN")
      });
      $(document).trigger("luhm:roleplay:dungeonRoom", [packet]);
      return packet;
    }
  });


  const goalStates = Object.freeze(["UNKNOWN","GAP","MUTATING","PROVING","SOFTWARE_CANDIDATE","PROFESSOR_GATE","CAST","POST_CAST_PHYSICAL_PROOF"]);

  $.codingRoleplay.goal = Object.freeze({
    states: goalStates,
    emit(state, input) {
      if (!goalStates.includes(state)) throw new Error("unknown goal state");
      const data = input || {};
      const map = {
        UNKNOWN:"checkpoint",
        GAP:"goalGap",
        MUTATING:"boundedMutation",
        PROVING:"proofReceipt",
        SOFTWARE_CANDIDATE:"softwareCandidate",
        PROFESSOR_GATE:"professorGate",
        CAST:"castReached",
        POST_CAST_PHYSICAL_PROOF:"postCastPhysicalProof"
      };
      if ((state === "PROVING" || state === "SOFTWARE_CANDIDATE" || state === "CAST") && !String(data.sourceRef || "").trim()) {
        throw new Error("evidence-bearing goal state requires sourceRef");
      }
      if (state === "PROVING" && !String(data.proofClass || "").trim()) {
        throw new Error("PROVING requires proofClass");
      }
      return $.codingRoleplay.emit(map[state], {
        speaker:data.speaker || "Lum",
        expression:data.expression || "working",
        lines:data.lines || [],
        evidenceRefs:data.evidenceRefs || [],
        machineState:data.machineState || state,
        authority:"presentationOnly",
        goalState:state,
        proofClass:data.proofClass || "",
        sourceRef:data.sourceRef || "",
        gate:state === "PROFESSOR_GATE" ? "ProfessorCrown" : (data.gate || ""),
        chaosSeed:data.chaosSeed || "0"
      });
    }
  });

  $(document).on("luhm:boss:capabilityRequest", function (_, packet) {
    $.codingRoleplay.emit("bossCapabilityRequest", {
      speaker:"Lum",
      expression:"working",
      lines:["Boss routing capability", packet.capability],
      machineState:"REQUESTED"
    });
  });

  $(document).on("luhm:boss:capabilityResult", function (_, packet) {
    $.codingRoleplay.emit("vendorCapabilityResult", {
      speaker:packet.provider,
      expression:packet.state === "GREEN" ? "ready" : "uncertain",
      lines:[packet.capability, packet.state],
      evidenceRefs:packet.evidenceRefs,
      machineState:packet.state
    });
  });
})(window.jQuery);
