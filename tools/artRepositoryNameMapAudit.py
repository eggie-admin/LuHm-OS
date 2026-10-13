#!/usr/bin/env python3
"""Source-only review of art.eggiebagelface.* naming vs actual DNS and GitHub repositories."""
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
data = json.loads((root / "doctrine/artRepositoryNameMapV1.json").read_text(encoding="utf-8"))
canon = json.loads((root / "doctrine/namingNamespaceCanonV1.json").read_text(encoding="utf-8"))
edge = json.loads((root / "doctrine/staticPublicEdgeV1.json").read_text(encoding="utf-8"))
cf = json.loads((root / "doctrine/cloudflareAirTrafficControllerV1.json").read_text(encoding="utf-8"))

def require(ok, reason):
    if not ok:
        raise SystemExit("RED_ART_REPO_DNS_" + reason)

require(data["schema"] == "luhmOs.artRepositoryNameMap.v1", "SCHEMA")
require(data["status"] == "SOURCE_ONLY_DNS_AND_REPO_PROPOSAL", "STATUS")
require(data["intent"]["rawRequestedPattern"] == "art.eggiebagelface.*", "USER_PATTERN")
require(data["intent"]["exactFqdnConfirmedByProfessor"] is False, "FQDN_NOT_YET_CONFIRMED")
require(data["intent"]["exactLiveFqdnProposed"] == "art.eggiebagelface.art", "PROPOSED_FQDN")
require(data["namespace"]["historicalInternalExample"] == canon["namespaceEscalation"]["example"]["repositoryKebabNamespace"]["namespacePattern"], "CANON_IDENTITY")
require(data["namespace"]["historicalExampleIsDnsRecord"] is False, "ALIAS_AS_DNS")
require(data["namespace"]["repositorySlugStyle"] == "lowercase-kebab-case", "SLUG_STYLE")
require(data["namespace"]["stateTokenStyle"] == "UPPERCASE_DRAGONTAIL", "DRAGON_TAIL_STYLE")
require(data["proposal"]["record"]["name"] == "art", "DNS_LABEL")
require(data["proposal"]["record"]["type"] == "CNAME", "DNS_RECORD_TYPE")
require(data["proposal"]["record"]["proxied"] is False, "DNS_ONLY")
require(data["proposal"]["record"]["target"] == "luhm-os-publication-site.onrender.com", "RENDER_TARGET")
require(data["sourceReferences"]["renderOriginUrl"] == edge["observedOrigins"]["publicationSite"]["currentUrl"], "EDGE_ORIGIN")
require(data["proposal"]["dnsProvider"] == cf["provider"] == "cloudflare", "CLOUDFLARE")
require(data["proposal"]["nameserverDelegation"] is False and data["proposal"]["reverseDnsPtr"] is False, "NS_PTR_LANE")
require(data["proposal"]["autoDnsMutation"] is False, "AUTO_DNS")
require(data["proposal"]["noRepositoryDirectNsTarget"] is True, "DIRECT_REPO_DNS")
require(data["authorityBoundary"]["crownStatus"] == "STOP", "CROWN")
require(all(value is False for key,value in data["authorityBoundary"].items() if key != "crownStatus"), "LIVE_AUTHORITY")
repos = data["repos"]["discovered"]
require(len(repos) == data["sourceReferences"]["repositoryInventorySize"] == 19, "REPO_COUNT")
require(len(set(repos)) == len(repos), "DUPLICATE_REPO")
require(all(x.startswith("eggie-admin/") for x in repos), "REPO_OWNER")
require(set(data["repos"]["candidateIndexLinks"]).issubset(set(repos)), "UNKNOWN_INDEX_REPO")
require(data["repos"]["indexState"] == "PROPOSED_LINKS_ONLY_NOT_PUBLISHED", "PUBLICATION_STATE")
for name in repos:
    slug = re.sub(r"[^a-z0-9]+", "-", name.split("/",1)[1].lower()).strip("-")
    require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) is not None, "SLUG")
require("Professor confirms intended FQDN and repository selection" in data["proofGates"], "PROFESSOR_SCOPE")
print("GREEN_ART_REPO_DNS_SOURCE_ONLY")
