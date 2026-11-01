import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import worker from "../host/edge/goddessGlassCapabilityWorker.mjs";

const source=(file)=>readFileSync(new URL("../"+file,import.meta.url),"utf8");
const policy=JSON.parse(source("doctrine/goddessGlassDomBridgeV1.json"));
const fixture=JSON.parse(source("publicationSite/goddessGlassCapabilities.v1.json"));

test("restricted DOM, no SQL or Cloudflare dependency at boot",()=>{
  assert.equal(policy.status,"STAGED_NO_REMOTE_DEPLOY");
  assert.equal(policy.sqlPolicy,"SQL_BACKEND_ONLY_NEVER_DOM_CLIENT");
  assert.equal(policy.mode,"OFFLINE_DEFAULT_EXPLICIT_USER_TAP_ONLY");
  for(const v of Object.values(policy.release))assert.equal(v,false);
  for(const k of ["credentialsInBrowser","directSQLFromBrowser","remoteWrite",
       "privilegedAdminPublic","remoteHTMLInjection","autoCloudFallback"]){
    assert.equal(policy.permissions[k],false,k);
  }
  const page=source("publicationSite/goddessGlassStudio.html");
  assert.match(page,/connect-src 'self'/);
  assert.match(page,/credentials:'omit'/);
  assert.match(page,/mode:'same-origin'/);
  assert.match(page,/button\.addEventListener\('click',async\(\)=>/);
  assert.match(page,/startFallback/);
  assert.doesNotMatch(page,/X-LuHm-Control-Token|localStorage|WebSocket|SELECT \*/);
});

test("static fixture and optional edge share a strict read-only capability schema",async()=>{
  const answer=await worker.fetch(new Request("https://test.invalid/api/glass/capabilities"));
  assert.equal(answer.status,200);
  assert.equal(answer.headers.get("access-control-allow-origin"),null);
  const fromEdge=await answer.json();
  for(const desc of [fixture,fromEdge]){
    assert.equal(desc.schema,"luhmOs.goddessGlassCapabilities.v1");
    assert.equal(desc.runtime,"NOT_ATTESTED");
    assert.equal(desc.sqlAccess,"BACKEND_ONLY");
    assert.equal(desc.writeAuthority,false);
    assert.equal(desc.cloudflareActive,false);
    assert.deepEqual(desc.capabilities.map(x=>x.id),
      ["glassViewer","assetCatalog","renderStatus","studioReceipts"]);
    assert.equal(desc.capabilities[1].status,"notConnected");
  }
});

test("optional worker rejects remote writes, arbitrary paths and admin routes",async()=>{
  for(const method of ["POST","PUT","PATCH","DELETE"]){
    const r=await worker.fetch(new Request("https://test.invalid/api/glass/capabilities",{method}));
    assert.equal(r.status,405);
  }
  for(const path of ["/api/sql","/admin","/api/glass/files","/api/glass/capabilities/extra"]){
    const r=await worker.fetch(new Request("https://test.invalid"+path));
    assert.equal(r.status,404);
  }
});