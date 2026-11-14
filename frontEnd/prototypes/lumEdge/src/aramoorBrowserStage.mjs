/* Aramoor browser proof: original procedural Babylon geometry, no remote art imports or engine authority. */
import {Engine} from "@babylonjs/core/Engines/engine.js";
import {Scene} from "@babylonjs/core/scene.js";
import {ArcRotateCamera} from "@babylonjs/core/Cameras/arcRotateCamera.js";
import {Vector3} from "@babylonjs/core/Maths/math.vector.js";
import {Color3,Color4} from "@babylonjs/core/Maths/math.color.js";
import {HemisphericLight} from "@babylonjs/core/Lights/hemisphericLight.js";
import {DirectionalLight} from "@babylonjs/core/Lights/directionalLight.js";
import {PointLight} from "@babylonjs/core/Lights/pointLight.js";
import {ShadowGenerator} from "@babylonjs/core/Lights/Shadows/shadowGenerator.js";
import {GlowLayer} from "@babylonjs/core/Layers/glowLayer.js";
import {PBRMaterial} from "@babylonjs/core/Materials/PBR/pbrMaterial.js";
import {DynamicTexture} from "@babylonjs/core/Materials/Textures/dynamicTexture.js";
import {MeshBuilder} from "@babylonjs/core/Meshes/meshBuilder.js";
import {chooseRenderPolicy} from "./lumRenderPolicy.mjs";
import {inspectAramoorWorld} from "./aramoorGraph.mjs";

const DAY={sea:"#12566e",abyss:"#142d52",sky:"#243a60",lantern:"#ffe3b0",shore:"#6599a9",mist:"#6d8da6"};
const GHOST={sea:"#271943",abyss:"#130f31",sky:"#120e29",lantern:"#f8a8e7",shore:"#8657a4",mist:"#7965a1"};
const radians=Math.PI/180;
function hexColor(hex){return Color3.FromHexString(hex);}
function tint(hex,scale){return Color3.FromHexString(hex).scale(scale);}
function material(scene,name,hex,{metallic=0.05,roughness=0.8,emissive=0,alpha=1,bump=null}={}){
  const mat=new PBRMaterial(name,scene);
  mat.albedoColor=hexColor(hex);mat.metallic=metallic;mat.roughness=roughness;mat.alpha=alpha;
  mat.emissiveColor=tint(hex,emissive);
  if(bump){mat.bumpTexture=bump;mat.bumpTexture.level=.23;}
  return mat;
}
function bumpNormals(scene) {
  // Deterministic normal map generated locally from a height field, not a borrowed asset.
  const tex=new DynamicTexture("aramoor-normal-tile",{width:128,height:128},scene,false);
  const ctx=tex.getContext();
  const img=ctx.createImageData(128,128);
  const height=(x,y)=>Math.sin(x*.33)*.25+Math.sin(y*.47)*.2+Math.sin((x+y)*.18)*.25;
  for(let y=0;y<128;y++)for(let x=0;x<128;x++){
    const dx=height(x+1,y)-height(x-1,y);
    const dy=height(x,y+1)-height(x,y-1);
    const magnitude=Math.hypot(dx,dy,1.7);
    const index=(y*128+x)*4;
    img.data[index]=Math.round(127.5*(1-dx/magnitude));
    img.data[index+1]=Math.round(127.5*(1-dy/magnitude));
    img.data[index+2]=Math.round(127.5*(1+1.7/magnitude));
    img.data[index+3]=255;
  }
  ctx.putImageData(img,0,0);tex.update(false);
  tex.uScale=3;tex.vScale=3;
  return tex;
}
function createGeometry(scene,kind,name,options,position,mat,zoneId) {
  const mesh=kind==="box"?MeshBuilder.CreateBox(name,options,scene):
    kind==="cylinder"?MeshBuilder.CreateCylinder(name,options,scene):
    kind==="sphere"?MeshBuilder.CreateSphere(name,options,scene):
    kind==="torus"?MeshBuilder.CreateTorus(name,options,scene):
    MeshBuilder.CreateGround(name,options,scene);
  mesh.position.copyFrom(position);mesh.material=mat;
  if(zoneId)mesh.metadata={zoneId};
  return mesh;
}
function rng(seed){let state=(seed>>>0)||1;return ()=>{state=(Math.imul(1664525,state)+1013904223)>>>0;return state/4294967296;};}

