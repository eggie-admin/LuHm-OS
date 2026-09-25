# LuHm OS / Project Hydra
## Illustrated AI Builder's Field Manual
### Working-title source edition

> **STATUS: UNDER CONSTRUCTION**
>
> Please excuse our mess. The repository, documentation, examples, tools, agent skills, and build pipeline are actively being reorganized.
>
> **Build weird things. Keep receipts. Pet the demon. Do not lie to the status board.**

---

# Mission

Project Hydra exists to make complicated computing systems more understandable, collaborative, creative, and considerably less boring.

We build AI-assisted software and hardware systems where humans remain in command, specialized agents work inside bounded roles, and important claims are backed by evidence.

Core rules:

- Build with receipts.
- Separate evidence from assumption.
- Keep source-of-truth authority explicit.
- Prefer reversible mutations.
- Explain why, not only which button to press.
- Let AI propose, inspect, research, build, and test inside its permissions.
- Keep consequential authority with humans.
- Have fun.

**AI proposes. Policy authorizes. CI proves. Human promotes.**

---

# A Word from Professor Iggy Bagelface

Greetings, nerds, artists, programmers, machine whisperers, hardware goblins, terminal archaeologists, AI wranglers, and people who clicked the repository because the logo looked suspicious.

I am **Professor Iggy Bagelface**.

"Professor" may occasionally mean professor.

It may also mean:

> Person standing next to a smoking computer saying, "Well, technically we learned something."

Project Hydra began the way many excellent bad ideas begin:

> "What if we connected this thing to that thing?"

Then somebody added an AI.

Then the AI needed tools.

Then the tools needed rules.

Then the rules needed documentation.

Then the documentation developed characters.

Then somebody apparently decided the documentation needed lore.

And now you are reading the manual.

Sorry about that.

The basic philosophy is simple:

**Build boldly. Measure everything. Break things only when you know how to put them back. Never confuse enthusiasm with evidence. Have some damn fun.**

You do not need to understand the entire Hydra before contributing.

Nobody understands the entire Hydra.

That is why it has multiple heads.

Pick one. Learn it. Document what you discover. Teach the next person.

Congratulations. You are now part of the problem.

---

# The Hydra Learning Loop

## 1. Quest
Define the objective before touching the machine.

## 2. Scout
Inspect current state. Read source. Check dependencies. Locate real artifacts. Do not mutate yet.

## 3. Plan
Choose the smallest safe change. Identify rollback and required evidence.

## 4. Mutate
Make one intentional, reviewable change.

## 5. Test
Run the test that matches the claim.

## 6. Collect Receipts
Compiler output, hashes, tests, screenshots, logs, artifact metadata, service checks, device proof, or source references.

## 7. Gate

- 🟢 **GREEN** — verified by evidence.
- 🟠 **AMBER** — promising or partial; proof still missing.
- 🔴 **RED** — failed, blocked, unsafe, or contradicted.
- ⚫ **UNKNOWN** — nobody checked.

Unknown is not bad.

Pretending UNKNOWN is GREEN is bad.

## 8. Seal
Update the source of truth, preserve receipts, record the mutation, list blockers, and identify the next safe state.

---

# Manual Voice

Write for the person who is interested.

Do not punish them for being interested.

Use short sentences. Use complete thoughts. Explain one thing at a time.

Do not turn a simple instruction into twelve paragraphs of enterprise oatmeal.

A joke may introduce the lesson. The technical meaning must immediately follow.

Example:

> **Do not clean the spaghetti temple yet. Find out which noodle is holding up the roof.**

Meaning:

Identify canonical authority before moving, renaming, deleting, or promoting anything.

## Recurring vocabulary

- **Forge** — build environment.
- **Crown** — consequential human authority.
- **Seal** — recorded verified state.
- **Receipts** — evidence.
- **Spaghetti temple** — organically messy architecture where structural pieces are unclear.
- **Collision gremlin** — two systems unexpectedly trying to own the same resource or responsibility.
- **Haunted toaster** — machine behavior that is possible but suspicious.
- **Green crayon** — unsupported success claim.

