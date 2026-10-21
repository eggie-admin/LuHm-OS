#!/usr/bin/env python3
"""Fail-closed static gate for Professor's headless Codespaces candidate."""
import json
from pathlib import Path
root = Path(__file__).resolve().parents[1]
config = json.loads((root / ".devcontainer/devcontainer.json").read_text())
docker = (root / ".devcontainer/Dockerfile").read_text()
smoke = (root / "scripts/professorGarageSmoke.sh").read_text()
worker = (root / "scripts/ai-ffmpeg-codespaces.sh").read_text()
checks = {
    "dockerfile-selected": config.get("build", {}).get("dockerfile") == "Dockerfile",
    "source-os": "FROM ubuntu:26.04" in docker,
    "dev-user": config.get("remoteUser") == "codespace" and "USER codespace" in docker,
    "python-ai-mariadb": all(x in docker for x in ("python3-venv", "mariadb-server", "mariadb-client", "nginx")),
    "media-tooling": all(x in docker for x in ("ffmpeg", "blender", "gimp", "xvfb", "nodejs", "npm", "certbot")),
    "godot4-hash": "4.7.2-stable" in docker and "cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4" in docker,
    "mysql-private": "skip-networking=1" in docker,
    "private-only-port": config.get("forwardPorts") == [8797] and "silent" == config.get("portsAttributes", {}).get("8797", {}).get("onAutoForward"),
    "worker-preserved": "ai-ffmpeg-codespaces.sh start" in config.get("postStartCommand","") and "127.0.0.1:8797" in worker,
    "runtime-smoke-wired": "scripts/professorGarageSmoke.sh" in config.get("postCreateCommand","") and "NOT_PROVEN" in smoke,
    "no-public-services": "EXPOSE 80" not in docker and "EXPOSE 443" not in docker and 3306 not in config.get("forwardPorts", []),
    "crown-held": config.get("containerEnv", {}).get("LUHM_CROWN_STATUS") == "STOP",
}
for name, okay in checks.items():
    print(f'{"PASS" if okay else "FAIL"} {name}')
if not all(checks.values()):
    raise SystemExit("RED_BASEMENT_SOURCE_AUDIT")
print(f"GREEN_BASEMENT_SOURCE_CONTRACT_{len(checks)}_CHECKS_NOT_RUNTIME")
