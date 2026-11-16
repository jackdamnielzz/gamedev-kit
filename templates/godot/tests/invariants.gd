extends RefCounted
## Named invariants that replay files can ask for (`expect.invariants`). Return "" when the world
## is fine, or a short message when it is not. Add one per bug class (PLAYTEST-AND-BUGS.md,
## section 6), e.g. moneyNeverNegative, noUnitOutsideMap. Names match the web template's.


static func check(invariant_name: String, world: World) -> String:
	match invariant_name:
		"tickNeverNegative":
			return "" if world.tick >= 0 else "tick is %d" % world.tick
	return "unknown invariant '%s' (add it to tests/invariants.gd)" % invariant_name