**Unify first. Delete last.**

---

# Pet-Powered Documentation

Tiny Lum is part of the information architecture.

The pet should indicate state before the reader parses the whole page.

## Core pet states

- 😺 `idle` — reading, explaining, inspecting.
- ⚔️👹 `attack` — intentional mutation or build.
- 💥🙀 `hit` — failure.

Manual shorthand:

- 🔎🐱 Scout — audit or inspection.
- 🧾😼 Receipt — evidence acquired.
- 👑😺 Crown — human approval required.
- 💤🐈 Parked — deferred, not broken.
- 🤨👹 Critic — unsupported claim detected.
- 🎉😸 Victory — GREEN supported by evidence.

Useful emoticons:

- `ฅ^•ﻌ•^ฅ` safe explanation.
- `( •̀ω•́ )σ` inspection.
- `(ง •̀_•́)ง` action.
- `(눈_눈)` suspicion.
- `ಠ_ಠ` critic intervention.
- `Σ(°△°|||)` failure.
- `(╯°□°）╯` Professor has encountered Gradle.
- `( •̀ᴗ•́ )و` evidence acquired.
- `(-ω-) zzz` parked.
- `ヽ(=^･ω･^=)丿` GREEN.

Do not dump twenty emoticons into one paragraph. Tiny Lum has dignity. Some.

---

# Comic Tutorial Template

Every practical tutorial should feel like a small mission.

## Panel 1 — Quest
What are we doing?

## Panel 2 — Monster
What is actually wrong?

## Panel 3 — Scout
Inspect before changing anything.

## Panel 4 — Safe Mutation
Make one bounded change.

## Panel 5 — Boss Fight
Run the test matching the claim.

## Panel 6 — Receipt
Show what was proved and what was not.

## Panel 7 — Crown Gate
Require human approval for consequential advancement.

## Panel 8 — Quest Clear
Only after the evidence supports GREEN.

---

# Supervise the Robot

> **The robot is allowed to be clever. The robot is not allowed to be unsupervised.**

AI can inspect, research, compare, draft, code, test, summarize, and propose mutations.

It can also:

- misunderstand the assignment;
- solve the wrong problem perfectly;
- overstate what evidence proves;
- assume stale state is current;
- promote AMBER to GREEN because everybody got excited;
- continue confidently after taking a wrong turn.

Professor's compact diagnosis:

> **"AI is a fickle bitch lol."**

The operational lesson is serious. Supervise it.

## The Crown Rule

Professor holds the Crown.

Agents may recommend and prepare. Humans authorize consequential actions.

## Correction protocol

When Professor corrects the robot:

1. Stop.
2. Restate the corrected target.
3. Discard the invalid assumption.
4. Recalculate the next safe action.
5. Continue from corrected state.

No ten-paragraph apology. Fix the work.

## Useful Professor commands

- **SANITY CHECK.** Re-read reality.
- **SOURCE OF TRUTH.** Resolve canonical authority.
- **AUDIT.** Inspect. Do not mutate.
- **MUTATE.** Make the smallest authorized change.
- **PROVE IT.** Produce evidence.
- **SEAL.** Record verified state.
- **PARK IT.** Preserve without advancing.
- **JUST BUILD THE FUCKING TOY.** Stop architecture tourism and produce the bounded candidate. Receipts still apply.

## Case file: mission drift

Professor:

> **"No omg sanity check we're working on the LuHm os manual"**

Lesson: local instructions do not erase the larger project mission.

The agent should ask: **What larger job are we inside?**

## Case file: unnecessary autonomy

Professor:

> **"no its just supervising a team of specialized coders"**

Lesson: do not inflate bounded orchestration into autonomous empire-building.

## Case file: constraint means constraint

Professor:

> **"no microsoft"**

Lesson: "Do not use X" does not mean "use X carefully."

## One receipt. One claim.

A compile receipt proves a compile.

It does not prove installation, launch, service health, visual correctness, device compatibility, or release readiness.

A file existing proves a file exists.

