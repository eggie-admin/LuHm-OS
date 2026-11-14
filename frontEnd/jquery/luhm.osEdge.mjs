/** LuHm-OS strict-case jQuery plugin adapter for read-only Cloudflare Canon.
 *  Optional source plugin. Existing $.fn.luhmCockpit/$.fn.luhmParallax stay untouched.
 *  $.fn is jQuery; jQuery UI's optional $.widget factory is not required here.
 */
import { classifyCloudflareRequest, getLuHmCloudflareBrand } from "../core/cloudflareCanon.mjs";

export const luhmOsDisplayName = "LuHm-OS";
export const luhmOsPluginMethod = "luhmOsEdge";
export const luhmOsEventName = "luhmOs:edge:inspected";

/** Exact case is essential. Do not lowercase the product name, aliases or API keys. */
export function isExactLuHmOs(value) {
  return value === luhmOsDisplayName;
}

/** Install an additive chainable $.fn plugin, never overriding existing slots. */
export function installLuHmOsEdgePlugin($) {
  if (!$ || !$.fn || typeof $ !== "function") {
    throw new TypeError("jQuery function and $.fn are required");
  }
  if (Object.prototype.hasOwnProperty.call($.fn, luhmOsPluginMethod)) {
    throw new Error("jQuery plugin slot already registered: " + luhmOsPluginMethod);
  }
  function luhmOsEdge(command = "inspect", request = {}) {
    if (command === "destroy") {
      // This stateless adapter attaches no handlers or timers, so destroy is
      // an explicit chainable no-op. No global state is ever mutated.
      return this.each(function () {});
    }
    if (command !== "inspect") throw new TypeError("unknown case-sensitive luhmOsEdge command");
    const result = classifyCloudflareRequest(request);
    return this.each(function () {
      $(this).trigger(luhmOsEventName, [result]);
    });
  }
  luhmOsEdge.version = "1.0.0-source-only";
  luhmOsEdge.displayName = getLuHmCloudflareBrand().product;
  luhmOsEdge.publicNetworkAccess = false;
  luhmOsEdge.authorityEffect = "none";
  $.fn[luhmOsPluginMethod] = luhmOsEdge;
  return $;
}

// No auto-install. This file is an optional module, NOT injected into the
// production cockpit or the owner-private ChatGPT Site App.
