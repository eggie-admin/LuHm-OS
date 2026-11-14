extends Node3D
## Original mechanics study. No Code Vein assets or game code.
var save_path: String = "user://ash_cathedral.cfg"
var touch_directions: Dictionary = {}
var player: CharacterBody3D
var companion: Node3D
var camera: Camera3D
var blade: MeshInstance3D
var hud: Label
var note: Label
var foes: Array[Dictionary] = []
var hp: float = 100.0
var stamina: float = 100.0
var ash: int = 0
var wave: int = 1
var attack_cd: float = 0.0
var dodge_time: float = 0.0
var invulnerable: float = 0.0
var pulse_cd: float = 0.0
var elapsed: float = 0.0
var facing = Vector3.FORWARD
var dodge_dir = Vector3.FORWARD
var paused: bool = false
var victory: bool = false
var touch_move = Vector2.ZERO
var status_text = "Lum: Stay close, darling. Wake the cathedral."
var checkpoint = Vector3(0, 1, 7)
var materials: Dictionary = {}

func material(color: Color, glow: bool = false) -> StandardMaterial3D:
	var m = StandardMaterial3D.new()
	m.albedo_color = color
	m.roughness = 0.8
	if glow:
		m.emission_enabled = true
		m.emission = color
		m.emission_energy_multiplier = 2.0
	return m

func box(parent: Node3D, pos: Vector3, size: Vector3, mat: Material) -> MeshInstance3D:
	var mesh = MeshInstance3D.new()
	var shape = BoxMesh.new()
	shape.size = size
	mesh.mesh = shape
	mesh.material_override = mat
	parent.add_child(mesh)
	mesh.position = pos
	return mesh

func solid(pos: Vector3, size: Vector3, mat: Material) -> void:
	var body = StaticBody3D.new()
	add_child(body)
	body.position = pos
	box(body, Vector3.ZERO, size, mat)
	var collision = CollisionShape3D.new()
	var shape = BoxShape3D.new()
	shape.size = size
	collision.shape = shape
	body.add_child(collision)

func actor(color: Color) -> CharacterBody3D:
	var body = CharacterBody3D.new()
	add_child(body)
	var shape = CollisionShape3D.new()
	var capsule = CapsuleShape3D.new()
	capsule.radius = 0.32
	capsule.height = 1.7
	shape.shape = capsule
	body.add_child(shape)
	var mesh = MeshInstance3D.new()
	var form = CapsuleMesh.new()
	form.radius = 0.32
	form.height = 1.7
	mesh.mesh = form
	mesh.material_override = material(color)
	body.add_child(mesh)
	box(body, Vector3(0, 0.45, -0.29), Vector3(0.42,0.12,0.12), materials.gold)
	box(body, Vector3(0, -0.2, 0.25), Vector3(0.65,1.2,0.12), materials.dark)
	return body

