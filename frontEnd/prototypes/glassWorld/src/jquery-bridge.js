/* Independent jQuery plugin, leaving accepted luhm.cockpit.js unchanged. */
import $ from "jquery";
const allowed = new Set(["placed", "selected", "moved", "removed", "saved"]);
$.fn.luhmSceneBridge = function (kind, detail = {}) {
  if (!allowed.has(kind) || !detail || typeof detail !== "object") return this;
  const record = {
    schema: "luhmOs.babylonSceneEvent.v1",
    project: "Project Premonition", product: "LuHm-OS",
    action: kind, objectId: detail.objectId || null,
    revision: Number.isInteger(detail.revision) ? detail.revision : null,
    authorityEffect: "none", nativeDispatch: false, crownGranted: false
  };
  return this.each(function () { $(this).trigger("luhm:scene:" + kind, [record]); });
};
export function sceneSignal(root, kind, detail) { $(root).luhmSceneBridge(kind, detail); }
