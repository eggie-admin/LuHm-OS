(function ($) {
  "use strict";
  const fieldMap = Object.freeze({
    schema:"s", providerId:"p", capabilityId:"c", taskId:"t", sourceRef:"r",
    scopeId:"q", inputRefs:"i", outputRefs:"o", evidenceRefs:"e", workerId:"w",
    state:"x", timestamp:"z", budget:"b", command:"m", escalation:"g",
    authorityClass:"a", stopConditions:"k", requiredOutputs:"y"
  });
  const reverseMap = Object.freeze(Object.fromEntries(Object.entries(fieldMap).map(([k,v]) => [v,k])));

  function remap(value, map) {
    if (Array.isArray(value)) return value.map(item => remap(item, map));
    if (!value || typeof value !== "object") return value;
    const out = {};
    Object.keys(value).forEach(key => {
      const nextKey = map[key] || key;
      const nextValue = remap(value[key], map);
      if (nextValue === undefined || nextValue === null || nextValue === false || nextValue === "") return;
      out[nextKey] = nextValue;
    });
    return out;
  }

  function compact(manifest) {
    return remap(manifest || {}, fieldMap);
  }

  function expand(wire) {
    return remap(wire || {}, reverseMap);
  }

  function stringify(manifest) {
    return JSON.stringify(compact(manifest));
  }

  $.luhmManifestMin = Object.freeze({ fieldMap, compact, expand, stringify });
}(jQuery));
