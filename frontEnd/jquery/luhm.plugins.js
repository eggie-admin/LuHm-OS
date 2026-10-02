(function ($, global) {
  "use strict";
  const plugins = Object.create(null);
  function register(name, factory) {
    if (!/^[a-z][A-Za-z0-9]*$/.test(name)) throw new Error("invalid LuHm plugin name");
    if (plugins[name]) throw new Error("duplicate LuHm plugin: " + name);
    if (typeof factory !== "function") throw new Error("LuHm plugin factory required");
    plugins[name] = factory;
  }
  function mount(name, root, options) {
    if (!plugins[name]) throw new Error("unknown LuHm plugin: " + name);
    return plugins[name]($(root), Object.freeze(Object.assign({}, options || {})));
  }
  function capabilities() {
    return Object.freeze({
      jquery: $.fn.jquery,
      jqueryUi: !!($.ui && $.widget),
      bootstrap: !!global.bootstrap
    });
  }
  global.LuHmPlugins = Object.freeze({ register: register, mount: mount, capabilities: capabilities });
}(jQuery, window));
