import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {createLayerConsoleView} from "../prototypes/gameLayerConsole/app.mjs";
const root=new URL("../../",import.meta.url);
const load=path=>JSON.parse(readFileSync(new URL(path,root),"utf8"));
const inventory=load("game/demo/gameLayerBuildInventoryV1.json");
const profiles=load("game/demo/originalCompanionProfilesV1.json");
const rules=load("game/demo/relationshipRulesV2.json");
const mods=load("game/demo/modInspirationCatalogV1.json");
test("one canonical source inventory wires real NPM HTML CSS JS GPL plugin and Godot",()=>{
  const app=createLayerConsoleView(inventory,profiles,rules,mods);
  assert.equal(app.crown,"STOP");
  assert.equal(app.runtime,"BROWSER_ONLY_NOT_GODOT");
  assert.equal(app.components.length,19);
  assert.equal(app.references.length,mods.sources.length);
  assert.equal(app.store.roster().length,3);
  const paths=new Set(app.components.map(x=>x.path));
  for(const path of ["host/api/machineRegistrySqliteV1.sql","frontEnd/package-lock.json",
     "frontEnd/prototypes/gameLayerConsole/index.html",
     "frontEnd/prototypes/gameLayerConsole/style.css",
     "frontEnd/prototypes/gameLayerConsole/app.mjs",
     "plugins/luhm-os/plugin.json","project.godot","scenes/CompanionModLab.tscn"])
     assert.ok(paths.has(path),path);
  assert.equal(inventory.rules.productionSqlMutation,false);
  assert.equal(inventory.rules.backendPluginEdited,false);
  assert.equal(inventory.rules.externalModsDownloaded,false);
});
test("seven gameplay actions run deterministic local relationship model",()=>{
  const a=createLayerConsoleView(inventory,profiles,rules,mods);
  assert.equal(Object.keys(a.actions).length,7);
  assert.equal(a.store.apply("vesperNocturne","help").stats.trust,30);
  assert.equal(a.store.apply("vesperNocturne","shell").accepted,false);
  assert.equal(a.store.evaluate("maraIronvale").stats.affection,15);
});
test("forged game, external binary provenance and self-authorization are rejected",()=>{
  const copy=v=>structuredClone(v);
  const badInventory=copy(inventory);badInventory.canon.crown="GREEN";
  assert.throws(()=>createLayerConsoleView(badInventory,profiles,rules,mods));
  const mut=copy(inventory);mut.rules.productionSqlMutation=true;
  assert.throws(()=>createLayerConsoleView(mut,profiles,rules,mods));
  const injected=copy(mods);injected.sources[0].fileReuse=true;
  assert.throws(()=>createLayerConsoleView(inventory,profiles,rules,injected));
  const dup=copy(inventory);dup.components[1].id=dup.components[0].id;
  assert.throws(()=>createLayerConsoleView(dup,profiles,rules,mods));
});
test("source-only console uses bounded local scripts, never a production SQL client",()=>{
  const html=readFileSync(new URL("frontEnd/prototypes/gameLayerConsole/index.html",root),"utf8");
  const js=readFileSync(new URL("frontEnd/prototypes/gameLayerConsole/app.mjs",root),"utf8");
  const css=readFileSync(new URL("frontEnd/prototypes/gameLayerConsole/style.css",root),"utf8");
  assert.match(html,/script type="module" src="\.\/app\.mjs"/);
  assert.match(html,/style\.css/);
  assert.match(js,/createRelationshipStore/);
  assert.match(css,/prefers-reduced-motion/);
  assert.doesNotMatch(js,/\beval\s*\(|\bnew\s+Function\s*\(/);
  assert.doesNotMatch(js,/cloudflare\.com\/api|sqlite3\.connect|privateKey/i);
});
