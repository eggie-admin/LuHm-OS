(function ($) {
  "use strict";

  const rooms = Object.freeze(["surface","sourceTruth","doctrine","receipts","memoryCrypt","contradictionVault","dependencyDepth","dungeonMap"]);
  const allowed = new Set(["professorIntent","workflowSummoned","oniEntered","bossCapabilityRequest","vendorCapabilityResult","evidenceFound","memoryRecovered","contradictionFound","repairProposed","checkpoint","professorNeeded","workflowReleased"]);

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
