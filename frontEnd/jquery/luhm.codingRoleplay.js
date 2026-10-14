(function ($) {
  "use strict";

  const fallbackRooms = Object.freeze(["surface","sourceTruth","doctrine","receipts","memoryCrypt","contradictionVault","dependencyDepth","dungeonMap"]);
  const fallbackEvents = Object.freeze(["professorIntent","workflowSummoned","oniEntered","vendorCapabilityResult","evidenceFound","memoryRecovered","contradictionFound","repairProposed","checkpoint","professorNeeded","workflowReleased","goalGap","boundedMutation","proofReceipt","softwareCandidate","professorGate","castReached","postCastPhysicalProof"]);

  const fallbackProposed = Object.freeze({
    id: "proposed",
    installMode: "virginInstall",
    betaAcceptanceRequired: false,
    releaseAcceptanceRequired: false,
    autoBuildActive: false,
    authority: "presentationOnly",
    prototypeAccept: Object.freeze(["compileOrRunFromKnownSource", "captureFailureOrSmokeReceipt", "retainSourceIdentity"])
  });

  let contractState = {
    schema: "builtInCompatibility",
    configured: false,
    sourceRef: "",
    rooms: fallbackRooms,
    allowed: new Set(fallbackEvents),
    proposed: fallbackProposed
  };

  function freezeList(value) {
    return Object.freeze(Array.isArray(value) ? value.slice() : []);
  }

  function configure(contract, sourceRef) {
    const value = contract || {};
    if (value.schema !== "luhmOs.codingRoleplayDirector.v2") {
      throw new Error("coding roleplay doctrine schema required");
    }

    const eventSpine = Array.isArray(value.eventSpine) ? value.eventSpine.filter(Boolean) : [];
    const roomList = Array.isArray(value.deepDungeonPresentation?.rooms) ? value.deepDungeonPresentation.rooms.filter(Boolean) : [];
    const bubbleLaw = value.bubbleLaw || {};
    const modeRouting = value.modeRouting || {};
    const proposed = value.proposedLane || {};

    if (eventSpine.length === 0 || roomList.length === 0) {
      throw new Error("coding roleplay doctrine is incomplete");
    }
    if (bubbleLaw.bubbleCannotEstablishGreen !== true || bubbleLaw.roleplayCannotRewriteEvidence !== true || bubbleLaw.roleplayCannotAdvanceGoalState !== true) {
      throw new Error("coding roleplay authority boundary drift");
    }
    if (modeRouting.defaultMode !== "normalChat" || modeRouting.explicitSceneEntryRequired !== true) {
      throw new Error("coding roleplay mode boundary drift");
    }

    if (proposed.id !== "proposed" || proposed.installMode !== "virginInstall" || proposed.priorPluginStateRequired !== false ||
        proposed.betaAcceptanceRequired !== false || proposed.releaseAcceptanceRequired !== false || proposed.autoBuildActive !== false ||
        proposed.authority !== "presentationOnly" || !Array.isArray(proposed.prototypeAccept) ||
        proposed.prototypeAccept.join("|") !== fallbackProposed.prototypeAccept.join("|")) {
      throw new Error("proposed virgin-install lane contract drift");
    }

    contractState = {
      schema: value.schema,
      configured: true,
      sourceRef: String(sourceRef || ""),
      rooms: Object.freeze(roomList.slice()),
      allowed: new Set(eventSpine),
      proposed: Object.freeze({ ...proposed, prototypeAccept: freezeList(proposed.prototypeAccept) })
    };

    const receipt = Object.freeze({
      schema: contractState.schema,
      configured: true,
      sourceRef: contractState.sourceRef,
      eventCount: contractState.allowed.size,
      roomCount: contractState.rooms.length,
      authority: "presentationOnly"
    });
    $(document).trigger("luhm:roleplay:configured", [receipt]);
    return receipt;
  }

  function emit(type, input) {
    if (contractState.allowed.has(type) === false) {
      throw new Error("unknown roleplay event");
    }
    const data = input || {};
    const packet = Object.freeze({
      type: String(type),
      speaker: String(data.speaker || "System"),
      expression: String(data.expression || "neutral"),
      lines: freezeList(data.lines).slice(0, 3),
      evidenceRefs: freezeList(data.evidenceRefs),
      machineState: String(data.machineState || "UNKNOWN"),
      authority: "presentationOnly",
      sourceRef: String(data.sourceRef || contractState.sourceRef || ""),
      gate: String(data.gate || ""),
      contractSchema: contractState.schema,
      doctrineConfigured: contractState.configured
    });
    $(document).trigger("luhm:roleplay:event", [packet]);
    return packet;
  }

  function dungeon(target) {
    const name = String(target || "").trim();
    if (name.length === 0) {
      throw new Error("dungeon target required");
    }
    return Object.freeze({
      target: name,
      rooms: contractState.rooms,
      depth: 0,
      machineState: "UNKNOWN",
      presentationState: "entering",
      authority: "presentationOnly"
    });
  }

  function status() {
    return Object.freeze({
      schema: contractState.schema,
      configured: contractState.configured,
      sourceRef: contractState.sourceRef,
      eventCount: contractState.allowed.size,
      roomCount: contractState.rooms.length,
      authority: "presentationOnly"
    });
  }

  function proposedLane() {
    return Object.freeze({
      ...contractState.proposed,
      sourceRef: contractState.sourceRef,
      machineState: "UNKNOWN",
      roleplayAuthority: "presentationOnly"
    });
  }

  const roleplay = Object.freeze({ configure, emit, dungeon, status, proposedLane });
  $.codingRoleplay = roleplay;

  $(document).on("luhm:roleplay:configure", function (_event, contract, sourceRef) {
    roleplay.configure(contract, sourceRef);
  });

  if (window.LuHmRoleplayContract && typeof window.LuHmRoleplayContract === "object") {
    roleplay.configure(window.LuHmRoleplayContract, window.LuHmRoleplaySourceRef || "");
  }
})(window.jQuery);
