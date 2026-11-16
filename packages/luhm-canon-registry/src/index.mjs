/** Source-locked LuHm identity registry. Read-only, no env, network or worker I/O. */
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { canonicalName, encodeCanonicalHex, decodeCanonicalHex, assertShorthand } from "./codec.mjs";

const ROOT = new URL("../../../", import.meta.url);
const sourceJson = (path) => JSON.parse(readFileSync(new URL(path, ROOT), "utf8"));
const EXPECTED_LAYERS = ["camelHump", "vowelRipped", "shorthand", "utf8Hex"];
const EXPECTED_LANES = ["numericStream", "textStream", "booleanStream", "aiManifestStream"];
const FORBIDDEN = new Set(["__proto__", "constructor", "prototype"]);

function verifyShape(data) {
  if (!data || typeof data !== "object" || Array.isArray(data)
      || data.schema !== "luhmOs.castIdentityHexRegistry.v1"
      || JSON.stringify(data.fourIdentityLayers) !== JSON.stringify(EXPECTED_LAYERS)
      || JSON.stringify(data.typedSqlLanes) !== JSON.stringify(EXPECTED_LANES)
      || JSON.stringify(data.tiers) !== JSON.stringify([0, 1, 2, 3])
      || !Array.isArray(data.bindings) || data.bindings.length < 20
      || data.bindings.length > 128 || !Array.isArray(data.legacyAliases)) {
    throw new TypeError("RED_IDENTITY_CANON_SCHEMA");
  }
  if (data.identityPolicy?.aliasMayGrantAuthority !== false
      || data.identityPolicy?.hexMayGrantAuthority !== false
      || data.identityPolicy?.allKindsCheckCollisionsAcrossEntries !== true
      || data.identityPolicy?.computedVowelAliasesNeverAcceptedAutomatically !== true
      || data.runtime?.activeWorkers !== 0
      || data.runtime?.actualNpmPublished !== false
      || data.crownStatus !== "STOP") {
    throw new TypeError("RED_IDENTITY_CANON_AUTHORITY");
  }
}

export function createRegistry(data) {
  verifyShape(data);
  const byCanonical = new Map();
  const allAliases = new Map();
  function register(alias, canonical, kind) {
    if (FORBIDDEN.has(alias)) throw new TypeError("RED_IDENTITY_UNSAFE_NAME");
    const existing = allAliases.get(alias);
    if (existing && existing.canonical !== canonical) {
      throw new TypeError("RED_IDENTITY_ALIAS_COLLISION");
    }
    allAliases.set(alias, { canonical, kind });
  }
  for (const input of data.bindings) {
    if (!input || typeof input !== "object" || Array.isArray(input)) {
      throw new TypeError("RED_IDENTITY_RECORD");
    }
    const name = canonicalName(input.canonical);
    canonicalName(input.vowelRipped);
    assertShorthand(input.shorthand);
    if (typeof input.humanMeaning !== "string"
        || !input.humanMeaning || input.humanMeaning.length > 240
        || input.authority !== "IDENTITY_ONLY"
        || input.utf8Hex !== encodeCanonicalHex(name)
        || decodeCanonicalHex(input.utf8Hex) !== name
        || byCanonical.has(name)) {
      throw new TypeError("RED_IDENTITY_RECORD_DRIFT");
    }
    const row = Object.freeze({
      canonical: name,
      humanMeaning: input.humanMeaning,
      vowelRipped: input.vowelRipped,
      shorthand: input.shorthand,
      utf8Hex: input.utf8Hex,
      authority: "IDENTITY_ONLY",
    });
    byCanonical.set(name, row);
    register(name, name, "camelHump");
    register(row.vowelRipped, name, "vowelRipped");
    register(row.shorthand, name, "shorthand");
    register(row.utf8Hex, name, "utf8Hex");
  }
  for (const alias of data.legacyAliases) {
    if (!alias || typeof alias !== "object"
        || typeof alias.alias !== "string" || !/^[a-z][A-Za-z0-9]{0,79}$/.test(alias.alias)
        || !byCanonical.has(alias.canonical)
        || alias.authority !== "COMPATIBILITY_ONLY") {
      throw new TypeError("RED_IDENTITY_LEGACY_ALIAS");
    }
    register(alias.alias, alias.canonical, "legacy");
  }
  const records = Object.freeze(Array.from(byCanonical.values()));
  const frozen = Object.freeze({
    schema: data.schema, count: records.length, layers: Object.freeze([...EXPECTED_LAYERS]),
    lanes: Object.freeze([...EXPECTED_LANES]), tiers: Object.freeze([0, 1, 2, 3]),
    get(name) {
      if (typeof name !== "string" || name.length > 160) {
        return { state: "VERIFY", canonical: null, authority: false };
      }
      const alias = allAliases.get(name);
      if (!alias) return { state: "VERIFY", canonical: null, authority: false };
      const row = byCanonical.get(alias.canonical);
      return {
        state: "RESOLVED_IDENTITY_ONLY",
        matchedAs: alias.kind, ...row,
        authorityGranted: false, executionAllowed: false,
      };
    },
    list() { return records.map((record) => ({...record})); },
    matrix() {
      return EXPECTED_LANES.flatMap(lane => EXPECTED_LAYERS.map(layer => ({
        typedLane: lane, identityLayer: layer,
        state: "REGISTERED_SOURCE_ONLY", runtimeProven: false, authority: false,
      })));
    },
  });
  if (frozen.matrix().length !== 16) throw new TypeError("RED_IDENTITY_4X4");
  return frozen;
}

