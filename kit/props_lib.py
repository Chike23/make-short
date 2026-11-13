"""props_lib.py: rooms and props from libraries (house rule: library first), Poly Haven CC0 models.

Download a model once with get_polyhaven(id) (glTF, 1k textures) into the asset folder, then place it with place().
furnish_living_room() swaps the hand-built furniture in kit.living_room() for Poly Haven pieces; the walls, floor,
window, lamp and rug stay from the kit because the library has no match for them.
"""
import bpy, os, json, math, urllib.request

import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths
LIB = paths.POLYHAVEN
UA = {'User-Agent': 'make-short/1.0'}


def _fetch(url, fp):
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r, open(fp, 'wb') as f:
        f.write(r.read())


def get_polyhaven(asset_id, res='1k', lib=LIB):
    """Download one Poly Haven model as glTF (with its .bin and textures). Skips it when already there."""
    folder = os.path.join(lib, asset_id)
    if os.path.isdir(folder) and any(f.endswith('.gltf') for f in os.listdir(folder)): return folder
    info = json.load(urllib.request.urlopen(urllib.request.Request(f'https://api.polyhaven.com/files/{asset_id}', headers=UA), timeout=30))
    g = info['gltf'][res]['gltf']
    _fetch(g['url'], os.path.join(folder, os.path.basename(g['url'])))
    for rel, inc in g.get('include', {}).items(): _fetch(inc['url'], os.path.join(folder, rel))
    return folder


def place(asset_id, loc, rot_z=0.0, scale=1.0, coll='ROOM', name=None, lib=LIB):
    """Import a downloaded model under one empty, put it at loc (metres) turned rot_z degrees, in collection coll."""
    folder = os.path.join(lib, asset_id)
    gltf = [f for f in os.listdir(folder) if f.endswith('.gltf')][0]
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(folder, gltf))
    new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new(name or f'{asset_id}_root', None)
    target = bpy.data.collections.get(coll) or bpy.context.scene.collection
    target.objects.link(root)
    for o in new:
        for u in list(o.users_collection): u.objects.unlink(o)
        target.objects.link(o)
        if o.parent is None: o.parent = root
    root.location = loc; root.rotation_euler = (0, 0, math.radians(rot_z)); root.scale = (scale, scale, scale)
    return root


# the living room of the anatomy explainer: back wall at y = 1.8, window on the right, lamp on the left
LIVING_ROOM = [
    ('Sofa_01', (1.15, 1.2, 0), 0, 1.0),
    ('side_table_01', (-0.85, 1.35, 0), 0, 1.0),
    ('potted_plant_04', (-0.55, 1.45, 0), 15, 1.0),
    ('GreenChair_01', (-1.85, 0.2, 0), 55, 1.0),
    ('potted_plant_01', (2.35, 1.45, 0), 0, 1.0),
    ('hanging_picture_frame_01', (-0.35, 1.74, 1.75), 0, 1.0),
    ('hanging_picture_frame_02', (0.3, 1.74, 1.8), 0, 1.0),
]
HAND_BUILT = ('sofa_base', 'sofa_back', 'sofa_arm_l', 'sofa_arm_r', 'cushion', 'frame0', 'frame1', 'art0', 'art1',
              'table_top', 'table_leg')


def furnish_living_room(layout=LIVING_ROOM):
    for n in HAND_BUILT:
        o = bpy.data.objects.get(n)
        if o: bpy.data.objects.remove(o, do_unlink=True)
    return [place(a, loc, rz, s) for a, loc, rz, s in layout]
