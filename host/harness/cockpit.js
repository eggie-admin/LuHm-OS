"use strict";
const $=id=>document.getElementById(id);
const state={pets:[],petIndex:0};

function isLoopback(){
  const h=location.hostname;
  return h==="127.0.0.1"||h==="localhost"||h==="::1";
}
function renderNetwork(cfg){
  const local=isLoopback();
  $("networkStatus").textContent=local?`${location.protocol}//${location.host}`:"Render HTTPS edge";
  $("networkNote").textContent=local?"IPv4 loopback development shell":"Public HTTP is redirected to HTTPS by Render; origin remains IPv4-only.";
  $("edgeBadge").textContent=local?"LOCAL / HTTP OK":"PUBLIC / HTTPS";
}
function renderLibraries(policy){
  const list=$("libraryList");list.textContent="";
  for(const lib of policy.libraries||[]){
    const el=document.createElement("span");el.className="chip";el.textContent=lib.name;list.appendChild(el);
  }
}
function showPet(){
  if(!state.pets.length)return;
  const pet=state.pets[state.petIndex%state.pets.length];
  $("petGlyph").textContent=pet.glyph||pet.name.slice(0,1);
  $("petName").textContent=pet.name;
  $("petRole").textContent=pet.role;
}
async function probeGodot(){
  try{
    const r=await fetch("/harness/godot-export/index.html",{method:"HEAD",cache:"no-store"});
    if(!r.ok)throw new Error("not staged");
    $("godotFrame").src="/harness/godot-export/index.html";
    $("godotFrame").style.display="block";
    $("godotEmpty").style.display="none";
    $("godotBadge").textContent="WEB EXPORT READY";
  }catch(_){
    $("godotBadge").textContent="EXPORT PENDING";
  }
}
async function boot(){
  const [cfg,pets]=await Promise.all([
    fetch("/harness/config.json",{cache:"no-store"}).then(r=>r.json()),
    fetch("/harness/pets.json",{cache:"no-store"}).then(r=>r.json())
  ]);
  state.pets=pets.pets||[];
  renderNetwork(cfg);
  renderLibraries(cfg.libraries||{});
  showPet();
  setInterval(()=>{state.petIndex=(state.petIndex+1)%Math.max(state.pets.length,1);showPet()},8000);
  $("petDock").addEventListener("click",()=>{state.petIndex=(state.petIndex+1)%Math.max(state.pets.length,1);showPet()});
  await probeGodot();
}
boot().catch(err=>{
  $("edgeBadge").textContent="HARNESS ERROR";
  console.error(err);
});
