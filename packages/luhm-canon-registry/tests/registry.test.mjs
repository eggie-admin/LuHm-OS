import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {registry, resolveIdentity, help, createRegistry, sourceAudit, planSystemVariables} from "../src/index.mjs";
import {encodeCanonicalHex, decodeCanonicalHex} from "../src/codec.mjs";

const raw = JSON.parse(readFileSync(new URL("../../../doctrine/castIdentityHexRegistryV1.json", import.meta.url), "utf8"));

test("25 identities and four layers x four typed SQL lanes", () => {
  const status = sourceAudit();
  assert.equal(status.status, "SOURCE_IDENTITIES_CONSISTENT_NOT_RUNTIME_PROVEN");
  assert.equal(status.bindingCount, 25);
  assert.equal(status.matrixCells, 16);
  assert.equal(status.helpAliasesVerified, 4);
  assert.equal(status.variableRegistrations, 8);
  assert.equal(status.npmPrivate, true);
  assert.equal(status.npmPublished, false);
  assert.equal(registry.matrix().length, 16);
});

test("canonical, vowel, shorthand, hex and legacy recover the same name", () => {
  const name = "belldandySecretary";
  for (const input of [name, "blldndyScrtry", "bs", "62656c6c64616e6479536563726574617279"]) {
    const row = resolveIdentity(input);
    assert.equal(row.state, "RESOLVED_IDENTITY_ONLY");
    assert.equal(row.canonical, name);
    assert.equal(row.executionAllowed, false);
    assert.equal(row.authorityGranted, false);
  }
  assert.equal(resolveIdentity("mgcCdngRlplay").canonical, "codingRoleplay");
  assert.equal(help("bs").canonicalName, "belldandySecretary");
});

test("UTF-8 hex is exact reversible bytes, not a shortened authorization hash", () => {
  for (const row of registry.list()) {
    assert.equal(encodeCanonicalHex(row.canonical), row.utf8Hex);
    assert.equal(decodeCanonicalHex(row.utf8Hex), row.canonical);
  }
  assert.equal(encodeCanonicalHex("sourceRef"), "736f75726365526566");
  for (const invalid of ["", "0", "ff", "00", "GG", "626", "736F", "a".repeat(162), 7, null]) {
    assert.throws(() => decodeCanonicalHex(invalid));
  }
});

test("unknown aliases, upper-case guesses and unsafe identifiers never execute", () => {
  for (const invalid of ["BS", "blldndyScrtry ", "bllndySecretary",
    "__proto__", "constructor", "Professor Lum", "0x62656c6c", 3, null]) {
    assert.equal(resolveIdentity(invalid).state, "VERIFY");
    assert.equal(help(invalid).state, "VERIFY");
  }
  assert.throws(() => encodeCanonicalHex("../shell"));
});

test("registered collisions and fake authority are rejected", () => {
  const collision = structuredClone(raw);
  collision.bindings.find(x => x.canonical === "professorLum").shorthand = "bs";
  assert.throws(() => createRegistry(collision), /RED_IDENTITY_ALIAS_COLLISION/);
  const fakeHex = structuredClone(raw);
  fakeHex.bindings[0].utf8Hex = "ff";
  assert.throws(() => createRegistry(fakeHex), /RED_IDENTITY_RECORD_DRIFT/);
  const fakeWorkers = structuredClone(raw);
  fakeWorkers.runtime.activeWorkers = 1;
  assert.throws(() => createRegistry(fakeWorkers), /RED_IDENTITY_CANON_AUTHORITY/);
});

test("environment planning uses explicit whitelist without reading or setting env", () => {
  const old = process.env.LUHM_USB_ENABLED;
  const p = planSystemVariables({
    LUHM_STAGE: "testing", LUHM_DISPLAY_BACKEND: "wayland",
    LUHM_BLUETOOTH_ENABLED: "readOnly",
  });
  assert.equal(p.state, "HOLD_DEVICE_PERMISSION");
  assert.equal(p.values.LUHM_USB_ENABLED, "off");
  assert.equal(p.liveOsEnvironmentRead, false);
  assert.equal(p.liveOsEnvironmentChanged, false);
  assert.equal(process.env.LUHM_USB_ENABLED, old);
  for (const injected of [
    {LD_PRELOAD: "./libattacker.so"}, {DISPLAY: ":0"},
    {LUHM_STAGE: "production"}, {LUHM_USB_ENABLED: "readWrite"},
    {LUHM_PRIVATE_TOKEN: "secret"},
  ]) assert.throws(() => planSystemVariables(injected));
});

test("Lum and mesh are distinct and never grant live agency", () => {
  assert.equal(resolveIdentity("lm").canonical, "lum");
  assert.equal(resolveIdentity("lmesh").canonical, "lumMesh");
  assert.equal(resolveIdentity("lumMesh").authorityGranted, false);
  assert.equal(registry.get("ffffffff").state, "VERIFY");
  assert.equal(planSystemVariables({}).state, "SOURCE_CONFIGURATION_ONLY");
});
