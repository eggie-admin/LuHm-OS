// Candidate story layer. Never modifies Godot save state or doctrine.
const $ = (id) => document.getElementById(id);
const scenes = Object.freeze({
  carriage: Object.freeze({
    heading:"The Forest of Forgotten Names",
    speaker:"NYX · THE CAT GODDESS",
    dialogue:"The carriage rolls beneath a million lanterns. Nyx settles into the knight's lap. ‘Human, you're permitted to rest. I'm on watch.’",
    choices:[["Ask about the lanterns","lanterns"],["Let Lum tell a joke","banter"],["Look toward the valley","arrival"]]
  }),
  lanterns: Object.freeze({
    heading:"The Lanterns Remember",
    speaker:"LUM · ONI COMPANION",
    dialogue:"‘The lanterns hold names of travelers who thought they had nowhere to belong,’ Lum whispers. Nyx presses a velvet paw against the knight's hand. ‘But yours isn't among them.’",
    choices:[["Keep Nyx close","arrival"],["Return to the carriage","carriage"]]
  }),
  banter: Object.freeze({
    heading:"An Outrageous Passenger",
    speaker:"LUM · ONI COMPANION",
    dialogue:"‘Darling! Our driver is a skeleton!’ The skeleton tips his hat. ‘Post-mortally employed, madam.’ Nyx yawns: ‘He has excellent references.’",
    choices:[["Pet Nyx and ride on","arrival"],["Back to the forest","carriage"]]
  }),
  arrival: Object.freeze({
    heading:"The Valley of Little Lanterns",
    speaker:"THE NARRATOR",
    dialogue:"At dawn, a valley of amber windows appears. A quiet cottage waits at the end of the path. On its porch, a single lantern burns beside a bowl of cat treats.",
    choices:[["Approach the cottage","sanctuary"],["Explore the town","town"],["Return to the carriage","carriage"]]
  }),
  town: Object.freeze({
    heading:"The Velvet Coffin",
    speaker:"LUM · ONI COMPANION",
    dialogue:"A bakery, an art studio and a tavern crowd the cobbled street. ‘I vote bakery,’ says Lum. ‘I vote tuna,’ says Nyx. The knight smiles.",
    choices:[["Find the cottage","sanctuary"],["Watch the lanterns","lanterns"]]
  }),
  sanctuary: Object.freeze({
    heading:"The Sanctuary's Keeper",
    speaker:"LADY MORRIGAN · PROPOSED STORY NPC",
    dialogue:"A violet-eyed keeper offers a small brass key. ‘The cottage is quiet. There is a chair by the window and room for a cat.’ Nyx purrs. Lum mutters, ‘I approve, provisionally.’",
    choices:[["Rest with Nyx by the hearth","rest"],["Explore Little Lanterns","town"]]
  }),
  rest: Object.freeze({
    heading:"The Knight Rests",
    speaker:"NYX · THE CAT GODDESS",
    dialogue:"The knight sets down his sword. Nyx curls beside him, purring softly. Nothing must be conquered tonight. Outside, the lanterns keep watch.",
    choices:[["Begin the chapter again","carriage"],["Visit the town tomorrow","town"]]
  })
});
const VALID = new Set(Object.keys(scenes));
const STORAGE_KEY = "luhmMoonlitCarriageCandidateV1";
const stage=$("stage"),lum=$("lum"),cat=$("cat"),status=$("notice");
const motion=window.matchMedia("(prefers-reduced-motion: reduce)");
let current="carriage", history=[], paused=false, blobTimeout=0, waveTimeout=0, blinkTimeout=0, checksPassed=false;
function safeScene(name){return VALID.has(name)?name:"carriage";}
function notice(text){status.textContent=text;}
function render(){
  const s=scenes[current];
  $("chapter").textContent="CHAPTER III / "+current.toUpperCase();
  $("heading").textContent=s.heading;
  $("dialogue").textContent=s.dialogue;
  $("speaker").textContent=s.speaker;
  stage.dataset.scene=current;
  const choices=$("choices"); choices.replaceChildren();
  for (const [label,next] of s.choices){
    const button=document.createElement("button");
    button.type="button";button.textContent=label;
    button.addEventListener("click",()=>navigate(next));
    choices.append(button);
  }
  $("back").disabled=history.length===0;
}
function navigate(id){
  if (!VALID.has(id))return;
  if(id!=="carriage" || current!=="carriage")history.push(current);
  if(history.length>30)history=history.slice(-30);
  current=id;render();
  if(id==="rest")notice("A place to rest. Story progress is session-only unless you save it.");
  else notice("Private narrative candidate. No game save or Canon mutation.");
}
$("back").addEventListener("click",()=>{if(history.length){current=safeScene(history.pop());render();}});
$("reset").addEventListener("click",()=>{current="carriage";history=[];render();notice("Chapter restarted. Local save untouched.");});
function blink(){
  if(paused || motion.matches)return;
  lum.classList.remove("is-blinking");void lum.offsetWidth;lum.classList.add("is-blinking");
  clearTimeout(blinkTimeout);blinkTimeout=setTimeout(()=>lum.classList.remove("is-blinking"),420);
}
function wave(){
  if(paused || motion.matches){notice("Motion is paused or reduced. Lum smiles at you.");return;}
  lum.classList.remove("is-waving");void lum.offsetWidth;lum.classList.add("is-waving");
  clearTimeout(waveTimeout);waveTimeout=setTimeout(()=>lum.classList.remove("is-waving"),1500);
}
function pet(){
  cat.classList.remove("is-petted");void cat.offsetWidth;
  if(!paused && !motion.matches)cat.classList.add("is-petted");
  clearTimeout(blobTimeout);blobTimeout=setTimeout(()=>cat.classList.remove("is-petted"),1400);
  notice("PRRRRRR. Nyx leans into your hand. +1 cozy moment. 🐾");
}
cat.addEventListener("click",pet);
$("pet").addEventListener("click",pet);
$("wave").addEventListener("click",wave);
$("blink").addEventListener("click",blink);
function setPaused(value){
  paused=Boolean(value);stage.classList.toggle("paused",paused);
  $("pause").textContent=paused?"Resume motion":"Pause motion";
  $("pause").setAttribute("aria-pressed",String(paused));
  if(paused){lum.style.removeProperty("--mx");lum.style.removeProperty("--my");}
}
$("pause").addEventListener("click",()=>setPaused(!paused));
function pointerMove(event){
  if(paused || motion.matches || document.hidden)return;
  const r=stage.getBoundingClientRect();
  const x=Math.max(-1,Math.min(1,(event.clientX-r.left-r.width/2)/(r.width/2)));
  const y=Math.max(-1,Math.min(1,(event.clientY-r.top-r.height/2)/(r.height/2)));
  lum.style.setProperty("--mx",(x*5).toFixed(2)+"px");
  lum.style.setProperty("--my",(y*3).toFixed(2)+"px");
}
stage.addEventListener("pointermove",pointerMove,{passive:true});
stage.addEventListener("pointerleave",()=>{lum.style.removeProperty("--mx");lum.style.removeProperty("--my");});
stage.addEventListener("keydown",(event)=>{
  if(event.target!==stage)return;
  if(event.key==="ArrowRight"){event.preventDefault();const next=scenes[current].choices[0]?.[1];if(next)navigate(next);}
  if(event.key==="ArrowLeft"){event.preventDefault();$("back").click();}
});
function validatedSave(value){
  return value && value.schema==="luhmOs.moonlitCarriageCandidate.v1" &&
    VALID.has(value.current) && Array.isArray(value.history) && value.history.length<=30 &&
    value.history.every(s=>typeof s==="string" && VALID.has(s));
}
$("save").addEventListener("click",()=>{
  try{localStorage.setItem(STORAGE_KEY,JSON.stringify({schema:"luhmOs.moonlitCarriageCandidate.v1",current,history}));notice("Saved only in this browser. No Godot or network write.");}
  catch{notice("Browser-local storage unavailable. This session continues normally.");}
});
try{
  const stored=localStorage.getItem(STORAGE_KEY);
  if(stored){const parsed=JSON.parse(stored);if(validatedSave(parsed)){current=parsed.current;history=[...parsed.history];}else localStorage.removeItem(STORAGE_KEY);}
}catch{ /* local storage may be blocked; fail closed */ }
render();
async function loadCanon(){
  const [truthRes,rulesRes] = await Promise.all([
    fetch("../../../doctrine/SOURCE_OF_TRUTH.json",{cache:"no-store"}),
    fetch("../../../game/demo/relationshipRulesV2.json",{cache:"no-store"})
  ]);
  if(!truthRes.ok || !rulesRes.ok)throw Error("Local source files unavailable; run from repository root.");
  const [truth,rules]=await Promise.all([truthRes.json(),rulesRes.json()]);
  if(truth.canonical_repository!=="eggie-admin/LuHm-OS" ||
     truth.authority!=="Professor" || truth.promotion!==false ||
     rules.schema!=="luhmOs.relationshipRules.v2" ||
     rules.crown!=="STOP" || rules.safety?.localStateOnly!==true)
      throw Error("Canon contract mismatch; candidate halted.");
  checksPassed=true;
  $("canon").textContent="CANON: AMBER / READ-ONLY CONTRACT VERIFIED";
}
loadCanon().catch((error)=>{$("canon").textContent="CANON: STOP / LOCAL CONTRACT UNVERIFIED";notice(error.message);});
const onVisibility=()=>{if(document.hidden)setPaused(true);};
document.addEventListener("visibilitychange",onVisibility);
const onMotion=()=>{if(motion.matches)setPaused(true);};
motion.addEventListener?.("change",onMotion);
window.addEventListener("pagehide",()=>{
  clearTimeout(waveTimeout);clearTimeout(blinkTimeout);clearTimeout(blobTimeout);
  stage.removeEventListener("pointermove",pointerMove);
  document.removeEventListener("visibilitychange",onVisibility);
  motion.removeEventListener?.("change",onMotion);
},{once:true});
