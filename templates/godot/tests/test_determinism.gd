extends RefCounted
## Same seed + same commands = same state; save/load in the middle changes nothing; every replay
## keeps its invariants and its pinned state_hash (PLAYTEST-AND-BUGS.md, section 6).

const Harness := preload("res://tests/replay_harness.gd")


func test_has_replays(t) -> bool:
	t.check(Harness.load_replays().size() > 0, "no replay fixtures in tests/fixtures/replays")
	return true


func test_serialize_round_trip(t) -> bool:
	var w := World.create(42)
	w.step([{"type": "add", "amount": 3}])
	t.check(World.deserialize(w.serialize()).serialize() == w.serialize(), "serialize -> deserialize -> serialize differs")
	return true


func test_two_runs_same_state(t) -> bool:
	for replay in Harness.load_replays():
		var a: String = Harness.run(replay)["state_hash"]
		var b: String = Harness.run(replay)["state_hash"]
		t.check(a == b, "%s: two runs gave %s and %s" % [replay["id"], a, b])
	return true


func test_save_load_halfway_same_state(t) -> bool:
	for replay in Harness.load_replays():
		var straight: String = Harness.run(replay)["state_hash"]
		var reloaded: String = Harness.run(replay, false, int(replay["ticks"]) / 2)["state_hash"]
		t.check(straight == reloaded, "%s: save/load halfway changed the outcome" % replay["id"])
	return true


func test_replays_keep_their_promises(t) -> bool:
	for replay in Harness.load_replays():
		var result := Harness.run(replay, true)
		var violations: Array = result["violations"]
		t.check(violations.is_empty(), "%s: %s" % [replay["id"], ", ".join(violations)])
		var pinned: Variant = (replay.get("expect", {}) as Dictionary).get("state_hash")
		if pinned is String and pinned != "":
			t.check(result["state_hash"] == pinned, "%s: state_hash changed to %s" % [replay["id"], result["state_hash"]])
		else:
			print("%s state_hash=%s" % [replay["id"], result["state_hash"]])
	return true
