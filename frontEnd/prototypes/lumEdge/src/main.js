/* LuHm-OS Lum Edge: client-only Vue controls, Babylon GPU scene, zero backend actions. */
import {createApp,h,ref,onMounted,onUnmounted} from "vue";
import {Engine} from "@babylonjs/core/Engines/engine.js";
import {Scene} from "@babylonjs/core/scene.js";
import {ArcRotateCamera} from "@babylonjs/core/Cameras/arcRotateCamera.js";
import {Vector3} from "@babylonjs/core/Maths/math.vector.js";
import {Color3,Color4} from "@babylonjs/core/Maths/math.color.js";
import {HemisphericLight} from "@babylonjs/core/Lights/hemisphericLight.js";
import {PointLight} from "@babylonjs/core/Lights/pointLight.js";
import {StandardMaterial} from "@babylonjs/core/Materials/standardMaterial.js";
import {MeshBuilder} from "@babylonjs/core/Meshes/meshBuilder.js";
import {createLocalLumAvatar} from "./lumAvatar.js";

function mountWorld(canvas) {
  const engine=new Engine(canvas,true,{stencil:false,preserveDrawingBuffer:false},false);
  engine.setHardwareScalingLevel(Math.max(1,Math.min(2,(window.devicePixelRatio||1)/1.3)));
  const scene=new Scene(engine);
  scene.clearColor=new Color4(.025,.014,.05,1);
  const camera=new ArcRotateCamera("Midnight Orbit",-Math.PI/2,Math.PI/2.4,6,new Vector3(0,1.4,0),scene);
  camera.lowerRadiusLimit=2;camera.upperRadiusLimit=16;camera.wheelPrecision=70;
  camera.attachControl(canvas,true);
  const hemi=new HemisphericLight("moon",new Vector3(0,1,0),scene);hemi.intensity=1.15;
  const lamp=new PointLight("magenta-key",new Vector3(-2.5,4,-1.8),scene);lamp.intensity=24;
  const rim=new PointLight("cyan-rim",new Vector3(2,3.8,2),scene);rim.intensity=15;
  const mat=(name,hex,glow=0)=>{
    const m=new StandardMaterial(name,scene);
    m.diffuseColor=Color3.FromHexString(hex);
    m.emissiveColor=Color3.FromHexString(hex).scale(glow);
    m.specularColor=new Color3(.18,.13,.26);
    return m;
  };
  const stone=mat("dark-violet-stone","#201a36");
  const line=mat("magic-ring","#b972fc",.65);
  const night=mat("arch-dark","#2d1d45");
  const teal=mat("arch-glass","#6bbacb",.28);
  const floor=MeshBuilder.CreateGround("midnight-floor",{width:22,height:22},scene);floor.material=stone;
  for(let i=-2;i<=2;i++){
    const x=i*1.45;
    for(const side of [-1,1]){
      const pillar=MeshBuilder.CreateCylinder("pillar-"+i+"-"+side,{height:4,diameter:.28,tessellation:8},scene);
      pillar.position.set(x*1.5,2,side*3.5);pillar.material=night;
    }
  }
  for(const x of [-2.9,2.9]){
    const col=MeshBuilder.CreateCylinder("portal-col-"+x,{height:3.5,diameter:.34,tessellation:9},scene);
    col.position.set(x,1.75,1.5);col.material=night;
    const glow=MeshBuilder.CreateSphere("portal-gem-"+x,{diameter:.25,segments:10},scene);
    glow.position.set(x,3.4,1.5);glow.material=teal;
  }
  const arch=MeshBuilder.CreateTorus("portal-arch",{diameter:5.85,thickness:.16,tessellation:64},scene);
  arch.position.set(0,2.7,1.5);arch.rotation.x=Math.PI/2;arch.material=line;
  const sigils=[.95,1.30,1.65].map((size,i)=>{
    const ring=MeshBuilder.CreateTorus("sigil-"+i,{diameter:size*2,thickness:.035,tessellation:64},scene);
    ring.position.set(0,.04+i*.013,0);ring.material=line;ring.rotation.x=Math.PI/2;
    return ring;
  });
  const avatar=createLocalLumAvatar(scene,camera);
  let cast=0,orbit=false,stopped=false;
  const tick=()=>{
    if(document.hidden)return;
    if(orbit)camera.alpha+=.0014;
    const t=performance.now()*.001;
    for(let i=0;i<sigils.length;i++){
      sigils[i].rotation.z=t*(i%2?-.25:.19);
      sigils[i].setEnabled(i<=cast);
    }
    arch.rotation.z=Math.sin(t*.23)*.017;
    scene.render();
  };
  engine.runRenderLoop(tick);
  const resize=()=>engine.resize();
  window.addEventListener("resize",resize);
  document.addEventListener("visibilitychange",resize);
  return {
    async load(file){return avatar.load(file)},
    run(on){return avatar.setRun(on)},
    orbit(on){orbit=!!on},
    cast(){cast=(cast+1)%4;return cast},
    reset(){cast=0;orbit=false;camera.alpha=-Math.PI/2;camera.beta=Math.PI/2.4;camera.radius=5;return cast},
    dispose(){
      if(stopped)return;stopped=true;
      engine.stopRenderLoop(tick);
      window.removeEventListener("resize",resize);
      document.removeEventListener("visibilitychange",resize);
      avatar.destroy();scene.dispose();engine.dispose();
    }
  };
}
const App={
  setup(){
    const phase=ref("INITIALIZING"), status=ref("Starting the 3D scene."),sigils=ref(0);
    const loading=ref(false),running=ref(true),orbit=ref(false);
    let world=null;
    onMounted(()=>{
      try {world=mountWorld(document.querySelector("#lum-edge-canvas"));
        phase.value="WEBGL ACTIVE";
        status.value="Touch-drag to orbit. Select a private Lum .glb file to render the actual character.";}
      catch(e){phase.value="WEBGL BLOCKED";status.value="Browser restricted WebGL: "+String(e?.message||e).slice(0,120);}
    });
    onUnmounted(()=>world?.dispose());
    const choose=async(event)=>{
      const file=event.target.files?.[0];
      if(!file)return;
      if(!world){status.value="3D unavailable in this browser.";return;}
      loading.value=true;status.value="Validating your private GLB locally...";
      try{
        const receipt=await world.load(file);
        running.value=!!receipt.rigAnimation;
        status.value=receipt.meshes+" mesh(es), "+receipt.animations+" animations. "+(receipt.activeClip||"Static pose")+". Nothing uploaded.";
      }catch(e){status.value="GLB blocked: "+String(e?.message||e).slice(0,120);}
      finally{loading.value=false;event.target.value="";}
    };
    const button=(label,click,active=false)=>h("button",{type:"button",disabled:loading.value||!world,onClick:click,"aria-pressed":String(active)},label);
    return ()=>h("main",{class:"shell"},[
      h("header",{class:"head"},[
        h("div",[h("small","LuHm-OS"),h("h1","LuHm-OS"),h("p","Your local 3D studio")]),
        h("span",{class:"status"},phase.value)]),
      h("section",{class:"world", "aria-label":"Lum's interactive 3D scene"},[
        h("canvas",{id:"lum-edge-canvas","aria-label":"Touch-rotatable Babylon WebGL Midnight Cathedral"}),
        h("div",{class:"world-chip"},"Private models stay on this device"),
        h("div",{class:"world-hint"},"Drag to rotate · pinch to zoom")]),
      h("section",{class:"controls","aria-label":"Scene controls"},[
        button("▶ Run",()=>{if(!world.run(true))status.value="Load an animated GLB to run.";else running.value=true;},running.value),
        button("Ⅱ Pause",()=>{if(!world.run(false))status.value="Load an animated GLB first.";else running.value=false;},!running.value),
        button("⟳ Orbit",()=>{orbit.value=!orbit.value;world.orbit(orbit.value);},orbit.value),
        button("✦ CAST",()=>{sigils.value=world.cast();status.value="Midnight sigil "+sigils.value+"/3. ⚡";})
      ]),
      h("label",{class:"upload"} ,[
        h("span",loading.value?"Loading private model...":"Load your Lum .glb from this device"),
        h("input",{type:"file",accept:".glb,model/gltf-binary",disabled:loading.value,onChange:choose})
      ]),
      h("p",{class:"message",role:"status","aria-live":"polite"},status.value),
      h("footer",{class:"foot"},"Original procedural 3D world. GLB read only after local file selection. No remote model, native APK, or independent agents.")]);
  }
};
createApp(App).mount("#app");
