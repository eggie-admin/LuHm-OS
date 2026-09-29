---
id: chapter07
title: "Professor Lecture: Tools of the Trade"
subtitle: "Gradle, venv, Termux, X11, npm, Android packaging, and device proof."
scene: ../scenes/07-professor-lecture-tools-of-the-trade.yaml
art: assets/scenes/08_luhm_os_field_manual_toolchain_to_device.png
statusSource: ../generated/status-blocks.md
---

# 07 // Professor Lecture: Tools of the Trade

*Gradle, venv, Termux, X11, npm, Android packaging, and device proof.*

{{ scene: chapter07-professor-lecture-tools-of-the-trade }}

## Professor Lecture

A build lane turns source into artifacts. It is not the same thing as the target runtime.

Python virtual environments isolate dependencies. npm manages JavaScript dependencies. Gradle drives Android builds. X11 can support desktop/Linux GUI experiments. Termux can be useful for development, but current Android doctrine explicitly rejects a Termux execution bridge as production architecture.

A candidate APK proves that an artifact exists. Device-GREEN requires installation and real-device validation. The current S24 FE physical proof remains pending.

Current source truth also keeps LAN DNS activation, Apache activation, physical install, persistent signing, enterprise readiness, and public exposure as separate unresolved gates.

## Lum Tech Demo / Field Notes

- SOURCE -> ENVIRONMENT -> BUILD -> PACKAGE -> CANDIDATE -> DEVICE VALIDATION
- Android: Gradle / Android SDK / ARM64 libraries / Godot export.
- Python: venv + dependency lock + tests.
- Web: npm only where the UI actually uses that ecosystem.
- Headless: automate repetitive builds, but log every meaningful result.

{{ statusBlock: current }}


> **Source law:** AI proposes. Policy authorizes. CI proves. Human promotes.
