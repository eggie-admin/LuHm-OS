(function ($) {
  "use strict";

  function postNative(type, detail) {
    const bridge = window.LuHmNative;
    if (!bridge || typeof bridge.postMessage !== "function") return false;
    bridge.postMessage(JSON.stringify({ type: type, detail: detail || {} }));
    return true;
  }

  function chaosSeed(text) {
    let hash = 2166136261;
    String(text).split("").forEach(function (ch) {
      hash ^= ch.charCodeAt(0);
      hash = Math.imul(hash, 16777619);
    });
    return hash >>> 0;
  }

  function randomFunDirector(text) {
    const pools = {
      mood: ["cathedralNoir", "coffeeEmergency", "pixelStorm", "neonRiverwalk"],
      fx: ["vhsFlutter", "cyanSparks", "magentaFog", "coffeeSteam"],
      event: ["catHatProtocol", "fakeBossIntro", "latteQuest", "tinyOniInvasion"]
    };
    const seed = chaosSeed(text);
    return {
      chaosSeed: seed,
      mood: pools.mood[seed % pools.mood.length],
      fx: pools.fx[(seed >>> 3) % pools.fx.length],
      event: pools.event[(seed >>> 7) % pools.event.length]
    };
  }

  function applyChaos($cockpit, scene) {
    $cockpit.attr("data-chaos-mood", scene.mood);
    $cockpit.attr("data-chaos-fx", scene.fx);
    $cockpit.attr("data-chaos-event", scene.event);
    $cockpit.find("[data-layer-fx]").text(scene.event + " · " + scene.fx);
  }

  function installParallax($cockpit) {
    const root = $cockpit.get(0);
    let raf = 0;
    function render(x, y) {
      raf = 0;
      root.style.setProperty("--parallaxX", x.toFixed(3));
      root.style.setProperty("--parallaxY", y.toFixed(3));
    }
    $cockpit.on("pointermove.luhmParallax", function (event) {
      if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
      const rect = root.getBoundingClientRect();
      const x = ((event.clientX - rect.left) / Math.max(rect.width, 1)) * 2 - 1;
      const y = ((event.clientY - rect.top) / Math.max(rect.height, 1)) * 2 - 1;
      if (raf) return;
      raf = window.requestAnimationFrame(function () { render(x, y); });
    });
    $cockpit.on("pointerleave.luhmParallax", function () { render(0, 0); });
  }

  $(function () {
    const $cockpit = $("[data-luhm-cockpit]");
    if (!$cockpit.length) return;

    $cockpit.luhmCockpit({ initialView: "chat" });
    installParallax($cockpit);

    $cockpit.on("luhm:backend:open", function (_event, detail) {
      postNative("world_requested", detail);
    });

    $cockpit.on("luhm:chat:submit", function (_event, detail) {
      const text = String((detail && detail.text) || "");
      const scene = randomFunDirector(text);
      applyChaos($cockpit, scene);
      postNative("chat_submitted", { text: text, chaosSeed: scene.chaosSeed });
      $cockpit.trigger("luhm:artOni:candidate", [scene]);
    });

    postNative("cockpit_ready");

    window.LuHmFrontEnd = Object.freeze({
      version: $.fn.luhmCockpit.version,
      jquery: $.fn.jquery,
      openBackend: function () { $cockpit.luhmCockpit("openBackend"); },
      closeBackend: function () { $cockpit.luhmCockpit("closeBackend"); },
      setView: function (view) { $cockpit.luhmCockpit("view", view); },
      randomFunDirector: randomFunDirector,
      nativeBridgeAvailable: function () {
        return !!(window.LuHmNative && typeof window.LuHmNative.postMessage === "function");
      }
    });
  });
}(jQuery));
