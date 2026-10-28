/* LuHm-OS: Project Premonition | pure, bounded scene state. No network or privilege. */
export const sceneSchema = "luhmOs.glassWorldScene.v1";
export const allowedKinds = Object.freeze(["box", "sphere", "cylinder", "torus"]);
export const maxObjects = 64;
const coordinateLimit = 18;
const coord = (value) => typeof value === "number" && Number.isFinite(value) && Math.abs(value) <= coordinateLimit;
function validObject(object) {
  return object && typeof object === "object" && !Array.isArray(object) &&
    Object.keys(object).sort().join(",") === "id,kind,position" &&
    typeof object.id === "string" && /^obj-[0-9]{3}$/.test(object.id) &&
    allowedKinds.includes(object.kind) &&
    object.position && Object.keys(object.position).sort().join(",") === "x,y,z" &&
    coord(object.position.x) && coord(object.position.y) && coord(object.position.z);
}
export function newScene() {
  return { schema: sceneSchema, objects: [], revision: 0 };
}
export function validateScene(scene) {
  if (!scene || typeof scene !== "object" || Array.isArray(scene) ||
      Object.keys(scene).sort().join(",") !== "objects,revision,schema" ||
      scene.schema !== sceneSchema || !Number.isSafeInteger(scene.revision) || scene.revision < 0 ||
      !Array.isArray(scene.objects) || scene.objects.length > maxObjects ||
      !scene.objects.every(validObject) ||
      new Set(scene.objects.map(object => object.id)).size !== scene.objects.length) {
    throw new Error("RED_INVALID_SCENE");
  }
  return scene;
}
export function placeObject(scene, kind, position = { x: 0, y: 0.8, z: 0 }) {
  validateScene(scene);
  if (!allowedKinds.includes(kind) || !coord(position?.x) || !coord(position?.y) || !coord(position?.z))
    throw new Error("RED_INVALID_OBJECT");
  if (scene.objects.length >= maxObjects) throw new Error("RED_SCENE_CAPACITY");
  let sequence = 1;
  const used = new Set(scene.objects.map(object => object.id));
  while (used.has("obj-" + String(sequence).padStart(3, "0"))) sequence++;
  if (sequence > 999) throw new Error("RED_SCENE_IDS");
  const object = { id: "obj-" + String(sequence).padStart(3, "0"), kind,
    position: { x: position.x, y: position.y, z: position.z } };
  return { schema: sceneSchema, objects: [...scene.objects, object], revision: scene.revision + 1 };
}
export function moveObject(scene, id, position) {
  validateScene(scene);
  if (!scene.objects.some(object => object.id === id) ||
      !coord(position?.x) || !coord(position?.y) || !coord(position?.z)) throw new Error("RED_MOVE");
  return { schema: sceneSchema, objects: scene.objects.map(object =>
    object.id === id ? { ...object, position: { x: position.x, y: position.y, z: position.z } } : object),
    revision: scene.revision + 1 };
}
export function removeObject(scene, id) {
  validateScene(scene);
  if (!scene.objects.some(object => object.id === id)) throw new Error("RED_REMOVE");
  return { schema: sceneSchema, objects: scene.objects.filter(object => object.id !== id),
    revision: scene.revision + 1 };
}
export function restoreScene(text) {
  if (typeof text !== "string" || text.length > 20000) throw new Error("RED_SCENE_SIZE");
  return validateScene(JSON.parse(text));
}
export function sceneReceipt(scene) {
  validateScene(scene);
  return JSON.stringify(scene);
}
