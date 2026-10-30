import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {CathedralEnvelope,normalizeEnvelope,sourceSnapshot} from '../src/envelope.mjs';
const v=JSON.parse(readFileSync(new URL('./vectors.json',import.meta.url),'utf8'));
test('golden vector: class, arrays and canonical functions',()=>{
 const x=normalizeEnvelope(v.valid);
 assert.equal(x.hashes[0],'b'.repeat(64));
 assert.equal(Object.isFrozen(x.hashes),true);
 assert.throws(()=>x.hashes.push('d'.repeat(64)));

 assert.equal(new CathedralEnvelope(v.valid).canonical(),JSON.stringify(x));
 assert.equal(sourceSnapshot(v.valid).executable,false);
});
for(const bad of v.invalid)test('fail closed '+bad.name,()=>assert.throws(()=>normalizeEnvelope({...v.valid,...bad.patch})));
test('unknown field blocked',()=>assert.throws(()=>normalizeEnvelope({...v.valid,token:'redacted'})));
