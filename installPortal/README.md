# LuHm OS private install portal

Canonical friendly endpoint:

`https://get.lum.eggiebagelface.lan/`

This directory is a static, private-LAN install surface for the Samsung candidate. It does not activate DNS, TLS, Apache, public exposure, release promotion, or production signing by itself.

## Bundle contract

The Samsung CI lane stages:

- `index.html`
- `manifest.json`
- `apk/current.apk`

as one artifact named `luhm-os-s24fe-lan-install-bundle`.

Serve that directory as the document root for `get.lum.eggiebagelface.lan` after the Professor explicitly activates the host-side DNS/TLS/Apache step.

## Phone flow

1. Open `get.lum.eggiebagelface.lan` on the S24 FE.
2. Tap **INSTALL LUHM**.
3. Android downloads `apk/current.apk` and hands it to the normal package installer.
4. In Key Mapper, map **START + SELECT** to **Open app → LuHm OS** for the CROWN CHORD.

Android can require a one-time per-source permission to install unknown apps. That permission belongs to the browser/file source chosen by the Professor. The portal does not bypass Android package-install controls.

## F-Droid lane

Reserved endpoint:

`https://get.lum.eggiebagelface.lan/fdroid/repo/`

F-Droid recognizes the conventional `/fdroid/repo/` URL shape and can hand such links into its repository-add flow once a real signed repository exists. The portal keeps this control disabled until `fdroidReady` is explicitly set true in a generated manifest.

The F-Droid repository signing key is a separate trust anchor. It must not be committed to this repository, emitted into CI logs, or embedded in the APK.

## Apache preference

LuHm OS prefers Apache HTTP Server 2 for the host-facing local web layer. Host configuration is intentionally not activated here because the current repository cannot prove the Professor workstation's present Apache paths, TLS state, LAN DNS, or service layout.

## Status law

A generated bundle can be GREEN as an artifact while DNS, host serving, physical installation, and release promotion remain separate gates.

**AI proposes. Policy authorizes. CI proves. Human promotes.**
