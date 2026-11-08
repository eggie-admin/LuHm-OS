import { cloudflareCanonLanes, classifyCloudflareRequest, getLuHmCloudflareBrand } from "./core/cloudflareCanon.mjs";

const brand = getLuHmCloudflareBrand();
const list = document.getElementById("edgeMatrix");
const summary = document.getElementById("edgeSummary");
const button = document.getElementById("showEdge");
let hasRendered = false;

function renderSourcePolicy() {
  if (hasRendered) return;
  list.replaceChildren();
  for (const lane of cloudflareCanonLanes) {
    const result = classifyCloudflareRequest({ lane, contentClass: "sha256Asset" });
    const item = document.createElement("li");
    // Render reviewed policy labels as plain text nodes only.
    item.textContent = `${lane}: ${result.state} · ${result.runtime} · Crown ${result.crown}`;
    list.appendChild(item);
  }
  summary.textContent = `${brand.product} · ${brand.publisher} · ${brand.world} · source rules inspected, CDN deployment unverified.`;
  hasRendered = true;
  button.disabled = true;
}
button.addEventListener("click", renderSourcePolicy);
