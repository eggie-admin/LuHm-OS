# Worm Dogs | Desert Shield / Desert Storm prologue
## Reusable verse-to-scene production template v1

**Creative authority:** Professor / Big Daddy  
**Studio:** Pirate Daddy's Film / Project Premonition  
**State:** source-only template in draft PR #589. No renders, soundtrack license, or public release.  
**Related prologue:** `../wormdog-desert-shield-storm-prologue-canon-candidate-v1.json`  
**Scoped cast seal:** `../wormdog-desert-war-prologue-cast-seal-v1.json`  
**Original sealed pilot:** `into-the-warp-approved-script.md`, SHA-256 `6f6054e86f6f6dd74ffc9355a34f86d2ff4c3822f1c8c4f2d20b8a701b38f9ef` (untouched).

### Narrative operating principle

A glossy, simplified 1990s war broadcast becomes an unreliable veteran's account. The government is depicted *metaphorically* as a Walt-Disney-style spectacle factory; the soldiers are the human "worm dogs" who know what the dust felt like. The story should not say Walt Disney, Disney the company, or any real person secretly controlled the government. The central in-character accusation is **"Everything you believe in is a lie."** That is the narrator's perspective, not a documentary verdict.

### How to match the song later

**Music reference:** Grim Salvo, "Walt Disney Wormdog." The actual recording and written lyrics are NOT bundled or cleared.

For each line or verse opening the Professor selects later, capture:
- **Cue ID:** e.g. `V01`, `V02`, `BR01`, `RF01`. Do not assume this is the song's verified formal section structure.
- **Private lyric pointer:** an approved owner-held timecode or note ID. Do not commit copyrighted lyrics to the public repository.
- **Audio in / out:** `HH:MM:SS:FF` after listening to a licensed reference; start frame, end frame and cut type.
- **Visual response:** image, silence, movement, anti-propaganda contrast, character reaction.
- **World / era / cast:** `physicalWorld` / `toonWorld`, `1990Shield` / `1991Storm` / `afterward` / `present`; use sealed cast IDs.
- **Historical annotation:** separate real-world geography and chronology from fictional personal testimony and supernatural/warp events.

**Do not claim beat-exact synchronization until actual audio has been aligned.** The following sequence is scene-order guidance, not validated timestamps.

### Starting eight-scene slate

| Slot | Lyric entrance to mark | Primary setting / picture | Cast IDs | Story turn |
|---|---|---|---|---|
| WD-00 | Opening atmosphere / first vocal `[PRIVATE CUE]` | Smiling 1990s TV victory broadcast rots into sand and CRT interference | `broadcastMask`, `wormDogChorus` | Sell the version of war that fits on television |
| WD-01 | Verse entrance `[PRIVATE CUE]` | 1990 Saudi deployment; shaved-head comrades, dog tags and `MR. BUTTONS` | `bigDaddy`, `antiDaddy`, `wormDogChorus` | Promise of Desert Shield and soldier-level doubt |
| WD-02 | First acceleration `[PRIVATE CUE]` | TV flash -> Desert Storm night fighting, radios and moving armor | `bigDaddy`, `antiDaddy`, `broadcastMask` | Wartime blitz of image and noise |
| WD-03 | Heavy or rapid vocal passage `[PRIVATE CUE]` | Fictional frontline combat, human fear and scattered perceptions | `bigDaddy`, `antiDaddy`, `wormDogChorus` | The soldiers are witnesses, not mascots |
| WD-04 | Bridge or breath `[PRIVATE CUE]` | Nonlinear return to Saudi stationing, fatigued men and empty mail | `bigDaddy`, `wormDogChorus` | Question what "protection" and prolonged presence mean |
| WD-05 | Sacred-geography entrance `[PRIVATE CUE]` | Accurate regional map: Saudi Arabia, Kuwait, Iraq, Israel, Jerusalem; missile broadcasts and sacred imagery | `bigDaddy` as voice, no deity impersonation | Belief contrasted with its political packaging |
| WD-06 | Refrain / accusation `[PRIVATE CUE]` | Broadcast dissolves; Big Daddy faces the lens; Anti-Daddy's memory leaks into frame | `bigDaddy`, `antiDaddy`, `broadcastMask` | **Everything you believe in is a lie** |
| WD-07 | Final musical transition `[PRIVATE CUE]` | Present-day trunk of preserved service gear; separate stolen game armor glitch; Anti-Daddy future silhouette | `bigDaddy`, `antiDaddy`, optional `mrButtonsMascot` | Open the path to the later digital betrayal |

### Copyable shot card

```yaml
shotId: WD-XX
sceneTitle: "[working title]"
sourceSnapshot: "wormdog-desert-shield-storm-prologue-canon-candidate-v1.json"
castSeal: "wormdog-desert-war-prologue-cast-seal-v1.json"
narrativeFunction: ""
songCue:
  cueId: ""                # V01 / V02 / BR01 / RF01 (do not guess)
  ownerPrivateLyricKey: "" # pointer, not lyric text
  startTimecode: null      # HH:MM:SS:FF after verified listening
  endTimecode: null
  firstVocalOnsetVerified: false
  cutOn: ""                # entrance / drum / pause / hard cut
scene:
  era: ""                  # 1990Shield | 1991Storm | afterward | present
  worldLayer: physicalWorld
  setting: ""
  geographyAccuracyNote: ""
  castIds: []
  originalVoiceoverDraft: ""
  actionAndBlocking: ""
  imageAndCamera: ""
  transition: ""
  alternateHistoryDisclosure: ""
lookAndSound:
  filmStockOrCRT: ""
  palette: "soot black / rust / brass / ember / CRT cyan"
  cameraMovement: ""
  radioOrSfxOnly: ""       # no copyrighted audio embedded
assets:
  canonSheetKeys: []
  userApprovedReferencePixelsInspected: false
  rightsAndReleaseChecked: false
  privateMediaPointers: []
verification:
  cueAlignedToAudio: false
  historyReviewed: false
  characterContinuityReviewed: false
  editedPreviewVerified: false
  professorReview: pending
```

### Cast seal and historical boundaries

- **Big Daddy** is one human across all eras; `Mr. Buttons` is his military callsign. The later pirate-cat mascot is not a second soldier or a replacement protagonist.
- **Anti-Daddy** begins in the same fictional unit, military buzz cut. His later silver-white ponytail, angular anime glasses and villain looks belong to subsequent eras.
- **Anonymous soldiers** are adult human members of the ensemble, not literal dogs. Do not assign unverified veteran identities, medals, combat claims or personal war histories.
- **Saudi Arabia** is a location for Desert Shield deployment and stationing; **Iraq occupied Kuwait**. A narrator's provocative use of "occupation" about Saudi stationing must remain attributed fiction, not an unqualified historical caption.
- **Israel / Jerusalem / Holy Land:** respect distinct locations and communities; religious symbols express the tension between faith and state rhetoric, not a claim that any faith caused the war.
- **1990-91 MMORPG / Internet-founder story threads** are acknowledged alternate-history/warp gags, not real chronology.
- **Physical veteran equipment** is different from **later stolen digital epic armor**.
- **Belldandy's DADDY Codex lore read** stays at original shot 401, not this prologue. No new dialogue is inserted into the sealed pilot.
- No Disney visual IP, Grim Salvo lyric text or commercial song master is distributed from this template.

### When the Professor returns with the verses

Bind each chosen vocal entrance to a cue ID; replace only the placeholders, preserve `WD-00` through `WD-07` until reviewed, then turn the cards into a silent animatic candidate. Keep exact source SHA, rights review, production test evidence and Professor promotion as separate gates.
