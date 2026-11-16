extends RefCounted
## Runs replay files (res://tests/fixtures/replays/*.json, format in PLAYTEST-AND-BUGS.md) against
## the sim. Used by the determinism and replay tests, and by bug fixing.

const REPLAY_DIR := "res://tests/fixtures/replays"
const Invariants := preload("res://tests/invariants.gd")


## Every replay in the folder (not in archive/), sorted by file name.
static func load_replays() -> Array[Dictionary]:
	var replays: Array[Dictionary] = []
	var files: Array = Array(DirAccess.get_files_at(REPLAY_DIR))
	files.sort()
	for file: String in files:
		if not file.ends_with(".json"):
			continue
		var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(REPLAY_DIR + "/" + file))
		if data is Dictionary:
			replays.append(data)
	return replays


## Returns {"world", "state_hash", "violations"}. save_load_at >= 0 serialises and reloads the
## world at that tick; check_invariants checks expect.invariants after every tick.
static func run(replay: Dictionary, check_invariants: bool = false, save_load_at: int = -1) -> Dictionary:
	var ticks := int(replay["ticks"])
	var by_tick := {}
	for c: Variant in replay["commands"]:
		var command: Dictionary = (c as Dictionary).duplicate()
		var t := int(command["tick"])
		command.erase("tick")
		if not by_tick.has(t):
			by_tick[t] = []
		by_tick[t].append(command)

	var world: World
	var save: Variant = replay.get("start_save")
	if save is String:
		world = World.deserialize(save)
	elif save is Dictionary:
		world = World.deserialize(JSON.stringify(save))
	else:
		world = World.create(int(replay["seed"]), replay.get("config", {}))

	var names: Array = []
	if check_invariants:
		names = (replay.get("expect", {}) as Dictionary).get("invariants", [])
	var violations: Array[String] = []
	var broken := {}
	for t in ticks:
		if t == save_load_at:
			world = World.deserialize(world.serialize())
		world.step(by_tick.get(t, []))
		for invariant_name: String in names:
			if broken.has(invariant_name):
				continue
			var problem := Invariants.check(invariant_name, world)
			if problem != "":
				broken[invariant_name] = true
				violations.append("%s broken after relative tick %d: %s" % [invariant_name, t, problem])
	return {"world": world, "state_hash": world.state_hash(), "violations": violations}
