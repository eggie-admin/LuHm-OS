extends SceneTree
var failures: int = 0
func check(ok: bool, label: String) -> void:
	if not ok:
		failures += 1
		push_error(label)
	else:
		print("PASS: ",label)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var game = load("res://Main.tscn").instantiate()
	game.save_path = "user://test_ash_%s.cfg" % Time.get_ticks_usec()
	root.add_child(game)
	game.set_physics_process(false)
	game.wave = 1
	game.spawn_wave()
	check(game.foes.size() == 3,"first wave has three sentinels")
	game.player.position = Vector3(0,1,0)
	game.facing = Vector3.FORWARD
	game.foes[0].node.position = Vector3(0,1,-1)
	var before: float = game.foes[0].hp
	check(game.strike(),"strike accepted")
	check(game.foes[0].hp == before-35,"strike damages target in range")
	check(not game.strike(),"strike cooldown prevents spam")
	game.stamina = 0
	game.attack_cd = 0
	check(not game.strike(),"empty stamina blocks strike")
	game.stamina = 100
	check(game.dodge(),"dodge consumes stamina")
	var vitality: float = game.hp
	game.receive_hit(20)
	check(game.hp == vitality,"dodge invulnerability prevents damage")
	game.invulnerable = 0
	game.receive_hit(20)
	check(game.hp == vitality-20,"unprotected hit damages player")
	game.hp = 50
	game.pulse_cd = 0
	check(game.pulse() and game.hp == 70,"companion heals")
	check(not game.pulse(),"companion cooldown enforced")
	check(not game.rest(),"remote shrine access rejected")
	game.player.position = game.checkpoint
	check(game.rest() and game.hp == 100,"shrine restores and saves")
	game.ash = 77
	game.save_progress()
	game.ash = 0
	game.load_progress()
	check(game.ash == 77,"save/load round trip")
	game.wave = 3
	game.spawn_wave()
	for foe in game.foes: game.damage_foe(foe,999)
	game._physics_process(0.016)
	check(game.victory,"last wave triggers victory")
	game.restart()
	check(game.wave == 1 and not game.victory and game.hp == 100,"new run resets after victory")
	game.touch_move = Vector2(1,0)
	var start: Vector3 = game.player.position
	for i in range(20):
		game._physics_process(1.0/60)
		await physics_frame
	check(game.player.position.x > start.x,"movement advances player")
	# Keep test state out of normal play.
	DirAccess.remove_absolute(ProjectSettings.globalize_path(game.save_path))
	for suffix in [".bak", ".tmp"]:
		DirAccess.remove_absolute(game.save_path + suffix)
	print("RESULT: ",failures," failures")
	quit(1 if failures else 0)
