"use strict";

const byId = id => document.getElementById(id);
const MAX_DESK_FILES = 24;
const MAX_DESK_BYTES = 128 * 1024 * 1024;
const MAX_ASSET_BYTES = 32 * 1024 * 1024;
const DESK_MIME = Object.freeze({
  ".png": ["image/png", "image"], ".jpg": ["image/jpeg", "image"],
  ".jpeg": ["image/jpeg", "image"], ".gif": ["image/gif", "image"],
  ".webp": ["image/webp", "image"], ".mp4": ["video/mp4", "video"],
  ".webm": ["video/webm", "video"], ".pdf": ["application/pdf", "pdf"]
});
const BOOT_TIMEOUT_MS = 10000;
const PET_SELECTION_KEY = "luhm.petSelection.v1";
const DEFAULT_PETS = Object.freeze([{ name: "Lum", role: "Companion", glyph: "L" }]);
function safePetSelection() {
  try { return sessionStorage.getItem(PET_SELECTION_KEY) || ""; } catch (_) { return ""; }
}
function rememberPetSelection(name) {
  try { sessionStorage.setItem(PET_SELECTION_KEY, name); } catch (_) { /* private browsing */ }
}
function validatePets(input) {
  if (!Array.isArray(input) || input.length < 1 || input.length > 32) throw new Error("invalid pet roster");
  const names = new Set();
  return input.map(item => {
    if (!item || typeof item.name !== "string" || !/^[\w -]{1,40}$/.test(item.name) || names.has(item.name) ||
        typeof item.role !== "string" || item.role.length > 100 ||
        (item.glyph != null && (typeof item.glyph !== "string" || [...item.glyph].length > 3))) throw new Error("invalid pet entry");
    names.add(item.name);
    return { name: item.name, role: item.role, glyph: item.glyph || item.name.slice(0, 1) };
  });
}

const state = {
  pets: [],
  loadingManifest: null,
  petIndex: 0,
  assets: [],
  assetIndex: 0,
  objectUrls: new Set(),
  raf: 0,
  pointerX: 0,
  pointerY: 0,
  godotReady: false
};

function setLoadingAgent(agentId, message) {
  const item=state.loadingManifest?.sprites?.find(x=>x.agentId===agentId);
  if(item){
    const slot=item.slot-1, col=slot%4, row=Math.floor(slot/4);
    byId("agentLoadingSprite").style.backgroundPosition=String(col*100/3)+"% "+String(row*100/3)+"%";
    byId("agentLoadingName").textContent=item.displayName;
  }
  byId("agentLoadingState").textContent=message;
}
function validateLoadingManifest(value) {
  const ids=(value?.sprites||[]).map(x=>x.agentId), goddesses=value?.goddessGroup?.machineIds||[];
  if(value?.schema!=="luhmOs.runtimeAgentLoadingSprites.v1"||ids.length<1||new Set(ids).size!==ids.length)throw new Error("invalid agent loading roster");
  if(goddesses.join(",")!=="urdDoctorGoddess,belldandySecretary,skuldResearch")throw new Error("invalid goddess roster");
  if(value?.grid?.columns!==4||value?.grid?.rows!==4)throw new Error("invalid sprite grid");
}

function normalizedHost() {
  const raw = location.hostname.toLowerCase();
  return raw.startsWith("[") && raw.endsWith("]") ? raw.slice(1, -1) : raw;
}

function isLoopback() {
  const h = normalizedHost();
  return h === "127.0.0.1" || h === "localhost" || h.endsWith(".localhost") || h === "::1";
}

function isRenderHost() {
  const h = normalizedHost();
  return h === "onrender.com" || h.endsWith(".onrender.com");
}

function renderNetwork() {
  if (isLoopback()) {
    byId("networkStatus").textContent = `${location.protocol}//${location.host}`;
    byId("networkNote").textContent = "Local .localhost/loopback shell. No remote asset upload.";
    byId("edgeBadge").textContent = "LOCAL / LOOPBACK";
    return;
  }

  if (isRenderHost()) {
    byId("networkStatus").textContent = "Render HTTPS edge";
    byId("networkNote").textContent = "Render redirects public HTTP to HTTPS. Origin remains IPv4-only.";
    byId("edgeBadge").textContent = "PUBLIC / HTTPS";
    return;
  }

  byId("networkStatus").textContent = `${location.protocol}//${location.host}`;
  byId("networkNote").textContent = "External host. Render and IPv4 claims are not assumed.";
  byId("edgeBadge").textContent = "EXTERNAL / UNVERIFIED";
}

function renderLibraries(policy) {
  const list = byId("libraryList");
  list.textContent = "";
  for (const lib of policy.libraries || []) {
    const el = document.createElement("span");
    el.className = "chip";
    el.textContent = `${lib.name} · ${lib.load}`;
    list.appendChild(el);
  }
}

