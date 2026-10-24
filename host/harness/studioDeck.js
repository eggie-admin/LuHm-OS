/* Shared standalone/MCP widget module. No provider SDK or remote script. */
(function (root) {
  "use strict";
  const contractSchema = "luhmOs.embeddedStudio.v1";
  const registerSchema = "luhmOs.assetRegister.v1";
  const maxFiles = 128, hashLimit = 32 * 1024 * 1024;
  const hosts = new Set(["youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be"]);
  function musicTarget(value) {
    const input = String(value).trim();
    if (!input) throw Error("Paste a YouTube video or playlist link first. Nothing is playing.");
    const url = new URL(input);
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
  function attachMusicDeck(doc) {
    const get = id => doc.getElementById(id);
    const input = get("studioMusicUrl"), stage = get("studioMusicStage");
    const status = get("studioMusicStatus"), link = get("studioMusicExternal");
    if (!input || !stage || !status || !link || input.dataset.musicWired === "true") return false;
    input.dataset.musicWired = "true";
    get("studioMusicLoad").addEventListener("click", () => {
      const value = input.value.trim();
      if (!value) {
        status.textContent = "Paste a YouTube video or playlist link first. Nothing is playing.";
        input.focus();
        return;
      }
      try {
        const target = musicTarget(value);
        const frame = doc.createElement("iframe");
        frame.title = "User-requested YouTube video or playlist";
        frame.referrerPolicy = "strict-origin-when-cross-origin";
        frame.loading = "lazy";
        frame.allow = "encrypted-media; picture-in-picture; fullscreen";
        frame.allowFullscreen = true;
        frame.src = target.embed;
        stage.replaceChildren(frame);
        link.href = target.external; link.hidden = false;
        status.textContent = "YouTube embed requested, not playback verified. Use its play control or open YouTube.";
      } catch (error) {
        status.textContent = String(error?.message || "Invalid link.").slice(0, 180);
      }
    });
    get("studioMusicStop").addEventListener("click", () => {
      stage.replaceChildren(); link.removeAttribute("href"); link.hidden = true;
      status.textContent = "Music player disconnected. No autoplay.";
    });
    return true;
  }
  function installJQueryMusicBridge(jq) {
    if (!jq?.fn || jq.fn.luhmMusicDeck) return;
    jq.fn.luhmMusicDeck = function () {
      return this.each(function () { attachMusicDeck(this.ownerDocument); });
    };
    jq.fn.luhmMusicDeck.version = "1.0.0";
  }
  function mountGlassDock(doc) {
    const get = id => doc.getElementById(id);
    const toggle = get("studioGlassToggle"), panel = get("studioGlassDock");
    if (!toggle || !panel || toggle.dataset.glassWired === "true") return false;
    toggle.dataset.glassWired = "true";
    const status = get("studioGlassStatus");
    function setOpen(open, returnFocus) {
      panel.hidden = !open;
      toggle.setAttribute("aria-expanded", String(open));
      if (open) get("studioGlassClose").focus();
      else if (returnFocus) toggle.focus();
    }
    toggle.addEventListener("click", () => setOpen(panel.hidden, false));
    get("studioGlassClose").addEventListener("click", () => setOpen(false, true));
    panel.addEventListener("keydown", e => {
      if (e.key === "Escape") { e.preventDefault(); setOpen(false, true); }
    });
    const targets = {
      music: "studioMusicUrl", avatars: "lum2dStage", yume: "studioAssetInput"
    };
    for (const control of panel.querySelectorAll("[data-studio-route]")) {
      control.addEventListener("click", () => {
        const route = control.dataset.studioRoute;
        if (route === "social") {
          status.textContent = "Social publishing needs an approved account and separate review. No posting tool is connected to this web cockpit.";
          return;
        }
        if (route === "admin") {
          get("studioPlaneInspector").open = true;
          status.textContent = "Seven visual planes are source-wired. Host, media and agent capabilities remain individually evidenced.";
          get("studioPlaneInspector").querySelector("summary").focus();
          return;
        }
        const target = get(targets[route]);
        if (!target) {
          status.textContent = "Module source is unavailable on this page.";
          return;
        }
        setOpen(false, false);
        target.scrollIntoView({behavior:"auto",block:"center"});
        target.focus({preventScroll:true});
        status.textContent = route === "music"
          ? "Music deck focused. Paste an authorized YouTube link to request an embed."
          : route === "avatars"
          ? "Lum 2D expression controls are available. Licensed Live2D rig is not claimed."
          : "Local asset registration focused. Rights and exports remain under review.";
      });
    }
    return true;
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
  function mountPocketCompanion(){
const $=id=>document.getElementById("pocket"+id);const palette={cyan:"#5ee3eb",pink:"#e95cb5",purple:"#6b35db"};let timer=null,bondCount=0;
function speak(t){$("expression").textContent=t}
function tone(freq=620){try{let A=window.AudioContext||window.webkitAudioContext;let ctx=new A(),o=ctx.createOscillator(),g=ctx.createGain();o.type="sine";o.frequency.setValueAtTime(freq,ctx.currentTime);o.frequency.exponentialRampToValueAtTime(freq*1.29,ctx.currentTime+.13);g.gain.setValueAtTime(.05,ctx.currentTime);g.gain.exponentialRampToValueAtTime(.0001,ctx.currentTime+.18);o.connect(g).connect(ctx.destination);o.start();o.stop(ctx.currentTime+.19);o.onended=()=>ctx.close()}catch(_){}}
$("palette").addEventListener("change",e=>{$("petBody").setAttribute("fill",palette[e.target.value]);speak("Lum changed her neon coat.");tone(550)});
const scenes={cathedral:"radial-gradient(ellipse at 50% 35%,#5832a9,#141026 70%)",city:"repeating-linear-gradient(90deg,#161132 0 35px,#2c1749 35px 45px,#0c101a 45px 72px)",lab:"repeating-linear-gradient(0deg,#101827 0 38px,#1a3652 40px 43px,#12102a 44px 80px)",stars:"radial-gradient(circle at 20% 18%,#5ee3eb 1px,transparent 3px),radial-gradient(circle at 75% 25%,#ede9ff 2px,transparent 4px),linear-gradient(125deg,#070d1d,#2d2561)",portal:"radial-gradient(circle at center,#e95cb5,#6b35db 23%,#0c101a 65%)",forest:"repeating-linear-gradient(104deg,#0b1525 0 46px,#152e3b 48px 60px,#0c101a 61px 96px)"};
$("scene").addEventListener("change",e=>{$("world").style.background=scenes[e.target.value];speak("New scene: "+e.target.options[e.target.selectedIndex].text+".")});
function blink(){clearTimeout(timer);$("openEyes").style.display="none";$("shutEyes").style.display="block";timer=setTimeout(()=>{$("openEyes").style.display="block";$("shutEyes").style.display="none"},260)}
$("blink").addEventListener("click",()=>{blink();speak("A tiny wink from Lum.");tone(460)});
$("bond").addEventListener("click",()=>{bondCount++;speak("Bond level "+bondCount+": Lum sends a heart back! ♥");tone(660);const e=document.createElement("span");e.className="pocketHeart";e.textContent="♥";e.style.left=(25+Math.random()*50)+"%";e.style.top=(26+Math.random()*50)+"%";$("bondHearts").append(e);setTimeout(()=>e.remove(),1350)});
$("cast").addEventListener("click",()=>{tone(880);speak("Sparkle spell! Just a visual effect, no model or API calls.");$("aura").style.opacity=".8";setTimeout(()=>$("aura").style.opacity=".25",450)});
$("pause").addEventListener("click",e=>{const v=document.querySelector(".pocketCompanion").classList.toggle("reduced");e.currentTarget.setAttribute("aria-pressed",String(v));e.currentTarget.textContent=v?"▶ Resume motion":"Ⅱ Pause motion"});

  }
  function wirePrivateLum(doc) {
    const element = id => doc.getElementById(id);
    const picker = element("studioPrivateLumFile");
    if (!picker || picker.dataset.wired) return;
    picker.dataset.wired = "true";
    const img = element("studioPrivateLumImage"), holder = element("studioPrivateLumStage");
    const status = element("studioPrivateLumStatus"), digest = element("studioPrivateLumDigest");
    const pause = element("studioPrivateLumPause"), clear = element("studioPrivateLumClear");
    const browser = doc.defaultView;
    let address, still, token = 0, stopped = false;
    const reset = () => {
      token++;
      img.removeAttribute("src");
      if (address) browser.URL.revokeObjectURL(address);
      address = null; still = null; stopped = false;
      holder.hidden = true; pause.disabled = true; clear.disabled = true;
      pause.textContent = "Pause animation";
      pause.setAttribute("aria-pressed", "false");
      digest.textContent = "No SHA-256 computed. Private session only.";
    };
    picker.addEventListener("change", async () => {
      reset();
      const file = picker.files && picker.files[0], request = token;
      if (!file) return;
      if (!file.size || file.size > 16 * 1024 * 1024) {
        status.textContent = "File rejected: GIF must be under 16 MiB."; return;
      }
      status.textContent = "Verifying selected GIF locally. Nothing is uploaded.";
      try {
        const header = new Uint8Array(await file.slice(0, 6).arrayBuffer());
        const signature = String.fromCharCode(...header);
        if (signature !== "GIF89a" && signature !== "GIF87a") throw Error("Not a GIF file.");
        const sha = await fingerprint(file, browser.crypto);
        if (!sha) throw Error("SHA-256 not available.");
        if (request !== token) return;
        address = browser.URL.createObjectURL(file);
        img.onload = () => {
          if (request !== token) return;
          const width = img.naturalWidth, height = img.naturalHeight;
          if (!width || !height || width > 2048 || height > 2048) {
            reset(); status.textContent = "Unsupported frame dimensions."; return;
          }
          const canvas = doc.createElement("canvas");
          canvas.width = width; canvas.height = height;
          canvas.getContext("2d").drawImage(img, 0, 0);
          still = canvas.toDataURL("image/png");
          img.onload = null; // Switching between animated/static sources must not repeat initialization.
          const match = sha === "a9df1d2b5c63d5740be8c476b59f389171b99609a14cd02fc8ae7568d27b2aba" &&
            width === 512 && height === 640;
          digest.textContent = "Local SHA-256: " + sha + " · " + width + " × " + height +
            " · " + (match ? "SELECTED CANDIDATE MATCH" : "DIFFERENT LOCAL CANDIDATE");
          status.textContent = match
            ? "Matching private Lum animation preview. Rights and Canon art approval pending."
            : "Local GIF testing only. This is not the selected Lum candidate.";
          holder.hidden = false; pause.disabled = false; clear.disabled = false;
          if (browser.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches) pause.click();
        };
        img.onerror = () => { reset(); status.textContent = "GIF failed to decode."; };
        img.src = address;
      } catch (_) { reset(); status.textContent = "GIF inspection failed. Nothing uploaded."; }
    });
    pause.addEventListener("click", () => {
      if (!address || !still) return;
      stopped = !stopped;
      img.src = stopped ? still : address;
      pause.setAttribute("aria-pressed", String(stopped));
      pause.textContent = stopped ? "Resume animation" : "Pause animation";
    });
    clear.addEventListener("click", () => {
      reset(); picker.value = ""; status.textContent = "Private preview cleared.";
    });
    browser.addEventListener("pagehide", reset, {once:true});
  }
  function mount(doc) {
    mountPocketCompanion();
    initLumLive2d();
    if (!doc.getElementById("luhmStudioDeck")) return null;
    const get = id => doc.getElementById(id);
    let records = [], busy = false, sourceRef = "UNKNOWN";
    const stage = get("luhmStudioDeck");
    installJQueryBridge(root.jQuery);
    if (root.jQuery?.fn?.luhmStudioParallax) root.jQuery(stage).luhmStudioParallax();
    else mountDepth(stage, doc.defaultView || root);
    mountGlassDock(doc);
    wirePrivateLum(doc);
    installJQueryMusicBridge(root.jQuery);
    if (root.jQuery?.fn?.luhmMusicDeck) root.jQuery(get("studioMusicStage")).luhmMusicDeck();
    else attachMusicDeck(doc);
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
