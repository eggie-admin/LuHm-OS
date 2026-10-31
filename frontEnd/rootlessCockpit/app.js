"use strict";
const $ = id => document.getElementById(id);
let currentState = null;
async function request(path, payload) {
  const response = await fetch(path, {
    method: payload === undefined ? "GET" : "POST",
    headers: payload === undefined ? {} : {"Content-Type":"application/json"},
    body: payload === undefined ? undefined : JSON.stringify(payload),
    credentials: "same-origin", cache: "no-store"
  });
  if (!response.ok) throw new Error("Local state unavailable: " + response.status);
  return await response.json();
}
function present(state) {
  currentState = state;
  $("speaker").textContent = "↳ " + state.speaker;
  $("dialogue").textContent = state.line;
  $("affinity").textContent = "AFFINITY · " + String(state.affinity).padStart(2,"0") + "/10";
  const box = $("choices"); box.replaceChildren();
  state.choices.forEach((label, choice) => {
    const button = document.createElement("button");
    button.textContent = "✦  " + label;
    button.type = "button";
    button.addEventListener("click", async () => {
      button.disabled = true;
      try { present(await request("/api/choice", {choice, revision: currentState.revision})); }
      catch { $("connection").textContent = "LOCAL STATE CONFLICT · RELOADING"; await refresh(); }
    });
    box.appendChild(button);
  });
  $("connection").textContent = state.ending ? "REHEARSAL COMPLETE · PRIVATE" : "PYTHON + SQLITE CONNECTED";
}
async function refresh() {
  try { present(await request("/api/state")); }
  catch { $("dialogue").textContent = "Start the local Python service in Termux, then reload."; $("connection").textContent = "OFFLINE COCKPIT SERVER NOT READY"; }
}
$("reset").addEventListener("click", async () => {
  if (!currentState) return;
  try { present(await request("/api/reset", {revision: currentState.revision})); }
  catch { await refresh(); }
});
document.querySelectorAll(".mode").forEach(button => button.addEventListener("click", () => {
  document.body.dataset.scene = button.dataset.scene;
  document.querySelectorAll(".mode").forEach(b => b.classList.toggle("selected", b === button));
}));
refresh();
