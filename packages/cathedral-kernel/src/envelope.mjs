import {readFileSync} from 'node:fs';
const C=JSON.parse(readFileSync(new URL('../contract.v1.json',import.meta.url),'utf8'));
const H=/^[0-9a-f]{64}$/; const S=/^[0-9a-f]{40}$/; const I=/^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$/;
function deny(reason){throw new Error(reason)}
export function normalizeEnvelope(v){
  if(!v||typeof v!=='object'||Array.isArray(v)) deny('NOT_OBJECT');
  if(Object.keys(v).length!==C.fields.length||C.fields.some(k=>!Object.hasOwn(v,k))) deny('FIELDS');
  if(Object.keys(v).some(k=>!C.fields.includes(k))) deny('UNKNOWN_FIELD');
  if(v.schema!==C.schema)deny('SCHEMA');
  if(typeof v.sourceRef!=='string'||!S.test(v.sourceRef))deny('SHA');
  if(!['taskId','scopeId'].every(k=>typeof v[k]==='string'&&I.test(v[k])))deny('ID');
  if(!C.origins.includes(v.origin)||!C.tiers.includes(v.tier)||!C.operations.includes(v.operation))deny('ROUTE');
  if(v.costUsd!==0||v.approval!==false||v.crown!=='STOP')deny('AUTHORITY');
  if(!Array.isArray(v.hashes)||v.hashes.length>C.maxHashes||v.hashes.some(h=>typeof h!=='string'||!H.test(h)))deny('HASH_ARRAY');
  if(new Set(v.hashes).size!==v.hashes.length)deny('DUPLICATE_HASH');
  return Object.freeze(Object.fromEntries(C.fields.map(k=>[k,k==='hashes'?[...v.hashes].sort():v[k]])));
}
export class CathedralEnvelope{
  constructor(value){this.value=normalizeEnvelope(value);Object.freeze(this)}
  canonical(){return JSON.stringify(this.value)}
  toJSON(){return this.value}
}
export function sourceSnapshot(value){return {canonical:new CathedralEnvelope(value).canonical(),sourceOnly:true,executable:false}}
