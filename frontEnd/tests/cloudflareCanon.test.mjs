import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  classifyCloudflareRequest, cloudflareCanonLanes, cloudflareCanonClasses,
  cloudflareCanonConditions, getLuHmCloudflareBrand
} from "../core/cloudflareCanon.mjs";

const cfg = JSON.parse(readFileSync(new URL("../../doctrine/cloudflareStaticTransmutationV1.json", import.meta.url)));
const counts = new Map();
let cases = 0;

test("LuHm-OS exact public identity and reviewed camelHump namespace", () => {
  assert.equal(cfg.identity.product, "LuHm-OS");
  assert.equal(cfg.identity.namespace, "luhmOs");
  assert.equal(getLuHmCloudflareBrand().product, "LuHm-OS");
  assert.deepEqual(cloudflareCanonLanes, cfg.routes.map(x => x.id));
  assert.deepEqual(cloudflareCanonClasses, cfg.contentClasses);
  assert.deepEqual(cloudflareCanonConditions, cfg.conditionCases);
  assert.equal(getLuHmCloudflareBrand().cloudflareCdnDeployed, false);
});

test("200 independent JavaScript policy decisions never grant runtime, CDN or Crown", () => {
  for (const lane of cloudflareCanonLanes) {
    for (const contentClass of cloudflareCanonClasses) {
      for (const condition of cloudflareCanonConditions) {
        const r = classifyCloudflareRequest({ lane, contentClass, condition });
        assert.equal(r.lane, lane);
        assert.equal(r.contentClass, contentClass);
        assert.equal(r.condition, condition);
        assert.equal(r.runtime, "UNVERIFIED");
        assert.equal(r.cloudflareCdnDeployed, false);
        assert.equal(r.authorityEffect, "none");
        assert.equal(r.crown, "STOP");
        assert.equal(Object.isFrozen(r), true);
        counts.set(r.state, (counts.get(r.state) || 0) + 1);
        cases += 1;
      }
    }
  }
  assert.equal(cases, 200);
  assert.deepEqual(Object.fromEntries([...counts].sort()), {
    BYPASS_CACHE: 52,
    DENY_PUBLIC: 108,
    HOLD_ORIGIN: 16,
    HOLD_SIGNATURE: 2,
    HOLD_TLS: 16,
    IMMUTABLE_ELIGIBLE_SOURCE_ONLY: 2,
    REVALIDATE_SOURCE_ONLY: 4,
  });
});

test("private, user-specific and executable content fail closed", () => {
  for (const lane of cloudflareCanonLanes) {
    for (const condition of ["privateAsset", "unapprovedArtwork", "remoteExecutable"]) {
      assert.equal(classifyCloudflareRequest({ lane, contentClass: "sha256Asset", condition }).state, "DENY_PUBLIC");
    }
    for (const condition of ["authorization", "sessionCookie", "setCookie"]) {
      const result = classifyCloudflareRequest({ lane, contentClass: "staticHtml", condition }).state;
      assert.ok(result === "BYPASS_CACHE" || lane === "privateSystem" && result === "DENY_PUBLIC");
    }
  }
  assert.equal(classifyCloudflareRequest({lane:"publicMcp",contentClass:"staticHtml"}).state,"BYPASS_CACHE");
  assert.equal(classifyCloudflareRequest({lane:"signedArt",contentClass:"sha256Asset"}).state,"HOLD_SIGNATURE");
  assert.equal(classifyCloudflareRequest({lane:"staticAssets",contentClass:"sha256Asset"}).state,"IMMUTABLE_ELIGIBLE_SOURCE_ONLY");
});

test("unknown lane, content class and condition never guess aliases", () => {
  for (const input of [
    { lane: "public_mcp", contentClass: "staticHtml" },
    { lane: "publicMcp", contentClass: "html_script" },
    { lane: "publicMcp", contentClass: "staticHtml", condition: "publicApproved" },
    { lane: undefined, contentClass: "staticHtml" }
  ]) assert.throws(() => classifyCloudflareRequest(input), /unregistered/);
});

test("static preview is branded and non-executable", () => {
  const html = readFileSync(new URL("../edgeCanon.html", import.meta.url), "utf8");
  const js = readFileSync(new URL("../edgeCanonPreview.mjs", import.meta.url), "utf8");
  assert.match(html, /LuHm-OS \| Cloudflare Canon Preview/);
  assert.match(html, /Eggie Bagelface/);
  assert.match(html, /Project Premonition/);
  assert.match(html, /\.\.\/publicationSite\/logo\.svg/);
  assert.doesNotMatch(js, /innerHTML|fetch\(|eval\(/);
  assert.match(js, /textContent/);
});
