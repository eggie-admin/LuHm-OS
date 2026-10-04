import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..');
const app = fs.readFileSync(path.join(root, 'app.js'), 'utf8');
const css = fs.readFileSync(path.join(root, 'ui-hardening.css'), 'utf8');

function requireToken(haystack, token, label) {
  if (!haystack.includes(token)) throw new Error(`${label} missing: ${token}`);
}

for (const token of [
  'MAX_STREAM_NODES = 120',
  'CONTEXT_STALE_MS = 5 * 60 * 1000',
  'sessionStorage',
  'MutationObserver',
  'visibilitychange',
  'providerNetworkTelemetry: false',
  'data-context-freshness',
]) requireToken(app, token, 'runtime hardening');

for (const token of [
  'safe-area-inset-bottom',
  'content-visibility: auto',
  'prefers-reduced-motion: reduce',
  'prefers-contrast: more',
  'min-height: var(--luhm-touch)',
]) requireToken(css, token, 'UI hardening CSS');

for (const forbidden of ['fetch(', 'XMLHttpRequest', 'WebSocket(', '.innerHTML', 'navigator.sendBeacon']) {
  if (app.includes(forbidden)) throw new Error(`front-end runtime gained forbidden network/raw-DOM primitive: ${forbidden}`);
}

console.log('LUHM_UI_HARDENING_GREEN');
