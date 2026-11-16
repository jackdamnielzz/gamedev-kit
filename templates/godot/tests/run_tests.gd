extends SceneTree
## Headless test runner without a framework:
##   godot --headless --path . --import
##   godot --headless --path . --script res://tests/run_tests.gd
## Runs every test_*() method of every res://tests/test_*.gd. A test method takes the runner as
## `t`, calls t.check(condition, message), and must end with `return true`; a method that stops
## on a script error returns null and counts as a failure. Exit code 1 on any failure.

var _failures: Array[String] = []
var _current := ""


func check(condition: bool, message: String) -> void:
	if not condition:
		_failures.append("%s: %s" % [_current, message])


func _initialize() -> void:
	var files: Array = Array(DirAccess.get_files_at("res://tests")).filter(
		func(f: String) -> bool: return f.begins_with("test_") and f.ends_with(".gd")
	)
	files.sort()
	var count := 0
	for file: String in files:
		var script: GDScript = load("res://tests/" + file)
		var suite: Object = script.new()
		for method: Dictionary in suite.get_method_list():
			var method_name: String = method["name"]
			if not method_name.begins_with("test_"):
				continue
			_current = "%s.%s" % [file, method_name]
			count += 1
			var finished: Variant = suite.call(method_name, self)
			if finished != true:
				_failures.append("%s: did not finish (script error, or a missing `return true`)" % _current)
	for failure in _failures:
		printerr("FAIL ", failure)
	print("%d tests, %d failures" % [count, _failures.size()])
	quit(1 if _failures.size() > 0 else 0)
