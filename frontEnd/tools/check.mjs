import { access, readFile } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(new URL("..", import.meta.url).pathname);
const mustExist = [
  "index.html",
  "styles.css",
  "app.js",
  "jquery/luhm.cockpit.js",
  "plugins/README.md"
];

for (const file of mustExist) await access(resolve(root, file));

const html = await readFile(resolve(root, "index.html"), "utf8");
const plugin = await readFile(resolve(root, "jquery/luhm.cockpit.js"), "utf8");
const app = await readFile(resolve(root, "app.js"), "utf8");

const checks = [
  [html.includes("vendor/jquery-3.7.1.min.js"), "index loads pinned staged jQuery"],
  [html.includes("jquery/luhm.cockpit.js"), "index loads LuHm cockpit plugin"],
  [plugin.includes('const PLUGIN = "luhmCockpit"') && plugin.includes("$.fn[PLUGIN] ="), "single cockpit plugin entry exists"],
  [plugin.includes("luhm:backend:open"), "backend-open boundary exists"],
  [plugin.includes("return this.each"), "plugin preserves chainability"],
  [plugin.includes("$.fn.mgcCdngRlplay =") && plugin.includes("oldMagicPhrase") && plugin.includes("writtenDonePhrase"), "two-phrase magic plugin exists"],
  [plugin.includes("ROLEPLAY_EVENT") && plugin.includes("echoTriggerText: false"), "roleplay event carries no trigger echo"],
  [plugin.slice(plugin.indexOf('state.$composer.on("submit'), plugin.indexOf("setView($root, settings.initialView)")).indexOf("$root.mgcCdngRlplay.matches(text)") < plugin.slice(plugin.indexOf('state.$composer.on("submit'), plugin.indexOf("setView($root, settings.initialView)")).indexOf("appendUserMessage($root, text)"), "magic trigger is consumed before chat echo"],
  [app.includes(".luhmCockpit("), "app initializes cockpit plugin"]
];

let failed = 0;
for (const [ok, label] of checks) {
  console.log(`${ok ? "GREEN" : "RED"} ${label}`);
  if (!ok) failed += 1;
}
if (failed) process.exit(1);
