/* Babylon owns WORLD ONLY. Godot live avatar compositing is not claimed. */
import { Engine } from "@babylonjs/core/Engines/engine.js";
import { Scene } from "@babylonjs/core/scene.js";
import { ArcRotateCamera } from "@babylonjs/core/Cameras/arcRotateCamera.js";
import { Vector3 } from "@babylonjs/core/Maths/math.vector.js";
import { Color3, Color4 } from "@babylonjs/core/Maths/math.color.js";
import { HemisphericLight } from "@babylonjs/core/Lights/hemisphericLight.js";
import { PointLight } from "@babylonjs/core/Lights/pointLight.js";
import { StandardMaterial } from "@babylonjs/core/Materials/standardMaterial.js";
import { MeshBuilder } from "@babylonjs/core/Meshes/meshBuilder.js";
import { PointerEventTypes } from "@babylonjs/core/Events/pointerEvents.js";
import { validateScene } from "./scene-state.mjs";
import { buildCrownLayout } from "./crown-cathedral-layout.mjs";

export function startBabylonWorld(canvas, onSelected) {
  const engine = new Engine(canvas, true, { preserveDrawingBuffer: false, stencil: false });
  engine.setHardwareScalingLevel(Math.min(2, Math.max(1, window.devicePixelRatio / 1.6)));
  const scene = new Scene(engine);
  scene.clearColor = new Color4(0.035, 0.035, 0.08, 1);
  const camera = new ArcRotateCamera("orbit", -Math.PI / 2, Math.PI / 2.75, 11,
    new Vector3(0, 0.6, 0), scene);
  camera.lowerRadiusLimit = 3;
  camera.upperRadiusLimit = 24;
  camera.attachControl(canvas, true);
  new HemisphericLight("sky", new Vector3(0, 1, 0), scene).intensity = 0.8;
  const lamp = new PointLight("worklight", new Vector3(-4, 8, -5), scene);
  lamp.intensity = 65;
  const ground = MeshBuilder.CreateGround("stage", { width: 36, height: 36 }, scene);
  const floorMaterial = new StandardMaterial("floor", scene);
  floorMaterial.diffuseColor = new Color3(0.09, 0.10, 0.16);
  floorMaterial.specularColor = new Color3(0.12, 0.65, 0.8);
  ground.material = floorMaterial;
  const meshes = new Map();
  // Environment is decorative, self-contained and never enters editable object/rights state.
  let environmentMeshes = [];
  let environmentMaterials = [];
  function clearEnvironment() {
    for (const mesh of environmentMeshes) mesh.dispose();
    for (const material of environmentMaterials) material.dispose();
    environmentMeshes = []; environmentMaterials = [];
  }
  function setEnvironment(mode) {
    // Validate before disposing the visible environment.
    const layout = buildCrownLayout(mode);
    const materialCache = new Map();
    const newMeshes = [], newMaterials = [];
    try {
      for (const spec of layout.parts) {
        const {x,y,z} = spec.size;
        const name = "cathedral:" + spec.id;
        const mesh = spec.kind === "box"
          ? MeshBuilder.CreateBox(name, {width:x, height:y, depth:z}, scene)
          : spec.kind === "sphere"
          ? MeshBuilder.CreateSphere(name, {diameterX:x, diameterY:y, diameterZ:z, segments:12}, scene)
          : spec.kind === "torus"
          ? MeshBuilder.CreateTorus(name, {diameter:x, thickness:Math.min(.14,x*.18), tessellation:20}, scene)
          : MeshBuilder.CreateCylinder(name, {
              diameterBottom:x, diameterTop: /(?:horn|spire)-/.test(spec.id) ? .02 : x,
              height:y, tessellation:12}, scene);
        newMeshes.push(mesh);
        mesh.position.set(spec.position.x,spec.position.y,spec.position.z);
        if(spec.kind==="torus")mesh.rotation.x=Math.PI/2;
        const key=spec.color+":"+spec.glow;
        let material=materialCache.get(key);
        if(!material){
          material=new StandardMaterial("crown:"+key,scene);
          material.diffuseColor=Color3.FromHexString(spec.color);
          material.specularColor=new Color3(.18,.13,.26);
          if(spec.glow)material.emissiveColor=Color3.FromHexString(spec.color).scale(.34);
          materialCache.set(key,material);
          newMaterials.push(material);
        }
        mesh.material=material;
      }
    }catch(error){
      for(const mesh of newMeshes)mesh.dispose();
      for(const material of newMaterials)material.dispose();
      throw error;
    }
    clearEnvironment();
    environmentMeshes=newMeshes;environmentMaterials=newMaterials;
    return {mode:layout.mode,parts:layout.parts.length,originalProxyOnly:true};
  }
  setEnvironment("cathedral");
  function spawn(item) {
    const mesh = item.kind === "sphere" ? MeshBuilder.CreateSphere(item.id, { diameter: 1.5, segments: 18 }, scene)
      : item.kind === "cylinder" ? MeshBuilder.CreateCylinder(item.id, { diameter: 1.4, height: 1.7 }, scene)
      : item.kind === "torus" ? MeshBuilder.CreateTorus(item.id, { diameter: 1.6, thickness: 0.35, tessellation: 24 }, scene)
      : MeshBuilder.CreateBox(item.id, { size: 1.5 }, scene);
    mesh.position.set(item.position.x, item.position.y, item.position.z);
    mesh.metadata = { objectId: item.id };
    const material = new StandardMaterial("mat-" + item.id, scene);
    const swatches = { box: new Color3(0.93, 0.32, 0.66), sphere: new Color3(0.30, 0.82, 0.94),
      cylinder: new Color3(0.69, 0.51, 0.94), torus: new Color3(0.99, 0.77, 0.42) };
    material.diffuseColor = swatches[item.kind];
    material.specularColor = new Color3(0.4, 0.45, 0.5);
    mesh.material = material;
    meshes.set(item.id, mesh);
  }
  function applyScene(next) {
    validateScene(next);
    const ids = new Set(next.objects.map(x => x.id));
    for (const [id, mesh] of meshes) {
      if (!ids.has(id)) { mesh.dispose(); meshes.delete(id); }
    }
    for (const item of next.objects) {
      if (!meshes.has(item.id)) spawn(item);
      else meshes.get(item.id).position.set(item.position.x, item.position.y, item.position.z);
    }
  }
  scene.onPointerObservable.add(event => {
    if (event.type !== PointerEventTypes.POINTERPICK) return;
    const id = event.pickInfo?.pickedMesh?.metadata?.objectId;
    if (id) onSelected(id);
  });
  const render = () => { if (!document.hidden) scene.render(); };
  engine.runRenderLoop(render);
  const resize = () => engine.resize();
  const visible = () => { if (!document.hidden) engine.resize(); };
  window.addEventListener("resize", resize);
  document.addEventListener("visibilitychange", visible);
  return {
    applyScene,
    setEnvironment,
    destroy() {
      clearEnvironment();
      engine.stopRenderLoop(render);
      window.removeEventListener("resize", resize);
      document.removeEventListener("visibilitychange", visible);
      scene.dispose(); engine.dispose();
    }
  };
}
