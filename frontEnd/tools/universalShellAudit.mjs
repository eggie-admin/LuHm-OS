// Deterministic source boundary for the browser-only LuHm cockpit.
// This is not a claim of Firefox, Safari, Pi or ChromeOS runtime acceptance.
import { readFile, access } from "node:fs/promises";
import { resolve, dirname } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");

export function auditStaticShell({ html, css, app }) {
  const failures = [];
  const requireValue = (ok, reason) => { if (!ok) failures.push(reason); };
  const policy = html.match(/<meta\s+http-equiv="Content-Security-Policy"\s+content="([^"]+)"/i)?.[1] || "";

  requireValue(html.startsWith("<!doctype html>"), "doctype");
  requireValue(/<meta\s+name="referrer"\s+content="no-referrer">/.test(html), "referrer_policy");
  for (const rule of ["default-src 'self'", "script-src 'self'", "style-src 'self'", "object-src 'none'",
                      "base-uri 'none'", "form-action 'none'", "connect-src 'self'"]) {
    requireValue(policy.split(";").some(v => v.trim() === rule), "csp_" + rule.split(" ")[0]);
  }
  requireValue(!/unsafe-inline|unsafe-eval|\bhttps?:|\bdata:/.test(policy.replace(/img-src[^;]*/g, "")), "csp_expansion");
  const tags = [...html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script\s*>/gi)];
  requireValue(tags.length >= 6, "script_inventory");
  const sources = [];
  for (const [, attrs, body] of tags) {
    const src = attrs.match(/(?:^|\s)src\s*=\s*"([^"]+)"/i)?.[1] || "";
    if (!src || body.trim()) failures.push("script_inline_or_missing_src");
    // A local script has no scheme, query, escaped slash or parent traversal.
    if (!/^(?:\.\/)?[A-Za-z0-9_-]+(?:\/[A-Za-z0-9_.-]+)*\.js$/.test(src) ||
        src.includes("..") || src.includes("\\")) failures.push("script_not_relative_local");
    sources.push(src.replace(/^\.\//, ""));
  }
  requireValue(sources[0] === "vendor/jquery-3.7.1.min.js" && sources.at(-1) === "app.js",
               "script_load_order");
  requireValue(/<link\s+rel="stylesheet"\s+href="\.\/styles\.css">/.test(html), "stylesheet_local");
  requireValue(!/<(?:script|link)[^>]+\b(?:src|href)="https?:/i.test(html), "external_script_style");
  requireValue(!/\son[a-z]+\s*=/.test(html), "inline_event");
  requireValue(html.includes('href="#messageInput"') && html.includes('id="messageInput"'), "keyboard_skip");
  requireValue(css.includes("height: 100vh;") && css.includes("height: 100dvh;"),
               "viewport_progressive_fallback");
  requireValue(css.includes(".composer input:focus-visible"), "keyboard_focus");
  requireValue(css.includes("prefers-reduced-motion"), "reduced_motion");
  requireValue(app.includes('["cockpit_ready", "world_requested", "oni_requested"]') &&
               app.includes("permitted.includes(type)") && app.includes("bridge.postMessage(JSON.stringify(payload))"),
               "native_bridge_allowlist");
  requireValue(app.includes("/^[a-z][A-Za-z0-9]{0,31}$/"), "native_agent_id_validation");
  requireValue(!/\b(eval|new Function)\s*\(/.test(app), "no_dynamic_eval");
  return { schema: "luhmOs.universalStaticShellAudit.v1", status: failures.length ? "RED_SOURCE" : "GREEN_SOURCE_ONLY",
           failures, sources, liveBrowserProof: false, kioskDeviceProof: false, releaseAuthorized: false };
}

async function main() {
  const html = await readFile(resolve(ROOT, "index.html"), "utf8");
  const css = await readFile(resolve(ROOT, "styles.css"), "utf8");
  const app = await readFile(resolve(ROOT, "app.js"), "utf8");
  const receipt = auditStaticShell({ html, css, app });
  for (const source of receipt.sources) {
    try { await access(resolve(ROOT, source)); }
    catch { receipt.failures.push("missing_local_asset:" + source); }
  }
  if (receipt.failures.length) receipt.status = "RED_SOURCE";
  process.stdout.write(JSON.stringify(receipt, null, 2) + "\n");
  if (receipt.failures.length) process.exitCode = 1;
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  await main();
}
