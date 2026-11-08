/** LuHmOS Tier-0 edge/static projection. Source-only, no fetch, DNS, HTML rewriting or authority. */
const lanes = Object.freeze(["publicMcp","staticAssets","publicSite","signedArt","privateSystem"]);
const contentClasses = Object.freeze(["staticHtml","jsonManifest","sha256Asset","publicCertificate"]);
const conditions = Object.freeze([
  "baseline","authorization","sessionCookie","setCookie","privateAsset",
  "unapprovedArtwork","remoteExecutable","unhashedAsset","unknownTls","unverifiedOrigin"
]);
export const cloudflareCanonLanes = lanes;
export const cloudflareCanonClasses = contentClasses;
export const cloudflareCanonConditions = conditions;

const decision = (state, lane, contentClass, condition) => Object.freeze({
  state, lane, contentClass, condition,
  runtime: "UNVERIFIED",
  cloudflareCdnDeployed: false,
  authorityEffect: "none",
  crown: "STOP"
});

/**
 * Classification only. The actual Cloudflare zone, origin and host must be
 * independently verified; SOURCE_ONLY eligibility must never be applied
 * directly as an HTTP Cache-Control header without reviewed deployment proof.
 */
export function classifyCloudflareRequest({ lane, contentClass, condition = "baseline" } = {}) {
  if (!lanes.includes(lane) || !contentClasses.includes(contentClass) || !conditions.includes(condition)) {
    throw new TypeError("unregistered camelHump edge namespace or condition");
  }
  if (["privateAsset","unapprovedArtwork","remoteExecutable"].includes(condition) ||
      lane === "privateSystem") {
    return decision("DENY_PUBLIC", lane, contentClass, condition);
  }
  if (["authorization","sessionCookie","setCookie"].includes(condition)) {
    return decision("BYPASS_CACHE", lane, contentClass, condition);
  }
  if (condition === "unknownTls") return decision("HOLD_TLS", lane, contentClass, condition);
  if (condition === "unverifiedOrigin") return decision("HOLD_ORIGIN", lane, contentClass, condition);
  if (condition === "unhashedAsset") return decision("DENY_PUBLIC", lane, contentClass, condition);
  if (lane === "publicMcp") return decision("BYPASS_CACHE", lane, contentClass, condition);
  if (lane === "signedArt") {
    return decision(["jsonManifest","sha256Asset"].includes(contentClass) ?
      "HOLD_SIGNATURE" : "DENY_PUBLIC", lane, contentClass, condition);
  }
  if (lane === "staticAssets") {
    if (contentClass === "sha256Asset") return decision("IMMUTABLE_ELIGIBLE_SOURCE_ONLY", lane, contentClass, condition);
    return decision(contentClass === "jsonManifest" ? "REVALIDATE_SOURCE_ONLY" : "DENY_PUBLIC", lane, contentClass, condition);
  }
  // publicSite only: HTML/manifests/certificate metadata revalidate, approved
  // hashed static assets may be immutable AFTER actual CDN+rights+TLS proof.
  return decision(contentClass === "sha256Asset" ?
    "IMMUTABLE_ELIGIBLE_SOURCE_ONLY" : "REVALIDATE_SOURCE_ONLY", lane, contentClass, condition);
}

/** Pure preview identity. Does not read the private plugin or load external assets. */
export function getLuHmCloudflareBrand() {
  return Object.freeze({
    product: "LuHm-OS",
    publisher: "Eggie Bagelface",
    world: "Project Premonition",
    brandColor: "#7C3AED",
    logoPath: "../publicationSite/logo.svg",
    sourceOnly: true,
    cloudflareCdnDeployed: false
  });
}
