/* Isolated prototype. Browser owns Babylon world, not releases or signing. */
import { createApp, h, ref } from "vue";
import { newScene, placeObject, removeObject, moveObject, restoreScene, sceneReceipt } from "./scene-state.mjs";
import { sceneSignal } from "./jquery-bridge.js";
import { startBabylonWorld } from "./babylon-world.js";
const root = document.getElementById("glass-world");
const active = ref(newScene());
const selection = ref(null);
const status = ref("Scene ready. No Godot avatar or production API is active.");
let world;
function update(scene, kind, id = null) {
  active.value = scene;
  world.applyScene(scene);
  sceneSignal(root, kind, { objectId: id, revision: scene.revision });
}
function selectedObject() {
  return active.value.objects.find(object => object.id === selection.value) || null;
}
function changeAxis(axis, input) {
  const selected = selectedObject();
  const number = Number(input);
  if (!selected || input === "" || !Number.isFinite(number)) return;
  try {
    update(moveObject(active.value, selected.id, { ...selected.position, [axis]: number }), "moved", selected.id);
    status.value = selected.id + " moved.";
  } catch { status.value = "Invalid position. Use coordinates from -18 to 18."; }
}
const Inspector = {
  setup() {
    const axis = key => h("label", { class:"num" }, [
      h("span", key.toUpperCase()), h("input", { type:"number", min:-18, max:18, step:0.25,
        value: selectedObject()?.position[key] ?? 0,
        disabled: !selectedObject(),
        onChange: e => changeAxis(key, e.target.value) })
    ]);
    return () => h("section", [
      h("h2","Vue 3 · Scene Inspector"),
      h("p",{ class:"small" },"Add and place real Babylon meshes. Avatar glass stays separate."),
      h("h3","Place objects"),
      h("div",{ class:"controls" }, ["box","sphere","cylinder","torus"].map(kind =>
        h("button",{ onClick:()=> {
          try {
            const next = placeObject(active.value,kind,{x:(active.value.objects.length%6)*2-5,y:1,z:0});
            const id=next.objects.at(-1).id;
            selection.value=id;update(next,"placed",id);
            status.value=id+" placed ("+kind+").";
          } catch (error) {status.value=error.message;}
        }},"+ "+kind)
      )),
      h("h3","Objects ("+active.value.objects.length+")"),
      h("div",active.value.objects.map(item=>h("button",{
        class:"object"+(selection.value===item.id?" active":""),
        onClick:()=>{selection.value=item.id;sceneSignal(root,"selected",{objectId:item.id,revision:active.value.revision});}
      },item.id+" · "+item.kind))),
      h("h3",selection.value?"Selected: "+selection.value:"Select an object"),
      axis("x"),axis("y"),axis("z"),
      h("div",{class:"controls"},[
        h("button",{ class:"danger", disabled:!selectedObject(),onClick:()=>{
          const id=selection.value;
          try{update(removeObject(active.value,id),"removed",id);selection.value=null;status.value=id+" removed.";}
          catch(error){status.value=error.message;}
        }},"Remove"),
        h("button",{onClick:()=>{
          try{localStorage.setItem("luhmGlassWorldCandidate",sceneReceipt(active.value));
            sceneSignal(root,"saved",{revision:active.value.revision}); status.value="Saved in this browser only. Not a studio master."; }
          catch{status.value="Local storage unavailable.";}
        }},"Save locally"),
        h("button",{onClick:()=>{
          try {
            const text=localStorage.getItem("luhmGlassWorldCandidate");
            if(!text)throw Error("No saved scene");
            update(restoreScene(text),"saved");selection.value=null;status.value="Local scene restored.";
          } catch { status.value="Saved scene missing or invalid."; }
        }},"Restore")
      ]),
      h("p",{class:"small",role:"status"},status.value),
      h("p",{class:"small"},"Godot 4: avatar-only candidate. Native alpha bridge NOT VERIFIED on Samsung."),
      h("p",{class:"small"},"No remote uploads, model downloads, or release actions.")
    ]);
  }
};
world = startBabylonWorld(document.getElementById("babylon-stage"),id=>{
  selection.value=id;sceneSignal(root,"selected",{objectId:id,revision:active.value.revision});
});
world.applyScene(active.value);
const vue = createApp(Inspector);
vue.mount("#vue-inspector");
window.addEventListener("pagehide",()=>{vue.unmount();world.destroy();},{once:true});
