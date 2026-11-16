import { test } from 'node:test';
import assert from 'node:assert/strict';
import { inspectHexReceipt, createHexReceiptCache, canonHexLayers, fourBeats } from '../core/canonHexLedger.mjs';
const sha='a'.repeat(40);
const counts={GREEN_SOURCE:12,AMBER_EXTERNAL_RECEIPT_REQUIRED:36,BLOCKED_CROWN:16};
function fixture(scale=256) {
  return {schema:'luhmOs.canonHexLedgerReceipt.v1',sourceRef:sha,scales:[scale],
    checkpointCount:scale/64, agentExecution:false,releaseAuthority:false,
    signingPerformed:false,crownStatus:'STOP',databaseSha256:'b'.repeat(64),
    checkpoints:Array.from({length:scale/64},(_,i)=>({scale,checkpoint:i+1,
      hexFirst:'0x'+(i*64).toString(16).padStart(3,'0'),
      hexLast:'0x'+(i*64+63).toString(16).padStart(3,'0'),
      prior:i?'c'.repeat(64):'0'.repeat(64),sha256:'c'.repeat(64),counts}))};
}
test('namespace identity and beat names remain canonical',()=>{
  assert.deepEqual([...canonHexLayers],['machineSqlDragonTail','repositoryKebabNamespace','vowelRippedStrictCamelHump','fullHumanCenteredCamelHump']);
  assert.deepEqual([...fourBeats],['hear','resolve','act','verify']);
});
test('256 assessed not 256 passed, red/amber remain grouped',()=>{
  const x=inspectHexReceipt(fixture(),sha);
  assert.equal(x.counts.assessed,256);assert.equal(x.counts.sourceGreen,48);
  assert.equal(x.counts.amber,144);assert.equal(x.counts.crownHold,64);
  assert.equal(x.crown,'STOP');assert.equal(x.independentDigestVerification,false);
});
test('stale source, fake Crown, shortened evidence and broken chain fail closed',()=>{
  const good=fixture();
  const failures=[
    {...good,sourceRef:'d'.repeat(40)},
    {...good,crownStatus:'GREEN'},
    {...good,checkpointCount:3},
    {...good,checkpoints:good.checkpoints.slice(1)},
    {...good,checkpoints:good.checkpoints.map((c,i)=>i===1?{...c,prior:'0'.repeat(64)}:c)},
    {...good,checkpoints:good.checkpoints.map((c,i)=>i===0?{...c,counts:{GREEN_SOURCE:64,UNKNOWN:1}}:c)}
  ];
  for (const x of failures) assert.throws(()=>inspectHexReceipt(x,sha),/RED_/);
});
test('cache deduplicates same SHA/digest and rejects stale source',()=>{
  const c=createHexReceiptCache(2), a=fixture(), b={...a,databaseSha256:'d'.repeat(64)};
  assert.equal(c.read(a,sha),c.read(a,sha));c.read(b,sha);
  assert.equal(c.size,2);assert.equal(c.pruneSource(sha),0);
  assert.throws(()=>c.read(a,'c'.repeat(40)),/RED_/);
  assert.throws(()=>createHexReceiptCache(65),/capacity/);
});
