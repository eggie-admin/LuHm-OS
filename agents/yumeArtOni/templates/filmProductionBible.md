# Yume Film Production Bible Template

> Human-readable preproduction master. This is not a publish receipt.

## Project header
- projectId:
- version:
- sourceRef:
- workingTitle:
- finalTitle:
- studioBrand:
- subtitle/tagline:
- platform:
- runtimeTarget:
- aspectRatio:
- audience:
- contentRatingTarget:

## Story
### Logline
### One-paragraph synopsis
### Theme / emotional promise
### Beginning / middle / end
### Beat sheet
### Scene cards
For each scene:
- sceneId
- INT/EXT
- location
- timeOfDay
- purpose
- characters
- action
- dialogue/VO
- emotionalTurn
- durationTarget

## Character department
For each character:
- characterId
- canonRef
- fixedTraits
- mutableTraits
- expressionRange
- silhouette
- hair/makeup
- wardrobe
- jewelry/props
- forbiddenDrift
- continuityNotes

## Wardrobe department
- lookId
- sceneUse
- garments
- materials
- colors
- accessories
- footwear
- continuity hazards

## Art department
### Locations / sets
### Props
### Graphic motifs
### Concept illustration briefs
### Practical vs generated vs stock vs existing-source notes

## Cinematography
- lensLanguage
- framingRules
- cameraHeight
- movementVocabulary
- screenDirection
- eyelineRules
- depthOfField
- heroAngles
- forbiddenAngles

## Lighting / color
- colorScript
- key/fill/rim direction
- practical lights
- time-of-day changes
- contrast target
- skin/character color continuity
- grade notes

## Storyboards
For each shot:
- shotId
- sceneId
- duration
- framing
- cameraMove
- action
- dialogue/caption
- audioCue
- transition
- continuityWarning
- storyboardRef

## Sound
### Dialogue recording
### Voiceover
### Room tone / ambience
### SFX
### Music / temp score
### Silence beats
### Loudness / ducking notes

## Editorial
- coldOpen
- hookBySecond2
- first20SecondPatternChanges
- averageShotLengthBySection
- intentionalHoldShots
- transitions
- captions
- patternInterrupts
- accessibility
- finalBrandCard

## Provider task cards
For each task:
- taskId
- providerLane
- providerReadiness
- exactInputRefs
- requestedOutput
- model/tool if proven
- license/provenance check
- stopConditions

Unconfigured providers are marked `PENDING_PROVIDER_SETUP` and must not block provider-neutral preproduction.

## Directory map
- privateReferences/
- script/
- artDirection/
- character/
- wardrobe/
- locations/
- storyboards/
- audio/
- edit/
- exports/
- receipts/

GitHub receives source/receipts/pointers. Raw private media stays outside public source.

## Render / delivery
- masterCodec
- width/height
- fps
- audioCodec/sampleRate
- subtitleFormat
- thumbnail
- postCopy
- accessibilityText
- checksum

## Approval ledger
- Professor review:
- approved items:
- rejected items:
- unresolved:
- publishCandidateHash:
- publicationAuthority: false
