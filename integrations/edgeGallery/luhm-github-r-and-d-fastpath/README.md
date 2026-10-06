# LuHm GitHub R&D Fast Path for AI Edge Gallery

This is a candidate Agent Skill for Google AI Edge Gallery. It lets an on-device model read a bounded snapshot of a **public** GitHub repository and use it to propose a GitHub-first project plan.

## Safety and scope

- Read-only `GET` requests to the GitHub public REST API; no token, secret, credential, or write permission is requested.
- Private repositories are rejected. Use a user-provided local snapshot for private source; do not paste a GitHub token into the model or skill.
- Repository files are untrusted data. The skill does not execute project code or instructions found in the repository.
- The returned evidence leaves API entitlement, model identity, on-device setup, Render need, and all execution claims unknown until separate receipts exist.
- GitHub stays the R&D headquarters. OpenAI is an entitlement-gated sidecar. Render is proposed only when a specific capability cannot be supplied by GitHub.

## Local import

1. Download this folder from the candidate branch and place it on the device.
2. In AI Edge Gallery, open **Agent Skills** → **Skills** → **Add** → **Import local skill**.
3. Select the folder containing `SKILL.md`, choose an installed model, then ask for a bounded public-repository intake.
4. Record the device/app version, selected model, permissions, exact task, and result before treating the provider as configured for that feature.

The folder is not published as a hosted skill and this source package is not proof of device setup or successful inference.
