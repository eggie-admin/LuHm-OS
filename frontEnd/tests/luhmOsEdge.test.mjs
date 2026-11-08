import { test } from "node:test";
import assert from "node:assert/strict";
import {
  installLuHmOsEdgePlugin, isExactLuHmOs,
  luhmOsDisplayName, luhmOsPluginMethod, luhmOsEventName
} from "../jquery/luhm.osEdge.mjs";

function fakeJQuery() {
  const calls = [];
  const $ = element => ({
    trigger(name, args) { calls.push({ element, name, args }); }
  });
  $.fn = {};
  return { $, calls };
}

test("case-sensitive public name and jQuery method are separate exact identifiers", () => {
  assert.equal(luhmOsDisplayName, "LuHm-OS");
  assert.equal(luhmOsPluginMethod, "luhmOsEdge");
  assert.equal(luhmOsEventName, "luhmOs:edge:inspected");
  assert.equal(isExactLuHmOs("LuHm-OS"), true);
  for (const wrong of ["luhmOs", "LuHmOS", "Luhm-OS", "LUHM-OS", "luhm-os", "LuHm-Os"]) {
    assert.equal(isExactLuHmOs(wrong), false, wrong);
  }
});

test("$.fn registered once, chainable, read-only and event scoped", () => {
  const { $, calls } = fakeJQuery();
  const preexistingCockpit = function () {};
  $.fn.luhmCockpit = preexistingCockpit;
  assert.equal(installLuHmOsEdgePlugin($), $);
  assert.equal($.fn.luhmCockpit, preexistingCockpit);
  assert.equal($.fn.LuHmOsEdge, undefined);
  assert.equal($.fn["LuHm-OS"], undefined);
  const node = { role: "sourceOnlyView" };
  const selection = {
    each(cb) { cb.call(node); return this; }
  };
  assert.equal(
    $.fn.luhmOsEdge.call(selection, "inspect", {
      lane: "staticAssets", contentClass: "sha256Asset", condition: "baseline"
    }),
    selection
  );
  assert.equal(calls.length, 1);
  assert.equal(calls[0].name, "luhmOs:edge:inspected");
  assert.equal(calls[0].args[0].state, "IMMUTABLE_ELIGIBLE_SOURCE_ONLY");
  assert.equal(calls[0].args[0].runtime, "UNVERIFIED");
  assert.equal(calls[0].args[0].cloudflareCdnDeployed, false);
  assert.equal(calls[0].args[0].crown, "STOP");
  assert.equal($.fn.luhmOsEdge.displayName, "LuHm-OS");
  assert.equal($.fn.luhmOsEdge.publicNetworkAccess, false);
  assert.equal($.fn.luhmOsEdge.call(selection, "destroy"), selection);
});

test("case-sensitive command and collision fail closed without triggering events", () => {
  const { $, calls } = fakeJQuery();
  installLuHmOsEdgePlugin($);
  const sel = { each(fn) { fn.call({}); return this; } };
  assert.throws(() => $.fn.luhmOsEdge.call(sel, "Inspect", {
    lane: "publicMcp", contentClass: "staticHtml"
  }), /case-sensitive/);
  assert.throws(() => $.fn.luhmOsEdge.call(sel, "inspect", {
    lane: "PublicMcp", contentClass: "staticHtml"
  }), /unregistered/);
  assert.equal(calls.length, 0);
  assert.throws(() => installLuHmOsEdgePlugin($), /already registered/);
  assert.throws(() => installLuHmOsEdgePlugin({ fn: {} }), /jQuery function/);
});
