import {createRelationshipStore} from "../companionAtelier/relationshipCore.mjs";
const root=new URL("../../../game/demo/",import.meta.url);
const documents={
  inventory:"gameLayerBuildInventoryV1.json",
  profiles:"originalCompanionProfilesV1.json",
  rules:"relationshipRulesV2.json",
  mods:"modInspirationCatalogV1.json"
};
const ACTIONS=Object.freeze({talk:"TALK",help:"HELP",explore:"EXPLORE",flirtElsewhere:"JEALOUSY",listen:"LISTEN",questComplete:"QUEST",apologize:"REPAIR"});
export function createLayerConsoleView(inventory,profiles,rules,mods){
  if(inventory?.schema!=="luhmOs.gameLayerBuildInventory.v1" ||
     inventory?.canon?.crown!=="STOP" || inventory?.rules?.productionSqlMutation!==false ||
     inventory?.rules?.backendPluginEdited!==false ||
     inventory?.rules?.externalModsDownloaded!==false)throw Error("RED_GAME_INVENTORY");
  if(!Array.isArray(inventory.components) || inventory.components.length<18 ||
     new Set(inventory.components.map(c=>c.id)).size!==inventory.components.length)throw Error("RED_COMPONENTS");
  if(!Array.isArray(mods?.sources)||mods.sources.length<8 ||
     mods.sources.some(s=>s.fileReuse!==false))throw Error("RED_MOD_RESEARCH");
  const store=createRelationshipStore(rules,profiles);
  if(store.roster().length!==3)throw Error("RED_ADULT_ROSTER");
  return Object.freeze({store,components:inventory.components.map(c=>({...c})),
     references:mods.sources.map(s=>({id:s.id,title:s.title,game:s.game,url:s.url,author:s.author})),
     actions:{...ACTIONS},crown:"STOP",runtime:"BROWSER_ONLY_NOT_GODOT"});
}
async function getJson(filename){
  const res=await fetch(new URL(filename,root),{cache:"no-store"});
  if(!res.ok)throw Error("CANON_MISSING_"+filename);
  return res.json();
}
async function boot(){
  const [inventory,profiles,rules,mods]=await Promise.all(Object.values(documents).map(getJson));
  const app=createLayerConsoleView(inventory,profiles,rules,mods),$=id=>document.getElementById(id);
  let selected=app.store.roster()[0].id;
  function draw(){
    const c=app.store.roster().find(row=>row.id===selected),s=app.store.evaluate(selected);
    if(!c||!s)throw Error("RED_SELECTION");
    document.documentElement.style.setProperty("--accent","#"+c.hexColor);
    $("personName").textContent=c.displayName;
    $("stats").textContent="TRUST "+s.stats.trust+" · AFFECTION "+s.stats.affection+" · JEALOUSY "+s.stats.jealousy;
    $("bondTier").textContent=s.bondTier.toUpperCase()+" / "+s.bondScore+" BOND";
    for(const btn of $("roster").querySelectorAll("button"))btn.setAttribute("aria-pressed",String(btn.dataset.id===selected));
  }
  for(const c of app.store.roster()){
    const btn=document.createElement("button");btn.type="button";btn.textContent=c.displayName;btn.dataset.id=c.id;
    btn.addEventListener("click",()=>{selected=c.id;draw();});$("roster").append(btn);
  }
  for(const [eventId,label] of Object.entries(app.actions)){
    const btn=document.createElement("button");btn.type="button";btn.textContent=label;
    btn.addEventListener("click",()=>{const result=app.store.apply(selected,eventId);
      $("reaction").textContent=result.accepted?result.reaction:"REJECTED";draw();});
    $("actions").append(btn);
  }
  for(const c of app.components){
    const article=document.createElement("article");article.className="layerCard";
    const title=document.createElement("strong");title.textContent=c.id;const sub=document.createElement("small");
    sub.textContent=c.componentClass+" / "+c.path;article.append(title,sub);$("layers").append(article);
  }
  for(const entry of app.references){
    const li=document.createElement("li"),a=document.createElement("a"),small=document.createElement("small");
    a.href=entry.url;a.rel="noopener noreferrer";a.target="_blank";a.textContent=entry.title;
    small.textContent=entry.game+" / "+entry.author+" · RESEARCH ONLY";li.append(a,small);$("references").append(li);
  }
  $("proof").textContent="SOURCE COMPONENTS "+app.components.length+" · ORIGINAL CHARACTERS "+app.store.roster().length+" · MOD REFS "+app.references.length+" · CROWN STOP";
  draw();
}
if(typeof document!=="undefined"){
  boot().catch(error=>{document.getElementById("proof").textContent="AMBER / "+error.message;});
}
