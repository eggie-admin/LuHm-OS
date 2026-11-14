import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
const base=new URL("../prototypes/moonlitCarriage/",import.meta.url);
const html=readFileSync(new URL("index.html",base),"utf8");
const css=readFileSync(new URL("scene.css",base),"utf8");
const js=readFileSync(new URL("scene.mjs",base),"utf8");

test("isolated scene assets and honest provenance",()=>{
  assert.match(html,/moonlitCarriage|Moonlit Carriage/);
  assert.match(html,/LIVE2D CUBISM: NOT MOUNTED/);
  assert.match(html,/CROWN STOP/);
  assert.match(html,/host\/harness\/studioDeck\.html/);
  assert.match(html,/script-src 'self'/);
  assert.doesNotMatch(html,/https?:\/\//);
});
test("reads Canon but never writes doctrine or game state",()=>{
  assert.match(js,/doctrine\/SOURCE_OF_TRUTH\.json/);
  assert.match(js,/game\/demo\/relationshipRulesV2\.json/);
  assert.match(js,/rules\.crown!=="STOP"/);
  assert.match(js,/truth\.promotion!==false/);
  assert.match(js,/localStorage\.setItem/);
  assert.doesNotMatch(js,/\b(?:XMLHttpRequest|WebSocket|eval|Function)\s*\(/);
  assert.doesNotMatch(js,/method\s*:\s*["'](?:POST|PUT|DELETE|PATCH)["']/i);
});
test("bounded authored scenes have valid branches and accessible inputs",()=>{
  assert.match(js,/const VALID = new Set\(Object\.keys\(scenes\)\)/);
  assert.match(js,/history\.length<=30/);
  assert.match(js,/choices\.replaceChildren\(\)/);
  assert.match(html,/aria-live="polite"/);
  assert.match(html,/id="pause" aria-pressed="false"/);
  assert.match(html,/id="cat".*aria-label="Pet Nyx/);
});
test("reduced motion, visibility pause, and lifecycle cleanup",()=>{
  assert.match(css,/prefers-reduced-motion:reduce/);
  assert.match(js,/document\.hidden/);
  assert.match(js,/pagehide/);
  assert.match(js,/clearTimeout/);
  assert.match(js,/removeEventListener/);
});
