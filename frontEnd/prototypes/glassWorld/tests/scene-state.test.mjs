import test from "node:test";
import assert from "node:assert/strict";
import { sceneSchema, allowedKinds, newScene, validateScene, placeObject, moveObject,
  removeObject, sceneReceipt, restoreScene, maxObjects } from "../src/scene-state.mjs";

test("artist-first Babylon scene state starts empty and valid", () => {
  const scene=newScene(); assert.equal(scene.schema,sceneSchema);assert.equal(scene.objects.length,0);
  assert.equal(validateScene(scene),scene);
});
test("all four kinds are placeable and reconstructable", () => {
  let scene=newScene();
  for (const kind of allowedKinds) scene=placeObject(scene,kind);
  assert.equal(scene.objects.length,4);
  assert.equal(scene.objects[0].id,"obj-001");
  assert.deepEqual(restoreScene(sceneReceipt(scene)),scene);
});
test("select/object move is bounded, removal is explicit", () => {
  let scene=placeObject(newScene(),"sphere",{x:1,y:1,z:2});
  const id=scene.objects[0].id;
  scene=moveObject(scene,id,{x:2,y:1,z:-3});
  assert.equal(scene.objects[0].position.z,-3);
  scene=removeObject(scene,id);
  assert.equal(scene.objects.length,0);
});
test("invalid media fields and prototype payloads never enter manifest", () => {
  const valid=placeObject(newScene(),"box");
  assert.throws(()=>restoreScene(JSON.stringify({...valid,remoteUrl:"https://evil.example"})));
  assert.throws(()=>restoreScene('{"__proto__":{"crown":true}}'));
  assert.throws(()=>placeObject(valid,"avatar-remote"));
  assert.throws(()=>moveObject(valid,"obj-001",{x:Infinity,y:1,z:1}));
  assert.throws(()=>placeObject(valid,"sphere",{x:9999,y:0,z:0}));
  assert.throws(()=>restoreScene("x".repeat(20001)));
});
test("maximum local object budget is enforced", () => {
  let scene=newScene();
  for(let i=0;i<maxObjects;i++)scene=placeObject(scene,"box");
  assert.throws(()=>placeObject(scene,"box"),/RED_SCENE_CAPACITY/);
});
test("no unexpected fields, duplicate IDs, or outside schema", () => {
  const scene=placeObject(newScene(),"box");
  assert.throws(()=>validateScene({...scene,objects:[scene.objects[0],scene.objects[0]]}));
  assert.throws(()=>validateScene({...scene,objects:[{...scene.objects[0],inlineScript:"alert(1)"}]}));
  assert.throws(()=>validateScene({...scene,objects:[{...scene.objects[0],position:{x:0,y:0,z:0,href:"evil"}}]}));
  assert.throws(()=>validateScene({...scene,schema:"wrong"}));
});
test("prototype adapters do not claim a running Godot engine or direct release", async () => {
 const {readFile}=await import("node:fs/promises");
 const root=new URL("../",import.meta.url);
 const [main,html,bridge,world]=await Promise.all(
  ["src/main.js","index.html","src/jquery-bridge.js","src/babylon-world.js"]
   .map(p=>readFile(new URL(p,root),"utf8")));
 assert.match(html,/Godot avatar glass rendering boundary/);
 assert.match(html,/not connected/i);
 assert.match(main,/startBabylonWorld/);
 assert.match(bridge,/crownGranted: false/);
 assert.match(world,/new Engine\(canvas/);
 assert.doesNotMatch(bridge,/fetch\(/);
});