Congratulations. Keep going.

## Good robot report

- What I did.
- What I observed.
- What I did not verify.
- Current gate.
- Next safe action.
- Crown required: yes/no.

Bad:

> Everything is configured correctly and ready for production!

Professor:

> **"Based on fucking what?"**

Good:

> Candidate configuration is written. Syntax validation passed. Deployment was not performed. Production health is UNKNOWN. Current state: AMBER.

Professor:

> **"Good robot."**

---

# Professor Lectures Lum: Base64, JSON, RSS, and the Enterprise Gate

Tiny Lum enters carrying a giant Base64 string.

Professor:

> "What the fuck is that?"

Lum:

> "Base64."

Professor:

> "Encrypted?"

Lum:

> "...encoded."

Professor:

> "Good. We are learning."

## Base64 is not security

Base64 is a transport representation. It is not encryption, authentication, permission, or secrecy.

Do not put passwords, API keys, refresh tokens, private keys, signing secrets, or bearer tokens inside manifests or feeds merely because they can be Base64 encoded.

Professor:

> **"If anybody can decode it with one command, it is not a fucking secret."**

## JSON is the manifest

Plain JSON is the canonical readable description.

A manifest may describe agent identity, provider, version, capabilities, permitted tools, artifact references, hashes, source commit, gate state, evidence references, and dependencies.

It should not contain secrets.

Professor:

> **"Describe the keyhole. Do not tape the fucking key to the manifest."**

## RSS/event feeds are pipelines

Feeds may carry event notifications, build status, release metadata, evidence references, artifact IDs, summaries, and source links.

A feed does not grant authority.

> **The conveyor belt does not become the foreman.**

## OpenAI as a compatibility layer

Hydra talks to a provider-neutral contract. OpenAI is one provider lane behind that contract.

## Hugging Face as a compatibility layer

Hugging Face provides another model, inference, evaluation, and artifact ecosystem behind the same general provider boundary where practical.

Providers provide capability. Policy provides authority. Humans provide final authorization.

## Cloudflare at the public edge

Target architecture uses Cloudflare for public perimeter functions such as DNS, TLS, Zero Trust access, edge policy, rate limiting, and outbound tunnel patterns.

The public gets the front door. It does not get a map of the ventilation system.

## Google as identity sentry

Authentication answers: **Who are you?**

Authorization answers: **What may you do?**

Approval answers: **Should this consequential action happen now?**

Evidence answers: **Did it happen correctly?**

Do not collapse these questions.

## HTTPS token-pull live login target

Target flow:

1. User authenticates over HTTPS.
2. Identity provider returns an authorization result.
3. Backend validates the response.
4. Backend exchanges the authorization grant.
5. Sensitive provider tokens remain protected server-side.
6. Hydra establishes a short-lived user session.
7. Client makes authenticated HTTPS requests.
8. Backend pulls required provider credentials internally.
9. Policy checks authorization.
10. Crown gates remain in force for consequential actions.

Prefer short-lived sessions, scoped permissions, revocable credentials, secure cookies, HTTP-only cookies where appropriate, SameSite protections, CSRF defenses, OAuth `state`, nonce where appropriate, PKCE where appropriate, expiration, and audit logs.

Architecture is not evidence.

A Cloudflare box on a diagram is not proof of a live tunnel. A Google shield is not proof of a working OAuth callback. A provider adapter is not proof of a working inference route.

If it has not been tested, it remains AMBER or UNKNOWN.

---

# Lum Tech Demo: One Hydra, Four Bodies

## Same Hydra brain. Different-sized body.

The agent philosophy stays recognizable across devices. The amount of work kept local changes with compute, memory, thermals, power, platform rules, and the job itself.

Do not force a tablet to pretend it is a workstation.

Do not make a desktop behave like a toaster.

Do not send everything to the cloud simply because a network exists.

## Standard mesh

```text
             👑 PROFESSOR
                  │
                  ▼
                👹 LUM
                  │
       ┌──────────┼───────────┐
       ▼          ▼           ▼
    CONTEXT      BUILD      RESEARCH
       │          │           │
       └──────────┼───────────┘
                  │
            CRITIC WHEN NEEDED
                  │
                  ▼
           TOOL EXECUTOR
```

