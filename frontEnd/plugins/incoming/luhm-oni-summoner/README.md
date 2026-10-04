# LuHm Oni Summoner jQuery plugin

Plugin-only candidate for the LuHm GUI layer. It uses the existing pinned jQuery 3.7.1 asset and does not replace the cockpit or grant backend authority.

## What it renders

- all canonical Lum/Oni names and roles from `doctrine/ONI_MESH_CONTROL_PLANE_V2.json`;
- skill paths and default authority;
- summon buttons that emit a bounded `luhm:oni:summon` event instead of executing work;
- observed worker states: `PARKED`, `QUEUED`, `ACTIVE`, `WAITING`, `VERIFYING`, `SUCCESS`, `ERROR`;
- chat-style activity bubbles with task id, source ref, process label, progress, and receipt reference;
- an activity rail suitable for background build/research/render/status events.

## “Thinking” boundary

The UI may echo concise **observed activity summaries** such as “checking source identity,” “build running,” or “waiting for CI.” It must not expose or invent hidden chain-of-thought. If no task/process receipt exists, the Oni stays `PARKED` or `WAITING` instead of performing fake animation.

## App usage

The existing front-end dependency remains `jquery@3.7.1`. Stage it first:

```bash
cd frontEnd
npm install --ignore-scripts --no-audit --no-fund
npm run stage:jquery
```

Then mount:

```js
const $summoner = $("#oniSummoner").luhmOniSummoner();

$summoner.on("luhm:oni:summon", (_event, request) => {
  // Host/router decides whether to accept the request.
});

$summoner.luhmOniSummoner("activity", {
  oni: "Tetsu",
  state: "ACTIVE",
  taskId: "build-123",
  sourceRef: "abc1234",
  processLabel: "Godot Android export",
  progress: 42,
  summary: "Exact-source build is running."
});
```

jQuery UI is optional. If `$.fn.tooltip` exists, the plugin uses it; it is not a dependency.

## ChatGPT / MCP Apps

`host/harness/oni-summoner-widget.html` is the in-chat adapter. It uses the same roster/activity semantics but stays dependency-free inside the MCP Apps frame. `luhm_open_oni_summoner` renders it and `luhm_request_oni` lets the widget make a real read-only `tools/call` summon request through Lum. A request does not start execution. The jQuery plugin remains the in-app host implementation.

## Authority

`AI proposes. Policy authorizes. CI proves. Human promotes.`

This plugin has no mutation, GREEN, merge, signing, publication, secret-write, or Crown authority.
