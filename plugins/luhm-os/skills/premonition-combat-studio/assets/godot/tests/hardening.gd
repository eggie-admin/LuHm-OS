extends SceneTree
var failures: int = 0
func check(ok: bool, label: String) -> void:
	if ok: print("PASS: ",label)
	else:
		failures += 1
		push_error(label)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var game = load("res://Main.tscn").instantiate()
	game.save_path = "user://hardening_%s.cfg" % Time.get_ticks_usec()
	root.add_child(game)
	game.set_physics_process(false)
	game.set_paused(true)
	check(not game.strike() and not game.dodge() and not game.pulse() and not game.rest(),"paused actions rejected at implementation boundary")
	game.hp = 0
	game.restart()
	check(not game.paused and game.hp == 100,"restart exits paused defeat")
	game.hp = 0
	check(not game.strike() and not game.pulse(),"dead actor cannot attack or heal")
	game.restart()
	game.victory = true
	check(not game.dodge() and not game.rest(),"victory blocks combat and shrine")
	game.restart()
	game.touch_directions['left'] = Vector2.LEFT
	game._notification(Node.NOTIFICATION_APPLICATION_FOCUS_OUT)
	check(game.paused and game.touch_directions.is_empty(),"focus loss pauses and clears touch")
	game.set_paused(false)
	game.player.position = Vector3.ZERO
	game.facing = Vector3.FORWARD
	game.foes[0].node.position = Vector3(0,0,1)
	game.foes[1].node.position = Vector3(0,0,-9)
	var back_hp: float = game.foes[0].hp
	var far_hp: float = game.foes[1].hp
	game.strike()
	check(game.foes[0].hp == back_hp and game.foes[1].hp == far_hp,"melee excludes rear and out-of-range targets")
	game.receive_hit(-50)
	game.receive_hit(NAN)
	check(game.hp == 100,"invalid incoming damage rejected")
	game.wave = 2
	game.ash = 42
	check(game.save_progress(),"save success returned")
	game.ash = 55
	check(game.save_progress(),"replacement save succeeds")
	var file = FileAccess.open(game.save_path,FileAccess.WRITE)
	file.store_string('[run]\nwave="invalid"\nash=[]\n')
	file.close()
	game.wave = 1
	game.ash = 0
	game.load_progress()
	check(game.wave == 2 and game.ash == 42,"invalid save recovers previous valid backup")
	var config = ConfigFile.new()
	config.set_value('run','wave',999)
	config.set_value('run','ash',-500)
	config.save(game.save_path)
	game.load_progress()
	check(game.wave == 3 and game.ash == 0,"save values bounded")
	var real_path: String = game.save_path
	game.save_path = 'user://nonexistent_directory/save.cfg'
	check(not game.save_progress(),"write failure reported")
	game.player.position = game.checkpoint
	game.rest()
	check('save failed' in game.status_text,"shrine displays write failure")
	game.save_path = real_path
	for suffix in ['', '.bak', '.tmp']: DirAccess.remove_absolute(real_path+suffix)
	print('RESULT: ',failures,' failures')
	quit(1 if failures else 0)
