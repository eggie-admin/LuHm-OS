import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {planThinPackages,tryThinPackages,applyThinPackages} from '../src/thin-package.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const policy=JSON.parse(fs.readFileSync(path.join(root,'doctrine/luhmThinPackagePlanV1.json'),'utf8'));
const sha='a'.repeat(40);
const run=(p=policy)=>planThinPackages(sha,structuredClone(p),root);
test('plan deterministically orders native and web dependencies without execution',()=>{
 const x=run();assert.equal(x.packageActionsExecuted,false);assert.equal(x.sourceIdentityVerified,false);assert.equal(x.crown,'STOP');
 assert(x.planOrder.indexOf('webGlass')<x.planOrder.indexOf('androidHost'));assert.deepEqual(x,run());
});
test('try stages only disposable temp receipt and rolls back',()=>{
 const x=tryThinPackages(run());assert.equal(x.stagingRemoved,true);assert.equal(x.hostChanged,false);
});
test('apply is impossible',()=>assert.throws(()=>applyThinPackages(),/APPLY_BLOCKED/));
test('no symbolic SHA alias',()=>assert.throws(()=>planThinPackages('main',policy,root),/EXACT_40_SHA/));
test('auto apply rejected',()=>{const p=structuredClone(policy);p.autoApply=true;assert.throws(()=>run(p),/UNSAFE_autoApply/)});
test('cycle rejected',()=>{const p=structuredClone(policy);p.modules[0].requires=['androidHost'];assert.throws(()=>run(p),/CYCLE/)});
test('dependency on quarantine rejected',()=>{const p=structuredClone(policy);p.modules[0].requires=['legacyDonors'];assert.throws(()=>run(p),/QUARANTINE_DEP/)});
test('path traversal rejected',()=>{const p=structuredClone(policy);p.modules[0].path='../sneak';assert.throws(()=>run(p),/UNSAFE_PATH/)});
test('duplicate modules rejected',()=>{const p=structuredClone(policy);p.modules[1].id='webGlass';assert.throws(()=>run(p),/DUPLICATE/)});
