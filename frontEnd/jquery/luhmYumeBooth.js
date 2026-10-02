/* LuHm Yume Art Booth beta.
 * Front-end spectacle only. No provider credentials, no canon authority.
 */
(function ($) {
  "use strict";

  const pluginName = "luhmYumeBooth";

  function getState($root) {
    return $root.data(pluginName);
  }

  function emit($root, type, detail) {
    $root.trigger("luhm:yume:" + type, [$.extend({
      authority: false,
      beta: true
    }, detail || {})]);
  }

  const methods = {
    init: function (options) {
      return this.each(function () {
        const $root = $(this);
        if (getState($root)) return;

        const state = {
          options: $.extend({
            mode: "artDirectionJam",
            sceneId: "unboundScene"
          }, options || {}),
          rejectedProofIds: []
        };

        $root.data(pluginName, state);

        $root.on("click." + pluginName, "[data-yume-mode]", function () {
          state.options.mode = String($(this).attr("data-yume-mode") || "artDirectionJam");
          $root.find("[data-yume-active-mode]").text(state.options.mode);
          emit($root, "modeChanged", { mode: state.options.mode });
        });

        $root.on("click." + pluginName, "[data-yume-cutscene]", function () {
          emit($root, "cutsceneRequested", {
            sceneId: state.options.sceneId,
            layers: ["cinematicVideo", "godot4Playback", "spriteField", "lowPolyField"]
          });
        });

        $root.on("click." + pluginName, "[data-yume-reject]", function () {
          const proofId = String($(this).attr("data-proof-id") || "currentProof");
          if (!state.rejectedProofIds.includes(proofId)) state.rejectedProofIds.push(proofId);
          emit($root, "proofRejected", { proofId: proofId });
        });
      });
    },

    setScene: function (sceneId) {
      return this.each(function () {
        const state = getState($(this));
        if (state) state.options.sceneId = String(sceneId || "unboundScene");
      });
    },

    destroy: function () {
      return this.each(function () {
        $(this).off("." + pluginName).removeData(pluginName);
      });
    }
  };

  $.fn[pluginName] = function (methodOrOptions) {
    if (methods[methodOrOptions]) {
      return methods[methodOrOptions].apply(this, Array.prototype.slice.call(arguments, 1));
    }
    if (typeof methodOrOptions === "object" || methodOrOptions == null) {
      return methods.init.apply(this, arguments);
    }
    $.error("Unknown " + pluginName + " method: " + methodOrOptions);
    return this;
  };

  $.fn[pluginName].version = "0.1.0-beta";
}(jQuery));
