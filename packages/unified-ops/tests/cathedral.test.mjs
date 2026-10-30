import test from "node:test";
import assert from "node:assert/strict";
import {packageErrors,proposedPlan,auditProposed} from "../src/cathedral.mjs";
const sha="f0cb6ee54066b490c0e80efc2c96200fec76ee2d";
test("dependency order and no release authority",()=>{
 const p=proposedPlan(sha),seen=new Set();
 for(const s of p.steps){for(const d of s.needs)assert.ok(seen.has(d));seen.add(s.id);}
 assert.equal(p.executor,"NONE");
 assert.equal(p.autoMerge,false);
 assert.equal(p.automaticCast,false);
 assert.equal(p.crown,"STOP");
});
test("bad or inferred source SHA fails closed",()=>{
 for(const x of [undefined,"main","abc123",sha.toUpperCase(),"",null])
  assert.throws(()=>proposedPlan(x));
});
test("npm drift and unresolved vendor code are rejected",()=>{
 const pkg={private:true,dependencies:{jquery:"3.7.1"}};
 const lock={lockfileVersion:3,packages:{"":{dependencies:{jquery:"3.7.1"}},
  "node_modules/jquery":{version:"3.7.1",integrity:"sha512-example"}}};
 assert.deepEqual(packageErrors(pkg,lock,"fixture"),[]);
 assert.ok(packageErrors({...pkg,private:false},lock,"fixture").length);
 assert.ok(packageErrors({...pkg,dependencies:{jquery:"^3.7.1"}},lock,"fixture").length);
 assert.ok(packageErrors(pkg,{...lock,packages:{"":lock.packages[""]}},"fixture").length);
});
test("repository static PASS never implies physical or Crown PASS",()=>{
 const r=auditProposed(sha);
 assert.equal(r.sourcePreflight,"PASS_SOURCE_ONLY");
 assert.equal(r.releaseAuthorized,false);
 assert.equal(r.blenderExecuted,false);
 assert.equal(r.debBuilt,false);
 assert.equal(r.godotDeviceVerified,false);
});
test("nonexistent source root is RED",()=>{
 const r=auditProposed(sha,"/not-a-real-luhm-source");
 assert.equal(r.sourcePreflight,"RED");
 assert.ok(r.errors.length>0);
});
