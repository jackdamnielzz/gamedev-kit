class_name CommandLog
extends RefCounted
## Records every command the sim receives, with its tick, so a bug report can replay the run
## (PLAYTEST-AND-BUGS.md, sections 5 and 6). Ticks are relative to the start of the log.

var seed_value: int
var config: Dictionary
var commands: Array[Dictionary] = []
var _start_tick: int = 0
var _start_save: Variant = null


func _init(p_seed: int, p_config: Dictionary) -> void:
	seed_value = p_seed
	config = p_config


func record(world: World, cmds: Array) -> void:
	for c: Variant in cmds:
		var entry: Dictionary = (c as Dictionary).duplicate()
		entry["tick"] = world.tick - _start_tick
		commands.append(entry)


## Call after loading a save, or when the log grows too large: the log restarts from this world.
func rebase(world: World) -> void:
	_start_tick = world.tick
	_start_save = world.serialize()
	commands.clear()


func to_replay(world: World) -> Dictionary:
	return {
		"format": 1,
		"seed": seed_value,
		"config": config,
		"start_save": _start_save,
		"ticks": world.tick - _start_tick,
		"commands": commands.duplicate(true),
	}
