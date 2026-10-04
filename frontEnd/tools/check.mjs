import { access, readFile } from "node:fs/promises";
import { resolve } from "node:path";
import vm from "node:vm";

const root = resolve(new URL("..", import.meta.url).pathname);
const mustExist = [
  "index.html",
  "styles.css",
  "app.js",
  "jquery/luhmManifestMin.js",
  "jquery/luhmManifestMin.min.js",
  "jquery/operationTitan7.js",
  "jquery/operationTitan7.min.js",
  "jquery/luhm.cockpit.js",
  "plugins/README.md"
];

for (const file of mustExist) await access(resolve(root, file));

const html = await readFile(resolve(root, "index.html"), "utf8");
const manifestSource = await readFile(resolve(root, "jquery/luhmManifestMin.js"), "utf8");
const manifestRuntime = await readFile(resolve(root, "jquery/luhmManifestMin.min.js"), "utf8");
const titan = await readFile(resolve(root, "jquery/operationTitan7.js"), "utf8");
const plugin = await readFile(resolve(root, "jquery/luhm.cockpit.js"), "utf8");
const app = await readFile(resolve(root, "app.js"), "utf8");

const sandbox = { jQuery: {} };
vm.runInNewContext(manifestRuntime, sandbox);
const manifestApi = sandbox.jQuery.luhmManifestMin;
const sample = { schema:"luhmOs.aiEvent.v1", taskId:"t1", sourceRef:"abc", scopeId:"q1", state:"active", evidenceRefs:["e1"] };
const compactSample = manifestApi.compact(sample);
const expandedSample = manifestApi.expand(compactSample);

const checks = [
  [html.includes("vendor/jquery-3.7.1.min.js"), "index loads pinned staged jQuery"],
  [html.includes("jquery/luhmManifestMin.min.js"), "index loads minified manifest adapter"],
  [html.includes("jquery/operationTitan7.min.js"), "index loads minified operationTitan7 plugin"],
  [manifestRuntime.length < manifestSource.length, "manifest runtime is minified"],
  [manifestRuntime.includes("$.luhmManifestMin"), "compact manifest adapter exists"],
  [compactSample.t === "t1" && compactSample.r === "abc" && compactSample.q === "q1", "manifest adapter compacts identity fields"],
  [expandedSample.taskId === "t1" && expandedSample.sourceRef === "abc" && expandedSample.scopeId === "q1", "manifest adapter round-trips identity fields"],
  [titan.includes('const pluginName = "operationTitan7"'), "canonical operationTitan7 plugin entry exists"],
  [titan.includes("forFuckSake") && titan.includes("scorchedEarth") && titan.includes("finalForm"), "three Titan7 escalation tiers exist"],
  [titan.includes("continueAll") && titan.includes("dryRun") && titan.includes("distro"), "npm-style Titan7 command surface exists"],
  [plugin.includes('const PLUGIN = "luhmCockpit"') && plugin.includes("$.fn[PLUGIN] ="), "single cockpit plugin entry exists"],
  [plugin.includes("$.fn.operationTitan7.parse") && plugin.includes("$root.operationTitan7"), "cockpit consumes explicit Titan7 commands"],
  [plugin.includes("$.fn.mgcCdngRlplay =") && plugin.includes("oldMagicPhrase") && plugin.includes("writtenDonePhrase"), "two-phrase magic plugin exists"],
  [app.includes("luhm:operationTitan7:invoke") && app.includes("operationTitan7: function"), "front-end exposes Titan7 control surface"]
];

let failed = 0;
for (const [ok, label] of checks) {
  console.log(`${ok ? "GREEN" : "RED"} ${label}`);
  if (!ok) failed += 1;
}
if (failed) process.exit(1);
