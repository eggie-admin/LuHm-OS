/** Canon 64-slot evidence in LLMOS JavaScript; pure/headless and zero vendor dependencies. */
import { namespaceLayers } from './namespaceCanon.mjs';
const SHA = /^[0-9a-f]{40}$/;
const HASH = /^[0-9a-f]{64}$/;
const allowedScales = new Set([256, 512, 1024]);
export const canonHexLayers = namespaceLayers;
export const fourBeats = Object.freeze(['hear', 'resolve', 'act', 'verify']);

export function inspectHexReceipt(report, exactSource) {
  if (!report || typeof report !== 'object' || Array.isArray(report) ||
      report.schema !== 'luhmOs.canonHexLedgerReceipt.v1' ||
      !SHA.test(report.sourceRef ?? '') || report.sourceRef !== exactSource ||
      !Array.isArray(report.scales) || !Array.isArray(report.checkpoints) ||
      !HASH.test(report.databaseSha256 ?? '') || report.crownStatus !== 'STOP' ||
      report.agentExecution !== false || report.releaseAuthority !== false ||
      report.signingPerformed !== false) throw new Error('RED_IDENTITY_OR_CROWN');
  const scales = new Set(report.scales);
  if (scales.size !== report.scales.length || ![...scales].every(s => allowedScales.has(s))) {
    throw new Error('RED_INVALID_SCALE');
  }
  const expected = report.scales.reduce((n, s) => n + s / 64, 0);
  if (report.checkpointCount !== expected || report.checkpoints.length !== expected) throw new Error('RED_INCOMPLETE_CHECKPOINTS');
  const totals = { assessed:0, sourceGreen:0, amber:0, hardRed:0, crownHold:0 };
  const groups = [];
  for (const scale of report.scales) {
    const group = report.checkpoints.filter(c => c.scale === scale).sort((a,b) => a.checkpoint - b.checkpoint);
    if (group.length !== scale / 64) throw new Error('RED_SCALE_COVERAGE');
    let prior = '0'.repeat(64);
    for (let i = 0; i < group.length; i++) {
      const c = group[i], first = '0x' + (i * 64).toString(16).padStart(3,'0');
      const last = '0x' + (i * 64 + 63).toString(16).padStart(3,'0');
      if (c.checkpoint !== i + 1 || c.hexFirst !== first || c.hexLast !== last ||
          c.prior !== prior || !HASH.test(c.sha256 ?? '') ||
          !c.counts || typeof c.counts !== 'object' || Array.isArray(c.counts)) throw new Error('RED_CHAIN_OR_RANGE');
      let subtotal = 0;
      for (const [status,count] of Object.entries(c.counts)) {
        if (!Number.isSafeInteger(count) || count < 0 ||
            !/^(GREEN_SOURCE|AMBER_[A-Z_]+|BLOCKED_CROWN|RED_[A-Z_]+)$/.test(status)) throw new Error('RED_UNTRUSTED_STATUS');
        subtotal += count;
        if (status === 'GREEN_SOURCE') totals.sourceGreen += count;
        else if (status.startsWith('AMBER_')) totals.amber += count;
        else if (status.startsWith('RED_')) totals.hardRed += count;
        else totals.crownHold += count;
      }
      if (subtotal !== 64) throw new Error('RED_PARTIAL_64_CHECKPOINT');
      totals.assessed += 64;
      prior = c.sha256;
    }
    groups.push(Object.freeze({ scale, checkpointCount:group.length, chainHead:prior }));
  }
  // Structure only. Verify SHA-256 independently with original raw cells in Python CI.
  return Object.freeze({ sourceRef:report.sourceRef, counts:Object.freeze(totals),
    groups:Object.freeze(groups), layers:canonHexLayers, beats:fourBeats,
    independentDigestVerification:false, vendorExecution:false,
    mutationAuthority:false, crown:'STOP' });
}

/** In-memory-only LRU with source/digest identity; no localStorage or network. */
export function createHexReceiptCache(capacity = 8) {
  if (!Number.isInteger(capacity) || capacity < 1 || capacity > 64) throw new RangeError('capacity 1..64');
  const items = new Map();
  return Object.freeze({
    read(report, exactSource) {
      if (!SHA.test(exactSource ?? '') || !HASH.test(report?.databaseSha256 ?? '')) throw new Error('RED_CACHE_SOURCE');
      const key = exactSource + ':' + report.databaseSha256;
      if (items.has(key)) {
        const value = items.get(key); items.delete(key); items.set(key,value); return value;
      }
      const value=inspectHexReceipt(report,exactSource);
      items.set(key,value);
      if (items.size > capacity) items.delete(items.keys().next().value);
      return value;
    },
    pruneSource(exactSource) {
      if (!SHA.test(exactSource ?? '')) throw new Error('RED_INVALID_PRUNE_SOURCE');
      let removed=0;
      for (const key of items.keys()) {
        if (!key.startsWith(exactSource + ':')) { items.delete(key); removed++; }
      }
      return removed;
    },
    get size() { return items.size; }
  });
}
