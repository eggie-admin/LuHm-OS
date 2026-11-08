# Project Premonition — Ash Cathedral

A playable Godot 4.6 combat prototype for LuHm-OS. Open project.godot in Godot 4.6 and press F6 on Main.tscn or F5. No external assets or add-ons required.

WASD/arrows move, J strikes, Space dodges, Q calls Lum's support pulse, E rests at the teal shrine, Escape pauses, R restarts after defeat or victory. On-screen controls support touch. Defeat all three waves. Enemies swell during their 0.75-second attack tell; dodge before impact. Shrine use restores resources and respawns the current wave. Saves use Godot user://, locally on the device.

This is an original gothic anime action-RPG mechanics study, inspired by the requested Code Vein direction. No Code Vein models, maps, audio, code, logos or story content are included. Characters are geometric placeholders, not approved Canon character art. The supplied studio HTML referenced unavailable artwork; it is not imported or published here.

Implemented: 3D collision/movement, directional melee, stamina/cooldowns, dodge invulnerability, enemy pursuit/telegraph/damage, support pulse, three-wave progression, defeat/restart, shrine save/load and touch buttons.

Not complete: production anime models/rigs/animation, inventory, quests, full campaign, audio, lock-on camera, Android exports and embedded ChatGPT gameplay. The installed ChatGPT bridge remains read-only. A package update is not a Site deployment or a full engine embedded in chat.

Validation: Godot 4.6.3 headless import and tests/smoke.gd. Run `godot --headless --path . --script tests/smoke.gd`. Visual/device testing is a separate gate. Tests use unique temporary save paths and clean up only their own files.

Source baseline inspected: eggie-admin/LuHm-OS@4392f0ce4ff5d8d58a67dea2354f5500a7b78e82. This prototype is a review candidate, not promotion of repository Canon.

Hardening: combat entry points reject paused/dead/victory states; focus loss clears touch controls and pauses; restart clears pause and resets companion/input state. Saves use a staged file plus last-good backup, strict integer validation, bounded values, backup recovery and honest write-failure messages. Run `godot --headless --path . --script tests/hardening.gd` for 13 additional regression checks.
