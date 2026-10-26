import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";
import core from "../lib/luhmUiCore.js";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const [script, plugin, html, pkg] = await Promise.all([
  readFile(resolve(root, "lib/luhmUiCore.js"), "utf8"),
  readFile(resolve(root, "jquery/luhm.cockpit.slimCandidate.js"), "utf8"),
  readFile(resolve(root, "index.html"), "utf8"),
  readFile(resolve(root, "package.json"), "utf8")
]);

const check = (value, label) => {
  assert.ok(value, label);
  console.log("GREEN " + label);
};

check(core.schema === "luhmOs.uiCore.v1", "original core machine identity");
check(core.matchesMagicTrigger("I invoke the old magic. So let it be written, so let it be done!"),
      "both magic phrases required");
check(!core.matchesMagicTrigger("I invoke the old magic.") &&
      !core.matchesMagicTrigger("so let it be written, so let it be done"),
      "a single phrase never activates anything");
check(!core.matchesMagicTrigger("I invoke the old magic; I revoke all my permissions"),
      "spoken magic cannot create authority");
check(core.normalizeMagicText("WITCHING HOUR") === "witching hour",
      "human display phrase normalized without renaming namespace");

for (const [source, expected] of [
  ["VENDOR DEBUG", "all"],
  ["DEBUG VENDOR", "all"],
  ["vendor debug OPENAI", "openAi"],
  ["debug Open Daddy", "openAi"],
  ["VENDOR DEBUG Big Brother", "googleAi"],
  ["debug google ai", "googleAi"],
  ["debug github copilot", "githubCopilot"],
  ["debug HF", "huggingFace"],
  ["debug EDGE GALLERY", "edgeGallery"]
]) {
  const parsed = core.parseVendorDebugCommand(source);
  assert.equal(parsed?.providerId, expected, source);
  assert.equal(parsed.command, parsed.command.toUpperCase());
}
console.log("GREEN canonical vendor aliases stay stable");
check(core.parseVendorDebugCommand("debug stranger") === null &&
      core.parseVendorDebugCommand("open camera") === null,
      "unknown commands rejected rather than executed");

for (const [raw, value] of [
  [undefined, 30000], [0, 30000], [1000, 15000], [15000, 15000],
  [30000, 30000], [500000, 120000], [NaN, 30000]
]) {
  assert.equal(core.clockIntervalMs(raw), value);
}
console.log("GREEN visibility-friendly bounded clock policy");

const context = { window: {} };
vm.runInNewContext(script, context, { timeout: 300 });
check(context.window.LuHmUiCore &&
      context.window.LuHmUiCore.matchesMagicTrigger("I invoke the old magic so let it be written so let it be done"),
      "script-tag browser global present");

const coreTag = html.indexOf('src="./lib/luhmUiCore.js"');
const jqueryTag = html.indexOf('src="./vendor/jquery-3.7.1.min.js"');
const pluginTag = html.indexOf('src="./jquery/luhm.cockpit.js"');
const nextTag = html.indexOf('src="./jquery/luhm.cockpit.slimCandidate.js"');
check(coreTag === -1 && nextTag === -1 && jqueryTag >= 0 && pluginTag > jqueryTag,
      "accepted browser runtime remains unchanged while new core is candidate-only");
check(plugin.includes('const matchesMagicTrigger = value => uiCore.matchesMagicTrigger(value)') &&
      plugin.includes('const parseVendorDebugCommand = value => uiCore.parseVendorDebugCommand(value)') &&
      plugin.includes('uiCore.clockIntervalMs(state.settings.clockIntervalMs)'),
      "candidate plugin delegates pure helpers without changing accepted runtime");
check(plugin.includes("HISTORICAL COMPATIBILITY REFERENCE") &&
      plugin.includes("$.fn.mgcCdngRlplay") &&
      plugin.includes("$.fn.vendorAiDebug") &&
      plugin.includes("$.fn[PLUGIN]"),
      "candidate historical source commented and future public API preserved");
check(pkg.includes('"private": true') &&
      pkg.includes('"jquery": "3.7.1"'),
      "upstream jQuery still pinned and npm package remains private");
check(!/fetch\s*\(|XMLHttpRequest|WebSocket|eval\s*\(|innerHTML|localStorage/.test(script),
      "pure core has no implicit network, execution or persistent storage");
console.log("GREEN_LUHM_CORE_SOURCE_ONLY");
