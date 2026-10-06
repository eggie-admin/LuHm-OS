"use strict";

const byId = id => document.getElementById(id);
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
}

function scheduleParallax() {
  if (state.raf) return;
  state.raf = requestAnimationFrame(() => {
    state.raf = 0;
    const x = Math.max(-1, Math.min(1, state.pointerX));
    const y = Math.max(-1, Math.min(1, state.pointerY));
    byId("pixelPet").style.transform = `translate3d(${x * 8}px,${y * 6}px,0) rotate(${x * 2}deg)`;
    byId("parallaxHeader").style.setProperty("--px", `${x * 10}px`);
    byId("parallaxHeader").style.setProperty("--py", `${y * 6}px`);
  });
}

function onPointerMove(event) {
  const rect = byId("parallaxHeader").getBoundingClientRect();
  state.pointerX = ((event.clientX - rect.left) / Math.max(rect.width, 1) - 0.5) * 2;
  state.pointerY = ((event.clientY - rect.top) / Math.max(rect.height, 1) - 0.5) * 2;
  scheduleParallax();
}

function classify(file) {
  if (file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf")) return "pdf";
  if (file.type.startsWith("image/")) return "image";
  if (file.type.startsWith("video/")) return "video";
  return "other";
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
  for (const file of files) {
    const kind = classify(file);
    if (!["image", "video", "pdf"].includes(kind)) continue;
    const record = safeAssetRecord(file);
    state.objectUrls.add(record.url);
    state.assets.push(record);
  }
  if (state.assetIndex >= state.assets.length) state.assetIndex = Math.max(0, state.assets.length - 1);
  renderAssetDesk();
}

function clearPreview() {
  for (const id of ["imagePreview", "videoPreview", "pdfPreview"]) {
    const el = byId(id);
    el.removeAttribute("src");
    el.style.display = "none";
  }
  byId("videoPreview").pause();
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
}

async function probeGodot() {
  const playButton = byId("playFirstNight");
  const playStatus = byId("playStatus");
  try {
    const response = await fetch("/harness/godot-export/index.html", { method: "HEAD", cache: "no-store" });
    if (!response.ok) throw new Error("not staged");
    state.godotReady = true;
    byId("godotFrame").src = "/harness/godot-export/index.html";
    byId("godotFrame").style.display = "block";
    byId("godotEmpty").style.display = "none";
    byId("godotBadge").textContent = "WEB EXPORT READY";
    if (playButton) {
      playButton.disabled = false;
      playButton.textContent = "▶ PLAY FIRST NIGHT";
    }
    if (playStatus) playStatus.textContent = "Riverwalk is ready. Click to jump into the game.";
  } catch (_) {
    state.godotReady = false;
    byId("godotBadge").textContent = "EXPORT PENDING";
    if (playButton) {
      playButton.disabled = true;
      playButton.textContent = "WEB EXPORT PENDING";
    }
    if (playStatus) playStatus.textContent = "This host has not staged the Godot browser build yet.";
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
  input.addEventListener("change", () => addFiles(input.files || []));
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
  const [cfg, pets, spriteManifest] = await Promise.all([
    fetch("/harness/config.json", { cache: "no-store" }).then(r => r.json()),
    fetch("/harness/pets.json", { cache: "no-store" }).then(r => r.json()),
    fetch("/harness/assets/agent-loading-sprites.json", { cache: "no-store" }).then(r => r.json())
  ]);
  state.loadingManifest = spriteManifest;
  setLoadingAgent("belldandySecretary", "Loading the verified agent roster");
  validateLoadingManifest(spriteManifest);
  setLoadingAgent("sumi", "Checking the large sprite atlas");
  const atlasResponse = await fetch(spriteManifest.assetUrl, { method: "HEAD", cache: "no-store" });
  if (!atlasResponse.ok) throw new Error("agent sprite atlas unavailable");
  state.pets = pets.pets || [];
  renderNetwork();
  renderLibraries(cfg.libraries || {});
  showPet();
  renderAssetDesk();
  wireDropZone();
  wirePlayButton();

  byId("petDock").addEventListener("click", () => {
    state.petIndex = (state.petIndex + 1) % Math.max(state.pets.length, 1);
    showPet();
  });
  byId("parallaxHeader").addEventListener("pointermove", onPointerMove);
  byId("parallaxHeader").addEventListener("pointerleave", () => {
    state.pointerX = 0;
    state.pointerY = 0;
    scheduleParallax();
  });
  byId("prevAsset").addEventListener("click", () => selectAsset(state.assetIndex - 1));
  byId("nextAsset").addEventListener("click", () => selectAsset(state.assetIndex + 1));
  byId("clearAssets").addEventListener("click", clearAssets);
  window.addEventListener("beforeunload", revokeAllObjectUrls, { once: true });

  setLoadingAgent("kugi", "Checking the Godot web viewer");
  await probeGodot();
  byId("agentLoadingScreen").hidden = true;
}

boot().catch(error => {
  byId("edgeBadge").textContent = "HARNESS ERROR";
  setLoadingAgent("urdDoctorGoddess", "Startup could not be verified");
  console.error(error);
});
