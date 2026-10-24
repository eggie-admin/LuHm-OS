# Lum five-lead operational orchestra

**Status:** Source candidate; five real deterministic source audit lanes now available in GitHub Actions, **not** operational AI worker release.

## Desired operating state

**Professor → Lum → resident cabinet → scoped Oni → evidence → Urd → Belldandy → Professor.**

| Lead | Actual recurring operational job | Minimum helper group | Stop condition |
| --- | --- | --- | --- |
| Lum | Train staff via validated skills and corrections; coordinate logistics/task queues; prevent duplicate workflows; route no more than three specialists; receive and reconcile receipts | all registered roles when independently released | no exact source/task scope or no executor |
| Urd | Monitor repo/system health, access control, malware risk, workflow integrity, secrets exposure and failed checks; issue clinical-style safety diagnosis packets | Kiri/Shiori only when explicitly routed | security breach or unsupported GREEN |
| Belldandy | Organize docs, version history, signed evidence ledger, licenses, licensing requirements, provenance, authored texts and corrected dictation | Fumi, Koe, Sumi for provenance | private writing or asset with no rights/access approval |
| Skuld | Architecture review, package/API/library and vendor compatibility, new upstream documentation, vulnerability advisories, cabinet updates and Oni capability problems | Momo, Shiori, Tetsu for source research | unverified vendor claims or unsafe network mutation |
| Yume | Art direction, branding, images, CSS, storyboards, FFmpeg/Blender/GIMP/Godot pipeline planning and approved media revisions | Sumi, Media Asset Factory, relevant art Oni | unknown rights, unavailable assets, unauthorized build or publicity |

Training here means updating **reviewed behavioral skills and procedures**, not automatically fine-tuning model weights. Urd's “doctor” role is **systems/security/evidence health**, not real-time medical observation of a person. Belldandy's licensing desk is record/provenance work, not a substitute for qualified legal review.

## Actually implemented read-only execution path

`tools/lumCabinetReadiness.py --source-ref <sha> --run-source-checks --output /tmp/cabinet.json`

Runs ten existing, bounded Python source audits in sequence and records exact source, individual exit states, hashes and output tails:

- Lum: `agentSystemDeploymentAudit.py`, `openingDayStaffTrainingAudit.py`
- Urd: `urdClinicalSecurityPracticeAudit.py`, `companyWideQuarantineAudit.py`
- Belldandy: `belldandyHousekeepingAudit.py`, `belldandyOniDeploymentGate.py`
- Skuld: `worldHeadquartersAudit.py`, `networkSpineAudit.py`
- Yume: `yumeArtCabinetAudit.py`, `yumeCreativePipelineAudit.py`

GitHub Action: `.github/workflows/lum-cabinet-readiness.yml`, PR-path-scoped plus on-demand manual, read-only token, exact SHA, bounded timeout, downloadable seven-day diagnostic receipt. No automatic scheduled/persistent workforce is claimed. Malformed roster, unsupervised activation, hidden workers, source concurrency and Crown spoof attempts fail the negative controls.

## Live activation is still a separate project

1. `doctrine/companyWideOperationalQuarantineV1.json` currently holds all 15: `state=QUARANTINED`, `activeTaskWorkersAllowed=false`. An audit passing does not authorize a model worker.
2. Actual tool/provider calls require a deployed authenticated executor with precise task/source/scope identity, bounded token/cost/time budgets, per-agent role permissions, durable queue, human-controlled resume and deterministic receipts. The currently installed Project Hydra Site tools are read-only. The repository's current `tools/openAiAgentTopology.py` reports **zero** provider agents executed; it is topology, not deployment.
3. Record a current-chat exact-source supervised Belldandy MCP invocation, Urd independently adjudicated evidence, and **explicit Professor resume tied to that receipt**. Release only one bounded worker route after proof, never all 15 by flipping a status flag. Real provider and tool actions must be verified individually.
4. A durable approved worker host owns scheduled/background execution. A GitHub Codespace may provide the tool workshop, but an idle-stopping Codespace is not a 24/7 service. GitHub Actions may handle scheduled read-only source verification, not replace a persistent clinical/AI orchestration runtime.
5. Never mix Alex's private iPhone ChatGPT test access with app-wide beta/stable distribution, Android APK signing, private creative rights, or public download packages.

## GitHub/source gates

The three pending source lanes remain separate:
- PR #382: workflow noise/CI tuning
- PR #383: ChatGPT mobile cockpit source candidate
- PR #384: Proposed/Beta/Stable GitHub release hub

This cabinet candidate does **not** silently merge those PRs or update `main`. Main protection must be restored, independent review and exact-head tests must pass, and any build/deploy requires its own policy-qualified authorization. Render workspace and OpenAI Codex are out of this GitHub-only lane.

**Progress doctrine:** machine action first, verify exact receipt, reconcile current Canon, report `PASS/RED/UNKNOWN`. Never call a task completed because an Oni icon appeared or a repository file describes it.