export function mountAramoorAtlas(canvas,world,{onPick=()=>{}}={}) {
  const graph=inspectAramoorWorld(world);
  if(!canvas) throw new Error("CANVAS_MISSING");
  const engine=new Engine(canvas,true,{stencil:false,preserveDrawingBuffer:true},false);
  const policy=chooseRenderPolicy({
    webGlVersion:engine.webGLVersion,
    coarsePointer:globalThis.matchMedia?.("(pointer: coarse)").matches??false,
    reducedMotion:globalThis.matchMedia?.("(prefers-reduced-motion: reduce)").matches??false
  });
  const scale=Math.max(1,(globalThis.devicePixelRatio||1)/policy.maxPixelRatio);
  engine.setHardwareScalingLevel(scale);
  const scene=new Scene(engine);
  const center=new Vector3(26,0,26);
  const camera=new ArcRotateCamera("TwinTidesCamera",-1.18,1.12,111,center,scene);
  camera.lowerRadiusLimit=24;camera.upperRadiusLimit=154;
  camera.lowerBetaLimit=.27;camera.upperBetaLimit=1.44;
  camera.wheelPrecision=60;camera.pinchPrecision=135;
  camera.attachControl(canvas,true);
  const hemi=new HemisphericLight("softSky",new Vector3(-.3,1,.1),scene);hemi.intensity=1.12;
  const sun=new DirectionalLight("singleShadowKey",new Vector3(-.6,-1,.5),scene);
  sun.position=new Vector3(32,62,-35);sun.intensity=1.1;
  let shadow=null;
  if(policy.shadowMapSize){
    shadow=new ShadowGenerator(policy.shadowMapSize,sun);
    shadow.bias=.0012;
    shadow.normalBias=.02;
    shadow.useBlurExponentialShadowMap=true;
    shadow.blurKernel=12;
  }
  let glow=null;
  if(engine.webGLVersion===2 && !policy.defaultShadows){
    // Reduced-motion and low-power variants avoid the blur-glow pass.
    glow=null;
  } else if(engine.webGLVersion===2){
    try{glow=new GlowLayer("neonTideGlow",scene,{blurKernelSize:24});glow.intensity=.34;}catch{glow=null;}
  }
  const normalTex=bumpNormals(scene);
  const state={
    tide:"livingTide",selected:"aramoorHarbor",orbit:false,
    materialCache:new Map(),zoneMarkers:new Map(),animated:[],shadowCasters:[],disposed:false
  };
  const renderRoot={current:null};
  const pos=(zone)=>new Vector3(zone.grid[0]*world.cellSize,0,zone.grid[1]*world.cellSize);
  function paint(name,hex,opt={}) {
    const key=name+":"+hex+":"+JSON.stringify(opt);
    if(state.materialCache.has(key))return state.materialCache.get(key);
    const m=material(scene,name,hex,opt);
    state.materialCache.set(key,m);
    return m;
  }
  function terrain(parent,zone,tide,r) {
    const x=parent.x,z=parent.z;
    const color=tide==="ghostTide"?"#3b365b":zone.color;
    const stone=paint("rock-"+color,color,{roughness:.84,bump:normalTex});
    const sand=paint("rim-"+color,tide==="ghostTide"?"#5c4476":"#63838b",{roughness:.9});
    const glowMat=paint("glow-"+zone.id,tide==="ghostTide"?"#e4a0f5":zone.accent,{metallic:.18,roughness:.33,emissive:.58});
    const floor=createGeometry(scene,"cylinder","islandBase:"+zone.id,{diameterTop:19.5,diameterBottom:21.8,height:3.2,tessellation:14},
      new Vector3(x,-.7,z),sand,zone.id);
    const cap=createGeometry(scene,"cylinder","islandCap:"+zone.id,{diameterTop:18,diameterBottom:19.5,height:.7,tessellation:14},
      new Vector3(x,1,z),stone,zone.id);
    cap.receiveShadows=true;
    if(state.shadowCasters.length<32)state.shadowCasters.push(cap);
    const ring=createGeometry(scene,"torus","coastHalo:"+zone.id,{diameter:19.65,thickness:.16,tessellation:54},
      new Vector3(x,.64,z),glowMat,zone.id);
    ring.scaling.y=.1;
    const local=paint("lamps"+zone.id,tide==="ghostTide"?"#cf80ff":zone.accent,{metallic:.36,roughness:.3,emissive:.9});
    const beacon=createGeometry(scene,"cylinder","beacon:"+zone.id,{height:4.4,diameterTop:.54,diameterBottom:1.04,tessellation:8},
      new Vector3(x,3.4,z),paint("beacon-stone","#1f2035",{roughness:.5}),zone.id);
    if(state.shadowCasters.length<32)state.shadowCasters.push(beacon);
    createGeometry(scene,"sphere","beaconFlame:"+zone.id,{diameter:.75,segments:10},new Vector3(x,5.9,z),local,zone.id);
    const light=new PointLight("islandLight:"+zone.id,new Vector3(x,5.2,z),scene);
    light.intensity=2.1;light.range=12;light.diffuse=hexColor(tide==="ghostTide"?"#bf89ff":zone.accent);
    light.specular=hexColor(tide==="ghostTide"?"#ffb0e8":"#d2e9ff");
    light.shadowEnabled=false;
    const accents=paint("accentstone"+zone.id,zone.accent,{metallic:.2,roughness:.56,emissive:.18});
    const pillar=paint("building-stone"+zone.id,tide==="ghostTide"?"#27203e":"#38404b",{roughness:.65,bump:normalTex});
    const jewel=paint("jewel"+zone.id,tide==="ghostTide"?"#d5a6fd":zone.accent,{roughness:.23,metallic:.5,emissive:.7});
    const baseCount=zone.prop==="cave"?4:zone.prop==="grove"?7:5;
    for(let i=0;i<baseCount;i++){
      const a=i*Math.PI*2/baseCount+.34;
      const radius=5.2+r()*1.7, px=x+Math.cos(a)*radius, pz=z+Math.sin(a)*radius;
      if(zone.prop==="grove"){
        createGeometry(scene,"cylinder","treeTrunk:"+zone.id+":"+i,{height:2.6,diameterTop:.35,diameterBottom:.6,tessellation:6},new Vector3(px,2.45,pz),pillar,zone.id);
        createGeometry(scene,"sphere","moonfern:"+zone.id+":"+i,{diameter:2.1+r()*.7,segments:8},new Vector3(px,4.15,pz),jewel,zone.id);
      }else if(zone.prop==="cave"){
        createGeometry(scene,"cylinder","seaCaveTeeth:"+zone.id+":"+i,{height:3+r()*2,diameterTop:0,diameterBottom:1.3,tessellation:6},new Vector3(px,3,pz),pillar,zone.id);
      }else if(zone.prop==="coral"){
        createGeometry(scene,"cylinder","reefCoral:"+zone.id+":"+i,{height:2.1+r(),diameterTop:.23,diameterBottom:1.2,tessellation:5},new Vector3(px,2.3,pz),jewel,zone.id);
      }else if(zone.prop==="spire"){
        createGeometry(scene,"cylinder","spireColumn:"+zone.id+":"+i,{height:3+r()*1.4,diameterTop:.35,diameterBottom:1.1,tessellation:7},new Vector3(px,3,pz),pillar,zone.id);
        createGeometry(scene,"sphere","spireGem:"+zone.id+":"+i,{diameter:.55,segments:8},new Vector3(px,5.3,pz),jewel,zone.id);
      }else{
        createGeometry(scene,"box","lanternHouse:"+zone.id+":"+i,{width:2.5,height:2+r(),depth:2.4},new Vector3(px,2.5,pz),pillar,zone.id);
        createGeometry(scene,"sphere","roofLight:"+zone.id+":"+i,{diameter:.8,segments:8},new Vector3(px,4.3,pz),jewel,zone.id);
      }
    }
    const focal=zone.id==="ghostShipCavern";
    if(focal){
      const hull=paint("ghostHull",tide==="ghostTide"?"#6f416b":"#52414c",{metallic:.15,roughness:.56,bump:normalTex});
      createGeometry(scene,"box","ghostShipHull",{width:3,height:1.8,depth:8},new Vector3(x+3,2.05,z-1),hull,zone.id);
      createGeometry(scene,"cylinder","ghostShipMast",{height:8,diameter:.35,tessellation:8},new Vector3(x+3,6.5,z-1),pillar,zone.id);
      createGeometry(scene,"box","ghostShipSail",{width:.22,height:4.2,depth:3.7},new Vector3(x+3,6.6,z-1),paint("sail",tide==="ghostTide"?"#d1abea":"#ddd9d0",{roughness:.9}),zone.id);
    }
    const mainPort=createGeometry(scene,"torus","tidePortal:"+zone.id,{diameter:3.4,thickness:.15,tessellation:48},
      new Vector3(x+3,2.4,z+2),jewel,zone.id);
    mainPort.rotation.z=Math.PI*.13;
    state.animated.push(mainPort);
    return {floor,light,ring};
  }
  function bridge(a,b,i,tide) {
    const ap=pos(graph.byId.get(a)),bp=pos(graph.byId.get(b));
    const mid=Vector3.Center(ap,bp);
    const len=Vector3.Distance(ap,bp);
    const mat=paint("bridgeWood",tide==="ghostTide"?"#735d98":"#b39b7e",{roughness:.7});
    const rail=paint("rail",tide==="ghostTide"?"#ad85c9":"#737d89",{metallic:.24,roughness:.54});
    const yaw=Math.atan2(bp.x-ap.x,bp.z-ap.z);
    const deck=createGeometry(scene,"box","bridgeDeck:"+i,{width:2.65,height:.28,depth:len-13},new Vector3(mid.x,1.48,mid.z),mat);
    deck.rotation.y=yaw;
    // Rail posts stay within the deck; no invisible giant collision meshes.
    for(let k=0;k<3;k++){
      const f=(k-1)*((len-17)/3);
      for(const side of [-1,1]){
        const bx=mid.x+Math.sin(yaw)*f+Math.cos(yaw)*side*1.13;
        const bz=mid.z+Math.cos(yaw)*f-Math.sin(yaw)*side*1.13;
        createGeometry(scene,"cylinder","bridgePost:"+i+":"+k+":"+side,
          {height:1.3,diameter:.16,tessellation:6},new Vector3(bx,2.1,bz),rail);
      }
    }
  }
  function makeEnvironment(tide) {
    const palette=tide==="ghostTide"?GHOST:DAY;
    scene.clearColor=new Color4(...(tide==="ghostTide"?[.048,.035,.1,1]:[.07,.14,.23,1]));
    scene.fogMode=Scene.FOGMODE_EXP2;
    scene.fogColor=hexColor(palette.mist);
    scene.fogDensity=.006;
    hemi.diffuse=hexColor(tide==="ghostTide"?"#b5a1df":"#e4e6eb");
    sun.diffuse=hexColor(tide==="ghostTide"?"#bea3f3":"#ffe2b5");
    const sea=paint("tideOcean",palette.sea,{metallic:.34,roughness:.27,emissive:.11});
    createGeometry(scene,"ground","endlessTideOcean",{width:142,height:142,subdivisions:1},new Vector3(26,-2.65,26),sea);
    const abyss=paint("horizon",palette.abyss,{emissive:.09,roughness:.97});
    createGeometry(scene,"ground","deepHorizon",{width:150,height:150,subdivisions:1},new Vector3(26,-2.9,26),abyss);
    const moon=paint("moonCrystal",palette.lantern,{emissive:1.15,roughness:.2});
    const orb=createGeometry(scene,"sphere","horizonMoon",{diameter:7,segments:14},new Vector3(-28,30,-28),moon);
    state.animated.push(orb);
    const shimmer=paint("surfaceShimmer",palette.shore,{emissive:.35,roughness:.22,alpha:.48});
    for(let k=0;k<7;k++){
      const halo=createGeometry(scene,"torus","oceanRipples:"+k,{diameter:19+k*8,thickness:.08,tessellation:64},
        new Vector3(26,-2.52+k*.005,26),shimmer);
      halo.scaling.y=.09;state.animated.push(halo);
    }
  }
  function rebuild(tide) {
    if(!["livingTide","ghostTide"].includes(tide)) throw new Error("INVALID_TIDE");
    const prev=renderRoot.current;
    // Scene meshes/materials are disposed between states to keep rebuild count bounded.
    if(prev){
      for(const mesh of [...scene.meshes]) mesh.dispose(false,false);
      for(const light of [...scene.lights]) {
        if(light!==hemi && light!==sun) light.dispose();
      }
      for(const [key,mat] of state.materialCache){mat.dispose();}
      state.materialCache.clear();
    }
    state.animated.length=0;
    state.shadowCasters.length=0;
    const random=rng(world.seed+(tide==="ghostTide"?999:0));
    makeEnvironment(tide);
    for(const zone of world.zones){terrain(pos(zone),zone,tide,random);}
    world.links.forEach(([a,b],i)=>bridge(a,b,i,tide));
    if(shadow){
      const list=shadow.getShadowMap();
      if(list)list.renderList=policy.defaultShadows?state.shadowCasters:[];
    }
    state.tide=tide;
    renderRoot.current=true;
  }
  rebuild("livingTide");
  scene.onPointerDown=(_evt,pick)=>{
    const zoneId=pick?.pickedMesh?.metadata?.zoneId;
    if(zoneId && graph.byId.has(zoneId))onPick(zoneId);
  };
  let frames=0;
  let phase=0;
  const update=()=>{
    if(state.disposed || document.hidden)return;
    if(!policy.defaultShadows || state.orbit){
      phase+=engine.getDeltaTime()*.00025;
    }
    if(state.orbit)camera.alpha+=Math.min(engine.getDeltaTime(),48)*.00008;
    for(const item of state.animated){
      if(item?.name.startsWith("tidePortal:"))item.rotation.y+=Math.min(engine.getDeltaTime(),32)*.00015;
    }
    frames++;
    scene.render();
  };
  engine.runRenderLoop(update);
  const onResize=()=>engine.resize();
  window.addEventListener("resize",onResize);
  return Object.freeze({
    renderer:policy.renderer,
    focus(zoneId){
      const zone=graph.byId.get(zoneId);
      if(!zone) return false;
      state.selected=zoneId;
      const position=pos(zone);
      camera.setTarget(new Vector3(position.x,1,position.z));
      camera.radius=43;
      return true;
    },
    overview(){camera.setTarget(center);camera.radius=111;camera.alpha=-1.18;camera.beta=1.12;},
    setTide(tide){rebuild(tide);return state.tide;},
    orbit(enabled){state.orbit=Boolean(enabled);},
    metrics(){
      return Object.freeze({zoneCount:graph.zones,bridgeCount:graph.bridges,tide:state.tide,
        meshCount:scene.meshes.length,shadowEnabled:Boolean(shadow&&policy.defaultShadows),
        normalTexturePresent:Boolean(normalTex),frames,renderer:policy.renderer,webGlVersion:engine.webGLVersion});
    },
    dispose(){
      if(state.disposed)return;
      state.disposed=true;engine.stopRenderLoop(update);
      window.removeEventListener("resize",onResize);
      scene.dispose();engine.dispose();
    }
  });
}
