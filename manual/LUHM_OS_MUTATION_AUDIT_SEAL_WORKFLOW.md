# LuHm OS Mutation Audit Seal Workflow

> **GREEN documentation workflow.**
>
> This workflow does not promote software, publish releases, sign production artifacts, or change runtime authority.

## Source law

**AI proposes. Policy authorizes. CI proves. Human promotes.**

## The loop

### 1. Quest
Define the objective.

Keep it short.

What are we changing?

What are we not changing?

### 2. Scout
Read reality first.

Check the current canonical repository.

Read current doctrine.

Inspect the actual artifact.

Find the receipts.

Do not mutate yet.

> **Professor:** "Sanity check. What are we actually working on?"

### 3. Plan
Choose the smallest safe mutation.

Name the rollback.

Name the proof you need.

If you cannot explain the proof, you are not ready to claim GREEN.

### 4. Mutate
Make one reviewable change.

Do not renovate the cathedral because one light bulb died.

### 5. Test
Run the test that matches the claim.

A JSON parse proves JSON syntax.

A rendered page proves the page rendered.

A hash proves the bytes you hashed.

None of those prove production readiness.

### 6. Collect Receipts
Keep evidence close to the claim.

Useful receipts include:

- source commit or branch;
- rendered pages;
- parse results;
- link checks;
- SHA-256 hashes;
- generated artifact metadata;
- source references;
- CI results when CI is relevant.

**One receipt. One claim.**

### 7. Gate
Use the status board correctly.

- 🟢 **GREEN** — verified by evidence matching the claim.
- 🟠 **AMBER** — promising or partial. Proof is still missing.
- 🔴 **RED** — failed, blocked, unsafe, or contradicted.
- ⚫ **UNKNOWN** — not checked.

Unknown is allowed.

Green crayon is not.

### 8. Seal
Record what changed.

Record what was proved.

Record what was not proved.

Preserve hashes and provenance.

Save verified documentation to the designated source.

Keep software promotion separate.

---

# Ten-Pass Hard Audit

## Pass 1 — Authority
Resolve the current source of truth.

Current beats old.

Detailed does not automatically mean canonical.

## Pass 2 — Scope
Write the mutation boundary.

A documentation pass is not a release pass.

## Pass 3 — Freshness
Compare current doctrine against older Hydra, KAI, Vue, Termux, build, and migration references.

Reuse useful history.

Do not resurrect dead architecture by accident.

## Pass 4 — Voice
Use short sentences.

Use complete thoughts.

Keep the Professor and Lum voice punchy.

A joke may open the door.

The technical meaning walks through immediately after it.

## Pass 5 — Evidence
Match every important claim to its receipt.

If the evidence does not prove it, downgrade the claim.

## Pass 6 — Security
No secrets.

No keys.

No bearer tokens.

No production signing material.

No private control-plane details in public-facing material.

## Pass 7 — Structure
Check:

- table of contents;
- headings;
- links;
- appendices;
- page flow;
- cross-references;
- print safety where applicable.

## Pass 8 — Machine Readability
Validate the AI manifest.

Validate the HTML companion.

Plain JSON is canonical machine-readable metadata.

Base64 is transport only.

It is not security.

## Pass 9 — Render and Hash
Render the human artifact.

Inspect every page or view.

Then hash the final files.

Do not hash the draft and call the final sealed.

## Pass 10 — Seal and Save
Write the documentation seal.

Save the verified package.

Record blockers.

Record the next safe state.

Do not promote software because the manual looks fabulous.

---

# Default Artifact Set

A full documentation mutation may produce:

1. Human-readable master document or print artifact.
2. Single-column HTML companion for in-app reference.
3. Plain JSON AI manifest.
4. Documentation seal JSON.
5. SHA-256 ledger.
6. Mutation receipt.
7. Optional packaged archive.

Only create the pieces the job needs.

Do not create bureaucracy as a hobby.

---

# Save Contract

## GitHub
Stage documentation changes in the canonical repository.

Use a reviewable branch when the mutation should not silently redefine canonical main.

## Google Drive
Save verified convenience copies only to the designated documentation folder.

A Drive copy is not automatically canonical.

Authority must be explicit.

## Legacy material
Reference selectively.

Do not merge unrelated histories merely because they exist.

**Unify first. Delete last.**

---

# Crown Boundary

GREEN documentation does not authorize:

- production signing;
- publishing;
- stable promotion;
- release promotion;
- remote shell execution;
- runtime architecture changes;
- Android loopback control planes;
- embedded provider secrets.

Those require their own evidence and authority.

> **Professor:** "Based on fucking what?"

That is a valid audit question.

---

# Final Report Shape

A good robot report says:

- What I changed.
- What I observed.
- What I proved.
- What I did not prove.
- Current gate.
- Next safe action.
- Crown required: yes or no.

That is enough.

No enterprise oatmeal.

**Build weird things. Keep receipts. Pet the demon. Do not lie to the status board.**
