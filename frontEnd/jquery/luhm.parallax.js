/* LuHm original parallax plugin: local-only UI, no network or privileged actions. */
(function ($) {
  "use strict";
  const KEY = "luhmParallax";
  $.fn.luhmParallax = function (command) {
    return this.each(function () {
      const el = this;
      const prior = $.data(el, KEY);
      if (command === "destroy") {
        if (prior) { prior.destroy(); $.removeData(el, KEY); }
        return;
      }
      if (prior || (command && command !== "start")) return;
      const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
      let raf = 0, x = 0, y = 0, disposed = false;
      const active = () => !disposed && !reduced.matches && !document.hidden;
      function draw() {
        raf = 0;
        el.style.setProperty("--luhm-px", (active() ? x * 8 : 0) + "px");
        el.style.setProperty("--luhm-py", (active() ? y * 6 : 0) + "px");
      }
      function reset() {
        x = y = 0;
        if (raf) cancelAnimationFrame(raf);
        raf = 0;
        draw();
      }
      function onMove(event) {
        if (!active() || event.pointerType === "touch" || !Number.isFinite(event.clientX) || !Number.isFinite(event.clientY)) return;
        const box = el.getBoundingClientRect();
        x = Math.max(-1, Math.min(1, ((event.clientX - box.left) / Math.max(box.width, 1) - .5) * 2));
        y = Math.max(-1, Math.min(1, ((event.clientY - box.top) / Math.max(box.height, 1) - .5) * 2));
        if (!raf) raf = requestAnimationFrame(draw);
      }
      function hidden() { if (document.hidden) reset(); }
      function destroy() {
        if (disposed) return;
        disposed = true;
        el.removeEventListener("pointermove", onMove);
        el.removeEventListener("pointerleave", reset);
        document.removeEventListener("visibilitychange", hidden);
        window.removeEventListener("blur", reset);
        reduced.removeEventListener("change", reset);
        if (raf) cancelAnimationFrame(raf);
        raf = 0;
        el.style.removeProperty("--luhm-px");
        el.style.removeProperty("--luhm-py");
      }
      $.data(el, KEY, { destroy: destroy });
      el.addEventListener("pointermove", onMove);
      el.addEventListener("pointerleave", reset);
      document.addEventListener("visibilitychange", hidden);
      window.addEventListener("blur", reset);
      reduced.addEventListener("change", reset);
      window.addEventListener("pagehide", destroy, { once: true });
      draw();
    });
  };
  $.fn.luhmParallax.version = "1.0.0";
}(jQuery));