function showPet() {
  if (!state.pets.length) return;
  const pet = state.pets[state.petIndex % state.pets.length];
  byId("petGlyph").textContent = pet.glyph || pet.name.slice(0, 1);
  byId("petName").textContent = pet.name;
  byId("petRole").textContent = pet.role;
  rememberPetSelection(pet.name);
}

const reducedHeaderMotion = typeof window.matchMedia === "function" ? window.matchMedia("(prefers-reduced-motion: reduce)") : { matches: false, addEventListener() {} };
function resetParallax() {
  if (state.raf) cancelAnimationFrame(state.raf);
  state.raf = 0;
  state.pointerX = 0;
  state.pointerY = 0;
  byId("pixelPet").style.transform = "";
  byId("parallaxHeader").style.setProperty("--px", "0px");
  byId("parallaxHeader").style.setProperty("--py", "0px");
}
function scheduleParallax() {
  if (reducedHeaderMotion.matches || document.hidden) { resetParallax(); return; }
  if (state.raf) return;
  state.raf = requestAnimationFrame(() => {
    state.raf = 0;
    const x = Math.max(-1, Math.min(1, state.pointerX));
    const y = Math.max(-1, Math.min(1, state.pointerY));
    byId("pixelPet").style.transform = "translate3d(" + x * 8 + "px," + y * 6 + "px,0) rotate(" + x * 2 + "deg)";
    byId("parallaxHeader").style.setProperty("--px", x * 10 + "px");
    byId("parallaxHeader").style.setProperty("--py", y * 6 + "px");
  });
}
function onPointerMove(event) {
  if (event.pointerType === "touch" || reducedHeaderMotion.matches || document.hidden || !Number.isFinite(event.clientX) || !Number.isFinite(event.clientY)) return;
  const rect = byId("parallaxHeader").getBoundingClientRect();
  state.pointerX = ((event.clientX - rect.left) / Math.max(rect.width, 1) - 0.5) * 2;
  state.pointerY = ((event.clientY - rect.top) / Math.max(rect.height, 1) - 0.5) * 2;
  scheduleParallax();
}

function classify(file) {
  const name = typeof file?.name === "string" ? file.name.toLowerCase() : "";
  const extension = name.slice(name.lastIndexOf("."));
  const expected = DESK_MIME[extension];
  if (!expected || file.type !== expected[0]) return "other";
  return expected[1];
}

function setDeskStatus(message) {
  const status = byId("deskStatus");
  if (status) status.textContent = message;
}

async function fetchJson(url) {
  const response = await fetch(url, { cache: "no-store", signal: AbortSignal.timeout(BOOT_TIMEOUT_MS) });
  if (!response.ok) throw new Error("Desktop dependency not available: " + url);
  const raw = await response.text();
  if (raw.length > 512 * 1024) throw new Error("Oversized desktop config: " + url);
  return JSON.parse(raw);
}

