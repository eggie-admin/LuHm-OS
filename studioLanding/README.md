# Eggie Bagelface · Studio Front Door

**Status:** public static website **source**. Not proof of a deployed website, domain mapping or verified TLS.

**Canonical domain:** `eggiebagelface.art` (exact spelling confirmed). Public Instagram: [@eggiebagelface](https://www.instagram.com/eggiebagelface/).

## Three creative desks

- **Pirate Daddy Studios**: umbrella studio identity.
- **Pirate Daddy Film**: film and motion. Existing historical branding includes `PIRATE DADDIES FILM` and `Pirate Daddy's Film`; do not overwrite legal/account names blindly.
- **Eggie Bagelface Art**: artist's original personal portfolio.

`index.html` is standalone HTML/CSS and contains **no private art**, credentials, APIs, embeds from private Drive, upload controls, or public approvals portal.

## Safer deployment path

1. Identify the **existing** Cloudflare DNS zone records and whatever serves `eggiebagelface.art`; do not overwrite working production routes.
2. Review / approve the exact site source. Use a **dedicated static hosting service** (for example an existing verified Render workspace or a reviewed Cloudflare Pages project) rather than repurposing the private MCP or Godot host.
3. Confirm origin, hostname and **publicly trusted Let's Encrypt** TLS from the real serving endpoint before DNS cutover; note Cloudflare Universal SSL cannot be forced to Let's Encrypt without appropriate certificate-management controls.
4. Keep the site's contact fallback as the known existing Gmail until the custom-domain Cloudflare aliases are actually verified and receiving mail.
5. Capture a real screenshot and mobile accessibility review, then only publish source-approved public content.

## Private workflow

Owner-only Drive Release Desk: `https://drive.google.com/drive/folders/1XO743urP4YxU_HTvAiXiv_hdgF2W3SFH`.

Individual brands each have `Drafts and Originals PRIVATE`, `In Review`, `Approved for Release` and `Published Receipts`. A folder is **not** an approval signal; record exact file/hash, rights, Professor sign-off and scheduled destination. Nothing in these folders should be published directly from this static page.

Instagram account `eggiebagelface` is linked in Windsor.ai. Metricool was connected to ChatGPT, but the Metricool brand does **not yet have an active social account** for drafting/scheduling. Once connected, Metricool review flow can request approval from the owner; its plan may need team management. Do not use Windsor.ai publishing actions to bypass the review.
