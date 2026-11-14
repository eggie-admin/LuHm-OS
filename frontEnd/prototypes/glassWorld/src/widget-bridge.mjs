/* MCP Apps standard bridge. Restrict UI calls, bound wait time, trust only parent. */
const allowed=new Set(["luhm_open_antenna","luhm_plan_antenna_creation"]);
export function widgetBridge(win,onResult=()=>{},timeoutMs=8000){
  let id=0,ready=false;const pending=new Map();
  function call(method,params){
    if(win.parent===win)return Promise.reject(Error("Chat host unavailable"));
    if(pending.size>=4)return Promise.reject(Error("Host busy"));
    return new Promise((resolve,reject)=>{
      const key=++id,timer=setTimeout(()=>{pending.delete(key);reject(Error("Host timed out"));},timeoutMs);
      pending.set(key,{resolve,reject,timer});
      win.parent.postMessage({jsonrpc:"2.0",id:key,method,params},"*");
    });
  }
  function receive(event){
    if(event.source!==win.parent)return;
    const message=event.data;if(!message||message.jsonrpc!=="2.0")return;
    if(pending.has(message.id)){
      const p=pending.get(message.id);pending.delete(message.id);clearTimeout(p.timer);
      if(message.error)p.reject(Error("Host request rejected"));else p.resolve(message.result);
    }else if(ready&&message.method==="ui/notifications/tool-result")onResult(message.params);
  }
  win.addEventListener("message",receive);
  return {
    async initialize(){
      const result=await call("ui/initialize",{appInfo:{name:"luhm-antenna",version:"0.1.0"},appCapabilities:{availableDisplayModes:["inline","fullscreen"]},protocolVersion:"2026-01-26"});
      if(!result||result.protocolVersion!=="2026-01-26")throw Error("Unsupported host protocol");
      ready=true;win.parent.postMessage({jsonrpc:"2.0",method:"ui/notifications/initialized",params:{}},"*");
    },
    callTool(name,args={}){
      if(!ready)return Promise.reject(Error("Host not initialized"));
      if(!allowed.has(name))return Promise.reject(Error("Tool not allowed"));
      return call("tools/call",{name,arguments:args});
    },
    destroy(){ready=false;win.removeEventListener("message",receive);for(const p of pending.values()){clearTimeout(p.timer);p.reject(Error("Widget closed"));}pending.clear();}
  };
}
