# KAI 9000 Cathedral candidate

This lane composes current LuHm OS pieces without restoring the old monolithic runtime.

```text
Godot 4 native world
        |
caged WebView / packaged website
        |
jQuery cockpit + jquery.luhmSite + Vue CMS island
        |
typed native bridge
        |
optional loopback KAI sidecar in ordinary Termux
        |
headless Ollama
```

The APK remains launchable without Termux. Termux/Ollama is an optional local inference companion for the testing/direct lane, not Android lifecycle authority.

The WebView has no direct network capability. The site plugin is presentation-only. Sidecar chat, model discovery, and candidate-memory writes are allowlisted and authenticated. Background learning produces inactive candidate memories only.

No generic exec, shell bridge, arbitrary filesystem bridge, arbitrary proxy, runtime CDN, automatic publish, production signing, or main merge is authorized by this candidate.
