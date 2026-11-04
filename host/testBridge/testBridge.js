"use strict";
let sessionToken = null;
const el = id => document.getElementById(id);
const msg = text => { el("message").textContent = text; };
async function api(path, {method="GET", value}={}) {
  const options={method,cache:"no-store",credentials:"omit",headers:{"Accept":"application/json"}};
  if (method === "POST") {
    if (!sessionToken) throw Error("Local session unavailable");
    options.headers["Content-Type"]="application/json";
    options.headers["X-TestBridge-Token"]=sessionToken;
    options.body=JSON.stringify(value);
  }
  const response=await fetch(path,options);
  if(!response.ok) throw Error("Local bridge rejected request ("+response.status+")");
  return await response.json();
}
async function session() {
  const data=await api("/api/testbridge/v1/session");
  if(data.schema!=="luhmOs.testBridgeSession.v1" || data.mode!=="LOCAL_VOLATILE_DEMO") throw Error("Unknown bridge");
  sessionToken=data.csrfToken;
}
async function status() {
  try {
    const data=await api("/api/testbridge/v1/status");
    el("status").textContent=JSON.stringify(data,null,2);
  } catch (err) {el("status").textContent="Not verified";msg(err.message);}
}
async function notes() {
  try {
    const data=await api("/api/testbridge/v1/notes");
    const list=el("notes");list.replaceChildren();
    for(const item of data.items){
      const li=document.createElement("li");
      const title=document.createElement("strong");title.textContent=item.displayName;
      const p=document.createElement("p");p.textContent=item.note;
      const del=document.createElement("button");del.type="button";del.textContent="Delete";
      del.addEventListener("click",async()=>{
        try{await api("/api/testbridge/v1/delete",{method:"POST",value:{id:item.id}});await notes();msg("Local record deleted.");}
        catch(err){msg(err.message);}
      });
      li.append(title,p,del);list.append(li);
    }
  }catch(err){msg(err.message);}
}
el("refresh").addEventListener("click",status);
el("list").addEventListener("click",notes);
el("noteForm").addEventListener("submit", async event=>{
  event.preventDefault();
  if(!el("consent").checked){msg("Consent is required.");return;}
  try{
    if(!sessionToken) await session();
    await api("/api/testbridge/v1/notes",{method:"POST",value:{
      displayName:el("displayName").value,
      note:el("note").value,
      consent:true
    }});
    el("noteForm").reset();await notes();msg("Saved in local memory only.");
  } catch(err){msg(err.message);}
});
session().then(()=>Promise.all([status(),notes()])).catch(err=>msg("Local session unavailable: "+err.message));
