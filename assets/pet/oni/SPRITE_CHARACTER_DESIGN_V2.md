# LuHm OS Oni Pet Sprite Character Design v2

## Runtime goal
Tiny chibi oni coworkers sit directly in the chat activity dock and show which LuHm workers are actually participating in the current task. They are status characters, not proof by themselves and not a claim of hidden background processing.

## Shared silhouette
- 128x128 logical frame, transparent RGBA.
- Readable at 32px, 48px, 64px and 128px.
- Oversized head, tiny seated/working body, two clear oni horns.
- Thick dark outer contour with crisp interior shapes.
- Expressive eyes remain legible at 32px.
- One role prop and one accent motif per Oni.
- No text baked into sprites.
- Keep feet/body close to lower frame edge so characters look like they are sitting on the chat dock.
- Avoid photorealism, soft watercolor edges, noisy texture, and over-detailed clothing.

## Sprite sheet contract
One 1024x128 horizontal sheet per Oni. Eight 128x128 frames:

1. `idle` — breathing / tiny eye movement
2. `thinking` — pondering / tiny question spark
3. `working` — role-specific action
4. `inspect` — close inspection / verification pose
5. `waiting` — holding position / hourglass-like pause
6. `success` — small confident victory sparkle
7. `alert` — clear warning pose, never comic panic
8. `sleep` — parked/inactive, eyes closed

Animation should be produced by frame variants or APNG later. This design document defines key poses only.

## Character lineup

### Lum — boss/orchestrator
Long dark-violet hair, cyan/magenta electric accents, elegant twin horns, tiny crown spark. Confident anime oni lead. Prop: crown-shaped cursor/tablet. `working`: directing floating task cards. `inspect`: one eye narrowed over a receipt. `waiting`: crown-lock icon hovering nearby.

### Fumi — secretary/records Oni
Short neat violet-black bob, cream paper accents, small tidy horns, rectangular hair tab. Prop: clipboard with paper tabs. `working`: stamping/sorting cards. `inspect`: comparing two file cards. `success`: tiny organized stack snaps into alignment.

### Dr. Nao — source-truth doctor
Mint-black hair, white mini lab coat, pale mint horns, calm expression. Prop: diagnostic tablet/stethoscope. `working`: checking heartbeat-like evidence line. `inspect`: magnified checksum/checkmark. `alert`: red diagnostic triangle.

### Tetsu — builder A
Compact sturdy oni, steel-blue hair, silver horns, small work apron. Prop: hammer and hex bolt. `working`: hammering a glowing build cube. `success`: finished cube with green check spark.

### Kaji — builder B clean-room forge
Flame-shaped orange-black hair, ember horns, dark forge apron. Prop: tongs and tiny forge flame. `working`: holding a separate glowing build cube in tongs. Silhouette must be clearly different from Tetsu.

### Kiri — context scout
Teal hood/scarf, icy horns, alert eyes. Prop: magnifier/map pin. `working`: tracing a path between tiny file cards. `inspect`: giant magnifier over an exact SHA card.

### Momo — research scout
Violet hair with antenna-like bun ornament, electric-blue horns. Prop: open book/telescope spark. `working`: scanning a floating page. `thinking`: antenna spark/question star.

### Shiori — critic
Sharp amber-black bangs, short warning-red horns, skeptical eyes. Prop: red pencil and critique card. `working`: circling contradiction on a card. `alert`: red exclamation card, firm not frantic.

### Kugi — deterministic executor
Graphite mechanic suit, cyan horns, compact toolbelt. Prop: terminal wrench/cursor gear. `working`: pressing one exact command tile. `inspect`: checking precondition checklist. `alert`: tool stops against a lock symbol.

### Yume — art/media forge
Long violet-magenta splash hair, curved artist horns, playful focused eyes. Prop: brush and film-frame star. `working`: painting a tiny sprite tile. `success`: sparkle frame/palette.

### Koe — dictation scribe
Cyan-black hair, acid-lime horn tips, headset. Prop: microphone/waveform. `working`: waveform becomes clean text cards. `waiting`: mic muted softly.

### Sumi — asset curator
Indigo hair with ink-tail shape, white horn tips, archivist vest. Prop: stamp/hash receipt. `working`: stamping an asset card. `inspect`: comparing two hashes. `success`: neatly labeled asset box.

## State color language
State is primarily motion/pose plus a tiny status light so character identity remains stable:
- idle: neutral dim
- queued/waiting: warm amber
- active: cyan pulse
- verifying: lime/mint pulse
- success: green sparkle
- error: red warning pulse
- parked: dim/sleep

Do not recolor whole characters by state.

## Chat presentation
- Lum remains visible as the leftmost boss pet.
- Only active/queued/verifying support Oni are shown beside her, maximum 3.
- Recently completed workers may linger briefly in success pose before disappearing/parking.
- At `CROWN_STOP`, Lum waits with crown-lock motif. No success confetti until human promotion actually happens.
- Mobile layout may collapse labels and show only 40–48px portraits plus status dots.

## Provenance gate
Generated concept art is `CONCEPT` until Sumi records provenance and Professor approves the character direction. Runtime sprite art becomes `GREEN_IMPORT_PROVEN` only after exact file hashes are imported and tested in the claimed chat runtime.
