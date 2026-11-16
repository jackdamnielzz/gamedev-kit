class_name World
extends RefCounted
## The simulation: pure, deterministic game rules (GODOT.md, section 5). A placeholder that shows
## the contract every game keeps; replace the state and the commands, keep these functions:
##   World.create(seed, config) -> World     a new run
##   world.step(commands)                    one tick
##   world.serialize() -> String             stable JSON (same world, same string)
##   World.deserialize(text) -> World
## Rules (checked by tests/test_sim_purity.gd): no Node or scene access, no global random
## functions (use the world's own RandomNumberGenerator), no clock; time is `tick`.

const SAVE_VERSION := 1

var tick: int = 0
var value: int = 0
var sparks: int = 0
var _rng := RandomNumberGenerator.new()


static func create(seed_value: int, config: Dictionary = {}) -> World:
	var w := World.new()
	w._rng.seed = seed_value
	w.value = int(config.get("start_value", 0))
	return w


func step(commands: Array) -> void:
	for c: Variant in commands:
		var command: Dictionary = c
		if command.get("type", "") == "add":
			value += int(command.get("amount", 0))
	# Example of seeded randomness: an occasional spark.
	if _rng.randi_range(1, 100) == 1:
		sparks += 1
	tick += 1


func serialize() -> String:
	# The RNG state is a 64-bit integer: stored as a string so JSON does not round it.
	var data := {"version": SAVE_VERSION, "tick": tick, "value": value, "sparks": sparks, "rng_state": str(_rng.state)}
	return JSON.stringify(data, "", true)


static func deserialize(text: String) -> World:
	var data: Dictionary = JSON.parse_string(text)
	if int(data["version"]) != SAVE_VERSION:
		push_error("save version %d needs a migration to %d" % [int(data["version"]), SAVE_VERSION])
		return null
	var w := World.new()
	w.tick = int(data["tick"])
	w.value = int(data["value"])
	w.sparks = int(data["sparks"])
	w._rng.state = String(data["rng_state"]).to_int()
	return w


## Same rule as the bug report and the web template: sha256 of serialize(), first 16 hex characters.
func state_hash() -> String:
	return serialize().sha256_text().substr(0, 16)
