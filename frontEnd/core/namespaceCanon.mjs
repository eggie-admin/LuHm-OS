/** LuHmOS Tier-0 namespace and evidence projection. No I/O, provider calls or authority. */
const SHA = /^[a-f0-9]{40}$/;
const CAMEL = /^[a-z][A-Za-z0-9]*$/;
const DRAGON = /^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*$/;
const KEBAB = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

export const namespaceLayers = Object.freeze([
  "machineSqlDragonTail",
  "repositoryKebabNamespace",
  "vowelRippedStrictCamelHump",
  "fullHumanCenteredCamelHump"
]);
const keys = new Set(namespaceLayers);
const freezeRecord = (obj) => Object.freeze({ ...obj });

/** Explicit reviewed aliases only. No guessing, dispatch or identity authority. */
export function createNamespaceRegistry(rows) {
  if (!Array.isArray(rows) || rows.length === 0) throw new TypeError("reviewed namespace rows required");
  const lookup = new Map();
  const identities = new Map();
  for (const row of rows) {
    if (!row || typeof row !== "object" || Array.isArray(row) ||
        Object.keys(row).some((key) => !keys.has(key))) throw new TypeError("unsupported namespace row");
    const machine = row.machineSqlDragonTail;
    const slug = row.repositoryKebabNamespace;
    const compact = row.vowelRippedStrictCamelHump;
    const canonical = row.fullHumanCenteredCamelHump;
    if (typeof machine !== "string" || !DRAGON.test(machine) ||
        typeof slug !== "string" || !KEBAB.test(slug) ||
        typeof compact !== "string" || !CAMEL.test(compact) ||
        typeof canonical !== "string" || !CAMEL.test(canonical)) {
      throw new TypeError("invalid machine/transport/human namespace spelling");
    }
    if (identities.has(canonical)) throw new Error("duplicate canonical identity");
    const record = freezeRecord({ ...row, authorityEffect: "none" });
    for (const alias of [machine, slug, compact, canonical]) {
      if (lookup.has(alias)) throw new Error("namespace alias collision: " + alias);
      lookup.set(alias, record);
    }
    identities.set(canonical, record);
  }
  return Object.freeze({
    count: identities.size,
    list: () => Object.freeze([...identities.values()]),
    resolve(value) {
      if (typeof value !== "string") return null;
      return lookup.get(value) || null; // exact and case-sensitive
    },
    explain(value) {
      const match = typeof value === "string" ? lookup.get(value) : null;
      return match ? freezeRecord({ ...match, resolved: true }) : freezeRecord({
        resolved: false, machineState: "UNKNOWN", authorityEffect: "none"
      });
    }
  });
}

/** Source-only receipts, never production, agent, CAST, deployment or Crown proof. */
export function reconcileSourceEvidence({ sourceRef, taskId, scopeId, receipts } = {}) {
  if (typeof sourceRef !== "string" || !SHA.test(sourceRef) ||
      typeof taskId !== "string" || !CAMEL.test(taskId) ||
      typeof scopeId !== "string" || !CAMEL.test(scopeId)) {
    throw new TypeError("exact sourceRef, taskId, scopeId required");
  }
  if (!Array.isArray(receipts)) throw new TypeError("receipts array required");
  if (receipts.length === 0) return freezeRecord({
    sourceRef, taskId, scopeId, machineState: "AMBER",
    reason: "NO_EVIDENCE", verifiedCount: 0,
    authorityEffect: "none", crown: "STOP", runtime: "UNVERIFIED"
  });
  let verifiedCount = 0;
  let hasRed = false;
  let hasAmber = false;
  const seen = new Set();
  for (const receipt of receipts) {
    if (!receipt || typeof receipt !== "object" || Array.isArray(receipt) ||
        typeof receipt.checkId !== "string" || !CAMEL.test(receipt.checkId) ||
        seen.has(receipt.checkId)) {
      throw new TypeError("unique camelHump checkId required");
    }
    seen.add(receipt.checkId);
    const matched = receipt.sourceRef === sourceRef &&
      receipt.taskId === taskId && receipt.scopeId === scopeId;
    if (receipt.state === "RED" && matched) hasRed = true;
    else if (receipt.state === "GREEN" && receipt.verified === true && matched &&
             typeof receipt.evidenceRef === "string" && receipt.evidenceRef.length > 0) {
      verifiedCount++;
    } else hasAmber = true;
  }
  const machineState = hasRed ? "RED" : hasAmber ? "AMBER" : "GREEN_SOURCE_ONLY";
  return freezeRecord({
    sourceRef, taskId, scopeId, machineState,
    reason: hasRed ? "FAILED_CHECK" : hasAmber ? "INCOMPLETE_OR_STALE_EVIDENCE" : "SOURCE_CHECKS_ONLY",
    verifiedCount, authorityEffect: "none", crown: "STOP", runtime: "UNVERIFIED"
  });
}
