/* First-party HTML5 display adapter. No provider/network/device/agent execution. */
const modes = new Set(["headless","witchingHour","corporate","githubDevelopment"]);
const safeRef = /^[0-9a-f]{40}$/;
const safeId = /^[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$/;
export function validateForgeProjection(data, expectedSourceRef) {
  if (!data || typeof data !== "object" || Array.isArray(data)) throw Error("OBJECT_REQUIRED");
  const required = ["schema","sourceRef","taskId","scopeId","mode","tier","sql",
    "workerExecuted","providerConnected","authorityEffect","crownStatus","evidenceHash"];
  if (Object.keys(data).length !== required.length ||
      !required.every(k => Object.prototype.hasOwnProperty.call(data,k))) throw Error("PROJECTION_FIELDS");
  if (data.schema !== "luhmOs.forgeSourceProjection.v1" ||
      !safeRef.test(data.sourceRef) || data.sourceRef !== expectedSourceRef) throw Error("SOURCE_MISMATCH");
  if (!safeId.test(data.taskId) || !safeId.test(data.scopeId)) throw Error("INVALID_ID");
  if (!modes.has(data.mode) || !Number.isInteger(data.tier) || data.tier < 0 || data.tier > 3) throw Error("INVALID_TIER");
  if (data.sql !== "SQLITE_STRICT_JSON1_GREEN" || data.workerExecuted !== false ||
      data.providerConnected !== false || data.authorityEffect !== "none" ||
      data.crownStatus !== "STOP" || !/^[a-f0-9]{64}$/.test(data.evidenceHash)) throw Error("AUTHORITY_OR_EVIDENCE_MISMATCH");
  return Object.freeze({mode:data.mode,tier:data.tier,taskId:data.taskId,
    sourceRef:data.sourceRef,status:"SOURCE_ONLY"});
}
export function showForgeProjection(element, data, expectedSourceRef) {
  const projection=validateForgeProjection(data,expectedSourceRef);
  if (!element || typeof element.textContent !== "string") throw Error("TEXT_ELEMENT_REQUIRED");
  element.textContent="Forge " + projection.mode + " | tier " + projection.tier +
    " | source-only; CROWN STOP";
  return projection;
}
