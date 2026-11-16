/** Fixed-width hardware hex keys, never a firmware accessor or permission. */
import { readFileSync } from "node:fs";
const policy = JSON.parse(readFileSync(
  new URL("../../../doctrine/machineFourArchitectureForgeV1.json", import.meta.url),
  "utf8"));
const ARCH = Object.freeze(["x86_64","aarch64","riscv64","ppc64le"]);
const LAYERS = Object.freeze(["isaCpu","firmwareBoot","memoryIo","acceleratorAi"]);
const HEX = /^[0-9a-f]+$/;
const RAM = /^(0|[1-9][0-9]{0,18})$/;
const MAXRAM = 9223372036854775807n;

function validatePolicy() {
  if (policy.schema !== "luhmOs.machineFourArchitectureForge.v1"
    || JSON.stringify(policy.fourArchitectureFamilies.map(x=>x.id)) !== JSON.stringify(ARCH)
    || JSON.stringify(policy.fourMachineLayers.map(x=>x.id)) !== JSON.stringify(LAYERS)
    || policy.firmwareRules.noFlash !== true
    || policy.patchLane.noRealPatchApplication !== true
    || policy.crownStatus !== "STOP") throw new TypeError("RED_MACHINE_CANON");
}
validatePolicy();

export function normalizeHardwareHex(kind, input) {
  const rule = policy.sort.fixedHexNormalization[kind];
  if (!rule || typeof kind !== "string") throw new TypeError("RED_HEX_KIND");
  const digits = rule.digits;
  let numeric;
  if (typeof input === "string") {
    if (!HEX.test(input) || input.length > digits
      || ((kind === "sourceRef" || kind === "artifactSha256") && input.length !== digits)) {
      throw new TypeError("RED_HEX_INPUT");
    }
    numeric = BigInt("0x" + input);
  } else if (typeof input === "number"
    && Number.isSafeInteger(input) && input >= 0
    && kind !== "sourceRef" && kind !== "artifactSha256") {
    numeric = BigInt(input);
  } else {
    throw new TypeError("RED_HEX_INPUT");
  }
  if (numeric >= (1n << BigInt(rule.bits))) throw new TypeError("RED_HEX_WIDTH");
  const hex = numeric.toString(16).padStart(digits,"0");
  return Object.freeze({
    kind, valueHex: hex, sortKey: kind + ":" + hex,
    widthBits: rule.bits, byteOrder: rule.byteOrder,
    hardwareVerified: false, authorityGranted: false,
  });
}

export function sortHexKeys(items) {
  if (!Array.isArray(items) || items.length > 1000 || items.length < 1) {
    throw new TypeError("RED_HEX_SORT_ITEMS");
  }
  const values = items.map(x => {
    if (!x || typeof x !== "object" || Array.isArray(x)) throw new TypeError("RED_HEX_SORT_ITEM");
    return normalizeHardwareHex(x.kind,x.value);
  });
  if (new Set(values.map(x => x.kind)).size !== 1) {
    throw new TypeError("RED_HEX_CROSS_BUS_COMPARISON");
  }
  return values.sort((a,b)=>a.valueHex.localeCompare(b.valueHex));
}

export function machineSortPlan({architecture, layer, ramBytesDecimal, busKind, busHex}) {
  const ai = ARCH.indexOf(architecture), li = LAYERS.indexOf(layer);
  if (ai < 0 || li < 0) throw new TypeError("RED_MACHINE_ARCH_LAYER");
  if (typeof ramBytesDecimal !== "string" || !RAM.test(ramBytesDecimal)
    || BigInt(ramBytesDecimal) > MAXRAM) throw new TypeError("RED_MACHINE_RAM");
  if (!["usbVendorId","usbProductId","pciVendorId","pciDeviceId"].includes(busKind)) {
    throw new TypeError("RED_MACHINE_BUS");
  }
  return {
    architecture, layer, machineSortOrdinal: ai*4+li,
    ramBytesDecimal, deviceId: normalizeHardwareHex(busKind,busHex),
    stage:"HOLD_HARDWARE_AND_VENDOR_APPROVAL",
    physicalMachineProven:false, firmwareWritable:false, gpuOrNpuProven:false,
    sourceOnly:true, authorityGranted:false,
  };
}
