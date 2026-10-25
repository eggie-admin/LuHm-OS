import {
  AmbientLight, Color, DirectionalLight, Group, Mesh, MeshStandardMaterial,
  PerspectiveCamera, Scene, SphereGeometry, TorusGeometry, WebGLRenderer
} from "./vendor/three.module.js";

const canvas = document.getElementById("castCanvas");
const sceneStatus = document.getElementById("sceneStatus");
const castStatus = document.getElementById("castStatus");
const pauseButton = document.getElementById("pauseButton");
const resetButton = document.getElementById("resetButton");
const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
const motion = {paused: reducedMotion, running: false, dragging: false, lastX: 0, angle: 0};
let renderer, frameId = 0, resizeObserver;

function updateStatus(message) {
  sceneStatus.textContent = message;
  castStatus.textContent = "Read-only source candidate · no CAST dispatch, agent runtime or Crown";
}

try {
  const supportsWebGL = Boolean(canvas.getContext("webgl2", {powerPreference:"low-power"}));
  if (!supportsWebGL) throw new Error("WebGL2 unavailable. Static fallback displayed.");
  renderer = new WebGLRenderer({canvas, antialias: true, alpha: true, powerPreference: "low-power"});
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 1.5));
  const scene = new Scene();
  scene.background = new Color("#0a1021");
  const camera = new PerspectiveCamera(43, 1, 0.1, 50);
  camera.position.set(0, 1.15, 6);
  camera.lookAt(0, 0, 0);
  const cast = new Group();
  scene.add(cast);
  scene.add(new AmbientLight("#acd5ff", 1.1));
  const key = new DirectionalLight("#b2fcff", 3);
  key.position.set(3, 5, 7);
  scene.add(key);
  const rim = new Mesh(new TorusGeometry(1.45, 0.15, 16, 72),
    new MeshStandardMaterial({color: "#6cbcff", metalness: 0.55, roughness: 0.28}));
  cast.add(rim);
  const glyphColors = ["#b479ff", "#64eaff", "#f5d282"];
  const sphereGeo = new SphereGeometry(0.27, 24, 16);
  glyphColors.forEach((color, i) => {
    const dot = new Mesh(sphereGeo, new MeshStandardMaterial({
      color, emissive: color, emissiveIntensity: 0.17, roughness: 0.5
    }));
    const a = i * Math.PI * 2 / 3 - Math.PI / 2;
    dot.position.set(Math.cos(a) * 1.47, Math.sin(a) * 1.47, 0);
    cast.add(dot);
  });
  function resize() {
    const {width, height} = canvas.getBoundingClientRect();
    const w = Math.max(1, Math.floor(width)), h = Math.max(1, Math.floor(height));
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h, false);
    renderOnce();
  }
  function renderOnce() { renderer.render(scene, camera); }
  function tick() {
    frameId = 0;
    if (motion.paused || document.hidden || !motion.running) return;
    cast.rotation.y += 0.007;
    cast.rotation.x = Math.sin(cast.rotation.y * 0.6) * 0.18;
    renderOnce();
    frameId = requestAnimationFrame(tick);
  }
  function refreshMotion() {
    if (frameId) cancelAnimationFrame(frameId);
    frameId = 0;
    if (!motion.paused && !document.hidden && motion.running) frameId = requestAnimationFrame(tick);
    else renderOnce();
    pauseButton.setAttribute("aria-pressed", String(motion.paused));
    pauseButton.textContent = motion.paused ? "Resume motion" : "Pause motion";
  }
  pauseButton.addEventListener("click", () => { motion.paused = !motion.paused; refreshMotion(); });
  resetButton.addEventListener("click", () => {
    cast.rotation.set(0, 0, 0);
    camera.position.set(0, 1.15, 6);
    camera.lookAt(0, 0, 0);
    renderOnce();
  });
  canvas.addEventListener("pointerdown", e => {
    motion.dragging = true; motion.lastX = e.clientX; canvas.setPointerCapture(e.pointerId);
  });
  canvas.addEventListener("pointermove", e => {
    if (!motion.dragging) return;
    cast.rotation.y += (e.clientX - motion.lastX) * 0.01;
    motion.lastX = e.clientX;
    renderOnce();
  });
  canvas.addEventListener("pointerup", () => { motion.dragging = false; });
  canvas.addEventListener("pointercancel", () => { motion.dragging = false; });
  document.addEventListener("visibilitychange", refreshMotion);
  canvas.addEventListener("webglcontextlost", event => {
    event.preventDefault();
    motion.running = false;
    if (frameId) cancelAnimationFrame(frameId);
    updateStatus("3D context lost. Static fallback; no automatic rebuild.");
  });
  resizeObserver = new ResizeObserver(resize);
  resizeObserver.observe(canvas.parentElement);
  motion.running = true;
  resize();
  refreshMotion();
  updateStatus("Three.js procedural cast preview · no models or external resources loaded");
} catch (_error) {
  updateStatus("3D engine unavailable. Static CAST demo remains safe; no network retry.");
  if (renderer) renderer.dispose();
  if (resizeObserver) resizeObserver.disconnect();
}
