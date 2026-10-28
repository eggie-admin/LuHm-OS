# LuHm-OS: Project Premonition | Glass World prototype

**This candidate is an isolated Babylon.js + Vue 3 + jQuery local web prototype. It does not embed a running Godot avatar on the tablet.** It does not replace the existing `frontEnd/index.html` or `project.godot` source authority. It implements issue #439's first, low-risk browser proof.

### Actual split
- Babylon.js draws one live WebGL scene with orbit/touch camera and selected, placeable 3D primitives.
- Vue 3 renders the world object inspector. UI supports placing four object kinds, selecting, editing X/Y/Z, removing, and saving/restoring validated JSON in *this browser only*.
- jQuery's standalone `luhmSceneBridge` emits typed `luhm:scene:*` UI events without privilege. The accepted cockpit remains unchanged.
- Godot 4 is the **avatar-only candidate render role**, to be integrated through a separately validated glass/compositor bridge. Current pane intentionally displays a placeholder, **not an active model**.
- Blender remains high-detail model authoring. Godot owns avatar materials, hair physics, expressions and animation previews; it does not author the primary world geometry.
- Python/SQL and FFmpeg/VLC remain distinct authority and media routes. No remote scripts or content fetches.

### Desktop/source smoke (Node 22.12+)
```bash
cd frontEnd/prototypes/glassWorld
npm install --ignore-scripts --no-audit --no-fund
npm test
npm run build
npm run dev
```
The isolated prototype dependencies are pinned, but **no lockfile was committed in the first source pass**. A subsequent source review must generate and commit a vetted lockfile and use `npm ci --ignore-scripts` before this qualifies as reproducible production packaging. Build outputs are not APKs.

### Runtime acceptance not implied by CI
1. Visually verify real 3D object placement and selection in Chrome desktop.
2. Verify touch/rotate, gestures, memory and real frame rate in Samsung SM-X400 System WebView. Honor reduced motion and visibility; consider a 30fps avatar and scaled scene.
3. Evaluate `GodotFragment` with transparent background and WebView Z order on the intended Android/Godot versions. An Android alpha issue was reported and fixed upstream, but practical integration is **not proven**.
4. Use approved avatar footage with actual alpha, or add a native bridge only if it preserves touch, security, and frame time. Fall back to a GLB character in Babylon if native dual engines underperform.
5. Test GLB import with rights and hash allowlist, then Blender → Godot shader/animation → avatar render and FFmpeg/VLC media capture.
6. Review artist credits, licensing, signing and distribution. Never publish original/private media without Professor authorization.

**Crown STOP:** no native APK build, no real Godot avatar, no Samsung compatibility proof, no funding claim.
