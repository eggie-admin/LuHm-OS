# LuHm OS | Unified brand shell candidate

**Status:** REVIEW ONLY. **Publisher:** Eggie Bagelface. **Product:** LuHm OS. **Authority:** Professor.
**Source:** `doctrine/organizationBrandRegistryV1.json` and `campaign/brandAndVoiceGuide.md`.

## One identity, many approved surfaces

The first common logo is the existing public horned-L SVG from `publicationSite/logo.svg`. The Render harness now keeps the same image as `host/harness/brandMark.svg` for same-origin loading without additional JavaScript, remote fetching, fonts, tracking or credentials. This is a copy of *already public source art*, not approval of any private character image or a claim that the skull/flame direction is final.

| Surface | Safe branded surface | Outside this patch |
| --- | --- | --- |
| GitHub | README mark, product name, publisher credit, source documentation | GitHub's own interface cannot be reskinned; social preview PNG must be uploaded in repository Settings after approval |
| Render | Our own `/harness/` loading overlay, page title and favicon served by the existing Python harness | Render dashboard, managed platform interstitials, cold-start waiting and provider identity |
| OpenAI API / ChatGPT | Our application's name, icon/approved metadata, custom hosted UI, tool presentation and responses | OpenAI Platform dashboard, ChatGPT chrome, model names, provider logos or provider-generated audio |
| Google AI Studio / Gemini | LuHm app source UI and authored app name/icon via reviewed GitHub synchronization | Google's dashboard, Gemini branding, existing Google product UI, partner status or provider trademarks |
| Godot / Galaxy | A proposed in-game loading/intro skin and eventually icon/splash derivative from approved marks | Native device system UI, installed APK and unpublished model materials |

## Brand gate

- Public names: **LuHm OS** and **Eggie Bagelface**. Do not add unapproved affiliations or use Google, OpenAI, GitHub or Render marks as a co-brand.
- Default colors in the existing public SVG: midnight `#17131f`, violet `#9f7aea`, pearl `#f7f4ff`. This is **not** a final universal palette.
- Generated art, Drive assets, private character rigs and gacha/donor files are **not** public by discovery alone. Require verified author/rights, source digest, approved derivative and Professor release permission.
- Do not add private Drive identifiers, token material, audio recordings or model weights to GitHub.
- Avoid adding decorative provider logos inside ChatGPT responses or duplicating the platform's built-in app identity. Keep ordinary UI accessible.
- Avoid turning a system loading state into a claim of readiness. Label game/device/backend verification separately.

## Minimal loader contract

1. Branded HTML and small same-origin SVG load first. No new NPM dependencies, Python workers, remote fonts, CDN round trips or plugin version changes for this patch.
2. Godot 4 remains **user-initiated** in the existing separate game layer, with an accessible static fallback if blocked.
3. The Python harness currently serves regular static assets with short public cache headers; private or dynamically personalized content must remain no-store. Hashed asset names and longer immutable caching can come after actual deployment acceptance.
4. Avoid automatic offline storage of secrets or private media. A USB/local filesystem cache is an optional future runtime capability, not a permission available to a ChatGPT sandbox.
5. A claimed 100-megabit ChatGPT cap remains **unverified**; do not treat it as a documented platform guarantee.

## Acceptance before deployment

- Review exact GitHub diff and asset byte equivalence with the original public logo.
- Run relevant source/CI checks; prove `/harness/assets/brandMark.svg` is actually served by the deployed source and loading overlay visibly renders on Android/desktop.
- Test contrast, reduced motion, mobile first frame, favicon response, cache headers, offline fallbacks and Godot touch launch. Verify launch separately from loader branding.
- Get Professor approval **before** merging, deploying, plugin release, provider metadata mutation, permission changes or publication.

**Current state:** Staged source candidate only, no production promotion or provider-side branding claim.
