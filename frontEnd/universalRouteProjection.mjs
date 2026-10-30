/* Universal read-only route-plan projection. No network, media, sensor or agent execution. */
const lanes=new Set(["nightly","beta","lts","legacy"]);
const routes=new Set(["currentRenderDirect","candidateCloudflareTunnel",
  "privateStudioLoopback","offlineFallback"]);
const capabilities=new Set(["sourceStatus","browserPreview","studioHardwareInventory","mediaPlan"]);
const roles=new Set(["lum","skuldResearch","tetsu","kaji","yume","belldandySecretary"]);
const fields=["schema","sourceRef","taskId","lane","transport","capability","proposedRole",
  "status","routeAvailable","workerExecuted","providerConnected","authorizedToMutate",
  "crownStatus","evidenceHash"];
export function validateUniversalRoute(receipt, sourceRef) {
  if(!receipt||typeof receipt!=="object"||Array.isArray(receipt)) throw Error("INVALID_RECEIPT");
  if(Object.keys(receipt).length!==fields.length||!fields.every(k=>Object.hasOwn(receipt,k)))
    throw Error("UNEXPECTED_FIELDS");
  if(receipt.schema!=="luhmOs.universalRoutePlan.v1"||
     !/^[a-f0-9]{40}$/.test(receipt.sourceRef)||receipt.sourceRef!==sourceRef)
    throw Error("SOURCE_REF_INVALID");
  if(!/^[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$/.test(receipt.taskId)||
     !lanes.has(receipt.lane)||!routes.has(receipt.transport)||
     !capabilities.has(receipt.capability)||!roles.has(receipt.proposedRole))
    throw Error("ROUTE_PARAMETERS_INVALID");
  if(receipt.status!=="SOURCE_ONLY"||receipt.routeAvailable!==false||
     receipt.workerExecuted!==false||receipt.providerConnected!==false||
     receipt.authorizedToMutate!==false||receipt.crownStatus!=="STOP"||
     !/^[a-f0-9]{64}$/.test(receipt.evidenceHash))
    throw Error("NO_RUNTIME_AUTHORITY");
  return Object.freeze({lane:receipt.lane,capability:receipt.capability,
    transport:receipt.transport,role:receipt.proposedRole,status:"SOURCE_ONLY"});
}
export function renderUniversalRoute(element,receipt,sourceRef) {
  const safe=validateUniversalRoute(receipt,sourceRef);
  if(!element||typeof element.textContent!=="string") throw Error("TEXT_CONTENT_ELEMENT_REQUIRED");
  element.textContent=safe.lane+" • "+safe.capability+" • "+safe.transport+
     " • "+safe.role+" (SOURCE ONLY; CROWN STOP)";
  return safe;
}
