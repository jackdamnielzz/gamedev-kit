extends RefCounted
## The Godot counterpart of the web template's lint rules: res://sim/ stays pure and deterministic.
## Scans every sim script (comments removed) for forbidden calls and node access.

const FORBIDDEN := {
	"(?<![\\w.])(randi|randf|randi_range|randf_range|randfn|randomize|rand_from_seed)\\s*\\(": "global randomness; use the world's RandomNumberGenerator",
	"\\b(Time|OS|Engine|Input)\\.": "clock, OS or input access; time is `tick`, input arrives as commands",
	"\\b(get_node|get_tree|get_viewport|add_child)\\s*\\(": "scene access; the sim knows no nodes",
	"\\$[A-Za-z_\"]": "node path access; the sim knows no nodes",
	"extends\\s+(Node|Node2D|Node3D|Control|CanvasItem)\\b": "the sim extends RefCounted or Resource, never a node",
	"(pre)?load\\(\"res://(scenes|game|ui|render|audio)/": "the sim may not load presentation code",
}


func test_sim_has_no_forbidden_calls(t) -> bool:
	var patterns := {}
	for source: String in FORBIDDEN:
		var re := RegEx.new()
		re.compile(source)
		patterns[re] = FORBIDDEN[source]
	for file: String in DirAccess.get_files_at("res://sim"):
		if not file.ends_with(".gd"):
			continue
		var lines := FileAccess.get_file_as_string("res://sim/" + file).split("\n")
		for i in lines.size():
			var code := lines[i].get_slice("#", 0)
			for re: RegEx in patterns:
				if re.search(code) != null:
					t.check(false, "sim/%s:%d: %s" % [file, i + 1, patterns[re]])
	return true