func _ready() -> void:
	materials = {"stone":material(Color("292a3f")), "dark":material(Color("101422")), "gold":material(Color("edbc79"),true), "pink":material(Color("d74977"),true), "teal":material(Color("61d7c6"),true)}
	var world = WorldEnvironment.new()
	world.environment = Environment.new()
	world.environment.background_mode = Environment.BG_COLOR
	world.environment.background_color = Color("101321")
	world.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	world.environment.ambient_light_color = Color("b1b9eb")
	world.environment.ambient_light_energy = 0.65
	add_child(world)
	var light = DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-55,-30,0)
	light.light_color = Color("b6c8ff")
	light.light_energy = 1.3
	add_child(light)
	solid(Vector3(0,-0.3,0),Vector3(24,0.6,30),materials.stone)
	for x in [-12,12]:
		solid(Vector3(x,1,0),Vector3(0.5,2,30),materials.dark)
	for z in [-15,15]:
		solid(Vector3(0,1,z),Vector3(24,2,0.5),materials.dark)
	for z in range(-12,13,4):
		for x in [-9,9]:
			solid(Vector3(x,2.5,z),Vector3(0.8,5,0.8),materials.dark)
			box(self,Vector3(x,5.1,z),Vector3(1.3,0.25,1.3),materials.gold)
			box(self,Vector3(x,2.7,z-0.43),Vector3(0.14,2.2,0.05),materials.pink)
		box(self,Vector3(0,0.015,z),Vector3(17,0.02,0.04),materials.gold)
	for x in [-6,6]:
		box(self,Vector3(x,0.02,0),Vector3(0.04,0.02,27),materials.gold)
	# A luminous fractured rose window at the far end.
	for i in range(16):
		var a = i * TAU / 16.0
		var petal = box(self,Vector3(sin(a)*3,4+cos(a)*3,-14.6),Vector3(0.16,1.5,0.1),materials.pink)
		petal.rotation.z = -a
	box(self,Vector3(0,4,-14.5),Vector3(0.2,5,0.1),materials.gold)
	box(self,Vector3(0,4,-14.5),Vector3(5,0.2,0.1),materials.gold)
	box(self,Vector3(0,0.08,7),Vector3(2.4,0.16,2.4),materials.teal)
	player = actor(Color("67c7c4"))
	player.position = checkpoint
	blade = box(player,Vector3(0.6,0,-0.35),Vector3(0.1,1.8,0.14),materials.gold)
	blade.rotation.z = -0.25
	companion = actor(Color("bd79bb"))
	companion.position = Vector3(2,1,7)
	camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 22
	add_child(camera)
	camera.position = Vector3(0,20,19)
	camera.look_at(Vector3(0,0,-2))
	camera.current = true
	build_ui()
	load_progress()
	spawn_wave()

func build_ui() -> void:
	var layer = CanvasLayer.new()
	add_child(layer)
	hud = Label.new()
	hud.position = Vector2(28,20)
	hud.add_theme_font_size_override("font_size",22)
	layer.add_child(hud)
	note = Label.new()
	note.position = Vector2(28,100)
	note.add_theme_font_size_override("font_size",16)
	layer.add_child(note)
	var controls = Label.new()
	controls.text = "WASD / arrows • J strike • Space dodge • Q companion • E shrine • Esc pause\nR restart after defeat / victory • Defeat three waves and seal the cathedral"
	controls.position = Vector2(28,154)
	controls.modulate = Color("b8bacb")
	layer.add_child(controls)
	var restart_button = Button.new()
	restart_button.text = "RESTART"
	restart_button.position = Vector2(1140,20)
	restart_button.size = Vector2(108,48)
	restart_button.pressed.connect(func():
		if hp <= 0 or victory: restart())
	layer.add_child(restart_button)
	var pause_button = Button.new()
	pause_button.text = "PAUSE / RESUME"
	pause_button.position = Vector2(950,20)
	pause_button.size = Vector2(180,48)
	pause_button.pressed.connect(func(): set_paused(not paused))
	layer.add_child(pause_button)
	for spec in [["↑",90,530,Vector2(0,-1)],["←",28,590,Vector2(-1,0)],["↓",90,590,Vector2(0,1)],["→",152,590,Vector2(1,0)]]:
		var b = Button.new()
		b.text = spec[0]
		b.position = Vector2(spec[1],spec[2])
		b.size = Vector2(56,56)
		b.focus_mode = Control.FOCUS_NONE
		b.button_down.connect(func(): touch_directions[spec[0]] = spec[3])
		b.button_up.connect(func(): touch_directions.erase(spec[0]))
		layer.add_child(b)
	for spec in [["STRIKE",910,590,"strike"],["DODGE",1025,590,"dodge"],["LUM",1140,590,"pulse"],["SHRINE",1140,525,"rest"]]:
		var b = Button.new()
		b.text = spec[0]
		b.position = Vector2(spec[1],spec[2])
		b.size = Vector2(108,56)
		b.pressed.connect(perform.bind(spec[3]))
		layer.add_child(b)

func set_paused(value: bool) -> void:
	paused = value
	touch_move = Vector2.ZERO
	touch_directions.clear()

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		set_paused(true)

func can_act() -> bool:
	return not paused and hp > 0 and not victory

func perform(action: String) -> void:
	if paused or hp <= 0 or victory:
		return
	match action:
		"strike": strike()
		"dodge": dodge()
		"pulse": pulse()
		"rest": rest()

