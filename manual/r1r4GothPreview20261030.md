# R1 → R4 : original adult goth oni 3D opening-screen preview
Candidate branch: draft PR #463. No external art, animation packages, models, cloud provider, GPU backend software or extra workflows added.

**What now opens:** the rootless Python + SQLite cockpit serves an original adult gothic oni **procedural indexed 3D mesh**, rendered with WebGL2 in a native browser canvas, with a large sculpted corset/bust, horn ornaments, animated breathing, touch-to-rotate, stylized face/hair/eyes, and reduced-motion support. If WebGL2 is unavailable, the original 2D SVG illustration stays visible. No nudity. This is not an imported Blender rig, fitted animated skin topology, a Godot scene or a native Android APK.

**Escalation and evidence:**
- R1 Proposed: exact-source SHA, policy, deterministic geometry tests, Python static-file checks; automated source-only checks.
- R2 Testing: **requires** independent full exact-head CI proof *and actual Samsung browser WebGL2 interaction/visible canvas acceptance*. Source CI cannot simulate the real tablet.
- R3 Signed beta: **requires** the separately existing owner-held signing/certificate workflow, legitimate distribution rights, Android target/ABI/install touch and upgrade evidence. A Chrome shortcut or Termux browser app is not a signed APK.
- R4 Public release: human owner approval of exact artifact, compatible license, verified public install/upgrade/rollback/HTTPS paths, privacy/accessibility and legal review.
- Any failure escalates 0→1→2→3 through the existing escalation kernel; **no escalation automatically changes permissions**.

**Open now from an unrooted tablet:** checkout PR #463 at its current exact SHA, `bash tools/termuxRootlessCast.sh start`, open `http://127.0.0.1:8787/`. You should see the WebGL2 character in the opening left-hand screen if Chrome/WebView's GPU path allows it; otherwise the SVG fallback persists. Drag directly on the 3D canvas to rotate; ArrowLeft/ArrowRight work if focused. The story is the existing offline Python/SQLite dating sim.

**Diagnostics:** `python3 -m tools.rootlessCastCockpit --check`, `node --test frontEnd/rootlessCockpit/tests/avatar3d.test.mjs`, and `python3 tools/r1r4ReleaseGate.py --source-ref "$(git rev-parse HEAD)" --output /tmp/r1-r4-proposed.json`.

**Caveat:** CI checks real mesh vertices/indices/finite normals, fallback source, code security and HTTP route, but *does not run a graphical Chrome GPU context*. Actual frame rates, material realism, topology deformation, hair simulation, sound, native Godot avatar compositing and other engines are still unverified.

Independent references: https://developer.mozilla.org/en-US/docs/Web/API/WebGL2RenderingContext and https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_android.html .
