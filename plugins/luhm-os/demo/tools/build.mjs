import { copyFile, mkdir, readFile, writeFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { gzipSync } from "node:zlib";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const target = resolve(root, "dist");
const inputs = [
  ["src/index.html", "index.html"],
  ["src/main.mjs", "main.mjs"],
  ["node_modules/three/build/three.module.js", "vendor/three.module.js"],
  ["node_modules/three/build/three.core.js", "vendor/three.core.js"]
];
await mkdir(resolve(target, "vendor"), {recursive: true});
const files = [];
for (const [source, output] of inputs) {
  const bytes = await readFile(resolve(root, source));
  if (!bytes.length) throw Error("Empty demo asset " + source);
  await copyFile(resolve(root, source), resolve(target, output));
  files.push({
    path: output, bytes: bytes.length,
    gzipBytes: gzipSync(bytes, {level: 9}).length,
    sha256: createHash("sha256").update(bytes).digest("hex")
  });
}
if (files.some(f => f.bytes > 2_000_000) || files.reduce((n, f) => n + f.bytes, 0) > 3_000_000) {
  throw Error("Demo exceeds bounded plugin asset budget");
}
const receipt = {
  schema: "luhmOs.pluginCastDemoBuild.v1",
  engine: "three", version: "0.186.1",
  mode: "OPT_IN_PROCEDURAL_SOURCE_PREVIEW",
  networkFetchesInDemo: false, additionalRuntimeBackend: false,
  privateAssetAccess: false, buildDispatched: false,
  liveHostMounted: false, crownStatus: "STOP",
  files
};
await writeFile(resolve(target, "asset-manifest.json"), JSON.stringify(receipt, null, 2) + "\n");
process.stdout.write(JSON.stringify({status:"PLUGIN_DEMO_BUILT_NOT_DEPLOYED",assets:files.length,gzipBytes:files.reduce((n, f) => n + f.gzipBytes, 0)}) + "\n");
