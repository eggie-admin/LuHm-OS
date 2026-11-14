import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {inspectAramoorWorld,travelBetween,reachableRegions} from "../src/aramoorGraph.mjs";
const world=JSON.parse(readFileSync(new URL("../../../../game/world/aramoorArchipelagoV1.json",import.meta.url),"utf8"));

test("the Godot Canon is the browser's nine-region, twelve-link private source",()=>{
  const graph=inspectAramoorWorld(world);
  assert.equal(graph.zones,9);
  assert.equal(graph.bridges,12);
  assert.equal(graph.tides,2);
  assert.equal(world.source.adventureLicense,"CC BY-SA 4.0");
  assert.equal(world.source.modulePdfInspected,false);
  assert.equal(world.gates.crown,"STOP");
});
test("one bridge permits crossing while non-neighboring islands remain inaccessible",()=>{
  assert.deepEqual(reachableRegions(world,"aramoorHarbor").sort(),["moonfernSanctuary","saltglassBoardwalk"]);
  const good=travelBetween(world,"aramoorHarbor","saltglassBoardwalk");
  assert.equal(good.ok,true);
  assert.equal(good.zoneId,"saltglassBoardwalk");
  const blocked=travelBetween(world,"aramoorHarbor","stormlightKeep");
  assert.equal(blocked.ok,false);
  assert.equal(blocked.reason,"BRIDGE_NOT_CONNECTED");
});
test("bad graph, fake source rights and release escalation fail closed",()=>{
  const clone=()=>structuredClone(world);
  const duplicate=clone();duplicate.zones[1].id=duplicate.zones[0].id;
  assert.throws(()=>inspectAramoorWorld(duplicate),/BAD_OR_DUPLICATE_ZONE/);
  const cut=clone();cut.links[0][1]="madeUpRegion";
  assert.throws(()=>inspectAramoorWorld(cut),/BROKEN_WORLD_EDGE/);
  const release=clone();release.artPolicy.publicAllowed=true;
  assert.throws(()=>inspectAramoorWorld(release),/RIGHTS_OR_CROWN_HOLD/);
  const fake=clone();fake.source.modulePdfInspected=true;
  assert.throws(()=>inspectAramoorWorld(fake),/RIGHTS_OR_CROWN_HOLD/);
  const self=clone();self.links[0][1]=self.links[0][0];
  assert.throws(()=>inspectAramoorWorld(self),/BROKEN_WORLD_EDGE/);
});
