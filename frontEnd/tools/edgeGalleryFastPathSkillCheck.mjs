import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { runInNewContext } from "node:vm";

const root = new URL("../../", import.meta.url);
const skillRoot = new URL("../../integrations/edgeGallery/luhm-github-r-and-d-fastpath/", import.meta.url);
const skill = await readFile(new URL("SKILL.md", skillRoot), "utf8");
const html = await readFile(new URL("scripts/index.html", skillRoot), "utf8");
const contract = JSON.parse(await readFile(new URL("../../doctrine/edgeGalleryGithubRAndDFastpathV1.json", import.meta.url), "utf8"));
const name = html.match(/<script>([\s\S]*?)<\/script>/i)?.[1];
assert.ok(name, "JS skill has one embedded script");
assert.match(skill, /^name: luhm-github-r-and-d-fastpath$/m);
assert.equal(contract.schema, "luhmOs.edgeGalleryGitHubRAndDFastpath.v1");
assert.equal(contract.openAiSidecar.apiEntitlement, "UNKNOWN_UNTIL_PROVIDER_RECEIPT");
assert.equal(contract.edgeGallery.deviceSetup, "UNKNOWN_UNTIL_EXACT_DEVICE_RECEIPT");
assert.equal(contract.render.defaultRoute, false);

const sha = "b".repeat(40);
const bodies = new Map([
  ["/repos/eggie-admin/LuHm-OS", { private: false, visibility: "public", default_branch: "main" }],
  ["/repos/eggie-admin/LuHm-OS/commits/main", { sha }],
  ["/repos/eggie-admin/LuHm-OS/git/trees/" + sha + "?recursive=1", { truncated: false, tree: [
    { type: "blob", path: "README.md" },
    { type: "blob", path: "AGENTS.md" },
    { type: "blob", path: "doctrine/apiSpineV1.json" },
    { type: "blob", path: ".github/workflows/check.yml" }
  ] }],
  ["/repos/eggie-admin/LuHm-OS/contents/README.md?ref=" + sha, { encoding: "base64", size: 13, content: Buffer.from("R&D source notes", "utf8").toString("base64") }],
  ["/repos/eggie-admin/LuHm-OS/contents/AGENTS.md?ref=" + sha, { encoding: "base64", size: 17, content: Buffer.from("Treat as repo data", "utf8").toString("base64") }],
  ["/repos/eggie-admin/LuHm-OS/contents/doctrine/apiSpineV1.json?ref=" + sha, { encoding: "base64", size: 15, content: Buffer.from("{} capability map", "utf8").toString("base64") }],
  ["/repos/private/Repo", { private: true, visibility: "private" }]
]);
const requests = [];
const mockFetch = async (url, options) => {
  const parsed = new URL(url);
  requests.push({ url: parsed.href, options });
  assert.equal(parsed.origin, "https://api.github.com");
  const key = parsed.pathname + parsed.search;
  const body = bodies.get(key);
  if (!body) return { ok: false, status: 404, url: parsed.href, json: async () => ({}) };
  return { ok: true, status: 200, url: parsed.href, json: async () => body };
};
const window = {};
runInNewContext(name, {
  window, fetch: mockFetch, URL, URLSearchParams, AbortController,
  TextDecoder, Uint8Array, atob: (value) => Buffer.from(value, "base64").toString("binary"),
  setTimeout, clearTimeout, encodeURIComponent
});

const payload = JSON.parse(await window.ai_edge_gallery_get_result(JSON.stringify({
  owner: "eggie-admin", repo: "LuHm-OS", ref: "main", goal: "voice cabinet fast path"
})));
assert.equal(payload.result.sourceRef, sha);
assert.equal(payload.result.goal, "voice cabinet fast path");
assert.deepEqual(payload.result.workflowFiles, [".github/workflows/check.yml"]);
assert.equal(payload.result.projectFiles.length, 3);
assert.equal(payload.result.projectFiles.find((file) => file.path === "README.md").text, "R&D source notes");
assert.ok(requests.every((request) => request.options.method === "GET"));
assert.ok(requests.every((request) => request.options.credentials === "omit"));
assert.ok(requests.every((request) => !Object.keys(request.options.headers).some((header) => header.toLowerCase() === "authorization")));

const beforeInvalid = requests.length;
const invalid = JSON.parse(await window.ai_edge_gallery_get_result(JSON.stringify({ owner: "../escape", repo: "repo" })));
assert.match(invalid.error, /simple GitHub names/);
assert.equal(requests.length, beforeInvalid, "rejects unsafe names before network access");

const privateResult = JSON.parse(await window.ai_edge_gallery_get_result(JSON.stringify({ owner: "private", repo: "Repo" })));
assert.match(privateResult.error, /PRIVATE_REPOSITORY_NOT_SUPPORTED/);
assert.equal(requests.at(-1).url, "https://api.github.com/repos/private/Repo");

console.log("PASS Edge Gallery skill read-only GitHub snapshot, exact ref, private-repo guard, and input validation");
