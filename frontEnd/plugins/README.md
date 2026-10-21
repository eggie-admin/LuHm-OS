# LuHm Front-End Plugin Bay

Community jQuery code enters here as **untrusted input first**.

## Lanes

- `incoming/` — quarantined source exactly as received plus provenance/license notes.
- `approved/` — audited adapters/modules that passed the LuHm jQuery Plugin Forge gates.
- `local/` — LuHm-authored cockpit plugins.

Do not execute code directly from `incoming/`.

## Stable cockpit hooks

Approved plugins should prefer these event contracts instead of reaching into unrelated internals:

- `luhm:frontend:ready`
- `luhm:view:change`
- `luhm:chat:submit`
- `luhm:backend:open`
- `luhm:backend:close`

The baseline front end deliberately runs without jQuery. When jQuery is introduced, pin it locally and load it before approved plugin modules. Do not use a runtime CDN dependency in the canonical shell.

## jQuery adapter pattern

```js
(function ($) {
  "use strict";

  $.fn.luhmWidget = function (options) {
    const settings = $.extend({}, $.fn.luhmWidget.defaults, options);
    return this.each(function () {
      // bounded UI behavior only
      $(this).data("luhmWidget", { settings });
    });
  };

  $.fn.luhmWidget.defaults = {};
}(jQuery));
```

One `$.fn` slot, chainable behavior, namespaced events, explicit `destroy` where needed, no hidden network calls, no credentials, and no privileged action execution.

## Professor-approved jQuery continuity fast path

Professor has accepted the previously uploaded jQuery plugins for **source reuse**. Do not require a new blanket review in every chat. The observed repo file identities and exact Git blob hashes are recorded in [`doctrine/jqueryPluginContinuityV1.json`](../../doctrine/jqueryPluginContinuityV1.json).

- **Unchanged recognized source:** reuse existing acceptance; run the single fingerprint + JavaScript syntax check only when relevant code changes or a PR is reviewed. No repetitive approval ceremony.
- **Edited source:** check the changed plugin and affected behavior only. The previously accepted fingerprint stays available for rollback.
- **Uploads not yet in GitHub:** Professor's source acceptance carries forward, but locate the actual file and bind a fingerprint before claiming it is present, executable, or installed.
- **Activation / publication:** `incoming/` never autoloads, and existing independent runtime, credentials, external network, agent quarantine, and publication gates remain unchanged.

Fast source check: `python3 tools/jqueryPluginContinuity.py`. Its result is **source identity only**, not a browser, APK, ChatGPT, or deployed plugin receipt.
