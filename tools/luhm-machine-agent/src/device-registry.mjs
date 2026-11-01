/** Zero-dependency binary/registry and session GUI utilities; no OS registry writes. */
import { createHash, timingSafeEqual } from "node:crypto";

export const namespace="deviceCapability";
export const platformIds=Object.freeze(["android","samsung","ios","webLinux"]);
export const capabilityIds=Object.freeze(["runtime","graphics","storage","distribution"]);
export const hexIds=Object.freeze(Array.from({length:16},(_,i)=>"0x"+i.toString(16).toUpperCase().padStart(2,"0")));
import {orderedActions} from "./workflow-rank.mjs";
export {orderedActions,initialCounts,sortActions,selectAction} from "./workflow-rank.mjs";
const fields=Object.freeze(["schema","registryHex","kind","byteCount","payloadBase64","sha256","rssBytes","rightsState"]);
const encoder=new TextEncoder();
const allowedKinds=["artNote","buildReceipt","benchmarkReceipt"];
const lowerHex=/^[0-9a-f]{64}$/;
const base64Pattern=/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/;
function fail(why){throw new Error("RED_"+why);}
function need(v,why){if(!v)fail(why);}
function isUInt(v){return typeof v==="number"&&Number.isSafeInteger(v)&&v>=0;}
export function checkRegistry(p){
  need(p && typeof p==="object" && !Array.isArray(p) &&
    p.schema==="luhmOs.deviceCapabilityRegistry.v1" && p.namespace===namespace &&
    p.authority==="Professor" && p.status==="DRAFT_SOURCE_ONLY" &&
    p.crownStatus==="STOP","REGISTRY_AUTHORITY");
  need(JSON.stringify(p.platforms)===JSON.stringify(platformIds) &&
       JSON.stringify(p.capabilities)===JSON.stringify(capabilityIds) &&
       Array.isArray(p.entries) && p.entries.length===16,"REGISTRY_MATRIX");
  for(let i=0;i<16;i++){
    const v=p.entries[i];
    need(v&&v.index===i&&v.hex===hexIds[i]&&v.namespace===namespace &&
      v.platform===platformIds[Math.floor(i/4)]&&v.capability===capabilityIds[i%4] &&
      v.proof==="SOURCE_REVIEW_ONLY"&&v.deviceVerified===false,"REGISTRY_HEX");
  }
  const q=p.typedPacket;
  need(q && q.schema==="luhmOs.typedArtMachinePacket.v1" &&
    q.maxUtf8Bytes===4096 && q.maxRawBase64Bytes===4096 &&
    q.hexNamespace===namespace && q.allowRssNull===true &&
    JSON.stringify(q.fields)===JSON.stringify(fields) &&
    JSON.stringify(q.kinds)===JSON.stringify(allowedKinds),"REGISTRY_PACKET");
  const gui=p.gui;
  need(gui && gui.policy==="SESSION_ONLY_NO_TELEMETRY" &&
    JSON.stringify(gui.defaultOrder)===JSON.stringify(orderedActions) &&
    gui.clearOnReload===true&&gui.userMayReset===true&&
    gui.disableBackgroundRecording===true &&
    gui.sort==="most selected session task first, descending count; ties preserve default order",
    "REGISTRY_GUI");
  for(const action of orderedActions){
    need(gui.activityCountInitial?.[action]===0 &&
      typeof gui.labels?.[action]==="string" && gui.labels[action].length>0,"REGISTRY_GUI_DEFAULT");
  }
  const g=p.sdkGates;
  need(g?.android?.targetSdk===36 && g.android.arm64===true &&
    g.android.check16KiBElfZipAlignment===true &&
    g.android.packageIdFromExportPreset==="art.eggiebagelface.luhmos.testing" &&
    g.samsung?.base==="Android SDK" && g.ios?.requiresMacOSXcodeForNative===true &&
    g.ios.iosBundleId==="UNREGISTERED" && g.web?.domFallback===true &&
    g.web.unrealRemote==="DISABLED","REGISTRY_SDK");
  const v=p.vendorUpdates;
  need(v?.doNotAutoUpgradeGradle===true&&v.doNotChangeSigningIdentity===true &&
    v.doNotAutoPublish===true&&v.proprietaryModulesMustNotBeCopiedIntoOpenCore===true,
    "REGISTRY_VENDOR");
  const safety=p.safety||{};
  need(safety.sourceOnly===true &&
    ["realPhysicalDeviceVerified","iosBuildSigned","galaxyStoreBuildUploaded",
      "playStoreBuildUploaded","localAiInferenceRunning","remoteAiAgentActivated",
      "unrealGpuServerActive","protectedRegistryWritten","kernelModified"]
      .every(k=>safety[k]===false),"REGISTRY_PROTECTED");
  need(JSON.stringify(p.releaseGates)===JSON.stringify([
    "typedJsPythonSQLiteParity","sourceOnlyCICheck","realDeviceCapabilities","rightsAndLicenseReview",
    "androidNative16KiBArtifactCheck","signedArtifactAndUpdateIdentity",
    "storeOwnerAuthorization","humanApproval"]),"REGISTRY_RELEASE_GATES");
  return true;
}
function checkedUtf8(value){
  need(typeof value==="string"&&value.length>0 && value===value.normalize("NFC") &&
    !/[\uD800-\uDFFF]/u.test(value) && !/[\u0000-\u0008\u000B-\u001F\u007F]/u.test(value),
    "TEXT_CANONICAL");
  const bytes=encoder.encode(value);
  need(bytes.length>0&&bytes.length<=4096,"TEXT_BYTES");
  return Buffer.from(bytes);
}
function checkedRss(n){need(n===null||isUInt(n),"RSS_BYTES");return n;}
export function encodePacket(value, options={}){
  const raw=checkedUtf8(value);
  const hex=options.registryHex??"0x00",kind=options.kind??"artNote",rss=checkedRss(options.rssBytes??null);
  need(hexIds.includes(hex),"HEX_NAMESPACE");
  need(allowedKinds.includes(kind),"PACKET_KIND");
  return {schema:"luhmOs.typedArtMachinePacket.v1",registryHex:hex,kind,
    byteCount:raw.byteLength,payloadBase64:raw.toString("base64"),
    sha256:createHash("sha256").update(raw).digest("hex"),
    rssBytes:rss,rightsState:"LOCAL_DRAFT"};
}
export function decodePacket(p){
  need(p&&typeof p==="object"&&!Array.isArray(p) &&
    Object.keys(p).sort().join(",")===fields.slice().sort().join(",") &&
    p.schema==="luhmOs.typedArtMachinePacket.v1" &&
    hexIds.includes(p.registryHex) && allowedKinds.includes(p.kind) &&
    isUInt(p.byteCount) && p.byteCount>=1 && p.byteCount<=4096 &&
    typeof p.payloadBase64==="string" && p.payloadBase64.length<=5464 &&
    base64Pattern.test(p.payloadBase64) &&
    typeof p.sha256==="string" && lowerHex.test(p.sha256) &&
    p.rightsState==="LOCAL_DRAFT","PACKET_SHAPE");
  checkedRss(p.rssBytes);
  const raw=Buffer.from(p.payloadBase64,"base64");
  need(raw.length===p.byteCount&&raw.length<=4096&&
    raw.toString("base64")===p.payloadBase64,"BASE64_LENGTH_CANONICAL");
  const hash=Buffer.from(createHash("sha256").update(raw).digest("hex"),"hex");
  need(timingSafeEqual(hash,Buffer.from(p.sha256,"hex")),"PACKET_HASH");
  const text=new TextDecoder("utf-8",{fatal:true}).decode(raw);
  need(checkedUtf8(text).equals(raw),"PACKET_UTF8");
  return {value:text,registryHex:p.registryHex,kind:p.kind,byteCount:raw.length,
    sha256:p.sha256,rssBytes:p.rssBytes,rightsState:p.rightsState};
}