Not every box must run on every device.

That would be architecture cosplay.

## Tier Zero: Mini Antenna

Job: listen, route, keep small context, handle simple local commands, and escalate work that does not belong there.

Good at:

- wake/intent logic;
- routing;
- device state;
- cached instructions;
- local UI reactions;
- small offline operations.

Bad at:

- giant context;
- large codebases;
- full builds;
- Blender rendering;
- heavyweight multimodal work;
- pretending a tiny model is secretly a data center.

Tiny Lum:

> **"Know your weight class."**

## Tier One: Light Samsung

Samsung is a mobile edge node and cockpit.

It may handle:

- LuHm UI;
- pet system;
- voice interaction;
- local state;
- lightweight inference;
- sensors and media;
- approved device actions;
- cached data;
- secure authentication;
- handoff to larger agents.

Professor:

> **"I want Lum living on the thing. I don't want the thing melting into the couch."**

Mobile builds remain Android builds.

Think APK, Gradle, Android SDK, permissions, ARM64 libraries, Godot Android export, WebView, Kotlin/Java where required, and Android-native inference runtimes.

Do not pretend Android is Ubuntu.

Termux may be useful as a development or experimental lane. That does not automatically make it part of production architecture.

## S24 FE / Samsung target doctrine

Treat the production device as Samsung Android, ARM64, Knox-aware, persistent app territory. Do not assume root. Do not disguise a Linux workstation as an Android app.

Historical experiments may include tiny local antenna models, optional larger local models, OpenAI reasoning, Godot UI, WebView UI, Kotlin bridges, native Android inference, and Secure Folder isolation. Each remains a proposal, experiment, or verified component according to its receipts.

## SM-X400 tablet role

The tablet provides more screen and cockpit room for 3D avatar, comic UI, split panels, agent dashboards, pet toys, receipts, and media tooling.

The philosophy remains: **mobile first, mobile rules.**

## Tier Two: Medium Hydra

Laptop, mini PC, or modest workstation.

Possible local roles:

- Lum coordinator;
- full Context agent;
- Build agent;
- Research support;
- local inference;
- FastAPI/backend services where the target architecture calls for them;
- database;
- Git tooling;
- FFmpeg;
- development builds;
- moderate rendering;
- test automation.

The network becomes an option, not life support.

## Tier Three: Beefy Desktop

The engine room.

Potential jobs:

- larger local models;
- simultaneous agents;
- complete development environments;
- Android and Linux builds;
- FFmpeg pipelines;
- Blender;
- Godot;
- asset processing;
- databases;
- local APIs;
- model experiments;
- long-context work;
- CI-style testing;
- artifact generation.

Professor:

> **"Now we're talking."**

Use the desktop for expensive thinking. Do not make the phone perform workstation jobs merely because it technically can.

## Compute escalation

Escalation is about resources, not authority.

A giant desktop does not outrank Professor. A cloud model does not outrank policy. A small antenna is not less trusted merely because it is small.

Compute size and permission level are different concepts.

## Ubuntu: the workbench

Useful when we want practical general-purpose Linux, developer comfort, broad packages, current hardware support, desktop tools, GPU integration, and rapid experimentation.

Professor:

> "I need the damn GPU to work."

Ubuntu:

> "I probably have a package for that."

## Debian: Debbie

Debian emphasizes stability, predictability, minimalism, and controlled package change.

Attractive for headless nodes, backend services, remote antennas, build VMs, reproducible environments, and long-lived infrastructure.

Professor:

> **"Debbie doesn't fuck around."**

## Build lane: Bill has been fired

A build lane is not an operating system.

It is the environment that turns source into an artifact.

The build machine does not need to be the target machine.

Example:

```text
🖥️ DESKTOP LINUX
      │
      │ builds
      ▼
   📦 APK
      │
      │ installs
      ▼
📱 SAMSUNG DEVICE
```

