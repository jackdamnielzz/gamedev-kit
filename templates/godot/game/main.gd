extends Node2D
## Glue: the fixed-step loop (_physics_process at the project's physics tick rate), input ->
## commands -> sim, sim state -> presentation. A placeholder: replace the Label with the real
## scenes; keep the loop, the command log and the F8 bug report.
## Start with a fixed seed: godot --path . -- --seed=7

var world: World
var cmd_log: CommandLog
var _pending: Array[Dictionary] = []

@onready var _label: Label = $Label


func _ready() -> void:
	var seed_value := randi()  # the game layer may use global randomness; the sim may not
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--seed="):
			seed_value = arg.get_slice("=", 1).to_int()
	world = World.create(seed_value, {})
	cmd_log = CommandLog.new(seed_value, {})
	print("started seed=%d" % seed_value)


func _unhandled_input(event: InputEvent) -> void:
	var key := event as InputEventKey
	if key == null or not key.pressed or key.echo:
		return
	if key.keycode == KEY_SPACE:
		_pending.append({"type": "add", "amount": 1})
	elif key.keycode == KEY_F8:
		_save_bug_report()


func _physics_process(_delta: float) -> void:
	var commands := _pending.duplicate()
	_pending.clear()
	cmd_log.record(world, commands)
	world.step(commands)
	_label.text = "tick %d   value %d   sparks %d\nSpace: add   F8: bug report" % [world.tick, world.value, world.sparks]


func _save_bug_report() -> void:
	var now := Time.get_datetime_string_from_system()
	var report := cmd_log.to_replay(world)
	report["id"] = "bug-" + now.replace("-", "").replace(":", "").replace("T", "-")
	report["game_version"] = str(ProjectSettings.get_setting("application/config/version", "0.1.0"))
	report["commit"] = _commit()
	var shot := ""
	var texture := get_viewport().get_texture()
	if texture != null:
		var image := texture.get_image()
		if image != null:
			shot = Marshalls.raw_to_base64(image.save_png_to_buffer())
	report["report"] = {
		"created_at": Time.get_datetime_string_from_system(true),
		"platform": OS.get_name(),
		"user_note": "",
		"state_hash": world.state_hash(),
		"screenshot_png_base64": shot,
	}
	DirAccess.make_dir_recursive_absolute("user://bugreports")
	var path := "user://bugreports/%s.json" % report["id"]
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		push_error("could not write %s" % path)
		return
	file.store_string(JSON.stringify(report, "  "))
	print("bug report saved: %s" % ProjectSettings.globalize_path(path))


## CI writes res://commit.txt before an export; local runs report "dev".
func _commit() -> String:
	if FileAccess.file_exists("res://commit.txt"):
		return FileAccess.get_file_as_string("res://commit.txt").strip_edges()
	return "dev"
