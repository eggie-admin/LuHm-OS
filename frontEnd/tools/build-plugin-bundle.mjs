/** Deterministic, offline LuHm-OS jQuery bundle for a future approved MCP UI resource.
 *  npm runs this locally after staging the exact jquery@3.7.1 lockfile entry.
 *  Not a ChatGPT Site editor, not a public npm release, not an executable update feed.
 */
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { createHash } from "node:crypto";
import { dirname, resolve, relative, sep } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "..");
const dest = resolve(root, "dist");
const sha = (text) => createHash("sha256").update(text).digest("hex");
const packageInfo = JSON.parse(await readFile(resolve(root, "package.json"), "utf8"));
const lockInfo = JSON.parse(await readFile(resolve(root, "package-lock.json"), "utf8"));
const exactVersion = "3.7.1";
if (packageInfo.private !== true || packageInfo.dependencies?.jquery !== exactVersion ||
    lockInfo.packages?.["node_modules/jquery"]?.version !== exactVersion ||
    lockInfo.packages?.[""]?.dependencies?.jquery !== exactVersion ||
    !String(lockInfo.packages?.["node_modules/jquery"]?.integrity || "").startsWith("sha512-")) {
  throw new Error("RED_NPM_LOCK_MISMATCH");
}
const sources = [
  "vendor/jquery-3.7.1.min.js",
  "jquery/luhm.codingRoleplay.js",
  "jquery/luhm.parallax.js",
  "jquery/luhm.cockpit.js",
  "jquery/luhm.cast.js",
  "app.js"
];
const inputs = [];
for (const p of sources) {
  const full = resolve(root, p);
  if (relative(root, full).startsWith("..") || !full.startsWith(root + sep)) {
    throw new Error("RED_BUNDLE_PATH_ESCAPE");
  }
  const bytes = await readFile(full);
  if (bytes.length < 20) throw new Error("RED_EMPTY_BUNDLE_INPUT");
  inputs.push({ path: p, bytes });
}
const license = await readFile(resolve(root, "vendor/jquery-LICENSE.txt"), "utf8");
if (!license.includes("Copyright OpenJS Foundation") ||
    !license.includes("Permission is hereby granted, free of charge") ||
    !license.includes('THE SOFTWARE IS PROVIDED "AS IS"')) {
  throw new Error("RED_MISSING_JQUERY_LICENSE");
}
const banner = "/* LuHm-OS source-only jQuery bundle. Private npm build, no runtime CDN. */\n";
const bundle = Buffer.concat([
  Buffer.from(banner),
  ...inputs.flatMap(({bytes}) => [bytes, Buffer.from("\n;\n")])
]);
const outputName = "luhm-os-jquery-ui.js";
const inventory = {
  schema: "luhmOs.npmPluginBundleReceipt.v1",
  status: "SOURCE_BUILD_NOT_CHATGPT_HOST_PROOF",
  displayName: "LuHm-OS",
  libraryApi: "$.fn",
  jqueryVersion: exactVersion,
  privateNpmPackage: true,
  outputName,
  outputSha256: sha(bundle),
  outputSizeBytes: bundle.length,
  inputs: inputs.map(({path,bytes}) => ({path,sha256:sha(bytes),sizeBytes:bytes.length})),
  license: "MIT-jquery+GPL-LuHm-source-compatibility-review-required",
  licenseFile: "jquery-LICENSE.txt",
  licenseSha256: sha(Buffer.from(license, "utf8")),
  liveSitePluginMutated: false,
  mcpServerReplaced: false,
  inChatUiMounted: false,
  cloudflareCdnPublished: false,
  publishingApproved: false,
  crownStatus: "STOP"
};
await mkdir(dest, {recursive:true});
await writeFile(resolve(dest, outputName), bundle);
await writeFile(resolve(dest, "jquery-LICENSE.txt"), license, "utf8");
await writeFile(resolve(dest, "luhm-os-bundle-receipt.json"), JSON.stringify(inventory, null, 2) + "\n", "utf8");
console.log(JSON.stringify({status:inventory.status, outputSha256:inventory.outputSha256,
  outputSizeBytes:inventory.outputSizeBytes, inputCount:inventory.inputs.length, crownStatus:"STOP"}));
