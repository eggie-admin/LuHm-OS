import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createNamespaceRegistry, namespaceLayers, reconcileSourceEvidence } from "../core/namespaceCanon.mjs";

const naming = JSON.parse(readFileSync(new URL("../../doctrine/namingNamespaceCanonV1.json", import.meta.url)));
const row = Object.freeze({
  machineSqlDragonTail: naming.namespaceEscalation.example.machineSqlDragonTail,
  repositoryKebabNamespace: naming.namespaceEscalation.example.repositoryKebabNamespace.slug,
  vowelRippedStrictCamelHump: naming.namespaceEscalation.example.vowelRippedStrictCamelHump,
  fullHumanCenteredCamelHump: naming.namespaceEscalation.example.fullHumanCenteredCamelHump
});
const sha = "a".repeat(40);
const scope = { sourceRef: sha, taskId: "canonCheck", scopeId: "sourceOnly" };
const receipt = (overrides = {}) => ({ checkId: "sourceAudit", ...scope, state: "GREEN", verified: true,
  evidenceRef: "githubActionsCheckRun", ...overrides });

test("four namespace layers match existing Canon exactly", () => {
  assert.deepEqual(namespaceLayers, naming.namespaceEscalation.orderedLayers);
  const registry = createNamespaceRegistry([row]);
  assert.equal(registry.count, 1);
  for (const alias of Object.values(row)) {
    assert.equal(registry.resolve(alias).fullHumanCenteredCamelHump, "operationTitan");
  }
  assert.equal(registry.resolve("OPERATION-TITAN"), null);
  assert.equal(registry.explain("unknown").machineState, "UNKNOWN");
  assert.equal(registry.resolve("OPERATION_TITAN").authorityEffect, "none");
});

test("namespace collisions and undeclared/invalid aliases fail closed", () => {
  assert.throws(() => createNamespaceRegistry([row, { ...row, fullHumanCenteredCamelHump: "otherName" }]), /collision/);
  assert.throws(() => createNamespaceRegistry([{ ...row, machineSqlDragonTail: "operationTitan" }]), /spelling/);
  assert.throws(() => createNamespaceRegistry([{ ...row, secretAlias: "foo" }]), /unsupported/);
  assert.throws(() => createNamespaceRegistry([]), /required/);
});

test("matching GREEN receipts yield source-only, never global Crown", () => {
  const output = reconcileSourceEvidence({ ...scope, receipts: [receipt()] });
  assert.equal(output.machineState, "GREEN_SOURCE_ONLY");
  assert.equal(output.crown, "STOP");
  assert.equal(output.runtime, "UNVERIFIED");
  assert.equal(Object.isFrozen(output), true);
});

test("missing, stale, conflicting, unverifiable or malformed receipts are not GREEN", () => {
  assert.equal(reconcileSourceEvidence({ ...scope, receipts: [] }).machineState, "AMBER");
  for (const patch of [
    { sourceRef: "b".repeat(40) }, { taskId: "different" }, { scopeId: "different" },
    { state: "UNKNOWN" }, { verified: false }, { evidenceRef: "" }
  ]) assert.equal(reconcileSourceEvidence({ ...scope, receipts: [receipt(patch)] }).machineState, "AMBER");
  assert.equal(reconcileSourceEvidence({ ...scope, receipts: [receipt({ state: "RED" })] }).machineState, "RED");
  assert.equal(reconcileSourceEvidence({ ...scope, receipts: [receipt({ state: "RED", sourceRef: "b".repeat(40) })] }).machineState, "AMBER");
  assert.throws(() => reconcileSourceEvidence({ ...scope, receipts: [receipt(), receipt()] }), /unique/);
  assert.throws(() => reconcileSourceEvidence({ ...scope, sourceRef: "main", receipts: [] }), /exact/);
});
