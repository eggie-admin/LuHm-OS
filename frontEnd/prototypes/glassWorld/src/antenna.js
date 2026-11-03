import {createApp,h,ref} from "vue";
import {profiles,endpointUrl,widgetIntent} from "./antenna-policy.mjs";

createApp({setup(){
  const mode=ref("antenna"),target=ref("remoteStudio"),address=ref("");
  const approved=ref(""),status=ref("No remote connection tested. No model or 3D engine loaded.");
  const receipt=ref(null);
  const brief=ref(""),recipe=ref("scenePreview"),planning=ref(false);
  async function planCreation(){
    if(planning.value)return;
    planning.value=true;
    try{
      if(target.value==="tablet")throw Error("Choose Raspberry Pi or remote studio for creation work.");
      const response=await fetch("./api/creation/plan",{method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({schema:"luhmOs.creationRequest.v1",recipe:recipe.value,target:target.value,brief:brief.value}),
        signal:AbortSignal.timeout(6000),credentials:"omit",cache:"no-store"});
      if(!response.ok)throw Error("Plan rejected or local Python bridge unavailable. Check the brief and server.");
      const data=await response.json();
      if(data.schema!=="luhmOs.creationPlan.v1"||data.executionEnabled!==false)throw Error("Unsupported plan response.");
      receipt.value=data;status.value="Draft plan ready. No AI call, render or upload has run.";
    }catch(error){status.value=error.message;}
    finally{planning.value=false;}
  }
  async function inspectLocal(){
    status.value="Checking local Python bridge…";
    try{
      const response=await fetch("./api/capabilities",{signal:AbortSignal.timeout(5000),credentials:"omit",cache:"no-store"});
      if(!response.ok)throw Error("Bridge unavailable");
      const data=await response.json();
      if(data.schema!=="luhmOs.antennaCapabilities.v1"||data.executionEnabled!==false)throw Error("Unsupported bridge");
      receipt.value=data;status.value="Local process inspected. Command presence does not prove a working tool or device permission.";
    }catch{status.value="Local Python bridge unavailable or incompatible. Use tools/kai9000Antenna.py; remote services remain untested.";}
  }
  function configure(){
    approved.value="";
    try{approved.value=endpointUrl(address.value);status.value="Address validated only. Open the service to authenticate; connectivity is unverified.";}
    catch(error){status.value=error.message;}
  }
  function emit(action){
    const request=widgetIntent(action,target.value,crypto.randomUUID());
    receipt.value=request;
    window.dispatchEvent(new CustomEvent("luhm:antenna:intent",{detail:request}));
    status.value="Widget request emitted locally. Host execution is unverified.";
  }
  return()=>h("div",[
    h("header",[h("h1","LuHm OS · Antenna"),h("small","SOURCE CANDIDATE")]),
    h("p","One studio front door. Keep the tablet light; choose where the work runs."),
    h("section",[
      h("h2","Workspace"),
      h("label",["Profile ",h("select",{value:mode.value,onChange:e=>mode.value=e.target.value},[
        h("option",{value:"antenna"},"Antenna · remote controls"),h("option",{value:"light"},"Light · optional local studio")])]),
      h("p",mode.value==="antenna"?"No local 3D, inference or media decoding starts here.":"The local Vue/Babylon studio opens only when requested. Godot is a separate service."),
      mode.value==="light"?h("a",{href:"./index.html"},"Open local 3D / HTML5 media studio"):null,
      h("small","Execution preference: "+profiles[mode.value].execution)
    ]),
    h("section",[
      h("h2","Remote media / Godot / studio"),
      h("p","Enter the HTTPS page supplied by VLC, your Pi or your studio host. Services open separately; this candidate does not proxy credentials or stream a desktop."),
      h("label",["Service address",h("input",{type:"url",value:address.value,placeholder:"https://studio.example/",onInput:e=>{address.value=e.target.value;approved.value="";}})]),
      h("div",{class:"row"},[h("button",{onClick:configure},"Validate address"),approved.value?h("a",{href:approved.value,target:"_blank",rel:"noopener noreferrer"},"Open service"):null])
    ]),
    h("section",[
      h("h2","Creation desk"),
      h("label",["Execution target ",h("select",{value:target.value,onChange:e=>target.value=e.target.value},["tablet","raspberryPi","remoteStudio"].map(t=>h("option",{value:t},t)))]),
      h("p","Choose a recipe and describe the result. Python prepares a draft plan for your selected remote target. Keep credentials out of the brief."),
      h("label",["Recipe ",h("select",{value:recipe.value,onChange:e=>recipe.value=e.target.value},[
        h("option",{value:"scenePreview"},"Blender scene preview"),h("option",{value:"imagePrepare"},"GIMP image preparation"),h("option",{value:"videoPreview"},"FFmpeg video preview")])]),
      h("label",["Creative brief",h("textarea",{value:brief.value,maxLength:2000,rows:4,onInput:e=>brief.value=e.target.value})]),
      h("button",{disabled:planning.value||!brief.value.trim(),onClick:planCreation},planning.value?"Preparing…":"Prepare draft plan")
    ]),
    h("section",[
      h("h2","Chat widget boundary"),
      h("button",{onClick:inspectLocal},"Inspect local Python bridge"),
      h("div",{class:"row"},["inspectCapabilities","openMedia","openGodot","inspectJob"].map(action=>h("button",{onClick:()=>emit(action)},action))),
      h("p","Requests carry no shell commands or tokens. A separately implemented host adapter must authorize, execute and return evidence."),
      receipt.value?h("pre",JSON.stringify(receipt.value,null,2)):null
    ]),
    h("p",{role:"status","aria-live":"polite"},status.value),
    h("small","JSON control messages; binary assets stay files. Base64 is reserved for bounded text-only transports. No automatic remote calls, storage or publication.")
  ]);
}}).mount("#antenna");
