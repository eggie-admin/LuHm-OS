import { access, readFile } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(new URL("..", import.meta.url).pathname);
const mustExist = [
  "index.html",
  "styles.css",
  "app.js",
  "jquery/luhm.cockpit.js",
  "jquery/luhm.parallax.js",
  "vue/LumLayeredPuppet.vue",
  "jquery/luhm.codingRoleplay.js",
  "plugins/README.md"
];

for (const file of mustExist) await access(resolve(root, file));

const html = await readFile(resolve(root, "index.html"), "utf8");
const plugin = await readFile(resolve(root, "jquery/luhm.cockpit.js"), "utf8");
const parallax = await readFile(resolve(root, "jquery/luhm.parallax.js"), "utf8");
const vueCandidate = await readFile(resolve(root, "vue/LumLayeredPuppet.vue"), "utf8");
const app = await readFile(resolve(root, "app.js"), "utf8");
const roleplay = await readFile(resolve(root, "jquery/luhm.codingRoleplay.js"), "utf8");

const checks = [
  [html.includes("jquery/luhm.parallax.js") && app.includes(".luhmParallax()"), "local parallax plugin mounted"],
  [parallax.includes("$.fn.luhmParallax =") && parallax.includes('command === "destroy"') && parallax.includes("prefers-reduced-motion") && !parallax.includes("fetch("), "bounded parallax lifecycle"],
  [vueCandidate.includes('from "vue"') && vueCandidate.includes("onBeforeUnmount") && vueCandidate.includes("prefers-reduced-motion") && !vueCandidate.includes("https://"), "Vue 3 separate candidate, no CDN imports"],
  [html.includes("vendor/jquery-3.7.1.min.js"), "index loads pinned staged jQuery"],
  [html.includes("jquery/luhm.cockpit.js"), "index loads LuHm cockpit plugin"],
  [plugin.includes('const PLUGIN = "luhmCockpit"') && plugin.includes("$.fn[PLUGIN] ="), "single cockpit plugin entry exists"],
  [plugin.includes("luhm:backend:open"), "backend-open boundary exists"],
  [plugin.includes("return this.each"), "plugin preserves chainability"],
  [plugin.includes("$.fn.mgcCdngRlplay") && plugin.includes("oldMagicPhrase") && plugin.includes("writtenDonePhrase"), "magic coding roleplay trigger exists"],
  [plugin.includes("$.fn.vendorAiDebug") && plugin.includes("VENDOR_AI_DEBUG") && plugin.includes("luhm:vendor:debug:request"), "uppercase vendor AI debug glass exists"],
  [plugin.includes("UNKNOWN_UNTIL_PROVIDER_RECEIPT") && plugin.includes("UNKNOWN_UNTIL_EXACT_EXECUTION_RECEIPT"), "vendor debug preserves unknown truth boundaries"],
  [html.includes("jquery/luhm.codingRoleplay.js"), "index loads coding roleplay presentation"],
  [roleplay.includes("$.codingRoleplay") && roleplay.includes("presentationOnly"), "coding roleplay remains presentation-only"],
  [app.includes("luhm:magic:roleplay:activate") && app.includes("luhm:vendor:debug:request"), "app wires bounded roleplay events"],
  [app.includes(".luhmCockpit("), "app initializes cockpit plugin"],
  [plugin.includes('document.addEventListener("visibilitychange", state.visibilityHandler)') &&
   plugin.includes('document.removeEventListener("visibilitychange", state.visibilityHandler)'),
   "clock pauses on hidden tab and releases listener at destroy"],
  [plugin.includes('if (document.hidden) return;') &&
   plugin.includes('Math.max(15000, configured)') &&
   plugin.includes('if (state.$clock.text() !== display)'),
   "clock avoids hidden/duplicate updates and timer storms"]
];

let failed = 0;
for (const [ok, label] of checks) {
  console.log(`${ok ? "GREEN" : "RED"} ${label}`);
  if (!ok) failed += 1;
}
if (failed) process.exit(1);
