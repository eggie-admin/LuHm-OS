/* Aramoor world preview: Vue is only UI; Babylon renders art; Godot owns game canon. */
import {createApp,h,ref,onMounted,onUnmounted} from "vue";
import world from "../../../../game/world/aramoorArchipelagoV1.json";
import {inspectAramoorWorld,reachableRegions,travelBetween} from "./aramoorGraph.mjs";
import {mountAramoorAtlas} from "./aramoorBrowserStage.mjs";

const graph=inspectAramoorWorld(world);
const byId=graph.byId;
const App={
  setup(){
    const active=ref("aramoorHarbor");
    const tide=ref("livingTide");
    const status=ref("Launching the archipelago...");
    const graphics=ref("Loading WebGL");
    const orbiting=ref(false);
    let stage=null;
    const accessible=ref(reachableRegions(world,active.value));
    function selectZone(id){
      const result=travelBetween(world,active.value,id);
      if(!result.ok){
        status.value=result.reason==="BRIDGE_NOT_CONNECTED"?
          "No direct bridge from "+byId.get(active.value).name+" to "+byId.get(id)?.name+". Travel through neighboring islands.":
          "That destination is not available.";
        return false;
      }
      active.value=id;
      accessible.value=reachableRegions(world,id);
      status.value=byId.get(id).beat;
      stage?.focus(id);
      return true;
    }
    function setTide(){
      if(!stage)return;
      const next=tide.value==="livingTide"?"ghostTide":"livingTide";
      stage.setTide(next);
      tide.value=next;
      status.value=next==="ghostTide"?"Ghost Tide. The same islands tell a different story.":"Living Tide. Dawn has returned to the coast.";
    }
    function reset(){
      stage?.overview();
      active.value="aramoorHarbor";
      accessible.value=reachableRegions(world,active.value);
      orbiting.value=false;stage?.orbit(false);
      status.value="Aramoor Harbor. Explore linked islands; choose your tide.";
    }
    function keyboard(e){
      if(e.altKey||e.metaKey||e.ctrlKey || /INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName||""))return;
      if(e.key.toLowerCase()==="t")setTide();
      if(e.key==="Escape")reset();
    }
    onMounted(()=>{
      try{
        stage=mountAramoorAtlas(document.getElementById("aramoor-canvas"),world,{onPick:selectZone});
        const meta=stage.metrics();
        graphics.value=meta.renderer+" · "+meta.meshCount+" meshes";
        status.value="Nine regions, twelve crossings. Follow the glowing bridges. Tap a neighboring island.";
        globalThis.__aramoorProof=Object.freeze({ready:true,metrics:()=>stage?.metrics()??null,travel:selectZone,tide:()=>tide.value});
        window.addEventListener("keydown",keyboard);
      }catch(error){
        graphics.value="WEBGL UNAVAILABLE";
        status.value=String(error?.message||error).slice(0,170);
        globalThis.__aramoorProof=Object.freeze({ready:false,error:status.value});
      }
    });
    onUnmounted(()=>{window.removeEventListener("keydown",keyboard);stage?.dispose();delete globalThis.__aramoorProof;});
    const button=(text,onClick,opts={})=>h("button",{type:"button",onClick,disabled:!stage,...opts},text);
    return ()=>h("main",{class:"aramoor-app"},[
      h("header",{class:"top-bar"},[
        h("div",{class:"branding"},[
          h("span",{class:"eyebrow"},"LUHM-OS · PROJECT PREMONITION"),
          h("h1","GHOST GIRLS OF ARAMOOR"),
          h("p",{class:"subtitle"},"Twin Tides · The Nine Isles")
        ]),
        h("div",{class:"build-tag",role:"status"},graphics.value)
      ]),
      h("section",{class:"hero"},[
        h("canvas",{id:"aramoor-canvas",tabindex:0,"aria-label":"Interactive three-dimensional Aramoor coast: drag to orbit, wheel to zoom, click neighboring island to travel"}),
        h("div",{class:"stage-overline"},[h("span",{class:"live-dot"}),tide.value==="livingTide"?"THE LIVING TIDE":"THE GHOST TIDE"]),
        h("div",{class:"stage-hint"},"DRAG TO ORBIT  ·  SCROLL TO ZOOM  ·  TAP A NEIGHBORING ISLAND"),
        h("div",{class:"tide-orb",title:"Two timelines share one coastline"},"☾")
      ]),
      h("section",{class:"lower"},[
        h("aside",{class:"region-panel"},[
          h("div",{class:"section-head"},[
            h("span",{class:"eyebrow"},"WORLD CHART"),
            h("strong","Nine islands")
          ]),
          h("nav",{id:"region-list","aria-label":"Travel by bridge"},world.zones.map((z,i)=>{
            const isHere=active.value===z.id;
            const reachable=accessible.value.includes(z.id);
            return h("button",{
              key:z.id,type:"button",class:["region",isHere?"current":"",reachable?"reachable":""],
              onClick:()=>selectZone(z.id),"aria-current":isHere?"location":undefined,
              "aria-disabled":(!isHere&&!reachable).toString(),
              "data-region":z.id
            },[
              h("span",{class:"region-num"},String(i+1).padStart(2,"0")),
              h("span",{class:"region-name"},z.name),
              h("span",{class:"region-icon"},isHere?"◆":reachable?"↗":"·")
            ]);
          }))
        ]),
        h("article",{class:"story-panel"},[
          h("div",{class:"section-head"},[
            h("span",{class:"eyebrow"},"WORLD EVENT"),
            h("strong",tide.value==="ghostTide"?"Echo timeline":"Present timeline")
          ]),
          h("div",{class:"location-name"},byId.get(active.value).name),
          h("p",{class:"story-text"},byId.get(active.value).beat),
          h("p",{class:"role-caption"},"Character scene socket: "+byId.get(active.value).npc.toUpperCase()+" · "+byId.get(active.value).biome),
          h("p",{class:"status-line",role:"status","aria-live":"polite","data-testid":"world-status"},status.value),
          h("div",{class:"toolbelt"},[
            button(tide.value==="ghostTide"?"☀ Return to Living Tide":"☾ Enter Ghost Tide",setTide,{
              "data-testid":"tide-toggle","aria-pressed":String(tide.value==="ghostTide"),class:"button-primary"}),
            button("◎ World View",reset,{"data-testid":"world-reset"}),
            button(orbiting.value?"Ⅱ Stop Orbit":"⟳ Orbit Camera",()=>{
              orbiting.value=!orbiting.value;
              stage?.orbit(orbiting.value);
            },{"aria-pressed":String(orbiting.value)})
          ])
        ])
      ]),
      h("footer",{class:"footnote"},[
        h("span","ORIGINAL PROCEDURAL 3D · VUE + BABYLON WEBGL · GODOT WORLD GRAPH"),
        h("span","Adventure basis: The Ghosts of Aramoor by JunkyardTornado · CC BY-SA 4.0 · Private concept proof; external character models not loaded.")
      ])
    ]);
  }
};
createApp(App).mount("#app");
