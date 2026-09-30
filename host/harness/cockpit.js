"use strict";

const byId = id => document.getElementById(id);
const state = {
  pets: [],
  petIndex: 0,
  assets: [],
  assetIndex: 0,
  objectUrls: new Set(),
  raf: 0,
  pointerX: 0,
  pointerY: 0
};

function isLoopback() {
  const h = location.hostname;
  return h === "127.0.0.1" || h === "localhost" || h === "::1";
}

function renderNetwork() {
  const local = isLoopback();
  byId("networkStatus").textContent = local ? `${location.protocol}//${location.host}` : "Render HTTPS edge";
  byId("networkNote").textContent = local
    ? "Loopback development shell. No remote asset upload."
    : "Render redirects public HTTP to HTTPS. Origin remains IPv4-only.";
  byId("edgeBadge").textContent = local ? "LOCAL / HTTP OK" : "PUBLIC / HTTPS";
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
  try {
    const response = await fetch("/harness/godot-export/index.html", { method: "HEAD", cache: "no-store" });
    if (!response.ok) throw new Error("not staged");
    byId("godotFrame").src = "/harness/godot-export/index.html";
    byId("godotFrame").style.display = "block";
    byId("godotEmpty").style.display = "none";
    byId("godotBadge").textContent = "WEB EXPORT READY";
  } catch (_) {
    byId("godotBadge").textContent = "EXPORT PENDING";
  }
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
  const [cfg, pets] = await Promise.all([
    fetch("/harness/config.json", { cache: "no-store" }).then(r => r.json()),
    fetch("/harness/pets.json", { cache: "no-store" }).then(r => r.json())
  ]);
  state.pets = pets.pets || [];
  renderNetwork();
  renderLibraries(cfg.libraries || {});
  showPet();
  renderAssetDesk();
  wireDropZone();

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

  await probeGodot();
}

boot().catch(error => {
  byId("edgeBadge").textContent = "HARNESS ERROR";
  console.error(error);
});
