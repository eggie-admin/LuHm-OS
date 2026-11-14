/* Browser-local, user-chosen GLB character staging. Zero storage or backend writes. */
import { SceneLoader } from "@babylonjs/core/Loading/sceneLoader.js";
import { TransformNode } from "@babylonjs/core/Meshes/transformNode.js";
import { Vector3 } from "@babylonjs/core/Maths/math.vector.js";
import "@babylonjs/loaders/glTF/2.0";
import { inspectLocalGlb } from "./lum-local-model.mjs";

export function createLocalLumAvatar(scene, camera) {
  let current = null, epoch = 0;
  function release() {
    if (!current) return;
    for (const group of current.container.animationGroups) group.stop();
    current.pivot.dispose(true, false);
    current.container.removeAllFromScene();
    current.container.dispose();
    current = null;
  }
  async function load(file) {
    const receipt = await inspectLocalGlb(file);
    const job = ++epoch;
    // The Babylon file: lane accepts a browser File, not a remote URL.
    const container = await SceneLoader.LoadAssetContainerAsync("file:", file, scene, null, ".glb");
    if (job !== epoch) { container.dispose(); throw new Error("RED_STALE_GLB_LOAD"); }
    let pivot = null;
    try {
      container.addAllToScene();
      let lo = new Vector3(Infinity,Infinity,Infinity), hi = new Vector3(-Infinity,-Infinity,-Infinity);
      const validMeshes = container.meshes.filter(mesh => mesh.getTotalVertices?.() > 0);
      if (!validMeshes.length) throw new Error("RED_GLB_NO_GEOMETRY");
      for (const mesh of validMeshes) {
        mesh.computeWorldMatrix(true);
        const bb = mesh.getBoundingInfo().boundingBox;
        lo = Vector3.Minimize(lo,bb.minimumWorld);
        hi = Vector3.Maximize(hi,bb.maximumWorld);
      }
      const size = hi.subtract(lo);
      const dimension = Math.max(size.x,size.y,size.z);
      if (!Number.isFinite(dimension) || dimension < .000001 || dimension > 100000) throw new Error("RED_GLB_BOUNDS");
      pivot = new TransformNode("local-lum-pivot",scene);
      const roots = container.rootNodes?.length ? container.rootNodes :
        [...container.meshes, ...container.transformNodes].filter(node => !node.parent);
      for (const node of roots) if (node !== pivot) node.parent = pivot;
      const scale = 2.6 / dimension;
      pivot.scaling.setAll(scale);
      pivot.position.set(-((hi.x+lo.x)/2)*scale, -lo.y*scale, -((hi.z+lo.z)/2)*scale);
      const group = container.animationGroups.find(group => /run/i.test(group.name)) || container.animationGroups[0] || null;
      if (group) group.start(true,1);
      release();
      current = {container,pivot,group};
      camera.setTarget(new Vector3(0,1.3,0));
      camera.radius = 5;
      camera.lowerRadiusLimit = 2;
      camera.upperRadiusLimit = 18;
      return {...receipt,rendering:"WEBGL_LOCAL",rigAnimation:!!group,activeClip:group?.name || null};
    } catch(error) {
      // Never leak partially imported geometry or GPU textures on failure.
      if (pivot) pivot.dispose(true,false);
      container.removeAllFromScene();
      container.dispose();
      throw error;
    }
  }
  return {
    load,
    setRun(running) {
      if (!current?.group) return false;
      if (running) current.group.play(true);
      else current.group.pause();
      return true;
    },
    destroy() {++epoch;release();}
  };
}
