import { createRelationshipStore } from "./relationshipCore.mjs";
import { inspectLive2dCandidate } from "./live2dAdapter.mjs";

const $ = (selector) => document.querySelector(selector);
const messages = $("#message");
const badge = $("#proof");
const portrait = $("#portrait");
let objectUrl = null;
let selectedId = null;
let store;

async function loadCanon() {
  const base = "../../../game/demo/";
  const [rulesRes,profilesRes] = await Promise.all([
    fetch(base + "relationshipRulesV2.json",{cache:"no-store"}),
    fetch(base + "originalCompanionProfilesV1.json",{cache:"no-store"})
  ]);
  if (!rulesRes.ok || !profilesRes.ok) throw Error("Canon files not reachable. Serve repository root over HTTP.");
  store = createRelationshipStore(await rulesRes.json(), await profilesRes.json());
  const saved = localStorage.getItem("luhmAtelierCandidateV2");
  if (saved) {
    try { if (!store.restore(JSON.parse(saved))) localStorage.removeItem("luhmAtelierCandidateV2"); }
    catch { localStorage.removeItem("luhmAtelierCandidateV2"); }
  }
  selectedId = store.roster()[0].id;
  for (const person of store.roster()) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = person.displayName;
    button.addEventListener("click",()=>{selectedId=person.id; message("Select an action to get a reaction.");render();});
    $("#roster").append(button);
  }
  for (const [eventId,label] of Object.entries({talk:"TALK",help:"HELP",explore:"EXPLORE",flirtElsewhere:"JEALOUSY",listen:"LISTEN",questComplete:"QUEST",apologize:"REPAIR"})) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent=label;
    button.addEventListener("click",()=>runAction(eventId));
    $("#actions").append(button);
  }
  render();
  badge.textContent="LOCAL DEMO | CANON CANDIDATE";
}
function message(line) { messages.textContent=line; }
function runAction(eventId) {
  const result=store.apply(selectedId,eventId);
  message(result.accepted?result.reaction:"Action rejected by Canon.");
  portrait.classList.remove("reacting");
  void portrait.offsetWidth;
  portrait.classList.add("reacting");
  render();
}
function render() {
  const person=store.roster().find((row)=>row.id===selectedId);
  const state=store.evaluate(selectedId);
  if (!person || !state) return;
  document.documentElement.style.setProperty("--accent","#"+person.hexColor);
  $("#name").textContent=person.displayName;
  $("#stats").textContent="TRUST "+state.stats.trust+"  ·  AFFECTION "+state.stats.affection+"  ·  JEALOUSY "+state.stats.jealousy;
  $("#bond").textContent=state.bondTier.toUpperCase()+"  /  "+state.bondScore+" BOND";
  $("#rewards").textContent=state.rewards.length ? "UNLOCKED: "+state.rewards.join(", ") : "COSTUME REWARDS LOCKED";
  for(const button of $("#roster").querySelectorAll("button"))button.setAttribute("aria-pressed",String(button.textContent===person.displayName));
}
$("#save").addEventListener("click",()=>{
  if(!store)return;
  try{localStorage.setItem("luhmAtelierCandidateV2",JSON.stringify(store.save())); message("Saved locally in this browser. No cloud upload.");}
  catch{message("Local save unavailable. State stays in session.");}
});
$("#reset").addEventListener("click",()=>{
  if(!store)return;
  store.reset();
  localStorage.removeItem("luhmAtelierCandidateV2");
  message("All relationship state reset.");render();
});
$("#file").addEventListener("change",(event)=>{
  const file=event.target.files?.[0];
  if(!file)return;
  if(!["image/png","image/jpeg","image/webp"].includes(file.type) || file.size>5*1024*1024){
    message("Use a local PNG, JPG or WebP image under 5 MB.");event.target.value="";return;
  }
  if(objectUrl)URL.revokeObjectURL(objectUrl);
  objectUrl=URL.createObjectURL(file);
  $("#userPortrait").src=objectUrl;
  $("#userPortrait").hidden=false;
  $("#illustration").hidden=true;
  message("Local portrait preview. File stays on your device; no upload.");
});
$("#fallback").addEventListener("click",()=>{
  if(objectUrl)URL.revokeObjectURL(objectUrl);
  objectUrl=null;$("#userPortrait").removeAttribute("src");
  $("#userPortrait").hidden=true;$("#illustration").hidden=false;
  message("Original animated CSS fallback restored.");
});
window.addEventListener("pagehide",()=>{if(objectUrl)URL.revokeObjectURL(objectUrl);});
const liveState=inspectLive2dCandidate(null);
$("#live2d").textContent="LIVE2D: "+liveState.mode+" | NO CUBISM RUNTIME OR MODEL LOADED";
loadCanon().catch((error)=>{badge.textContent="AMBER / CANON NOT LOADED";message(error.message);});