Professor's Forge Rule:

> **"Don't make the tablet manufacture its own battleship unless we have a reason."**

## Same request, different body

Professor:

> "Lum, summarize this note."

📡 Antenna:

> "Done."

Professor:

> "Lum, show me the animated pet."

📱 Samsung:

> "Done."

Professor:

> "Lum, rebuild the backend and run tests."

💻 Medium box:

> "Done."

Professor:

> "Lum, compile the Android candidate, render the 3D avatar, encode the trailer, run the local models, and don't bother me until there are receipts."

🖥️ Desktop fans:

> **WHOOOOOOOOOOO**

Tiny Lum:

`(ง •̀_•́)ง`

> **"Now we're cooking."**

## Final lecture

Professor points at antenna:

> "Tiny jobs."

Points at Samsung:

> "Mobile jobs."

Points at medium computer:

> "Real workstation jobs."

Points at giant desktop:

> "Stupid giant jobs."

Lum:

> "Technically heavyweight compute."

Professor:

> "Stupid giant jobs."

Lum:

> "Accepted."

Professor points at Ubuntu:

> "Workbench."

Points at Debian:

> "Stable engine room."

Points at build pipeline:

> "Forge."

Points at Samsung:

> "Mobile target."

Professor:

> "And what are they?"

Lum:

> "Different bodies."

Professor:

> "And the architecture?"

Lum:

> "One Hydra."

# 🐉 ONE HYDRA
## 📡 SMALL WHEN IT CAN BE
## 📱 MOBILE WHEN IT SHOULD BE
## 💻 LOCAL WHEN IT MAKES SENSE
## 🖥️ HUGE WHEN THE JOB DESERVES IT

### AND NEVER MAKE THE HAUNTED TOASTER RENDER BLENDER.

---

# Contributing

Please contribute.

Good contributions include bug reports, documentation fixes, tutorials, diagrams, accessibility improvements, reproducible tests, agent skills, build tooling, architecture criticism, research references, platform work, artwork, examples, translations, cleanup, and better explanations.

You do not need to be an expert.

Useful contributions often begin with:

> **"I didn't understand this section."**

That is valuable information.

Do not merely make Hydra bigger. Make Hydra easier for the next person to understand.

A Patreon is planned to help support continued development, documentation, infrastructure, artwork, experiments, hardware testing, tutorials, and the considerable quantity of caffeine apparently required to keep a Hydra properly hydrated.

Details will be announced when ready.

---

# Repository Under Construction

The LuHm OS / Project Hydra repositories are undergoing active restructuring.

Expect changing layouts, documentation migration, renamed components, incomplete examples, experimental branches, missing polish, temporary scaffolding, and old references awaiting archival.

Until cleanup is complete, explicitly designated source-of-truth manifests and branches outrank stray historical files.

When uncertain:

**Ask. Inspect. Verify.**

Please excuse the mess.

We are building the building while standing inside it.

---

# Closing Words from Professor Iggy Bagelface

If this manual has done its job, you understand something important:

The project is not merely the code.

Hydra is the process surrounding the code.

The questions. Experiments. Receipts. Failures. Rebuilds. Diagrams. Arguments with compilers. Tiny GREEN boxes appearing after suspicious AMBER boxes.

Explore.

Build something.

Break something responsibly.

Fix something somebody else broke responsibly.

Teach somebody.

Ask stupid questions. They are frequently much better than the clever ones.

If you discover a better way of doing something in this manual:

**PLEASE TELL US.**

Better yet:

**CONTRIBUTE IT.**

Hydras are supposed to grow.

Just label the new head properly.

Have fun.

Make weird things.

Keep receipts.

And please do not deploy directly to production because a cartoon demon told you it was probably fine.

— **Professor Iggy Bagelface**

---

## Manual Motto

**BUILD WEIRD THINGS.**

**LOOK BEFORE YOU BONK.**

**KEEP RECEIPTS.**

**HUMANS HOLD THE CROWN.**

**PET THE DEMON.**

**DO NOT LIE TO THE STATUS BOARD.**
