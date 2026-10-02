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
          rejectedProofIds: [],
          frameRequest: 0,
          pointerX: 0,
          pointerY: 0
        };

        $root.data(pluginName, state);

        function paintDepth() {
          state.frameRequest = 0;
          $root[0].style.setProperty("--yumeX", String(state.pointerX));
          $root[0].style.setProperty("--yumeY", String(state.pointerY));
          $root[0].style.setProperty("--yumeScroll", String($root.scrollTop()));
        }

        function requestDepthPaint() {
          if (state.frameRequest) return;
          state.frameRequest = requestAnimationFrame(paintDepth);
        }

        $root.on("pointermove." + pluginName, function (event) {
          const rect = $root[0].getBoundingClientRect();
          state.pointerX = Math.max(-1, Math.min(1, ((event.clientX - rect.left) / Math.max(rect.width, 1) - 0.5) * 2));
          state.pointerY = Math.max(-1, Math.min(1, ((event.clientY - rect.top) / Math.max(rect.height, 1) - 0.5) * 2));
          requestDepthPaint();
        });

        $root.on("pointerleave." + pluginName, function () {
          state.pointerX = 0;
          state.pointerY = 0;
          requestDepthPaint();
        });

        $root.on("scroll." + pluginName, requestDepthPaint);

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

    snapshot: function () {
      const state = getState(this.first());
      if (!state) return null;
      return {
        mode: state.options.mode,
        sceneId: state.options.sceneId,
        rejectedProofIds: state.rejectedProofIds.slice(),
        authority: false,
        beta: true
      };
    },

    destroy: function () {
      return this.each(function () {
        const $root = $(this);
        const state = getState($root);
        if (state && state.frameRequest) cancelAnimationFrame(state.frameRequest);
        $root.off("." + pluginName).removeData(pluginName);
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
