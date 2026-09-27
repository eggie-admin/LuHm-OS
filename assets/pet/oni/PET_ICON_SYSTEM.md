# LuHm OS Oni Pet Icon System

Status: **CONCEPT / architecture branch**

This system extends the Field Manual's pet-powered documentation language into a consistent icon family for Lum and bounded Oni helpers.

## Source rules

The Field Manual already defines pet icons as information architecture. The icon must communicate role/state before the user reads a label.

The existing sitter rules remain authoritative:

- 128x128 logical canvas per pet
- transparent RGBA
- PNG/APNG or sprite sheet
- integer nearest-neighbor scaling
- original or license-audited art only
- no watermarks or ripped franchise sprites
- provenance required before shipping

## Shared silhouette

All Oni pets belong to one visual family:

- compact chibi/pixel-anime oni head-and-upper-body silhouette
- two small horns with character-specific accent shape
- large readable eyes
- tiny fang or mischievous mouth option
- dark charcoal/ink base with neon role accents
- strong 1-2 pixel outer silhouette at logical resolution
- readable at 32x32, expressive at 64x64, authored at 128x128
- no fine detail that disappears below 64x64

The pets are mini representations of adult LuHm/Oni characters, not separate child characters.

## Palette family

Use a common dark neutral body/outline and reserve high-saturation color for role identity.

- **Lum**: electric cyan + hot magenta, lightning spark
- **DrNao**: mint + white, medical check/stethoscope
- **Tetsu**: steel blue + silver, hammer/hex bolt
- **Kaji**: ember orange + red, forge flame/tongs
- **Kiri**: teal + ice blue, magnifier/map marker
- **Momo**: violet + electric blue, research antenna/book spark
- **Shiori**: amber + warning red, critic card/red pencil/skeptical brow
- **Kugi**: graphite + cyan, terminal cursor/gear/nail motif
- **Yume**: violet + hot magenta, brush + film-frame/star motif
- **Koe**: cyan + acid-lime, microphone + waveform/speech bubble
- **Sumi**: indigo + white, ink stamp + tag/hash/receipt motif

Color is redundant with silhouette/prop. Never rely on color alone to communicate role.

## Core runtime states

Every shipping pet supports the existing eight sitter states:

1. `idle` — neutral readable role silhouette
2. `blink` — two-frame eye close/open
3. `talk` — two- or three-frame mouth/bubble pulse
4. `inspect` — focused eyes plus role-specific inspection cue
5. `sleep` — softened pose plus tiny `zzz`
6. `alert` — high-contrast exclamation/spark
7. `drag` — grabbed/leaning pose suitable for UI movement
8. `dismiss` — tiny poof/slide-away frame, never violent

Optional documentation overlays may map Field Manual states:

- Scout -> `inspect`
- Receipt -> role icon + receipt/check overlay
- Crown -> role icon + crown gate overlay
- Parked -> `sleep`
- Critic -> Shiori `inspect/alert`
- Victory -> role icon + verified check/spark overlay

## Role identity

### Lum
Boss/orchestrator. Twin cyan horns with magenta lightning notch. Confident cat-oni eyes. Small electric tail/spark may break the square silhouette slightly.

### Dr. Nao Oni
Source-truth doctor. Mint horn tips. Tiny stethoscope loop or medical check. Expression is calm and suspicious rather than cheerful when inspecting.

### Tetsu Oni
Builder A. Squared horn tips and tiny steel hammer/hex bolt. Stable, workbench-like silhouette.

### Kaji Oni
Builder B / clean-room forge. Flame-like horn accent and tiny tongs/ember. Visually related to Tetsu but clearly independent.

### Kiri Oni
Context scout. One horn accent shaped like a locator notch. Magnifier/map pin prop.

### Momo Oni
Research scout. Antenna/book spark. Curious raised-brow expression.

### Shiori Oni
Critic. Amber warning accent, tiny red pencil/card, unmistakable skeptical eyes.

### Kugi Oni
Deterministic executor. Terminal cursor/gear/nail motif. Minimal expression variation to reinforce literal execution.

### Yume Oni
Art/media forge. Brush crossing a small film frame or star. More expressive sparkle without becoming visually busier than Lum.

### Koe Oni
Dictation/scribe. Microphone capsule and waveform/speech bubble. Mouth/talk state must be especially readable.

### Sumi Oni
Asset curator. Ink stamp/tag/receipt motif. Clean square badge silhouette with checksum/hash cue.

## Production sequence

Do not generate all state animation frames before role silhouettes are approved.

1. role-icon contact sheet, one `idle` master per character
2. Professor selects/adjusts silhouettes and role props
3. Sumi assigns stable asset IDs and provenance entries
4. derive eight state frames from the approved master
5. export transparent 128x128 source sprites
6. run pixel/readability audit at 32/64/128
7. import into Godot/UI using exact hashes
8. capture runtime receipt

## Naming

Canonical pattern:

`assets/pet/oni/<agent>/<agent>_<state>_v<major>.png`

Examples:

- `assets/pet/oni/yume/yume_idle_v1.png`
- `assets/pet/oni/koe/koe_talk_v1.png`
- `assets/pet/oni/drNao/drNao_inspect_v1.png`

A sprite sheet may use:

`assets/pet/oni/<agent>/<agent>_states_v<major>.png`

## Truth boundary

A generated concept sheet is **CONCEPT**.

Professor visual approval makes it **APPROVED_ART**.

Sumi provenance/import metadata does not by itself make it runtime GREEN.

Only the exact approved asset hash successfully imported and tested in the claimed runtime may become **GREEN_IMPORT_PROVEN**.
