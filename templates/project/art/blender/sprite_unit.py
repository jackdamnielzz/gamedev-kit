import argparse
import json
import math
import sys
from pathlib import Path

import bpy


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--directions", type=int, default=8)
    p.add_argument("--size", type=int, default=128)
    return p.parse_args(argv)


def reset_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def make_material(name, rgb):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.6
    return mat


def build_model(palette):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.25))
    hull = bpy.context.active_object
    hull.scale = (1.0, 0.6, 0.25)
    bevel = hull.modifiers.new("bevel", "BEVEL")
    bevel.width = 0.05
    bevel.segments = 2
    hull.data.materials.append(make_material("hull", palette["hull"]))

    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.08, depth=0.7, location=(0.4, 0, 0.5), rotation=(0, math.pi / 2, 0)
    )
    barrel = bpy.context.active_object
    barrel.data.materials.append(make_material("metal", palette["metal"]))

    root = bpy.data.objects.new("root", None)
    bpy.context.scene.collection.objects.link(root)
    hull.parent = root
    barrel.parent = root
    return root


def setup_scene(size):
    scene = bpy.context.scene

    cam_data = bpy.data.cameras.new("cam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 2.5
    cam = bpy.data.objects.new("cam", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (0, -4, 4)
    cam.rotation_euler = (math.radians(45), 0, 0)
    scene.camera = cam

    sun_data = bpy.data.lights.new("sun", "SUN")
    sun_data.energy = 3.0
    sun = bpy.data.objects.new("sun", sun_data)
    scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(50), 0, math.radians(30))

    # Engine identifier differs between Blender versions.
    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue

    scene.render.resolution_x = size
    scene.render.resolution_y = size
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"


def render_directions(root, out_dir, n):
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = []
    for i in range(n):
        root.rotation_euler = (0, 0, 2 * math.pi * i / n)
        path = out_dir / f"dir_{i:02d}.png"
        bpy.context.scene.render.filepath = str(path.resolve())
        bpy.ops.render.render(write_still=True)
        frames.append(path.name)
    meta = {"directions": n, "frames": frames}
    (out_dir / "frames.json").write_text(json.dumps(meta, indent=2))


def main():
    args = parse_args()
    palette_path = Path(__file__).resolve().parents[1] / "palette.json"
    palette = json.loads(palette_path.read_text())
    reset_scene()
    root = build_model(palette)
    setup_scene(args.size)
    render_directions(root, Path(args.out), args.directions)


main()
