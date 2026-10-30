import test from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { GoddessOrchestra, beats, quarters, layers } from "../src/orchestra.mjs";

test("64 routes are structured, bounded and inert", () => {
  const engine = new GoddessOrchestra();
  const all = engine.matrix();
  assert.equal(all.length, 64);
  assert.equal(new Set(all.map(x => [x.quarter, x.layer, x.beat].join(":"))).size, 64);
  assert.ok(all.every(x => x.authority === "NONE" && !x.executionEnabled && x.crown === "STOP"));
  assert.equal(engine.workerCount, 0);
});

test("four quarters and canonical layers compose without role privilege", () => {
  assert.deepEqual(quarters, ["local", "remote", "studio", "company"]);
  assert.deepEqual(beats, ["hear", "resolve", "act", "verify"]);
  assert.deepEqual(layers, ["coreLibrary", "pluginExtension", "classWidgetOrganization", "stubAdapterBoundary"]);
  const plan = new GoddessOrchestra().plan("studio", "pluginExtension", "act");
  assert.equal(plan.ownerRole, "kaji");
  assert.equal(plan.sourceRef, null);
  assert.equal(plan.authority, "NONE");
});

test("unknown labels never become executable", () => {
  const engine = new GoddessOrchestra();
  for (const args of [
    ["production", "coreLibrary", "act"],
    ["studio", "rootShell", "act"],
    ["company", "pluginExtension", "deploy"]
  ]) assert.throws(() => engine.plan(...args), TypeError);
});

test("song contains four beats and independent reviewer", () => {
  const song = new GoddessOrchestra().song();
  assert.deepEqual(song.map(x => x.beat), beats);
  assert.ok(song.every(x => !x.canStartWorker));
  assert.equal(song.at(-1).independentReview, "urdDoctorGoddess");
});

test("CLI blocks unregistered and extra commands", () => {
  const cli = new URL("../src/cli.mjs", import.meta.url).pathname;
  for (const command of [["deploy"], ["plan", "company", "coreLibrary", "deploy"], ["audit", "extra"]]) {
    const result = spawnSync(process.execPath, [cli, ...command], {encoding:"utf8",timeout:5000});
    assert.equal(result.status, 2);
  }
});
