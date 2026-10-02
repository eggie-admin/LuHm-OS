(function (global) {
  "use strict";
  const defaults = Object.freeze({
    mode: "localFirst", assetBase: "./", remoteAssetBase: "",
    fallbackAssetBase: "./", assetPath: "assets/v1/"
  });
  function parse(text) {
    const out = Object.assign({}, defaults);
    String(text || "").split(/\r?\n/).forEach(function (line) {
      const clean = line.trim();
      if (!clean || clean.charAt(0) === "#" || clean.indexOf("=") < 1) return;
      const at = clean.indexOf("=");
      out[clean.slice(0, at).trim()] = clean.slice(at + 1).trim();
    });
    return Object.freeze(out);
  }
  function join(base, path) {
    return String(base || "./").replace(/\/?$/, "/") + String(path || "").replace(/^\//, "");
  }
  function resolver(config) {
    const cfg = config || defaults;
    return Object.freeze({
      local: function (path) { return join(cfg.assetBase, path); },
      remote: function (path) { return cfg.remoteAssetBase ? join(cfg.remoteAssetBase, path) : ""; },
      candidates: function (path) {
        const local = join(cfg.assetBase, path), remote = cfg.remoteAssetBase ? join(cfg.remoteAssetBase, path) : "";
        return remote ? [remote, local] : [local];
      }
    });
  }
  global.LuHmStaticService = Object.freeze({ defaults: defaults, parse: parse, resolver: resolver });
}(window));
