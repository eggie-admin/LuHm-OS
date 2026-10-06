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
