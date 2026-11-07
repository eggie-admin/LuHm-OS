import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRelationshipStore } from "../prototypes/companionAtelier/relationshipCore.mjs";
import { inspectLive2dCandidate } from "../prototypes/companionAtelier/live2dAdapter.mjs";
const root = new URL("../../",import.meta.url);
const rules = JSON.parse(readFileSync(new URL("game/demo/relationshipRulesV2.json",root)));
const profiles = JSON.parse(readFileSync(new URL("game/demo/originalCompanionProfilesV1.json",root)));
test("Seven allowlisted actions are local and deterministic",()=>{
  const store=createRelationshipStore(rules,profiles);
  assert.equal(store.roster().length,3);
  assert.equal(store.apply("vesperNocturne","help").stats.trust,30);
  assert.equal(store.apply("vesperNocturne","flirtElsewhere").stats.jealousy,3);
  assert.equal(store.apply("maraIronvale","executeCode").accepted,false);
  assert.equal(store.evaluate("maraIronvale").stats.jealousy,0);
});
test("Bond rewards are threshold-based and not random or paid",()=>{
  const store=createRelationshipStore(rules,profiles);
  for(let i=0;i<12;i++)store.apply("elyraRunebound","questComplete");
  assert.deepEqual(store.evaluate("elyraRunebound").rewards,["neonAccent","moonlitWardrobe"]);
  assert.equal(rules.safety.noGambling,true);
  assert.equal(rules.safety.noPurchase,true);
});
test("State snapshot restore validates every record atomically",()=>{
  const store=createRelationshipStore(rules,profiles);
  store.apply("vesperNocturne","listen");
  const snapshot=store.save();
  store.reset();
  assert.equal(store.evaluate("vesperNocturne").stats.trust,25);
  assert.equal(store.restore(snapshot),true);
  assert.equal(store.evaluate("vesperNocturne").stats.trust,28);
  const corrupted=JSON.parse(JSON.stringify(snapshot));
  corrupted.items[1].stats.trust=500;
  assert.equal(store.restore(corrupted),false);
  assert.equal(store.evaluate("vesperNocturne").stats.trust,28);
});
test("Proprietary Live2D loading is not silently enabled",()=>{
  assert.equal(inspectLive2dCandidate(null).accepted,false);
  assert.equal(inspectLive2dCandidate({provenance:"UNKNOWN",clearance:"VERIFIED",modelFormat:"cubism5",modelManifest:"private.model3.json"}).accepted,false);
  assert.equal(inspectLive2dCandidate({provenance:"OWNER_AUTHORED_OR_LICENSED",clearance:"VERIFIED",modelFormat:"cubism5",modelManifest:"models/hero.model3.json"}).mode,"ADAPTER_NOT_INSTALLED");
});
