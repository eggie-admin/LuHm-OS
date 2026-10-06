# LuHm OS private install portal

Canonical friendly endpoint:

`http://get.lum.eggiebagelface.lan/`

This directory is a static, private-LAN install surface for the Samsung candidate. The private `.lan` lane intentionally uses HTTP so a local CA or self-signed certificate is not required just to install a testing APK. It does not activate DNS, Apache, public exposure, release promotion, production signing, or a future public HTTPS route by itself.

## Bundle contract

The Samsung CI lane stages:

- `index.html`
- `manifest.json`
- `apk/current.apk`
- `SHA256SUMS.txt`
- `README-FIRST.txt`

as one artifact named `luhm-os-s24fe-lan-install-bundle`.

Serve that directory as the document root for `get.lum.eggiebagelface.lan` after the Professor explicitly activates the host-side LAN DNS and Apache step.

## Phone flow

1. Open `http://get.lum.eggiebagelface.lan/` on the S24 FE.
2. Tap **INSTALL LUHM**.
3. Android downloads `apk/current.apk` and hands it to the normal package installer.
4. In Key Mapper, map **START + SELECT** to **Open app → LuHm OS** for the CROWN CHORD.

Android can require a one-time per-source permission to install unknown apps. That permission belongs to the browser or file source chosen by the Professor. The portal does not bypass Android package-install controls.

## Direct APK lane

Once the host is activated, the exact current APK is also available at:

`http://get.lum.eggiebagelface.lan/apk/current.apk`

The portal displays the generated APK SHA-256 from `manifest.json`, and the bundle includes `SHA256SUMS.txt` for an independent hash check.

## F-Droid lane

Reserved endpoint:

`http://get.lum.eggiebagelface.lan/fdroid/repo/`

F-Droid supports custom repositories served from ordinary HTTP(S) endpoints. The conventional `/fdroid/repo/` path is reserved here for a future signed LuHm repository. The portal keeps this control disabled until `fdroidReady` is explicitly set true in a generated manifest.

The F-Droid repository signing key is a separate trust anchor. It must not be committed to this repository, emitted into CI logs, or embedded in the APK.

## Apache preference

LuHm OS prefers Apache HTTP Server 2 for the host-facing local web layer. Host configuration is intentionally not activated here because the current repository cannot prove the Professor workstation's present Apache paths, LAN address, DNS service, or service layout.

A future public route remains a separate HTTPS/Cloudflare gate. Nothing in this private-LAN bundle opens or publishes a public endpoint.

## Status law

A generated bundle can be GREEN as an artifact while LAN DNS, Apache serving, physical installation, F-Droid signing, and release promotion remain separate gates.

**AI proposes. Policy authorizes. CI proves. Human promotes.**
