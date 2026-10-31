/* Historical path kept for in-repo imports. Native DOM events replace isolated jQuery. 
 * The separately governed frontEnd/jquery legacy module is intentionally untouched.
 */
const allowed = new Set(["placed", "selected", "moved", "removed", "saved"]);
export function sceneSignal(root, kind, detail = {}) {
  if (!allowed.has(kind) || !root || typeof root.dispatchEvent !== "function" ||
      !detail || typeof detail !== "object" || Array.isArray(detail)) return false;
  const record = {
    schema: "luhmOs.babylonSceneEvent.v1",
    project: "Project Premonition", product: "LuHm-OS",
    action: kind, objectId: detail.objectId || null,
    revision: Number.isInteger(detail.revision) ? detail.revision : null,
    authorityEffect: "none", nativeDispatch: false, crownGranted: false
  };
  root.dispatchEvent(new CustomEvent("luhm:scene:" + kind, {
    detail: record, bubbles: false, composed: false
  }));
  return true;
}
