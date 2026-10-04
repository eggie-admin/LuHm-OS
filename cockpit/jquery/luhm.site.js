(function ($) {
  "use strict";

  const pluginName = "luhmSite";
  const defaults = {
    home: "cathedral",
    allowedRoutes: ["cathedral", "agents", "cms", "memory", "system"]
  };

  function stateFor(node, options) {
    const $node = $(node);
    let state = $node.data(pluginName);
    if (!state) {
      state = { options: $.extend({}, defaults, options || {}), route: null };
      $node.data(pluginName, state);
    }
    return state;
  }

  function route(node, name) {
    const $node = $(node);
    const state = stateFor(node);
    const target = String(name || state.options.home);
    if (!state.options.allowedRoutes.includes(target)) {
      throw new Error("site route not allowlisted: " + target);
    }
    $node.find("[data-luhm-site-view]").attr("hidden", true);
    $node.find('[data-luhm-site-view="' + target + '"]').removeAttr("hidden");
    state.route = target;
    $node.trigger("luhm:site:route", [{ route: target }]);
    return target;
  }

  const methods = {
    init(options) {
      return this.each(function () {
        const $node = $(this);
        const state = stateFor(this, options);
        $node.on("click.luhmSite", "[data-luhm-site-route]", function () {
          route($node[0], $(this).attr("data-luhm-site-route"));
        });
        route(this, state.options.home);
        $node.trigger("luhm:site:ready", [{ route: state.route }]);
      });
    },
    route(name) {
      return this.each(function () { route(this, name); });
    },
    destroy() {
      return this.each(function () { $(this).off(".luhmSite").removeData(pluginName); });
    }
  };

  $.fn[pluginName] = function (methodOrOptions) {
    if (methods[methodOrOptions]) {
      return methods[methodOrOptions].apply(this, Array.prototype.slice.call(arguments, 1));
    }
    if (typeof methodOrOptions === "object" || methodOrOptions === undefined) {
      return methods.init.apply(this, arguments);
    }
    throw new Error("unknown luhmSite method: " + methodOrOptions);
  };
}(jQuery));
