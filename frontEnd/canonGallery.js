/* Private Canon Studio: user-selected images only, no network/persistence. */
(function () {
  "use strict";
  const MAX_IMAGES = 8;
  const MAX_IMAGE_BYTES = 16 * 1024 * 1024;
  const NATIVE_IMAGE_PREFIX = "data:image/jpeg;base64,";
  const MIME = new Set(["image/png", "image/jpeg", "image/webp"]);
  const entries = [];
  let gallery = null;
  let grid = null;
  let status = null;

  function report(message) {
    if (status) status.textContent = message;
  }

  function clear() {
    entries.splice(0).forEach(entry => {
      if (entry.objectUrl) URL.revokeObjectURL(entry.objectUrl);
    });
    if (grid) grid.replaceChildren();
    report("Session cleared. Private artwork stays on your Samsung.");
  }

  function addImage(name, src, objectUrl) {
    if (!grid) return false;
    if (entries.length >= MAX_IMAGES) {
      if (objectUrl) URL.revokeObjectURL(objectUrl);
      report("Maximum eight images per session. Clear to choose another set.");
      return false;
    }
    const figure = document.createElement("figure");
    figure.className = "canonGalleryCard";
    const img = document.createElement("img");
    img.src = src;
    img.alt = "Private character design art: " + String(name).slice(0, 80);
    img.loading = "lazy";
    img.tabIndex = 0;
    const toggleZoom = () => figure.classList.toggle("isExpanded");
    img.addEventListener("click", toggleZoom);
    img.addEventListener("keydown", event => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        toggleZoom();
      }
    });
    const caption = document.createElement("figcaption");
    caption.textContent = String(name).slice(0, 80);
    figure.append(img, caption);
    grid.appendChild(figure);
    entries.push({ objectUrl: objectUrl || null });
    report(entries.length + " private artwork image" + (entries.length === 1 ? "" : "s") + " loaded locally. Nothing uploaded.");
    return true;
  }

  function addFromNative(label, dataUrl) {
    if (typeof dataUrl !== "string" ||
        !dataUrl.startsWith(NATIVE_IMAGE_PREFIX) ||
        dataUrl.length > 4 * 1024 * 1024 ||
        !/^[A-Za-z0-9+/]*={0,2}$/.test(dataUrl.slice(NATIVE_IMAGE_PREFIX.length))) {
      report("Native artwork was rejected by the local size/type gate.");
      return false;
    }
    return addImage(label, dataUrl, null);
  }

  function nativeError(message) {
    const known = {
      picker_unavailable: "Samsung Files picker is unavailable.",
      image_unreadable: "The selected image could not be read.",
      image_too_large: "Image is too large for the private gallery preview.",
      image_format_rejected: "Only PNG, JPEG and WebP images are supported."
    };
    report(known[message] || "Local file selection was cancelled or unavailable.");
  }

  window.LuHmCanonGallery = Object.freeze({ addFromNative, nativeError });

  document.addEventListener("DOMContentLoaded", () => {
    gallery = document.querySelector("[data-luhm-canon-gallery]");
    grid = document.querySelector("[data-luhm-gallery-grid]");
    status = document.querySelector("[data-luhm-gallery-status]");
    const input = document.querySelector("[data-luhm-gallery-file]");
    if (!gallery || !grid || !status || !input) return;
    const openGallery = () => {
      gallery.hidden = false;
      const menu = document.querySelector("[data-luhm-menu]");
      if (menu) menu.hidden = true;
      const close = gallery.querySelector("[data-luhm-gallery-close]");
      if (close) close.focus();
    };
    const closeGallery = () => { gallery.hidden = true; };
    document.querySelectorAll("[data-luhm-gallery-button]").forEach(button => {
      button.addEventListener("click", openGallery);
    });
    gallery.querySelector("[data-luhm-gallery-close]").addEventListener("click", closeGallery);
    gallery.querySelector("[data-luhm-gallery-clear]").addEventListener("click", clear);
    gallery.querySelector("[data-luhm-gallery-pick]").addEventListener("click", () => {
      const bridge = window.LuHmNative;
      if (bridge && typeof bridge.postMessage === "function") {
        bridge.postMessage(JSON.stringify({ type: "local_art_pick_requested" }));
        report("Choose PNG or JPEG artwork in Samsung Files…");
      } else {
        input.click();
      }
    });
    input.addEventListener("change", () => {
      Array.from(input.files || []).slice(0, MAX_IMAGES).forEach(file => {
        if (!MIME.has(file.type) || file.size <= 0 || file.size > MAX_IMAGE_BYTES) {
          report("Only PNG/JPEG/WebP up to 16 MB per image can be previewed.");
          return;
        }
        addImage(file.name, URL.createObjectURL(file), true);
      });
      input.value = "";
    });
    document.addEventListener("keydown", event => {
      if (event.key === "Escape" && !gallery.hidden) closeGallery();
    });
    window.addEventListener("pagehide", clear, { once: true });
    const cockpit = document.querySelector("[data-luhm-cockpit]");
    if (cockpit && window.jQuery) {
      window.jQuery(cockpit).on("luhm:view:change", (_event, detail) => {
        if (detail && detail.view === "library") openGallery();
      });
    }
  });
}());
