<script setup>
// Original Live2D-style Vue 3 island, optional SOURCE component.
// This is not the proprietary Cubism SDK or a licensed model runtime.
import { ref, computed, onMounted, onBeforeUnmount } from "vue";

const mood = ref("smile");
const blinked = ref(false);
const waving = ref(false);
const paused = ref(false);
const reducedMotion = ref(true);
const pointer = ref({ x: 0, y: 0 });
let preference;
let blinkTimer = 0;
let waveTimer = 0;
const active = computed(() => !paused.value && !reducedMotion.value);
const pose = computed(() => ({
  "--vue-x": (active.value ? pointer.value.x * 8 : 0) + "px",
  "--vue-y": (active.value ? pointer.value.y * 5 : 0) + "px",
  "--vue-rot": (active.value ? pointer.value.x * 2 : 0) + "deg"
}));
const status = computed(() => paused.value ? "Motion paused" : "Lum is listening");
function reset() { pointer.value = { x: 0, y: 0 }; }
function move(event) {
  if (!active.value || event.pointerType === "touch" || !Number.isFinite(event.clientX) || !Number.isFinite(event.clientY)) return;
  const box = event.currentTarget.getBoundingClientRect();
  const clamp = value => Math.max(-1, Math.min(1, value));
  pointer.value = {
    x: clamp(((event.clientX - box.left) / Math.max(box.width, 1) - .5) * 2),
    y: clamp(((event.clientY - box.top) / Math.max(box.height, 1) - .5) * 2)
  };
}
function blink() {
  clearTimeout(blinkTimer);
  blinked.value = true;
  blinkTimer = setTimeout(() => { blinked.value = false; }, 220);
}
function wave() {
  clearTimeout(waveTimer);
  waving.value = active.value;
  waveTimer = setTimeout(() => { waving.value = false; }, 750);
}
function toggleMood() { mood.value = mood.value === "smile" ? "neutral" : "smile"; }
function onPreference(event) { reducedMotion.value = event.matches; if (event.matches) reset(); }
function visibility() { if (document.hidden) reset(); }
onMounted(() => {
  preference = window.matchMedia("(prefers-reduced-motion: reduce)");
  reducedMotion.value = preference.matches;
  preference.addEventListener("change", onPreference);
  document.addEventListener("visibilitychange", visibility);
});
onBeforeUnmount(() => {
  clearTimeout(blinkTimer);
  clearTimeout(waveTimer);
  if (preference) preference.removeEventListener("change", onPreference);
  document.removeEventListener("visibilitychange", visibility);
});
</script>

<template>
  <section class="luhmVuePuppet" aria-label="Vue 3 layered Lum 2D candidate">
    <div class="luhmVueStage" :style="pose" :class="{ waving: waving && active }"
         @pointermove="move" @pointerleave="reset">
      <svg viewBox="0 0 300 320" role="img" aria-label="Original neon horned Lum-inspired 2D puppet">
        <g class="outerAura"><circle cx="150" cy="154" r="125" fill="none" stroke="#5ee7ff" stroke-width="3"/></g>
        <g class="puppetBody"><path d="M58 320Q68 229 131 225L181 225Q241 242 254 320Z" fill="#271940" stroke="#e95cb5" stroke-width="5"/></g>
        <g class="puppetHead">
          <path d="M70 257Q48 157 70 91Q99 40 153 44Q227 31 238 103Q259 207 233 264Z" fill="#5d349c"/>
          <path d="M96 104L92 28L131 87M177 86L212 28L216 111" fill="#ede9ff" stroke="#5ee7ff" stroke-width="5"/>
          <ellipse cx="152" cy="158" rx="78" ry="91" fill="#eed4f7" stroke="#633b86" stroke-width="4"/>
          <g v-if="!blinked" fill="#2d1c45"><ellipse cx="124" cy="153" rx="11" ry="15"/><ellipse cx="180" cy="153" rx="11" ry="15"/></g>
          <g v-else fill="none" stroke="#2d1c45" stroke-width="5"><path d="M112 156Q124 167 138 156M167 156Q181 167 194 156"/></g>
          <path v-if="mood === 'smile'" d="M132 193Q151 209 171 193" stroke="#b64b8b" stroke-width="5" fill="none"/>
          <path v-else d="M132 198L171 198" stroke="#b64b8b" stroke-width="5" fill="none"/>
          <path d="M73 128Q74 64 151 62Q220 59 228 124Q181 94 170 96Q140 125 73 128Z" fill="#9b54b3" stroke="#e95cb5" stroke-width="4"/>
        </g>
      </svg>
    </div>
    <div class="luhmVueButtons" role="group" aria-label="Vue 3 Lum puppet controls">
      <button type="button" @click="blink">Blink</button>
      <button type="button" @click="toggleMood">Expression</button>
      <button type="button" @click="wave">Wave</button>
      <button type="button" :aria-pressed="paused" @click="paused = !paused; reset()">Motion</button>
    </div>
    <p role="status" aria-live="polite">{{ status }}</p>
  </section>
</template>

<style scoped>
.luhmVuePuppet{display:grid;gap:10px;color:#f6e9ff}
.luhmVueStage{display:grid;place-items:center;min-height:300px;background:radial-gradient(circle,#633aa055,#101020 73%);overflow:hidden;touch-action:pan-y}
.luhmVueStage svg{width:min(95%,320px);height:auto}
.puppetHead{transform:translate(var(--vue-x),var(--vue-y)) rotate(var(--vue-rot));transform-origin:150px 155px}
.outerAura{transform:translate(var(--vue-x),var(--vue-y))}
.luhmVueButtons{display:flex;flex-wrap:wrap;gap:8px}
.luhmVueButtons button{min-height:44px;padding:9px;background:#251738;color:#f6e9ff;border:1px solid #5ee7ff;border-radius:8px}
@media(prefers-reduced-motion:reduce){.puppetHead,.outerAura{transform:none!important;animation:none!important;transition:none!important}}
</style>
