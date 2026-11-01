# LuHm-OS: Project Premonition | Search and public-release staging

**State:** draft GitHub source, not a new website deployment, public launch, social post, search-engine submission, Android release or signed installation.

## Brand and web-card source

The product name is **LuHm-OS**. The active development identity is **Project Premonition**; **Project Hydra** remains the historical name. Publisher: Eggie Bagelface. The existing horned-L vector remains a source-present mark with final public-art approval pending. Do not suggest Samsung, Google, Apple, OpenAI or other vendors sponsor this project.

The homepage now carries truthful descriptive title and summary metadata, site name and text-based **Open Graph/Twitter summary card** fields. The site keeps distinct page titles and descriptions across its seven public-alpha source pages. The `publicationSite/share-card-preview.html` mock-up is **noindex** and never treated as an approved image asset. It is an HTML layout for private review, not a platform-crawlable PNG. A public `og:image` / `twitter:image` needs a verified HTTPS image URL, raster dimensions, file digest, artwork provenance and explicit release approval. Do not scrape a private master, invent app screenshots, or pretend a generated character portrait is approved public branding.

Tags in `doctrine/premonitionPublicDiscoveryV1.json` are a **topic taxonomy for discoverable site content**, not the deprecated, easily abused `meta keywords` field. They describe only what existing source and public alpha really demonstrate: Godot experiments, creative tools, interactive art, read-only tester previews and source-backed software engineering. SEO cannot guarantee ranking.

## Search-indexing gate

The current canonical production hostname and actual deployed static source commit are **not proven** in this audit. The existing Render static service's source policy references `publication/plugin-full-green-20260930`, **not this draft branch**. Therefore neither a guessed production `rel=canonical` nor an unapproved production `robots.txt` or `sitemap.xml` is added to `publicationSite`.

The source registry holds seven candidate future sitemap routes: root, release notes, tester, Pocket Art Studio, support, privacy and terms. Search indexing is **not automatically requested**. Existing alpha pages may already be indexed and this draft does not blindly delist them. `noindex` protects the standalone card mock-up *if deployed and crawled*, but noindex is not authentication. Never use robots exclusions as protection for private media or secrets.

Google's search guidance:
- https://developers.google.com/search/docs/fundamentals/seo-starter-guide
- https://developers.google.com/search/docs/crawling-indexing/block-indexing
- https://developers.google.com/search/docs/appearance/structured-data/organization

Only after verified host/TLS and owner approval should a later reviewed change add absolute canonical URLs, a real XML sitemap, appropriately scoped robots rules, verified Organization structured data and an approved raster social image. Submit to Search Console only from an approved owner account with real site access. Confirm crawl and rich-preview outcomes externally; local tests cannot prove Google indexing or social-network preview rendering.

## Flags and release tags

`doctrine/premonitionPublicDiscoveryV1.json` holds default-off flags for full public release, sitemap publication/submission, marketing, app downloads, approved share-card image, merges and deploys. These source flags are **release assertions**, not a hidden runtime feature service; flipping a JSON value cannot grant publication authority. GitHub's draft PR provides revision history and test receipts. Do not create a public GitHub Release or `v*` tag merely because SEO checks turn green.

Use `python tools/premonitionSeoReleaseAudit.py` and `python -m unittest discover -s tests -p 'testPremonitionSeoReleaseAudit.py' -v`. The focused PR CI verifies link targets, branded page titles and metadata, one H1 per page, text social tags, the noindex mock-up and all release locks without network calls. It returns `SOURCE_METADATA_STAGED_ONLY`, not a search ranking or release-ready receipt.

## Remaining final public gates

1. Verify the actual deployed static-site branch, expected public origin, TLS, redirect policy, accessibility and responsiveness.
2. Produce and approve correctly licensed 1200×630 social-banner raster(s), test accessible alt descriptions and check real social preview rendering.
3. Confirm each intended public page content, imagery, privacy, support, licensing and signing claims against actual artifacts.
4. Review target platform app signing, Samsung installation and optional Play/F-Droid distribution independently; no unsupported download links or store badges.
5. Obtain the Professor's explicit approval of the exact publication source, target hostname, release tag, outreach language and rollback. Only then add sitemap, robots, canonical/social image URLs and deploy through existing separate authority gates.

**Current state:** source metadata staged; no new public site deployment, SEO submission, release tag, or marketing outreach was performed.
