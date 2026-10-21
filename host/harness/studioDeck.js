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
  function mount(doc) {
    if (!doc.getElementById("luhmStudioDeck")) return null;
    const get = id => doc.getElementById(id);
    let records = [], busy = false, sourceRef = "UNKNOWN";
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
  const api = {musicTarget, category, validContract, fingerprint, mount, hashLimit, maxFiles};
  if (typeof module === "object" && module.exports) module.exports = api;
  root.LuHmStudio = api;
  if (root.document) root.luhmStudioDeck = mount(root.document);
})(typeof window !== "undefined" ? window : globalThis);
