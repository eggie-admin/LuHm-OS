import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const json = async name => JSON.parse(await readFile(resolve(root, name), "utf8"));
test("plugin-only workspace pins one engine, no extra npm service", async () => {
  const pkg = await json("package.json");
  const lock = await json("package-lock.json");
  assert.equal(pkg.name, "@luhm-os/cast-demo");
  assert.equal(pkg.private, true);
  assert.deepEqual(Object.keys(pkg.dependencies), ["three"]);
  assert.equal(pkg.dependencies.three, "0.186.1");
  assert.equal(lock.packages["node_modules/three"].version, "0.186.1");
  assert.match(lock.packages["node_modules/three"].integrity, /^sha512-/);
});
test("rehearsal source uses local module only, has no network or worker dispatch", async () => {
  const js = await readFile(resolve(root, "src/main.mjs"), "utf8");
  const html = await readFile(resolve(root, "src/index.html"), "utf8");
  assert.match(js, /from "\.\/vendor\/three\.module\.js"/);
  assert.match(js, /prefers-reduced-motion/);
  assert.match(js, /webglcontextlost/);
  assert.match(html, /<script type="module" src="\.\/main\.mjs"><\/script>/);
  assert.match(html, /LuHm-OS/);
  assert.doesNotMatch(js + html, /\bfetch\s*\(|XMLHttpRequest|sendBeacon|WebSocket|https?:\/\//);
});
test("deterministic output manifest binds each staged asset by SHA256", async () => {
  const manifest = await json("dist/asset-manifest.json");
  assert.equal(manifest.schema, "luhmOs.pluginCastDemoBuild.v1");
  assert.equal(manifest.liveHostMounted, false);
  assert.equal(manifest.additionalRuntimeBackend, false);
  assert.equal(manifest.buildDispatched, false);
  assert.equal(manifest.crownStatus, "STOP");
  assert.deepEqual(manifest.files.map(f => f.path), [
    "index.html", "main.mjs", "vendor/three.module.js", "vendor/three.core.js"
  ]);
  for (const f of manifest.files) {
    const bytes = await readFile(resolve(root, "dist", f.path));
    assert.equal(f.bytes, bytes.length);
    assert.equal(f.sha256, createHash("sha256").update(bytes).digest("hex"));
  }
});