func _unhandled_key_input(event: InputEvent) -> void:
	if not event is InputEventKey or not event.pressed or event.echo:
		return
	match event.physical_keycode:
		KEY_ESCAPE: set_paused(not paused)
		KEY_J: perform("strike")
		KEY_SPACE: perform("dodge")
		KEY_Q: perform("pulse")
		KEY_E: perform("rest")
		KEY_R:
			if hp <= 0 or victory:
				restart()

func spawn_wave() -> void:
	for foe in foes:
		foe.node.queue_free()
	foes.clear()
	for i in range(wave + 2):
		var body = actor(Color("bd4567"))
		body.position = Vector3(-5 + i * 2.4,1,-6 - (i % 2) * 3)
		foes.append({"node":body,"hp":60.0 + wave*10,"timer":1.0+i*0.3,"windup":false})

func strike() -> bool:
	if not can_act() or attack_cd > 0 or stamina < 22:
		return false
	stamina -= 22
	attack_cd = 0.45
	for foe in foes:
		var offset: Vector3 = foe.node.position-player.position
		offset.y = 0
		if foe.hp > 0 and offset.length() < 2.7 and facing.dot(offset.normalized()) > -0.2:
			damage_foe(foe,35)
	return true

func dodge() -> bool:
	if not can_act() or stamina < 30 or dodge_time > 0:
		return false
	stamina -= 30
	dodge_time = 0.25
	invulnerable = 0.35
	dodge_dir = facing
	return true

func damage_foe(foe: Dictionary, amount: float) -> void:
	if foe.hp <= 0 or amount <= 0 or not is_finite(amount):
		return
	foe.hp -= amount
	if foe.hp <= 0:
		foe.node.visible = false
		foe.node.collision_layer = 0
		ash += 10

func receive_hit(amount: float) -> void:
	if not can_act() or invulnerable > 0 or amount <= 0 or not is_finite(amount):
		return
	hp = maxf(0,hp-amount)
	invulnerable = 0.6
	if hp <= 0:
		status_text = "FALLEN — Press R to return to the shrine."

func pulse() -> bool:
	if not can_act() or pulse_cd > 0:
		return false
	pulse_cd = 9
	hp = minf(100,hp+20)
	for foe in foes:
		if foe.node.position.distance_to(player.position) < 6:
			damage_foe(foe,25)
	status_text = "Lum: I have you. +20 vitality / nearby enemies disrupted."
	return true

func rest() -> bool:
	if not can_act():
		return false
	if player.position.distance_to(checkpoint) > 2.6:
		status_text = "Return to the teal shrine to rest and save."
		return false
	hp = 100
	stamina = 100
	pulse_cd = 0
	spawn_wave()
	var saved = save_progress()
	status_text = "SHRINE — Progress saved. Sentinels restored." if saved else "SHRINE — Restored, but save failed. Previous save retained."
	return true

func save_progress() -> bool:
	var config = ConfigFile.new()
	config.set_value("run", "schema", 1)
	config.set_value("run", "wave", clampi(wave, 1, 3))
	config.set_value("run", "ash", clampi(ash, 0, 999999))
	var temporary = save_path + ".tmp"
	var backup = save_path + ".bak"
	if config.save(temporary) != OK:
		return false
	var had_save = FileAccess.file_exists(save_path)
	if had_save:
		if FileAccess.file_exists(backup):
			if DirAccess.remove_absolute(backup) != OK:
				return false
		if DirAccess.rename_absolute(save_path, backup) != OK:
			return false
	if DirAccess.rename_absolute(temporary, save_path) != OK:
		if had_save:
			DirAccess.rename_absolute(backup, save_path)
		return false
	return true

func load_progress() -> void:
	for candidate in [save_path, save_path + ".bak"]:
		var config = ConfigFile.new()
		if config.load(candidate) != OK:
			continue
		var stored_wave = config.get_value("run", "wave", null)
		var stored_ash = config.get_value("run", "ash", null)
		var schema = config.get_value("run", "schema", 1)
		if typeof(schema) != TYPE_INT or schema != 1:
			continue
		if typeof(stored_wave) != TYPE_INT or typeof(stored_ash) != TYPE_INT:
			continue
		wave = clampi(stored_wave, 1, 3)
		ash = clampi(stored_ash, 0, 999999)
		return

