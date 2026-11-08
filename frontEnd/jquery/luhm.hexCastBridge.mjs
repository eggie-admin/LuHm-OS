/** Explicit opt-in jQuery bridge. Does not touch existing luhmCockpit
 * or luhmParallax. No auto-install, no remote event listener or CAST dispatch.
 */
import {getLuHmHexCastIntent,luhmCastHexIdentity} from "../core/machineCastHexBridge.mjs";
export function installLuHmHexCastBridgePlugin($) {
  if (!$ || !$.fn || typeof $.fn.each !== "function") {
    throw new TypeError("RED_JQUERY_INSTANCE_REQUIRED");
  }
  const slot="luhmHexCastBridge";
  if (Object.prototype.hasOwnProperty.call($.fn, slot)) {
    throw new Error("RED_JQUERY_SLOT_COLLISION");
  }
  $.fn[slot]=function(request) {
    const intent=getLuHmHexCastIntent(request);
    return this.each(function() {
      const element=$(this);
      if (typeof element.trigger !== "function") throw new TypeError("RED_JQUERY_EVENT_REQUIRED");
      element.trigger(luhmCastHexIdentity.eventName, [intent]);
    });
  };
  return $;
}
