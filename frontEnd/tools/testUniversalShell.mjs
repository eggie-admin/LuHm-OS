import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { auditStaticShell } from "./universalShellAudit.mjs";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const sample = {
  html: await readFile(resolve(root, "index.html"), "utf8"),
  css: await readFile(resolve(root, "styles.css"), "utf8"),
  app: await readFile(resolve(root, "app.js"), "utf8")
};
const check = override => auditStaticShell({ ...sample, ...override });

test("current cockpit passes source-only browser and kiosk contract", () => {
  const result = check({});
  assert.equal(result.status, "GREEN_SOURCE_ONLY", result.failures.join(", "));
  assert.equal(result.liveBrowserProof, false);
  assert.equal(result.kioskDeviceProof, false);
  assert.equal(result.releaseAuthorized, false);
});

test("remote and traversal script imports fail closed", () => {
  for (const src of ["https://example.invalid/exploit.js", "../private.js"]) {
    const result = check({ html: sample.html.replace("./app.js", src) });
    assert.equal(result.status, "RED_SOURCE");
  }
});

test("inline script or event handler fails closed", () => {
  assert.equal(check({ html: sample.html.replace("</body>", "<script>alert(1)</script></body>") }).status, "RED_SOURCE");
  assert.equal(check({ html: sample.html.replace("<body>", '<body onload="x()">') }).status, "RED_SOURCE");
});

test("CSP expansion or removal fails closed", () => {
  const result = check({ html: sample.html.replace("script-src 'self'", "script-src 'self' 'unsafe-inline'") });
  assert.equal(result.status, "RED_SOURCE");
  assert.equal(check({ html: sample.html.replace('http-equiv="Content-Security-Policy"', 'http-equiv="nothing"') }).status, "RED_SOURCE");
});

test("missing keyboard/fallback protections fail closed", () => {
  assert.equal(check({ css: sample.css.replace("height: 100vh;", "height: auto;") }).status, "RED_SOURCE");
  assert.equal(check({ html: sample.html.replace('href="#messageInput"', 'href="#missing"') }).status, "RED_SOURCE");
});

test("native bridge free-form messages or unvalidated agent IDs fail closed", () => {
  assert.equal(check({ app: sample.app.replace("permitted.includes(type)", "true") }).status, "RED_SOURCE");
  assert.equal(check({ app: sample.app.replace("/^[a-z][A-Za-z0-9]{0,31}$/", "/.*/") }).status, "RED_SOURCE");
});
