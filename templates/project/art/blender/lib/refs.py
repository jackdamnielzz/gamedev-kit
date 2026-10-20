import math
from pathlib import Path

import bpy

VIEW_ROTATIONS = {
    "front": (math.pi / 2, 0.0, 0.0),          # XZ plane, seen from -Y
    "side": (math.pi / 2, 0.0, math.pi / 2),   # YZ plane, seen from +X
    "top": (0.0, 0.0, 0.0),                    # XY plane, seen from +Z
}


def add_reference(image_path: Path, view: str, size: float) -> bpy.types.Object:
    """size = real-world length of the image's longest side in Blender units."""
    img = bpy.data.images.load(str(image_path), check_existing=True)
    empty = bpy.data.objects.new(f"ref_{view}", None)
    empty.empty_display_type = "IMAGE"
    empty.data = img
    empty.empty_display_size = size
    # Bottom-centred for front/side so the ground line sits at z = 0; centred for top.
    empty.empty_image_offset = (-0.5, -0.5) if view == "top" else (-0.5, 0.0)
    empty.rotation_euler = VIEW_ROTATIONS[view]
    empty.use_empty_image_alpha = True
    empty.color[3] = 0.5                       # semi-transparent in the viewport
    empty.hide_render = True
    bpy.context.scene.collection.objects.link(empty)
    return empty


def add_reference_set(ref_dir: Path, size: float) -> dict:
    """Loads front.png, side.png and top.png from a sliced reference folder if present."""
    return {
        view: add_reference(ref_dir / f"{view}.png", view, size)
        for view in VIEW_ROTATIONS
        if (ref_dir / f"{view}.png").exists()
    }
