/**
 * LuHm-OS machine CAST hex bridge. Presentation/intent-only ES module.
 * 0x43415354 = ASCII 'CAST' (display notation); 0xC1 = candidate command ID.
 * No fetch(), SQL, eval, dynamic plugin loads, implicit installation, CAST dispatch.
 */
export const luhmCastHexIdentity = Object.freeze({
  displayName:"LuHm-OS", machineNamespace:"luhmOs",
  asciiHex:"43415354", opcode:"0xC1", commandName:"castIntent",
  eventName:"luhm:cast:intent", approval:"NONE"
});

const stages = Object.freeze(["castTesting","castProposed","castBridge","cast"]);
const beats = Object.freeze(["hear","resolve","act","verify"]);
const tiers = Object.freeze(["technologyFastPath","forFuckSake","scorchedEarth","finalForm"]);
const nameRe = /^[a-z][A-Za-z0-9]{0,79}$/;
const shaRe = /^[0-9a-f]{40}$/;

export function decodeLuHmHexCommand(value) {
  if (value !== "0xC1") throw new TypeError("RED_UNKNOWN_EXACT_HEX_OPCODE");
  return Object.freeze({
    opcode:"0xC1",asciiHex:"43415354",command:"castIntent",
    effect:"INTENT_ONLY",dispatchAuthorized:false
  });
}

export function buildLuHmHexCastManifest({sourceRef,taskId="machineCastReview",
  scopeId="machineSql",beat="hear",tier="technologyFastPath"}={}) {
  if (typeof sourceRef !== "string" || !shaRe.test(sourceRef)) {
    throw new TypeError("RED_EXACT_SOURCE_REQUIRED");
  }
  if (![taskId,scopeId].every(x => typeof x === "string" && nameRe.test(x))) {
    throw new TypeError("RED_BOUNDED_TASK_SCOPE_REQUIRED");
  }
  if (!beats.includes(beat) || !tiers.includes(tier)) {
    throw new TypeError("RED_CANON_COORDINATE_REQUIRED");
  }
  const opcode = decodeLuHmHexCommand("0xC1");
  // Fresh instances; no authority-bearing shared mutable references.
  return {
    schema:"luhmOs.aiTaskManifest.v2", status:"SOURCE_CANDIDATE",
    providerId:"luhmOsLocal", capabilityId:"machineCastBridge",
    taskId, sourceRef, scopeId, inputRefs:[],
    requiredOutputSchema:"luhmOs.machineCastHexBridgeReceipt.v1",
    budget:{maxRequests:1,maxParallel:1,maxPasses:1},
    stopConditions:["scopeComplete","evidenceConflict","sourceMismatch","budgetExhausted"],
    authority:{mutation:false,green:false,crown:false},
    responseRequired:["providerId","taskId","sourceRef","scopeId","responseId",
      "outputRefs","claims","timestamp"],
    machineBridge:{
      schema:"luhmOs.machineCastHexBridgeIntent.v1",
      displayName:luhmCastHexIdentity.displayName,
      asciiHex:opcode.asciiHex, opcode:opcode.opcode,
      mode:"inspectCandidate",fromStage:stages[1],stage:stages[2],
      beat,tier,dispatchAuthorized:false,machineSqlWritable:false
    }
  };
}

export function getLuHmHexCastIntent(packet) {
  if (packet === null || typeof packet !== "object" || Array.isArray(packet) ||
      Object.keys(packet).some(x => !["sourceRef","taskId","scopeId","beat","tier"].includes(x))) {
    throw new TypeError("RED_UNKNOWN_CAST_INPUT");
  }
  const manifest=buildLuHmHexCastManifest(packet);
  return {schema:"luhmOs.machineHexCastJsIntent.v1",
    status:"CANDIDATE_ONLY_PYTHON_REVALIDATION_REQUIRED",
    opcode:"0xC1",manifest,sourceBound:"NOT_SERVER_VALIDATED",
    dispatchAuthorized:false,sqlWritable:false,crownGranted:false};
}
