/* Shared standalone/MCP widget module. No provider SDK or remote script. */
(function (root) {
  "use strict";
  const contractSchema = "luhmOs.embeddedStudio.v1";
  const registerSchema = "luhmOs.assetRegister.v1";
  const maxFiles = 128, hashLimit = 32 * 1024 * 1024;
  const hosts = new Set(["youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be"]);
  function musicTarget(value) {
    const url = new URL(String(value).trim());
    if (url.protocol !== "https:" || !hosts.has(url.hostname) || url.username || url.password || url.port) throw Error("Use an HTTPS YouTube or YouTube Music link.");
    let video = url.hostname === "youtu.be" ? url.pathname.slice(1) : url.searchParams.get("v");
    if (!video && /^\/(shorts|embed)\//.test(url.pathname)) video = url.pathname.split("/")[2];
    const playlist = url.searchParams.get("list");
    if (video && !/^[A-Za-z0-9_-]{11}$/.test(video)) throw Error("That video ID is invalid.");
    if (playlist && !/^[A-Za-z0-9_-]{10,128}$/.test(playlist)) throw Error("That playlist ID is invalid.");
    if (!video && !playlist) throw Error("Choose a video or playlist link.");
    const embed = new URL(video ? "https://www.youtube-nocookie.com/embed/" + video : "https://www.youtube-nocookie.com/embed/videoseries");
    embed.searchParams.set("autoplay", "0"); embed.searchParams.set("playsinline", "1");
    if (playlist) embed.searchParams.set("list", playlist);
    const external = new URL(video ? "https://www.youtube.com/watch" : "https://www.youtube.com/playlist");
    if (video) external.searchParams.set("v", video);
    if (playlist) external.searchParams.set("list", playlist);
    return {embed: embed.href, external: external.href};
  }
  function category(name) {
    const ext = String(name).toLowerCase().split(".").pop();
    if (["glb", "gltf", "fbx", "blend", "obj"].includes(ext)) return "models";
    if (["zip", "rar", "7z", "pak", "ucas", "utoc"].includes(ext)) return "archivesPendingInspection";
    if (["wav", "mp3", "flac", "aac", "ogg", "m4a"].includes(ext)) return "audio";
    if (["mp4", "mov", "mkv", "webm"].includes(ext)) return "video";
    if (["png", "jpg", "jpeg", "webp", "svg", "gif", "dds", "exr"].includes(ext)) return "visualReferences";
    return "documentsAndOther";
  }
  function validContract(value) {
    return value?.schema === contractSchema && value?.lane === "testing" &&
      value?.serverWrites === false && value?.productionPromotion === false &&
      value?.quarantine?.activeTaskWorkersAllowed === false &&
      typeof value?.sourceRef === "string";
  }
  async function fingerprint(file, cryptoApi) {
    if (file.size > hashLimit) return null; // Index large binaries without allocating them.
    const digest = await cryptoApi.subtle.digest("SHA-256", await file.arrayBuffer());
    return Array.from(new Uint8Array(digest), x => x.toString(16).padStart(2, "0")).join("");
  }
  // Scroll-driven depth is a presentation effect. It never changes runtime state.
  function depthOffsets(scrollTop, reducedMotion = false) {
    const n = Number(scrollTop);
    const scroll = reducedMotion || !Number.isFinite(n) ? 0 : Math.max(0, Math.min(n, 1600));
    return {
      rear: -Math.round(scroll * 0.10) + "px",
      middle: -Math.round(scroll * 0.22) + "px",
      front: -Math.round(scroll * 0.38) + "px"
    };
  }
  function mountDepth(el, win) {
    if (!el || !win || !win.document) return null;
    const ownerDoc = el.ownerDocument || win.document;
    const motion = typeof win.matchMedia === "function"
      ? win.matchMedia("(prefers-reduced-motion: reduce)") : null;
    let raf = 0, disposed = false;
    function render() {
      raf = 0;
      if (disposed) return;
      const scroller = ownerDoc.scrollingElement || ownerDoc.documentElement || ownerDoc.body;
      const value = depthOffsets(scroller?.scrollTop || 0, !!motion?.matches || !!ownerDoc.hidden);
      el.style.setProperty("--studioRearY", value.rear);
      el.style.setProperty("--studioMiddleY", value.middle);
      el.style.setProperty("--studioFrontY", value.front);
    }
    function schedule() {
      if (!raf && !disposed) raf = win.requestAnimationFrame(render);
    }
    function destroy() {
      if (disposed) return;
      disposed = true;
      win.removeEventListener("scroll", schedule);
      win.removeEventListener("resize", schedule);
      win.removeEventListener("orientationchange", schedule);
      win.removeEventListener("pagehide", destroy);
      ownerDoc.removeEventListener("visibilitychange", schedule);
      motion?.removeEventListener?.("change", schedule);
      if (raf) win.cancelAnimationFrame(raf);
      for (const name of ["--studioRearY", "--studioMiddleY", "--studioFrontY"]) {
        el.style.removeProperty(name);
      }
    }
    win.addEventListener("scroll", schedule, {passive:true});
    win.addEventListener("resize", schedule);
    win.addEventListener("orientationchange", schedule);
    win.addEventListener("pagehide", destroy, {once:true});
    ownerDoc.addEventListener("visibilitychange", schedule);
    motion?.addEventListener?.("change", schedule);
    render();
    return {render, destroy};
  }
  // In the standalone cockpit this is a real jQuery plugin. The MCP resource
  // has a native no-remote-script fallback, so its controls still function.
  function installJQueryBridge(jq) {
    if (!jq?.fn || jq.fn.luhmStudioParallax) return;
    const DATA_KEY = "luhmStudioParallax";
    jq.fn.luhmStudioParallax = function (command) {
      return this.each(function () {
        const old = jq.data(this, DATA_KEY);
        if (command === "destroy") {
          if (old) { old.destroy(); jq.removeData(this, DATA_KEY); }
        } else if (!old && (!command || command === "start")) {
          jq.data(this, DATA_KEY, mountDepth(this, this.ownerDocument.defaultView));
        }
      });
    };
    jq.fn.luhmStudioParallax.version = "1.0.0";
  }
  function embedTarget(win) {
    // Exact known Godot origin; never accept untrusted user URLs or scripts.
    const host = String(win?.location?.hostname || "").toLowerCase();
    if (host === "localhost" || host === "127.0.0.1" || host.endsWith(".localhost")) {
      return new URL("/harness/godot-export/index.html", win.location.origin).href;
    }
    return "https://luhm-os-godot-harness-green.onrender.com/harness/godot-export/index.html";
  }
function initLumLive2d() {
  const byId = id => document.getElementById(id);
  const root = byId("lum2dPanel"), stage = byId("lum2dStage");
  if (!root || !stage || root.dataset.initialized === "true") return;
  root.dataset.initialized = "true";
  const reduced = typeof window.matchMedia === "function" ? window.matchMedia("(prefers-reduced-motion: reduce)") : { matches: false, addEventListener() {}, removeEventListener() {} };
  let raf = 0, blinkTimer = 0, waveTimer = 0, disposed = false;
  let x = 0, y = 0, manualPause = false, mood = "smile";
  const clamp = n => Number.isFinite(n) ? Math.max(-1, Math.min(1, n)) : 0;
  const motionAllowed = () => !disposed && !manualPause && !reduced.matches && !document.hidden;
  const announce = value => { byId("lum2dMessage").textContent = value; };
  function draw() {
    raf = 0;
    const px = motionAllowed() ? clamp(x) : 0;
    const py = motionAllowed() ? clamp(y) : 0;
    stage.style.setProperty("--l2x", px * 8 + "px");
    stage.style.setProperty("--l2y", py * 5 + "px");
    stage.style.setProperty("--l2rot", px * 2 + "deg");
    stage.style.setProperty("--l2bx", px * -4 + "px");
    stage.style.setProperty("--l2by", py * -3 + "px");
    stage.dispatchEvent(new CustomEvent("luhm:live2d:pose", {
      detail: { x: px, y: py, mood: mood, motion: motionAllowed() }
    }));
  }
  function schedule() {
    if (!raf && !disposed) raf = requestAnimationFrame(draw);
  }
  function reset() {
    x = 0; y = 0;
    if (raf) cancelAnimationFrame(raf);
    raf = 0;
    if (!disposed) draw();
  }
  function pointerMove(event) {
    if (!motionAllowed() || event.pointerType === "touch" || !Number.isFinite(event.clientX) || !Number.isFinite(event.clientY)) return;
    const rect = stage.getBoundingClientRect();
    x = clamp(((event.clientX - rect.left) / Math.max(rect.width, 1) - .5) * 2);
    y = clamp(((event.clientY - rect.top) / Math.max(rect.height, 1) - .5) * 2);
    schedule();
  }
  function blink() {
    if (blinkTimer) clearTimeout(blinkTimer);
    stage.classList.add("is-blinking");
    announce("Lum blinked. ◡");
    blinkTimer = setTimeout(() => { blinkTimer = 0; stage.classList.remove("is-blinking"); }, 230);
  }
  function wave() {
    if (waveTimer) clearTimeout(waveTimer);
    stage.classList.remove("is-waving");
    if (motionAllowed()) {
      void stage.offsetWidth;
      stage.classList.add("is-waving");
    }
    announce(motionAllowed() ? "Lum waves from the 2D stage. ✧" : "Wave selected. Motion is reduced.");
    waveTimer = setTimeout(() => { waveTimer = 0; stage.classList.remove("is-waving"); }, 760);
  }
  function smile() {
    mood = mood === "smile" ? "neutral" : "smile";
    stage.dataset.mood = mood;
    byId("lum2dMouth").setAttribute("d", mood === "smile" ? "M160 229Q181 245 202 229" : "M165 230Q181 229 198 230");
    byId("lum2dSmile").setAttribute("aria-pressed", String(mood === "smile"));
    announce(mood === "smile" ? "Lum smiles. ♡" : "Lum is listening.");
    schedule();
  }
  function toggleMotion() {
    manualPause = !manualPause;
    root.classList.toggle("is-motion-paused", manualPause);
    byId("lum2dPause").setAttribute("aria-pressed", String(manualPause));
    byId("lum2dPause").textContent = manualPause ? "Resume motion" : "Pause motion";
    announce(manualPause ? "Motion paused. Buttons still work." : "Motion respects your accessibility settings.");
    reset();
  }
  function visibility() { if (document.hidden) reset(); }
  function destroy() {
    if (disposed) return;
    disposed = true;
    stage.removeEventListener("pointermove", pointerMove);
    stage.removeEventListener("pointerleave", reset);
    document.removeEventListener("visibilitychange", visibility);
    window.removeEventListener("blur", reset);
    reduced.removeEventListener("change", reset);
    if (raf) cancelAnimationFrame(raf);
    clearTimeout(blinkTimer);
    clearTimeout(waveTimer);
    stage.classList.remove("is-waving", "is-blinking");
  }
  stage.addEventListener("pointermove", pointerMove);
  stage.addEventListener("pointerleave", reset);
  document.addEventListener("visibilitychange", visibility);
  window.addEventListener("blur", reset);
  reduced.addEventListener("change", reset);
  window.addEventListener("pagehide", destroy, { once: true });
  byId("lum2dBlink").addEventListener("click", blink);
  byId("lum2dWave").addEventListener("click", wave);
  byId("lum2dSmile").addEventListener("click", smile);
  byId("lum2dPause").addEventListener("click", toggleMotion);
  draw();
}

  root.initLumLive2d = initLumLive2d;
  function mount(doc) {
    initLumLive2d();
    if (!doc.getElementById("luhmStudioDeck")) return null;
    const get = id => doc.getElementById(id);
    let records = [], busy = false, sourceRef = "UNKNOWN";
    const stage = get("luhmStudioDeck");
    installJQueryBridge(root.jQuery);
    if (root.jQuery?.fn?.luhmStudioParallax) root.jQuery(stage).luhmStudioParallax();
    else mountDepth(stage, doc.defaultView || root);
    // A full-viewport frame stays inert until the Professor explicitly opts in.
    const backdrop = get("studioBackdropFrame");
    get("studioBackdropLoad").addEventListener("click", () => {
      if (!backdrop) return;
      backdrop.src = embedTarget(doc.defaultView || root);
      backdrop.hidden = false;
      get("studioBackdropStatus").textContent =
        "Embedded Godot scene requested. Runtime rendering and input remain unverified; use static mode if it fails.";
    });
    get("studioBackdropStop").addEventListener("click", () => {
      if (backdrop) { backdrop.hidden = true; backdrop.removeAttribute("src"); }
      get("studioBackdropStatus").textContent = "Static background active. No embedded scene connection.";
    });
    function showRegister() {
      const groups = new Map();
      for (const row of records) groups.set(row.category, (groups.get(row.category) || 0) + 1);
      get("studioAssetList").replaceChildren();
      for (const [name, count] of groups) {
        const li = doc.createElement("li"); li.textContent = name + " · " + count;
        get("studioAssetList").append(li);
      }
      const hashed = records.filter(x => x.sha256).length;
      get("studioAssetStatus").textContent = records.length + " assets · " + hashed + " fingerprinted · " + (records.length - hashed) + " need hash verification. Rights/canon: awaiting review.";
    }
    function configure(value) {
      if (!validContract(value)) {
        sourceRef = "UNKNOWN";
        get("studioLaneStatus").textContent = "Workspace contract unavailable or mismatched · testing only.";
        get("studioCrewStatus").textContent = "Agent state UNKNOWN. No workers activated.";
        get("studioSourceStatus").textContent = "Source: UNKNOWN";
        return false;
      }
      sourceRef = value.sourceRef;
      get("studioLaneStatus").textContent = "Testing draft · production remains on its separately approved release.";
      get("studioCrewStatus").textContent = "Lum coordinates. Urd, Belldandy, Skuld and Yume are registered; worker execution remains held by the current contract.";
      get("studioSourceStatus").textContent = "Source: " + sourceRef;
      return true;
    }
    get("studioMusicLoad").onclick = () => {
      try {
        const target = musicTarget(get("studioMusicUrl").value);
        const frame = doc.createElement("iframe");
        frame.title = "YouTube music video or playlist player";
        frame.referrerPolicy = "strict-origin-when-cross-origin";
        frame.allow = "encrypted-media; picture-in-picture; fullscreen";
        frame.allowFullscreen = true; frame.src = target.embed;
        get("studioMusicStage").replaceChildren(frame);
        const link = get("studioMusicExternal"); link.href = target.external; link.hidden = false;
        get("studioMusicStatus").textContent = "YouTube player requested. Use its play control; if embedding is unavailable, open on YouTube.";
      } catch (error) { get("studioMusicStatus").textContent = error.message; }
    };
    get("studioMusicStop").onclick = () => {
      get("studioMusicStage").replaceChildren();
      get("studioMusicExternal").hidden = true;
      get("studioMusicStatus").textContent = "YouTube disconnected.";
    };
    async function addFiles(files) {
      if (busy) return;
      busy = true;
      for (const id of ["studioAssetInput", "studioAssetClear", "studioAssetExport"]) get(id).disabled = true;
      const selected = Array.from(files).slice(0, maxFiles - records.length);
      let duplicates = 0, failures = 0;
      try {
        for (const file of selected) {
          get("studioAssetStatus").textContent = "Fingerprinting locally: " + String(file.name).slice(0, 256);
          let sha256 = null;
          try { sha256 = await fingerprint(file, root.crypto); } catch (_) { failures++; }
          if (sha256 && records.some(x => x.sha256 === sha256)) { duplicates++; continue; }
          records.push({originalName:String(file.name).slice(0,256),bytes:file.size,mime:String(file.type || "application/octet-stream").slice(0,128),category:category(file.name),sha256,rights:"UNKNOWN",canon:"UNAPPROVED",lane:"needsReview"});
        }
      } finally {
        busy = false;
        for (const id of ["studioAssetInput", "studioAssetClear", "studioAssetExport"]) get(id).disabled = false;
        get("studioAssetInput").value = "";
        showRegister();
        get("studioAssetStatus").textContent += " " + duplicates + " exact duplicates skipped; " + failures + " hash reads failed. Maximum 128 files; files over 32 MiB stay unhashed.";
      }
    }
    get("studioAssetInput").addEventListener("change", e => { void addFiles(e.target.files || []); });
    get("studioAssetClear").onclick = () => { if (!busy) { records = []; showRegister(); } };
    get("studioAssetExport").onclick = () => {
      const manifest = {schema:registerSchema,sourceRef,createdAt:new Date().toISOString(),serverWrites:false,productionPromotion:false,assets:records};
      const url = URL.createObjectURL(new Blob([JSON.stringify(manifest, null, 2)], {type:"application/json"}));
      const link = doc.createElement("a"); link.href = url; link.download = "luhm-asset-register.json"; doc.body.append(link); link.click(); link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    };
    configure(null);
    return {configure, addFiles, register:() => records.map(row => ({...row}))};
  }
  const api = {musicTarget, category, validContract, fingerprint, depthOffsets, mountDepth, embedTarget, installJQueryBridge, mount, hashLimit, maxFiles};
  if (typeof module === "object" && module.exports) module.exports = api;
  root.LuHmStudio = api;
  if (root.document) root.luhmStudioDeck = mount(root.document);
})(typeof window !== "undefined" ? window : globalThis);