const canonical = sourceJson("doctrine/castIdentityHexRegistryV1.json");
export const registry = createRegistry(canonical);

export function resolveIdentity(input) {
  return registry.get(input);
}

export function help(input) {
  const answer = registry.get(input);
  if (answer.state !== "RESOLVED_IDENTITY_ONLY") {
    return { state: "VERIFY", help: "Unknown or ambiguous alias. Use a registered canonical name.", authorityGranted: false };
  }
  return {
    canonicalName: answer.canonical,
    humanMeaning: answer.humanMeaning,
    aliases: { vowelRipped: answer.vowelRipped, shorthand: answer.shorthand, utf8Hex: answer.utf8Hex },
    matchedAs: answer.matchedAs, authorityBoundary: "Identity lookup only; no command execution",
  };
}

export function planSystemVariables(proposal) {
  const contract = canonical.systemVariableRegistry;
  const host = sourceJson("doctrine/hostileModForge4x4V1.json").env;
  if (!proposal || typeof proposal !== "object" || Array.isArray(proposal)) {
    throw new TypeError("RED_ENV_PROPOSAL_SHAPE");
  }
  const registered = contract.bindings.map(item => item.name);
  if (registered.length !== 8 || new Set(registered).size !== 8
      || registered.some(name => !Object.hasOwn(host.permitted, name))
      || registered.some(name => !Object.hasOwn(host.defaults, name))) {
    throw new TypeError("RED_ENV_CANON_DRIFT");
  }
  const result = { ...host.defaults };
  const requested = Object.keys(proposal);
  if (requested.length > 8) throw new TypeError("RED_ENV_TOO_MANY");
  for (const key of requested) {
    if (!registered.includes(key)
        || typeof proposal[key] !== "string"
        || !host.permitted[key].includes(proposal[key])) {
      throw new TypeError("RED_ENV_UNAUTHORIZED_FIELD_OR_VALUE");
    }
    result[key] = proposal[key];
  }
  const blockers = [];
  if (result.LUHM_USB_ENABLED === "readOnly") blockers.push("USB_OS_PERMISSION_REQUIRED");
  if (result.LUHM_BLUETOOTH_ENABLED === "readOnly") blockers.push("BLUETOOTH_OS_PERMISSION_REQUIRED");
  if (result.LUHM_INPUT_MODE === "userAuthorized") blockers.push("INPUT_OWNER_PERMISSION_REQUIRED");
  return {state: blockers.length ? "HOLD_DEVICE_PERMISSION" : "SOURCE_CONFIGURATION_ONLY",
    values: result, blockers, liveOsEnvironmentRead: false, liveOsEnvironmentChanged: false,
    mutationAuthority: false, publicEnvExposure: false};
}

export function sourceAudit() {
  const naming = sourceJson("doctrine/namingNamespaceCanonV1.json");
  const helper = sourceJson("doctrine/commandHelpV1.json");
  const typed = sourceJson("doctrine/typedFourLaneSqlV1.json");
  const cast = sourceJson("doctrine/castTwoThreadBridgeV1.json");
  const hostile = sourceJson("doctrine/hostileModForge4x4V1.json");
  if (naming.personCenteredDegradation?.recoveryLaw?.canonicalIdentityNeverDiscarded !== true
      || helper.behavior?.allAliasesResolveToCanonical !== true
      || JSON.stringify(typed.lanes.map(row => row.id)) !== JSON.stringify(EXPECTED_LANES)
      || JSON.stringify(cast.fourTypedDataLanes.map(row => row.id)) !== JSON.stringify(EXPECTED_LANES)
      || JSON.stringify(cast.visualThreads.map(row => row.id)) !== JSON.stringify(["professorLum", "lumMesh"])
      || canonical.package.private !== true
      || canonical.package.publishAuthorized !== false) {
    throw new TypeError("RED_NAMING_CAST_SQL_DRIFT");
  }
  for (const entry of helper.builtins) {
    const record = registry.get(entry.canonicalName);
    if (record.state !== "RESOLVED_IDENTITY_ONLY"
      || record.vowelRipped !== entry.aliases.vowelRipped
      || record.shorthand !== entry.aliases.shorthand
      || record.humanMeaning !== entry.humanMeaning) {
      // Human help text may be fuller than compact registry text, but the
      // canonical identity and explicitly registered aliases must agree.
      if (record.state !== "RESOLVED_IDENTITY_ONLY"
          || record.vowelRipped !== entry.aliases.vowelRipped
          || record.shorthand !== entry.aliases.shorthand) {
        throw new TypeError("RED_COMMAND_HELP_ALIAS_DRIFT");
      }
    }
  }
  if (JSON.stringify(canonical.systemVariableRegistry.bindings.map(x => x.name))
        !== JSON.stringify(Object.keys(hostile.env.permitted))) {
    throw new TypeError("RED_SYSTEM_VARIABLE_REGISTRY_DRIFT");
  }
  const namesDigest = createHash("sha256")
    .update(JSON.stringify(registry.list())).digest("hex");
  return {
    status: "SOURCE_IDENTITIES_CONSISTENT_NOT_RUNTIME_PROVEN",
    bindingCount: registry.count, matrixCells: registry.matrix().length,
    typedLanes: [...EXPECTED_LANES], canonicalDigestSha256: namesDigest,
    helpAliasesVerified: helper.builtins.length,
    variableRegistrations: canonical.systemVariableRegistry.bindings.length,
    npmPrivate: true, npmPublished: false,
    sqlSchemaChanged: false, actualRuntimeAliasesInstalled: false,
    activeWorkers: 0, authorityGranted: false, crownAuthority: false,
  };
}
