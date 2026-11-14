/** Offline receipt verification, never uploads or runs the compiled bundle. */
import { createHash } from "node:crypto";
import { readFile, stat } from "node:fs/promises";
import { dirname, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const hash = data => createHash("sha256").update(data).digest("hex");
const receipt = JSON.parse(await readFile(resolve(root, "dist/luhm-os-bundle-receipt.json"), "utf8"));
if (receipt.schema !== "luhmOs.npmPluginBundleReceipt.v1" ||
    receipt.status !== "SOURCE_BUILD_NOT_CHATGPT_HOST_PROOF" ||
    receipt.displayName !== "LuHm-OS" || receipt.libraryApi !== "$.fn" ||
    receipt.jqueryVersion !== "3.7.1" || receipt.privateNpmPackage !== true ||
    receipt.outputName !== "luhm-os-jquery-ui.js" ||
    receipt.licenseFile !== "jquery-LICENSE.txt" ||
    !Array.isArray(receipt.inputs) || receipt.inputs.length !== 6 ||
    receipt.liveSitePluginMutated !== false || receipt.mcpServerReplaced !== false ||
    receipt.inChatUiMounted !== false || receipt.cloudflareCdnPublished !== false ||
    receipt.publishingApproved !== false || receipt.crownStatus !== "STOP") {
  throw new Error("RED_BUNDLE_RECEIPT_POLICY");
}
const licenseBytes = await readFile(resolve(root, "dist/jquery-LICENSE.txt"));
if (hash(licenseBytes) !== receipt.licenseSha256 ||
    !licenseBytes.toString("utf8").includes("Permission is hereby granted, free of charge")) {
  throw new Error("RED_JQUERY_LICENSE_RECEIPT");
}
const bundle = await readFile(resolve(root, "dist/luhm-os-jquery-ui.js"));
if (receipt.outputSha256 !== hash(bundle) || receipt.outputSizeBytes !== bundle.length) {
  throw new Error("RED_BUNDLE_HASH_OR_SIZE");
}
for (const item of receipt.inputs) {
  if (!item || typeof item.path !== "string" || !/^(vendor|jquery)\/|^app\.js$/.test(item.path) ||
      item.path.split("/").includes("..")) throw new Error("RED_INPUT_PATH");
  const full = resolve(root, item.path);
  if (!full.startsWith(root + sep)) throw new Error("RED_INPUT_ESCAPE");
  const input = await readFile(full);
  if (hash(input) !== item.sha256 || input.length !== item.sizeBytes) {
    throw new Error("RED_INPUT_DIGEST");
  }
}
if (!/^[a-f0-9]{64}$/.test(receipt.outputSha256) ||
    !(await stat(resolve(root, "dist/luhm-os-jquery-ui.js"))).isFile()) {
  throw new Error("RED_NOT_SHA256");
}
console.log("GREEN_SOURCE_ONLY_LUHM_OS_BUNDLE_6_SHA256_INPUTS_AND_OUTPUT");