func restart() -> void:
	set_paused(false)
	facing = Vector3.FORWARD
	dodge_dir = Vector3.FORWARD
	if victory:
		wave = 1
		ash = 0
	victory = false
	hp = 100
	stamina = 100
	player.position = checkpoint
	player.rotation = Vector3.ZERO
	companion.position = checkpoint + Vector3(1.8,0,1.6)
	player.velocity = Vector3.ZERO
	attack_cd = 0
	dodge_time = 0
	invulnerable = 0
	pulse_cd = 0
	spawn_wave()
	status_text = "Lum: Again, darling. We finish what we start."

func _physics_process(delta: float) -> void:
	hud.text = "PROJECT PREMONITION  /  ASH CATHEDRAL\nVITALITY %03d    STAMINA %03d    ASH %d    WAVE %d/3" % [hp,stamina,ash,wave]
	note.text = ("PAUSED — Esc to resume" if paused else status_text) + "    |    Lum %s" % ("READY" if pulse_cd <= 0 else "%.1fs" % pulse_cd)
	if paused or hp <= 0 or victory:
		return
	elapsed += delta
	attack_cd = maxf(0,attack_cd-delta)
	dodge_time = maxf(0,dodge_time-delta)
	invulnerable = maxf(0,invulnerable-delta)
	pulse_cd = maxf(0,pulse_cd-delta)
	stamina = minf(100,stamina+delta*19)
	var axis = touch_move
	for held in touch_directions.values():
		axis += held
	if Input.is_physical_key_pressed(KEY_A) or Input.is_physical_key_pressed(KEY_LEFT): axis.x -= 1
	if Input.is_physical_key_pressed(KEY_D) or Input.is_physical_key_pressed(KEY_RIGHT): axis.x += 1
	if Input.is_physical_key_pressed(KEY_W) or Input.is_physical_key_pressed(KEY_UP): axis.y -= 1
	if Input.is_physical_key_pressed(KEY_S) or Input.is_physical_key_pressed(KEY_DOWN): axis.y += 1
	var direction = Vector3(axis.x,0,axis.y).limit_length()
	if direction.length() > 0.1 and dodge_time <= 0:
		facing = direction.normalized()
		player.rotation.y = atan2(-facing.x,-facing.z)
	var motion = dodge_dir * 16 if dodge_time > 0 else direction * 5
	player.velocity = Vector3(motion.x,player.velocity.y-20*delta,motion.z)
	player.move_and_slide()
	blade.rotation.x = -attack_cd * 5
	player.scale = Vector3.ONE * (0.92 if dodge_time > 0 else 1.0)
	companion.position = companion.position.lerp(player.position+Vector3(1.8,0,1.6),delta*3)
	var alive = 0
	for foe in foes:
		if foe.hp <= 0: continue
		alive += 1
		var offset: Vector3 = player.position-foe.node.position
		offset.y = 0
		var distance = offset.length()
		foe.timer -= delta
		if foe.windup:
			foe.node.scale = Vector3.ONE * (1.0 + 0.12*sin(elapsed*30))
			if foe.timer <= 0:
				if distance < 2.3: receive_hit(16+wave*2)
				foe.windup = false
				foe.timer = 1.4
				foe.node.scale = Vector3.ONE
		elif distance < 2 and foe.timer <= 0:
			foe.windup = true
			foe.timer = 0.75
		else:
			var velocity = offset.normalized() * (1.5+wave*0.2) if distance > 1.5 else Vector3.ZERO
			foe.node.velocity = Vector3(velocity.x,-2,velocity.z)
			foe.node.move_and_slide()
			if distance > 0.1: foe.node.look_at(foe.node.position+offset)
	if hp <= 0:
		return
	if alive == 0:
		if wave < 3:
			wave += 1
			hp = minf(100,hp+25)
			spawn_wave()
			status_text = "The cathedral stirs. Next wave / +25 vitality."
		else:
			victory = true
			status_text = "CATHEDRAL SEALED — You and Lum survived. R for a new run."
