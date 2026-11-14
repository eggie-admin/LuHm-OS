/* LuHm-OS Canon Control Room: proposed, local-only candidate. No backend credentials. */
export const pinnedSourceRef = "a6e3ce843d099361a8696eab68869dcf367c4f26";
export const canonicalRoster = Object.freeze([
 "lum","urdDoctorGoddess","belldandySecretary","skuldResearch",
 "kiri","momo","shiori","kugi","tetsu","kaji","fumi","sumi","koe","yume","mediaAssetFactory"
]);
export const workflowStages = Object.freeze(["sanityCheck","audit","ingest","mutation","test","apply","continue","deploy"]);
export const routing = Object.freeze({
 architecture:["lum","skuldResearch","urdDoctorGoddess"],
 canon:["lum","belldandySecretary","urdDoctorGoddess"],
 health:["lum","urdDoctorGoddess","skuldResearch"],
 art:["lum","yume","sumi"],
 assets:["lum","sumi","yume"],
 install:["lum","skuldResearch","urdDoctorGoddess"],
 orchestration:["lum","belldandySecretary","skuldResearch"]
});
export const observedServices = Object.freeze([
 {id:"github",name:"GitHub source / CI",state:"SOURCE_OBSERVED",detail:"Canonical repository and main SHA inspected; no CI run claimed"},
 {id:"googleDrive",name:"Google Drive binaries",state:"SOURCE_OBSERVED",detail:"Inventory folders observed; bytes not bulk-ingested"},
 {id:"openAiPrimary",name:"OpenAI primary conversation",state:"CURRENT_CHAT",detail:"Human-facing task coordination only"},
 {id:"openAiMini",name:"OpenAI mini-agent second thread",state:"UNVERIFIED",detail:"Logical handoff contract; independent running thread not proven"},
 {id:"googleAiPro",name:"Google AI Pro consumer subscription",state:"HISTORICALLY_CONFIRMED",detail:"Google welcome email September 2, 2026; current subscription dashboard not directly checked"},
 {id:"googleAi",name:"Google AI / Gemini Developer API",state:"BLOCKED",detail:"October 30 Gemini API suspended-tier notice; November 6 Google Cloud billing termination notice. No authenticated reinstatement, live quota or authorized API smoke receipt"},
 {id:"render",name:"Render services",state:"UNVERIFIED",detail:"Workspace selection and exact live receipts required"},
 {id:"chatGptWidget",name:"ChatGPT app widget host",state:"UNVERIFIED",detail:"Host mount and invocation proof required"},
 {id:"godot",name:"Godot 4 / Android runtime",state:"UNVERIFIED",detail:"Build and device proof separate from source files"},
 {id:"localInstall",name:"Local install portal",state:"SOURCE_CONFIGURED",detail:"Explicit allow uses Android's normal OS installer; no bypass"}
]);
export function classifyAssetFile(name) {
 const suffix=String(name||"").toLowerCase().split(".").pop();
 if(["zip","rar","7z","tar","gz"].includes(suffix))return "archive";
 if(["blend","glb","gltf","fbx","obj","pck"].includes(suffix))return "models";
 if(["png","jpg","jpeg","webp","gif","ase","aseprite","svg"].includes(suffix))return "sprites";
 if(["mp4","mov","webm","mkv","avi"].includes(suffix))return "video";
 if(["wav","ogg","mp3","flac"].includes(suffix))return "audio";
 if(["gd","py","js","mjs","sh","bat","exe","dll"].includes(suffix))return "quarantineScripts";
 return "unclassified";
}
export function assetSummary(files) {
 const counts={},sizes={};let totalBytes=0;
 for(const file of files){
  const lane=classifyAssetFile(file.name);const bytes=Number(file.size)||0;
  counts[lane]=(counts[lane]||0)+1;sizes[lane]=(sizes[lane]||0)+bytes;totalBytes+=bytes;
 }
 return {count:files.length,totalBytes,counts,sizes};
}
export function createTaskEnvelope(input) {
 const lane=String(input.lane||"").trim();
 const intent=String(input.intent||"").trim();
 const taskId=String(input.taskId||"").trim();
 const scopeId=String(input.scopeId||"").trim();
 const sourceRef=String(input.sourceRef||"").trim();
 if(!routing[lane]||!intent||intent.length>500||!taskId||!scopeId||!(/^[0-9a-f]{40}$/).test(sourceRef))throw new Error("Invalid task identity, source, scope or lane");
 const workers=routing[lane];
 if(workers.some(w=>!canonicalRoster.includes(w))||workers.length>4||workers[0]!=="lum")throw new Error("Noncanonical agent route");
 return {
  schema:"luhmOs.aiTaskManifest.v2",taskId,scopeId,sourceRef,intent,
  providerId:"openAi",capabilityId:"supervisedTaskRouting",inputRefs:[],
  requiredOutputSchema:"luhmOs.aiTaskReview.v1",
  budget:{maxRequests:1,maxParallel:1,maxPasses:1},
  stopConditions:["scopeComplete","evidenceConflict","sourceMismatch","budgetExhausted","quarantineHeld"],
  authority:{mutation:false,green:false,crown:false},
  responseRequired:["providerId","taskId","sourceRef","scopeId","responseId","outputRefs","claims","timestamp"],
  lane,workerIds:workers,authorityClass:"PLAN_ONLY",
  status:"CANDIDATE_NOT_EXECUTED",crownStatus:"STOP",
  threads:{
   primaryConversation:{provider:"openAi",status:"CURRENT_CHAT_ONLY"},
   miniAgentEvidence:{provider:"openAi",status:"UNVERIFIED_NOT_RUNNING"}
  },
  maxParallelSupportWorkers:3,oneMutableSourceLane:true,
  providerPolicy:{googleAi:"BLOCKED_AFTER_2026_11_06_BILLING_NOTICE_UNTIL_REINSTATEMENT_AND_SMOKE",googleAiPro:"HISTORICALLY_CONFIRMED_SUBSCRIPTION_ONLY",fallback:"deterministicLocal"},
  artifactPolicy:{binaryAuthority:"googleDrive",sourceAuthority:"github",publicApproved:false},
  workflowStages:[...workflowStages],
  requiredEvidence:["exactSourceRef","taskIdScopeIdMatch","licenseAndProvenance","deterministicTestReceipt"],
  notes:"This is a planning envelope, not worker invocation, API authorization, deployment or Crown."
 };
}
export function inspectReceipt(value, expected={}) {
 if(!value||typeof value!=="object"||Array.isArray(value))return {accepted:false,reason:"NOT_OBJECT"};
 const taskId=String(value.taskId||""),scopeId=String(value.scopeId||""),sourceRef=String(value.sourceRef||"");
 if(!taskId||!scopeId||!(/^[0-9a-f]{40}$/).test(sourceRef))return {accepted:false,reason:"MISSING_EXACT_TASK_SOURCE_SCOPE"};
 for(const k of ["taskId","scopeId","sourceRef"]){
  if(expected[k]&&value[k]!==expected[k])return {accepted:false,reason:"IDENTITY_MISMATCH_"+k};
 }
 if(!Array.isArray(value.evidenceRefs)||!value.evidenceRefs.length)return {accepted:false,reason:"NO_EVIDENCE_REFS"};
 return {accepted:true,reason:"SHAPE_ACCEPTED_NOT_GREEN"};
}
export function canPromote({quarantine,rightsApproved,hostProof,deviceProof,humanApproval}) {
 return !quarantine&&!!rightsApproved&&!!hostProof&&!!deviceProof&&!!humanApproval;
}
const $=id=>document.getElementById(id);
const safeText=(id,s)=>{const el=$(id);if(el)el.textContent=String(s);};
const formattedBytes=n=>n>=1073741824?(n/1073741824).toFixed(2)+" GiB":n>=1048576?(n/1048576).toFixed(1)+" MiB":(n/1024).toFixed(1)+" KiB";
function downloadJson(data,name){
 const link=document.createElement("a");const blob=new Blob([JSON.stringify(data,null,2)+"\n"],{type:"application/json"});
 const url=URL.createObjectURL(blob);link.href=url;link.download=name;document.body.append(link);link.click();link.remove();
 setTimeout(()=>URL.revokeObjectURL(url),2000);
}
function initControlRoom(){
 const nav=[...document.querySelectorAll("[data-tab]")],panels=[...document.querySelectorAll("[data-panel]")];
 let current=0;let metadata=[],receiptReview=[],lastTask=null;let previewUrl=null;
 function show(index){
  current=(index+nav.length)%nav.length;
  nav.forEach((n,i)=>{const active=i===current;n.classList.toggle("active",active);n.setAttribute("aria-current",active?"page":"false");});
  panels.forEach((p,i)=>{p.hidden=i!==current;});
  safeText("viewTitle",nav[current].textContent.trim());
 }
 nav.forEach((btn,i)=>btn.addEventListener("click",()=>show(i)));
 let startX=0,startY=0;
 const surface=$("shell");
 surface.addEventListener("touchstart",e=>{if(e.touches.length===1){startX=e.touches[0].clientX;startY=e.touches[0].clientY;}},{passive:true});
 surface.addEventListener("touchend",e=>{
  if(!e.changedTouches.length)return;
  if(e.target.closest("input,textarea,button,a,select,pre"))return;
  const dx=e.changedTouches[0].clientX-startX,dy=e.changedTouches[0].clientY-startY;
  if(Math.abs(dy)>85&&Math.abs(dy)>Math.abs(dx)*1.6)show(current+(dy<0?1:-1));
 },{passive:true});
 const workerList=$("workerList");
 canonicalRoster.forEach((id,i)=>{
  const row=document.createElement("div");row.className="record";
  const name=document.createElement("strong");name.textContent=id;row.append(name);
  const state=document.createElement("span");state.className="state warn";state.textContent=i<4?"REGISTERED · QUARANTINED":"STANDBY · QUARANTINED";
  row.append(state);workerList.append(row);
 });
 const services=$("serviceList");
 observedServices.forEach(s=>{
  const el=document.createElement("div");el.className="serviceRecord";
  const heading=document.createElement("div");heading.className="serviceHeading";
  const title=document.createElement("strong");title.textContent=s.name;
  const status=document.createElement("span");status.className="state "+(s.state==="BLOCKED"?"stop":"warn");status.textContent=s.state;
  heading.append(title,status);const note=document.createElement("p");note.textContent=s.detail;el.append(heading,note);services.append(el);
 });
 workflowStages.forEach((stage,i)=>{
  const el=document.createElement("div");el.className="record";
  const name=document.createElement("strong");name.textContent=String(i+1).padStart(2,"0")+"  "+stage;
  const state=document.createElement("span");state.className="state warn";state.textContent=i<2?"SOURCE INSPECTED · NOT GREEN":"REQUIRES EXACT RECEIPT";
  el.append(name,state);$("stageList").append(el);
 });
 function intakeFiles(files){
  files=[...files].slice(0,10000);
  metadata=files.map(f=>({name:f.webkitRelativePath||f.name,size:f.size,lane:classifyAssetFile(f.name),sha256:null,rightsState:"UNKNOWN",publicApproved:false,source:"localBrowserSelection",status:"METADATA_ONLY_NOT_INGESTED"}));
  const sum=assetSummary(files);
  safeText("assetCount",String(sum.count));safeText("assetSize",formattedBytes(sum.totalBytes));
  safeText("assetLanes",Object.entries(sum.counts).map(([k,n])=>k+": "+n).join(" · ")||"No files selected");
  safeText("assetNotice","Selected files stay on this device; only names, sizes and categories enter this temporary draft. Archives are not unpacked or installed.");
 }
 $("filePicker").addEventListener("change",e=>intakeFiles(e.target.files));
 $("directoryPicker").addEventListener("change",e=>intakeFiles(e.target.files));
 $("portraitPicker").addEventListener("change",e=>{
  if(previewUrl){URL.revokeObjectURL(previewUrl);previewUrl=null;}
  const file=e.target.files&&e.target.files[0];if(!file)return;
  const allowed=["image/png","image/webp","image/jpeg","image/gif"];
  if(!allowed.includes(file.type)||file.size>20*1024*1024){safeText("assetNotice","Local portrait rejected: unsupported image type or larger than 20 MiB.");return;}
  previewUrl=URL.createObjectURL(file);const image=$("portraitPreview");image.src=previewUrl;image.hidden=false;
 });
 $("receiptPicker").addEventListener("change",async e=>{
  for(const file of [...e.target.files].slice(0,20)){
   if(file.size>2097152){receiptReview.push({file:file.name,status:"REJECTED_TOO_LARGE"});continue;}
   try{const packet=JSON.parse(await file.text());const verdict=inspectReceipt(packet,lastTask||{});receiptReview.push({file:file.name,...verdict,status:verdict.accepted?"CANDIDATE_SHAPE_ONLY":"REJECTED"});}
   catch{receiptReview.push({file:file.name,status:"REJECTED_JSON_PARSE"});}
  }
  safeText("receiptOutput",JSON.stringify(receiptReview,null,2));
  safeText("receiptCount",String(receiptReview.filter(r=>r.accepted).length));
 });
 $("exportAssets").addEventListener("click",()=>{
  const summary={schema:"luhmOs.localAssetCandidate.v1",sourceRef:pinnedSourceRef,sourceAuthority:"github",binaryAuthority:"googleDrive",status:"METADATA_ONLY",publicApproved:false,files:metadata};
  downloadJson(summary,"luhm-asset-candidate.json");
 });
 $("taskForm").addEventListener("submit",e=>{
  e.preventDefault();
  const lane=$("taskLane").value,intent=$("taskIntent").value;
  const input={taskId:"controlRoom"+Date.now(),scopeId:"privateLocalCandidate",sourceRef:pinnedSourceRef,lane,intent};
  try{lastTask=createTaskEnvelope(input);safeText("taskOutput",JSON.stringify(lastTask,null,2));$("exportTask").disabled=false;}
  catch(err){safeText("taskOutput","Rejected: "+err.message);}
 });
 $("exportTask").addEventListener("click",()=>{if(lastTask)downloadJson(lastTask,"luhm-task-envelope.json");});
 $("localAudit").addEventListener("click",()=>{
  const checks={
   canonicalName:"LuHm-OS",sourceRef:pinnedSourceRef,rosterCount:canonicalRoster.length,
   singleConversationalBoss:routing.architecture[0]==="lum",
   maxSupportWorkers:3,oneMutableSourceLane:true,
   quarantineHeld:true,rightsApproval:false,
   googleAiRuntime:"UNVERIFIED",secondThreadRuntime:"UNVERIFIED",
   installRuntime:"UNVERIFIED",publicDeployment:"NOT_AUTHORIZED"
  };
  safeText("auditOutput",JSON.stringify({schema:"luhmOs.localCandidateAudit.v1",scope:"staticClientChecksOnly",state:"CANDIDATE_NOT_GREEN",checks},null,2));
 });
 $("exportUpgrade").addEventListener("click",()=>{
  downloadJson({
   schema:"luhmOs.distributionUpgradeCandidate.v1",product:"LuHm-OS",sourceRef:pinnedSourceRef,
   stages:[...workflowStages],status:"PROPOSED_REVIEW_ONLY",
   merge:false,deploy:false,sign:false,crown:false,agentExecution:false,
   targets:["frontEndCockpit","godot4","chatGptWidget","localInstallPortal","privateDriveAssetIndex"],
   existingInventoryRef:"artAssets/manifests/archiveInventory.json",
   assetBytesNotCopied:true,rightsReviewPending:true,
   runtimeProofRequired:["chatGptAppHost","providerEntitlements","nativeInstall","deviceSmoke","serviceHealth"]
  },"luhm-distribution-upgrade-candidate.json");
 });
 show(0);
}
if(typeof document!=="undefined") {
 if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",initControlRoom);
 else initControlRoom();
}
