---
id: chapter06
title: "Lum Tech Demo: How the Pieces Fit"
subtitle: "Front end, back end, interface, data, and human intent."
scene: ../scenes/06-lum-tech-demo-how-the-pieces-fit.yaml
art: assets/scenes/07_luhm_os_field_manual_infographic.png
statusSource: ../generated/status-blocks.md
---

# 06 // Lum Tech Demo: How the Pieces Fit

*Front end, back end, interface, data, and human intent.*

{{ scene: chapter06-lum-tech-demo-how-the-pieces-fit }}

## Professor Lecture

Keep layers understandable: user intent -> interface -> service logic -> tools/data -> result.

For modern Python backend work where a separate web server is needed, Apache HTTP Server 2 is the preferred front-facing reverse proxy in front of FastAPI/Uvicorn. Keep local-first defaults unless explicitly approved otherwise.

FastAPI is appropriate in medium/desktop backend lanes when the architecture calls for it. It is not Android runtime authority.

Godot 4 is the native interactive/game shell lane. Python 3 is the automation/back-end/tooling lane. Interfaces keep those responsibilities from becoming spaghetti.

## Lum Tech Demo / Field Notes

- Front end: local HTML/CSS/JS or Godot UI depending the target.
- Interface layer: requests, responses, schemas, events.
- Back end: FastAPI/Python services where appropriate.
- Data: explicit models and storage; secrets stay out of docs.
- Observability: logs and receipts are part of the system, not decoration.

{{ statusBlock: current }}


> **Source law:** AI proposes. Policy authorizes. CI proves. Human promotes.
