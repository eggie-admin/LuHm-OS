import { access, readFile } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(new URL("..", import.meta.url).pathname);
const mustExist = [
  "index.html",
  "styles.css",
  "app.js",
  "jquery/luhm.cockpit.js",
  "jquery/luhm.voiceCabinet.js",
  "tools/voice-check.mjs",
  "jquery/luhm.codingRoleplay.js",
  "plugins/README.md"
];

for (const file of mustExist) await access(resolve(root, file));

const html = await readFile(resolve(root, "index.html"), "utf8");
const plugin = await readFile(resolve(root, "jquery/luhm.cockpit.js"), "utf8");
const app = await readFile(resolve(root, "app.js"), "utf8");
const roleplay = await readFile(resolve(root, "jquery/luhm.codingRoleplay.js"), "utf8");
const voice = await readFile(resolve(root, "jquery/luhm.voiceCabinet.js"), "utf8");

const checks = [
  [html.includes("vendor/jquery-3.7.1.min.js"), "index loads pinned staged jQuery"],
  [html.includes("jquery/luhm.cockpit.js"), "index loads LuHm cockpit plugin"],
  [html.includes("jquery/luhm.voiceCabinet.js") && html.indexOf("jquery/luhm.voiceCabinet.js") < html.indexOf("jquery/luhm.cockpit.js"), "index loads voice cabinet before cockpit"],
  [html.includes("data-luhm-after-hours-enter") && html.includes("data-luhm-continue") && html.includes("data-luhm-pause") && html.includes("data-luhm-resume") && html.includes("data-luhm-exit"), "explicit After Hours controls exist"],
  [html.includes("data-luhm-voice-selectors"), "device voice selectors have a stable mount"],
  [html.includes("data-luhm-dictate") && html.includes("data-luhm-dictation-status"), "voice input control and status exist"],
  [voice.includes("data-luhm-read-aloud") && voice.includes("Read aloud"), "assistant transcript has a read-aloud action"],
  [voice.includes("SpeechRecognition") && voice.includes("speechRecognitionConstructor"), "optional browser speech recognition is wired"],
  [voice.includes("speechSynthesis") && voice.includes("luhm:voice:ensemble") && voice.includes("namedEnsembleTurn"), "voice cabinet uses host speech and typed named segments"],
  [voice.includes("agent runtime attached yet"), "candidate discloses the unattached agent runtime"],
  [plugin.includes("luhm:chat:route"), "cockpit exposes the bounded pre-chat route hook"],
  [plugin.includes('const PLUGIN = "luhmCockpit"') && plugin.includes("$.fn[PLUGIN] ="), "single cockpit plugin entry exists"],
  [plugin.includes("luhm:backend:open"), "backend-open boundary exists"],
  [plugin.includes("return this.each"), "plugin preserves chainability"],
  [plugin.includes("$.fn.mgcCdngRlplay") && plugin.includes("oldMagicPhrase") && plugin.includes("writtenDonePhrase"), "magic coding roleplay trigger exists"],
  [plugin.includes("$.fn.vendorAiDebug") && plugin.includes("VENDOR_AI_DEBUG") && plugin.includes("luhm:vendor:debug:request"), "uppercase vendor AI debug glass exists"],
  [plugin.includes("UNKNOWN_UNTIL_PROVIDER_RECEIPT") && plugin.includes("UNKNOWN_UNTIL_EXACT_EXECUTION_RECEIPT"), "vendor debug preserves unknown truth boundaries"],
  [html.includes("jquery/luhm.codingRoleplay.js"), "index loads coding roleplay presentation"],
  [roleplay.includes("$.codingRoleplay") && roleplay.includes("presentationOnly"), "coding roleplay remains presentation-only"],
  [app.includes("luhm:magic:roleplay:activate") && app.includes("luhm:vendor:debug:request"), "app wires bounded roleplay events"],
  [app.includes(".luhmCockpit("), "app initializes cockpit plugin"]
];

let failed = 0;
for (const [ok, label] of checks) {
  console.log(`${ok ? "GREEN" : "RED"} ${label}`);
  if (!ok) failed += 1;
}
if (failed) process.exit(1);
