import test from "node:test";
import assert from "node:assert/strict";
import {animationRequest,antennaBudget} from "../src/animation-contract.mjs";
import {widgetBridge} from "../src/widget-bridge.mjs";
test("animation protocol accepts bounded imported-clip operations only",()=>{
  assert.deepEqual(animationRequest("play","dance"),{schema:"luhmOs.avatarAnimation.v1",action:"play",clip:"dance",time:0});
  for(const args of [["shell"],["play",""],["play","x".repeat(129)],["seek","",NaN],["seek","",Infinity],["seek","",-1],["seek","",3601]])assert.throws(()=>animationRequest(...args));
  assert.equal(antennaBudget.totalBytes,12500000);
  assert.equal(antennaBudget.basis,"provisionalProjectBudgetNotHostLimit");
  assert.equal(antennaBudget.modelBytesInWidget,0);
});
function hostFixture(respond=true){
  const listeners=new Set(),sent=[];
  const win={addEventListener:(_name,fn)=>listeners.add(fn),removeEventListener:(_name,fn)=>listeners.delete(fn)};
  win.parent={postMessage(message){sent.push(message);if(respond&&message.id)queueMicrotask(()=>{
    const event={source:win.parent,data:{jsonrpc:"2.0",id:message.id,result:message.method==="ui/initialize"?{protocolVersion:"2026-01-26"}:{structuredContent:{executionEnabled:false}}}};
    listeners.forEach(fn=>fn(event));
  });}};
  return {win,sent,listeners};
}
test("widget initializes before allowlisted host calls and cleans up",async()=>{
  const f=hostFixture(),bridge=widgetBridge(f.win);
  await assert.rejects(bridge.callTool("luhm_open_antenna"));
  await bridge.initialize();
  await bridge.callTool("luhm_open_antenna");
  await assert.rejects(bridge.callTool("arbitrary_shell"));
  assert.equal(f.sent.filter(x=>x.method==="tools/call").length,1);
  assert.equal(f.sent[1].method,"ui/notifications/initialized");
  bridge.destroy();assert.equal(f.listeners.size,0);
});
test("host timeout is bounded and non-parent results are ignored",async()=>{
  const f=hostFixture(false),bridge=widgetBridge(f.win,()=>{},10);
  const pending=bridge.initialize();
  f.listeners.forEach(fn=>fn({source:{},data:{jsonrpc:"2.0",id:1,result:{protocolVersion:"2026-01-26"}}}));
  await assert.rejects(pending,/timed out/);bridge.destroy();
});
