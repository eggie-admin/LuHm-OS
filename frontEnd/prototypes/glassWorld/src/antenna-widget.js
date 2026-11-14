import {createApp,h,ref} from "vue";
import {widgetBridge} from "./widget-bridge.mjs";
import {antennaBudget} from "./animation-contract.mjs";
import "../antenna.css";
const status=ref("Connecting to chat host…"),data=ref(null),brief=ref(""),busy=ref(false);
function renderResult(result){
  const value=result?.structuredContent;
  if(!value||!["luhmOs.antennaStatus.v1","luhmOs.creationPlan.v1"].includes(value.schema)||value.executionEnabled!==false){status.value="Unsupported host result";return;}
  data.value=value;status.value=value.schema==="luhmOs.creationPlan.v1"?"Animation draft ready. No render has run.":"Source services loaded. Device and runtime proof remain separate.";
}
const bridge=widgetBridge(window,renderResult);
async function invoke(name,args={}){if(busy.value)return;busy.value=true;try{renderResult(await bridge.callTool(name,args));}catch(error){status.value=error.message;}finally{busy.value=false;}}
createApp({setup(){return()=>h("div",[
  h("h1","LuHm OS · Animation antenna"),
  h("p","Phone controls and source-backed services. Models, motion and rendering stay outside this widget."),
  h("button",{disabled:busy.value,onClick:()=>invoke("luhm_open_antenna")},"Inspect cockpit services"),
  data.value?.services?h("section",[h("h2","Canon service map"),...data.value.services.map(service=>h("p",[h("strong",service.label+" · "),service.status]))]):null,
  h("section",[h("h2","Character animation"),h("p","Game work is on hold. Prepare a Blender → GLB → Godot/Babylon animation handoff."),
    h("label",["Animation brief",h("textarea",{value:brief.value,maxLength:2000,rows:3,onInput:e=>brief.value=e.target.value})]),
    h("button",{disabled:busy.value||!brief.value.trim(),onClick:()=>invoke("luhm_plan_antenna_creation",{recipe:"characterAnimation",target:"remoteStudio",brief:brief.value})},"Prepare animation plan")]),
  h("p",{role:"status","aria-live":"polite"},status.value),
  data.value?.schema==="luhmOs.creationPlan.v1"?h("pre",JSON.stringify(data.value,null,2)):null,
  h("small","Widget budget "+antennaBudget.widgetBytes+" bytes. No model downloads or autoplay.")
]);}}).mount("#antenna");
bridge.initialize().then(()=>invoke("luhm_open_antenna")).catch(error=>{status.value=error.message;});
window.addEventListener("pagehide",()=>bridge.destroy(),{once:true});
