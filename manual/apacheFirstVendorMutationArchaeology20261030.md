# Apache-first vendor minimization and historical mutation audit
Date: 2026-10-30. Draft candidate only. No code deletion, license mutation, merge or deployment authorized by this document.

## Ground truth
The LuHm root and plugin/npm declarations remain GPL-3.0-only; zero first-party modules have proved Apache-2.0 eligibility. Apache-2.0 code may be incorporated into a GPLv3-compatible combined work under the applicable terms; GPLv3 code cannot simply be relabeled Apache-2.0. Keep upstream copyright, NOTICE, license text and source offers where required.

## Historical mutation archaeology
For each proposed Apache-family dependency, use repository history and official upstream history: original source tag -> first import commit -> patches/forks -> YAML/config change -> plugin/API boundary -> current dependency -> redistribution notice. Record commit hashes, original license and changed ownership. No historical lineage is established merely by name similarity.

| Candidate | Minimum decision | License/provenance gate |
|---|---|---|
| Apache Friends XAMPP | Do not install full stack by default; dev-only optional | Bundle has mixed licenses, not uniformly Apache-2.0 |
| Apache HTTP Server | Keep only if chosen edge reverse proxy | Apache-2.0 plus module/NOTICE inventory |
| Apache Tomcat | Exclude unless a real servlet/Jakarta workload is proven | Apache-2.0 and dependencies |
| Apache Maven/Ant | Exclude unless required by an actual Java build | Compare against existing Gradle |
| Apache Commons/Log4j | Only retain if direct transitive need is demonstrated | License, security version and transitive census |
| Apache YAML configurations | YAML is a data format, not an Apache project or license | Per-file copyright and source provenance |
| Apache plugins/modules | Prefer built-in httpd modules over extra proxies | Module licensing and attack surface |
| Python 3/SQLite | Retain minimal backend and receipts | PSF/public-domain SQLite nuances and packaged dependencies |
| npm | Keep existing lockfile-backed frontend tooling only | npm transitive package-by-package notices |
| Blender/Godot/FFmpeg | Keep necessary 3D/video production tools as isolated workers | GPL/MIT/LGPL/GPL build-specific obligations |

## Reduction algorithm
1. Inventory exact Git SHA, lockfiles, imports, running services and required hardware features.
2. Classify each dependency: essential runtime, build-only, optional studio, compatibility target, duplicate, unknown.
3. Trace historical imports and mutations from upstream tag to current fork, including Apache httpd, Tomcat, plugins and YAML.
4. Build an offline removal candidate with unchanged license/notice files and SBOM.
5. Prove negative tests, security behavior, boot path, API compatibility and 3D pipeline still pass.
6. Measure before/after cold start, RAM, disk footprint and dependency count.
7. Review rollback, security maintenance and copyright before removing any package or approving a merge.

## Four-by-four
| Layer | Source/history | Runtime minimum | Security/license | Verification |
|---|---|---|---|---|
| Machine | firmware and kernel provenance | distro-native services | OEM/GPL boundaries | read-only device receipt |
| Network | Apache/httpd config history | one proxy, no redundant LB | TLS modules, certs | offline routing fixtures |
| AI/backend | Python/npm plugin lineage | one coordinator and SQLite | deny-by-default tools | offline contract tests |
| Studio/frontend | engine import lineage | isolated Blender/Godot/FFmpeg | copyleft and third-party notices | synthetic asset tests |

## No-go
Do not rip out security patches, boot-critical packages, OEM firmware, working TLS, or third-party license notices. No relicense, main merge, live network change, vendor source copy, or production promotion without separately verified receipts.

## Upstream references
https://apache.org/licenses/GPL-compatibility.html
https://www.apache.org/foundation/license-faq.html
https://apache.org/licenses/license-history.html
https://httpd.apache.org/docs/current/mod/mod_proxy.html
https://tomcat.apache.org/
https://www.apachefriends.org/
https://ffmpeg.org/legal.html
