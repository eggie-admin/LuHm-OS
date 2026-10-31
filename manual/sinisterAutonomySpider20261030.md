# Sinister autonomy / one workflow, less human effort by evidence

One controller: `python3 -m tools.r1UnifiedFlow --source-ref "$(git rev-parse HEAD)" --depth 0x10 --spider`.
The helper `tools/sinisterSpider.py` is NOT another agent, installer, crawler or promotion authority. It parses a bounded set of local Python imports, static JavaScript imports, rootless HTML references and declared CI commands, checks existing files, and records deterministic source-edge/hash counts. Python AST is **parsed not executed**. GitHub donor URLs are never crawled and no project media or private secrets are uploaded.

## Zero human need → manual human need, then down again
- **0** (`0x00`): deterministic source checks and safe closing; reproducible draft repairs can be proposed, not silently merged.
- **1** (`0x01`): notify/review only after automated investigations cannot resolve ambiguity or independent evidence is incomplete.
- **2** (`0x02`): owner supplies actual device, legal/rights or account evidence when necessary. A verified receipt can lower this *attention level*, but not release authority.
- **3** (`0x03`): owner authorization for privileged actions including signing, publishing, protected-main merge, paid providers and firmware/kernel/grub changes. **Never automatic**.

This is a human-intervention index, distinct from the existing zero-based 0–3 escalation **tier** and R1–R4 release **stage**. A passing CI check does not reduce a signing gate to zero.

## Reconcile dimensions
- **2×2**: source/runtime × machine/human (four planning cells).
- **4×4**: impact0..3 × human0..3 (16 routing cells).
- **8×8**: eight engineering layers × eight evidence classes (64 conceptual evidence slots).
- **4×4×8×16**: existing R1 2,048 conceptual addresses, only 256 sampled by policy.
- Hex audit depths: `0x00 → 0x02 → 0x04 → 0x08 → 0x10 → 0x20 → 0x40 → 0x80 → 0x100`. Depth above `0x10` remains planned until independent device, model or owner evidence.

A spider report's `nodesVisited` and `edgesChecked` are genuine filesystem reads, **not** verified CI runs, Android installs, 3D frames, AI benchmark runs, or release authorizations. Missing referenced source or symlink traversal is RED. CI is the authority for how many of these source checks passed at the exact commit.

## Operationally safe mutation and merging
Keep previously approved source changes and new narrow fixes together on **draft PR #463**, no blind merges with unrelated PR #460/#461, no protected-main merge or public release from this tool. Source-only CI may produce a proposed patch for humans to review. No automatic agent activation, firmware modification, GRUB installation, Samsung rooting, remote spider, model calls, paid dependencies, APK installation or signing. On unrooted Samsung Termux, `bash tools/termuxRootlessCast.sh audit` is enough.

### Example command
```sh
python3 -m tools.r1UnifiedFlow --source-ref "$(git rev-parse HEAD)" --depth 0x10 --spider --output /tmp/r1-spider.json
python3 -m unittest tests.testSinisterSpider -v
```
A receipt can support de-escalation back to zero human attention **only for closed, read-only tasks**. Final CAST stays with the owner, Crown STOP.
