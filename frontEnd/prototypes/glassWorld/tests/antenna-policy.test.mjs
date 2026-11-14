import test from "node:test";
import assert from "node:assert/strict";
import {profiles,endpointUrl,widgetIntent} from "../src/antenna-policy.mjs";
test("antenna never opts into local rendering or inference",()=>{
  assert.equal(profiles.antenna.local3d,false);assert.equal(profiles.antenna.localInference,false);
  assert.equal(profiles.light.local3d,"optIn");assert.equal(profiles.light.autoplay,false);
});
test("remote endpoints require TLS, reject credentials and token-like URL fields",()=>{
  assert.equal(endpointUrl("https://studio.example/media"),"https://studio.example/media");
  assert.equal(endpointUrl("http://127.0.0.1:8765"),"http://127.0.0.1:8765/");
  for(const url of ["http://192.168.1.2/","javascript:alert(1)","file:///etc/passwd","https://u:p@studio.example/","https://studio.example/?token=a","https://studio.example/#secret","http://localhost.evil/"])
    assert.throws(()=>endpointUrl(url),undefined,url);
});
test("widget intent cannot carry execution authority or arbitrary actions",()=>{
  const request=widgetIntent("openGodot","raspberryPi","test-123");
  assert.equal(request.executionProof,false);assert.equal(request.encoding,"json");
  assert.equal(request.authority,"requestOnly");assert.ok(Object.isFrozen(request));
  assert.throws(()=>widgetIntent("shell","tablet","test-123"));
  assert.throws(()=>widgetIntent("openMedia","unknown","test-123"));
  assert.throws(()=>widgetIntent("openMedia","tablet","../test"));
});