function safeAssetRecord(file) {
  return {
    id: crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`,
    name: file.name,
    type: classify(file),
    mime: file.type || "application/octet-stream",
    size: file.size,
    url: URL.createObjectURL(file)
  };
}

function revokeAllObjectUrls() {
  for (const url of state.objectUrls) URL.revokeObjectURL(url);
  state.objectUrls.clear();
}

function addFiles(files) {
  let accepted = 0, rejected = 0;
  let totalBytes = state.assets.reduce((sum, item) => sum + item.size, 0);
  for (const file of Array.from(files || [])) {
    const kind = classify(file);
    if (kind === "other" || !Number.isSafeInteger(file.size) || file.size < 1 ||
        file.size > MAX_ASSET_BYTES || state.assets.length >= MAX_DESK_FILES ||
        totalBytes + file.size > MAX_DESK_BYTES) {
      rejected += 1;
      continue;
    }
    const record = safeAssetRecord(file);
    state.objectUrls.add(record.url);
    state.assets.push(record);
    totalBytes += file.size;
    accepted += 1;
  }
  if (state.assetIndex >= state.assets.length) state.assetIndex = Math.max(0, state.assets.length - 1);
  renderAssetDesk();
  setDeskStatus(accepted + " added, " + rejected + " skipped. Local only; max 24 files, 32 MiB each, 128 MiB total. PNG, JPG, GIF, WebP, MP4, WebM, PDF.");
}

function clearPreview() {
  byId("videoPreview").pause();
  for (const id of ["imagePreview", "videoPreview", "pdfPreview"]) {
    const el = byId(id);
    el.removeAttribute("src");
    el.style.display = "none";
  }
}

function selectAsset(index) {
  if (!state.assets.length) {
    state.assetIndex = 0;
    renderAssetDesk();
    return;
  }
  state.assetIndex = (index + state.assets.length) % state.assets.length;
  renderAssetDesk();
}

function renderPreview() {
  clearPreview();
  const empty = byId("previewEmpty");
  if (!state.assets.length) {
    empty.style.display = "block";
    byId("assetCounter").textContent = "0 / 0";
    return;
  }
  const asset = state.assets[state.assetIndex];
  empty.style.display = "none";
  byId("assetCounter").textContent = `${state.assetIndex + 1} / ${state.assets.length}`;
  if (asset.type === "image") {
    const el = byId("imagePreview");
    el.src = asset.url;
    el.style.display = "block";
  } else if (asset.type === "video") {
    const el = byId("videoPreview");
    el.src = asset.url;
    el.style.display = "block";
  } else if (asset.type === "pdf") {
    const el = byId("pdfPreview");
    el.src = asset.url;
    el.style.display = "block";
  }
}

function renderThumbs() {
  const rail = byId("thumbRail");
  rail.textContent = "";
  state.assets.forEach((asset, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "thumb" + (index === state.assetIndex ? " active" : "");
    button.textContent = asset.type === "image" ? "IMG" : asset.type === "video" ? "VID" : "PDF";
    button.title = asset.name;
    button.addEventListener("click", () => selectAsset(index));
    rail.appendChild(button);
  });
}

function treeBranch(title, items, expanded = true) {
  const group = document.createElement("div");
  group.className = "treeBranch";
  const button = document.createElement("button");
  button.type = "button";
  button.className = "treeToggle";
  button.setAttribute("aria-expanded", String(expanded));
  button.textContent = `${expanded ? "▾" : "▸"} ${title}`;
  const children = document.createElement("div");
  children.className = "treeChildren";
  children.hidden = !expanded;
  button.addEventListener("click", () => {
    const next = button.getAttribute("aria-expanded") !== "true";
    button.setAttribute("aria-expanded", String(next));
    button.textContent = `${next ? "▾" : "▸"} ${title}`;
    children.hidden = !next;
  });
  for (const item of items) children.appendChild(item);
  group.append(button, children);
  return group;
}

function renderTree() {
  const tree = byId("assetTree");
  tree.textContent = "";
  const localItems = state.assets.map((asset, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "treeItem";
    button.textContent = `${asset.type === "pdf" ? "▱" : asset.type === "video" ? "▶" : "▧"} ${asset.name}`;
    button.title = `${asset.mime} · ${asset.size} bytes`;
    button.addEventListener("click", () => selectAsset(index));
    return button;
  });
  if (!localItems.length) {
    const empty = document.createElement("div");
    empty.className = "treeEmpty";
    empty.textContent = "No local assets";
    localItems.push(empty);
  }
  const godotItem = document.createElement("div");
  godotItem.className = "treeItem static";
  godotItem.textContent = "◈ godot-export/";
  tree.append(
    treeBranch("Hydra Media", localItems, true),
    treeBranch("Godot", [godotItem], true)
  );
}

function renderAssetDesk() {
  renderPreview();
  renderThumbs();
  renderTree();
}

function clearAssets() {
  clearPreview();
  revokeAllObjectUrls();
  state.assets = [];
  state.assetIndex = 0;
  renderAssetDesk();
  setDeskStatus("Local media cleared and preview URLs revoked.");
}

async function probeGodot() {
  const playButton = byId("playFirstNight");
  const playStatus = byId("playStatus");
  try {
    const response = await fetch("/harness/godot-readiness.json", { method: "GET", cache: "no-store", signal: AbortSignal.timeout(BOOT_TIMEOUT_MS) });
    if (!response.ok) throw new Error("3D readiness endpoint unavailable");
    const proof = await response.json();
    if (proof?.schema !== "luhmOs.godotEmbedReadiness.v1" || proof?.ready !== true || proof?.integrity !== "SHA256_PASS" || proof?.wasmCount < 1 || proof?.pckCount < 1) throw new Error("3D bundle not proven");
    state.godotReady = true;
    const externalLink = byId("godotExternalLink");
    if (externalLink) externalLink.hidden = true;
    byId("godotFrame").src = "/harness/godot-export/index.html";
    byId("godotFrame").style.display = "block";
    byId("godotEmpty").style.display = "none";
    byId("godotBadge").textContent = "3D ASSET INTEGRITY PASS";
    if (playButton) {
      playButton.disabled = false;
      playButton.textContent = "▶ PLAY FIRST NIGHT";
    }
    if (playStatus) playStatus.textContent = "Riverwalk is ready. Click to jump into the game.";
  } catch (_) {
    state.godotReady = false;
    // The MCP cockpit and Godot 3D player are separate Render services.
    // Offer an explicit user-initiated cross-origin handoff without bypassing
    // the same-origin SHA256 gate or claiming the remote player is proven.
    const externalLink = byId("godotExternalLink");
    if (externalLink) externalLink.hidden = false;
    byId("godotBadge").textContent = "LOCAL EXPORT PENDING";
    if (playButton) {
      playButton.disabled = true;
      playButton.textContent = "WEB EXPORT PENDING";
    }
    if (playStatus) playStatus.textContent = "This origin has no verified embedded 3D export. Use the separate Godot service link and verify it there.";
  }
}

function wirePlayButton() {
  const button = byId("playFirstNight");
  if (!button) return;
  button.addEventListener("click", () => {
    if (!state.godotReady) return;
    const stage = byId("godotStage");
    if (stage) stage.scrollIntoView({ behavior: "smooth", block: "center" });
    window.setTimeout(() => byId("godotFrame")?.focus(), 350);
  });
}

function wireDropZone() {
  const input = byId("assetInput");
  const zone = byId("dropZone");
  input.addEventListener("change", () => { addFiles(input.files || []); input.value = ""; });
  for (const eventName of ["dragenter", "dragover"]) {
    zone.addEventListener(eventName, event => {
      event.preventDefault();
      zone.classList.add("dragging");
    });
  }
  for (const eventName of ["dragleave", "drop"]) {
    zone.addEventListener(eventName, event => {
      event.preventDefault();
      zone.classList.remove("dragging");
    });
  }
  zone.addEventListener("drop", event => addFiles(event.dataTransfer?.files || []));
}



async function boot() {
  // Local creative desk stays usable even if the network/config stage fails.
  renderNetwork();
  initLumLive2d();
  state.pets = DEFAULT_PETS.map(p => ({ ...p }));
  renderAssetDesk();
  wireDropZone();
  wirePlayButton();
  // The entire local media desk must remain functional if config or sprites fail.
  byId("petDock").addEventListener("click", () => {
    state.petIndex = (state.petIndex + 1) % Math.max(state.pets.length, 1);
    showPet();
  });
  byId("parallaxHeader").addEventListener("pointermove", onPointerMove);
  byId("parallaxHeader").addEventListener("pointerleave", resetParallax);
  window.addEventListener("blur", resetParallax);
  document.addEventListener("visibilitychange", () => { if (document.hidden) resetParallax(); });
  reducedHeaderMotion.addEventListener("change", resetParallax);
  window.addEventListener("pagehide", resetParallax, { once: true });
  byId("prevAsset").addEventListener("click", () => selectAsset(state.assetIndex - 1));
  byId("nextAsset").addEventListener("click", () => selectAsset(state.assetIndex + 1));
  byId("clearAssets").addEventListener("click", clearAssets);
  window.addEventListener("beforeunload", revokeAllObjectUrls, { once: true });

  const previousSelection = safePetSelection();
  showPet();
  const [cfg, pets, spriteManifest] = await Promise.all([
    fetchJson("/harness/config.json"),
    fetchJson("/harness/pets.json"),
    fetchJson("/harness/assets/agent-loading-sprites.json")
  ]);
  window.luhmStudioDeck?.configure(cfg.embeddedStudio);
  state.loadingManifest = spriteManifest;
  setLoadingAgent("belldandySecretary", "Loading the verified agent roster");
  validateLoadingManifest(spriteManifest);
  setLoadingAgent("sumi", "Checking the large sprite atlas");
  if (typeof spriteManifest.assetUrl !== "string" || !/^\/harness\/assets\/agent-roster-v1\.png$/.test(spriteManifest.assetUrl)) throw new Error("Unexpected sprite atlas URL");
  const atlasResponse = await fetch(spriteManifest.assetUrl, { method: "HEAD", cache: "no-store", signal: AbortSignal.timeout(BOOT_TIMEOUT_MS) });
  if (!atlasResponse.ok) throw new Error("agent sprite atlas unavailable");
  const validatedPets = validatePets(pets.pets);
  state.pets = validatedPets;
  state.petIndex = Math.max(0, validatedPets.findIndex(p => p.name === previousSelection));
  renderLibraries(cfg.libraries || {});
  showPet();

  setLoadingAgent("kugi", "Checking the Godot web viewer");
  await probeGodot();
  byId("edgeBadge").textContent = "SOURCE-VERIFIED DEMO";
}

boot().catch(error => {
  byId("edgeBadge").textContent = "DESKTOP OFFLINE / UNVERIFIED";
  setDeskStatus("Configuration unavailable. Local media desk remains usable; hosted 3D is unverified.");
  console.error("LuHm desktop dependency unavailable", error);
}).finally(() => {
  byId("agentLoadingScreen").hidden = true;
});
