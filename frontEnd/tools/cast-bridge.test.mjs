import test from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { parseOptions, helpText, checkReceipt } from "./cast-bridge.mjs";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const script = resolve(repoRoot, "frontEnd/tools/cast-bridge.mjs");
const sourceRef = "a".repeat(40);

test("safe defaults are tier zero, CAST bridge preview, no force", () => {
  const o = parseOptions([]);
  assert.equal(o.tier, 0);
  assert.equal(o.phase, "castBridge");
  assert.equal(o.forceRequested, false);
  assert.equal(o.dryRun, true);
  assert.deepEqual(o.tasks, ["mobileMainHost", "chatGptInlineMount"]);
});
test("all short options preserve read-only semantics", () => {
  const o = parseOptions(["-v", "-h", "-d", "-f", "--tier", "3"]);
  assert.equal(o.verbose, true);
  assert.equal(o.docs, true);
  assert.equal(o.help, true);
  assert.equal(o.forceRequested, true);
  assert.equal(o.tier, 3);
  assert.match(helpText, /--force.*cannot override a gate/);
});
test("typed strict validation blocks invalid or unbounded input", () => {
  const bad = [
    ["--tier", "4"], ["--tier", "2.0"], ["--tier", "abc"],
    ["--tasks", "a,a"], ["--tasks", "__SQL"], ["--tasks", "a,,b"],
    ["--scope-id", ";DROP TABLE"], ["--source-ref", "main"],
    ["--source-ref", "A".repeat(40)], ["--phase", "release"],
    ["--register", "superuser"], ["--intent", "x\nexec"],
    ["--intent", "x".repeat(281)], ["--deploy"],
    ["--tier"], ["--tasks", "a", "--tasks", "b"],
    ["--force=true"], ["--dry-run=false"]
  ];
  for (const argv of bad) assert.throws(() => parseOptions(argv), undefined, argv.join(" "));
});
test("typed alternatives and human request label never imply action", () => {
  const o = parseOptions([
    "--tasks=chatGptInlineMount", "--tier=2", "--intent", "Review Android UI",
    "--source-ref", sourceRef, "--scope-id", "professor/phone", "--register", "colleague"
  ]);
  assert.deepEqual(o.tasks, ["chatGptInlineMount"]);
  assert.equal(o.tier, 2);
  assert.equal(o.intent, "Review Android UI");
  assert.equal(o.sourceRef, sourceRef);
});
test("hard receipt gate refuses forged privilege or completion", () => {
  const options = parseOptions(["--tasks", "chatGptInlineMount"]);
  const base = {
    schema: "luhmOs.humanCenteredCastPreview.v1",
    status: "READ_ONLY_SOURCE_CANDIDATE_NOT_HOST_MOUNTED",
    sourceRef, scopeId: options.scopeId, workflowPhase: "castBridge",
    castEnvelopesGranted: 0, buildDispatched: false, agentWorkersStarted: 0,
    hostMountVerified: false, releaseAuthorized: false,
    crownGranted: false, crownStatus: "STOP", taskCount: 1,
    tasks: [{buildDispatched:false, sourceMutated:false}]
  };
  assert.equal(checkReceipt(base, options, sourceRef), true);
  for (const replacement of [
    { buildDispatched: true }, { castEnvelopesGranted: 1 },
    { crownStatus: "GREEN" }, { releaseAuthorized: true },
    { hostMountVerified: true }, { sourceRef: "b".repeat(40) },
    { tasks: [{buildDispatched: false, sourceMutated: true}] }
  ]) assert.throws(() => checkReceipt({...base, ...replacement}, options, sourceRef));
});
test("real Python Canon preview stays source-only even with tier 3 and force", () => {
  const run = spawnSync(process.execPath, [
    script, "--json", "--force", "--tier", "3",
    "--source-ref", sourceRef, "--tasks", "mobileMainHost,chatGptInlineMount"
  ], {cwd: repoRoot, encoding: "utf8", timeout: 20000});
  assert.equal(run.status, 0, run.stderr);
  const receipt = JSON.parse(run.stdout);
  assert.equal(receipt.status, "READ_ONLY_REVIEW_REQUIRED");
  assert.equal(receipt.forceRequested, true);
  assert.equal(receipt.forceApplied, false);
  assert.equal(receipt.dispatchAuthority, false);
  assert.equal(receipt.canonicalPreview.castEnvelopesGranted, 0);
  assert.equal(receipt.canonicalPreview.buildDispatched, false);
  assert.equal(receipt.canonicalPreview.hostMountVerified, false);
  assert.equal(receipt.crownStatus, "STOP");
});
