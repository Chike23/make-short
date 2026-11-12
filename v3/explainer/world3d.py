"""world3d.py: a painted 3D room for 2D characters (the skill's own look: lib/look.py), library-first.

Walls, floor and window are simple shapes with the skill's painted textures (v3/tex) and toon materials (cel
shading: cool purple shadows, warm light) with ink outlines. Furniture comes from Poly Haven (props_lib), repainted
in the same toon style from each model's own texture colour. Light and grade come from look.apply_mood and
look.setup_compositor (painterly filter, bloom, grade, depth ink lines, haze, vignette).

    import world3d as W
    W.living_room(); W.light('interior', 1, 300, lamp_at=W.LAMP_AT); W.grade()
"""
import bpy, os, sys, math
import numpy as np
from mathutils import Vector

V3 = os.path.expanduser('~/Downloads/make-short-test/v3')
sys.path.insert(0, os.path.join(V3, 'lib'))
import look                                    # noqa: E402
import props_lib as PL                         # noqa: E402

TEX = os.path.join(V3, 'tex')
LAMP_AT = (-1.6, 1.25, 1.62)


def _lin(c): return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)


def hexlin(h): h = h.lstrip('#'); return _lin([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])


def coll(name):
    c = bpy.data.collections.get(name)
    if c is None: c = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c)
    return c


def box(name, size, loc, mat, rot=(0, 0, 0), ink=0.012, c='WORLD'):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for u in list(o.users_collection): u.objects.unlink(o)
    coll(c).objects.link(o)
    o.data.materials.append(mat)
    if ink: look.ink_hull(o, ink)
    return o


def cyl(name, r, h, loc, mat, r2=None, seg=32, ink=0.01, c='WORLD', rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(vertices=seg, radius1=r, radius2=r if r2 is None else r2, depth=h, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name
    for u in list(o.users_collection): u.objects.unlink(o)
    coll(c).objects.link(o); o.data.materials.append(mat)
    for p in o.data.polygons: p.use_smooth = True
    if ink: look.ink_hull(o, ink)
    return o


def toon(name, hexrgb, tex=None, ink=False):
    return look.toon_mat(name, hexlin(hexrgb), tex=os.path.join(TEX, tex) if tex else None, ink=ink)


def _newmat(name):
    m = bpy.data.materials.new(name)
    try: m.use_nodes = True
    except Exception: pass
    return m


def emit(name, hexrgb, strength=1.0):
    m = _newmat(name); nt = m.node_tree; nt.nodes.clear()
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*hexlin(hexrgb), 1); em.inputs['Strength'].default_value = strength
    o = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(em.outputs[0], o.inputs[0]); return m


def sky_mat(name, stops):
    m = _newmat(name); nt = m.node_tree; nt.nodes.clear(); L = nt.links.new
    tc = nt.nodes.new('ShaderNodeTexCoord'); sp = nt.nodes.new('ShaderNodeSeparateXYZ'); rp = nt.nodes.new('ShaderNodeValToRGB')
    els = rp.color_ramp.elements
    while len(els) < len(stops): els.new(0.5)
    for e, (p, h) in zip(els, stops): e.position = p; e.color = (*hexlin(h), 1)
    em = nt.nodes.new('ShaderNodeEmission'); o = nt.nodes.new('ShaderNodeOutputMaterial')
    L(tc.outputs['Generated'], sp.inputs[0]); L(sp.outputs['Z'], rp.inputs['Fac']); L(rp.outputs['Color'], em.inputs['Color']); L(em.outputs[0], o.inputs[0])
    return m


# ---------------------------------------------------------------- library furniture, repainted toon
def _avg_tex_colour(mat):
    """Mean colour of the image feeding a Principled base colour (Poly Haven), else the base colour itself."""
    if mat is None or not mat.node_tree: return (0.5, 0.5, 0.5)
    for n in mat.node_tree.nodes:
        if n.bl_idname == 'ShaderNodeBsdfPrincipled':
            s = n.inputs['Base Color']
            if s.is_linked:
                src = s.links[0].from_node
                while src and src.bl_idname != 'ShaderNodeTexImage' and src.inputs and any(i.is_linked for i in src.inputs):
                    src = [i for i in src.inputs if i.is_linked][0].links[0].from_node
                if src is not None and src.bl_idname == 'ShaderNodeTexImage' and src.image:
                    im = src.image; px = np.empty(len(im.pixels), np.float32); im.pixels.foreach_get(px)
                    rgb = px.reshape(-1, 4)[:, :3].mean(0)
                    return tuple(float(v) for v in rgb) if im.colorspace_settings.name != 'sRGB' else _lin(rgb)
            return tuple(s.default_value[:3])
    return (0.5, 0.5, 0.5)


def toonify(root, ink=0.008, sat=1.15, tint=None):
    """Repaint every mesh under `root` in the skill's toon style, keeping each part's own (average) colour."""
    for o in [root] + list(root.children_recursive):
        if o.type != 'MESH': continue
        cols = [_avg_tex_colour(s.material) for s in o.material_slots] or [(0.5, 0.5, 0.5)]
        mats = []
        for i, c in enumerate(cols):
            c = np.array(c); g = c.mean(); c = np.clip(g + (c - g) * sat, 0, 1)
            if tint: c = np.array(hexlin(tint)) * (0.75 + 0.5 * min(1.0, g / 0.35))   # tint replaces the colour
            mats.append(look.toon_mat(f'{o.name}_toon{i}', tuple(float(v) for v in c), ink=False))
        o.data.materials.clear()
        for m in mats: o.data.materials.append(m)
        if ink: look.ink_hull(o, ink)
    return root


def furniture(asset, loc, rot_z=0.0, scale=1.0, tint=None):
    PL.get_polyhaven(asset)
    root = PL.place(asset, loc, rot_z, scale, coll='WORLD')
    return toonify(root, tint=tint)


# ---------------------------------------------------------------- the room
def living_room():
    wall = toon('wall', '#c9926c'); wall2 = toon('wall2', '#b98262'); wains = toon('wainscot', '#8a4a3c')
    floor = toon('floor', '#c99a62', 'wood_deck.png'); trim = toon('trim', '#efe0cc')
    box('floor', (12, 10, 0.1), (0, -1.0, -0.05), floor, ink=0)
    # back wall at y = 2.0 with a window opening (x 0.35..1.45, z 0.95..2.35)
    for n, s, l in (('wall_l', (4.35, 0.2, 3.4), (-1.825, 2.1, 1.7)), ('wall_r', (3.55, 0.2, 3.4), (3.225, 2.1, 1.7)),
                    ('wall_b', (1.1, 0.2, 0.95), (0.9, 2.1, 0.475)), ('wall_t', (1.1, 0.2, 1.05), (0.9, 2.1, 2.875))):
        box(n, s, l, wall, ink=0)
    box('wall_side', (0.2, 8, 3.4), (-2.9, -1.8, 1.7), wall2, ink=0)
    box('ceiling', (12, 10, 0.1), (0, -1.0, 3.4), toon('ceiling', '#c9a690'), ink=0)
    box('wainscot', (2.7, 0.05, 0.9), (-1.0, 1.99, 0.45), wains, ink=0); box('wainscot_r', (3.2, 0.05, 0.9), (3.05, 1.99, 0.45), wains, ink=0)
    box('wainscot_side', (0.05, 8, 0.9), (-2.79, -1.8, 0.45), wains, ink=0)
    box('rail', (6.8, 0.06, 0.05), (0.4, 1.97, 0.92), trim, ink=0.005); box('rail_side', (0.06, 8, 0.05), (-2.77, -1.8, 0.92), trim, ink=0.005)
    box('skirting', (6.8, 0.06, 0.12), (0.4, 1.96, 0.06), trim, ink=0.006)
    box('skirting_side', (0.06, 8, 0.12), (-2.76, -1.8, 0.06), trim, ink=0.006)
    # window frame, sill, mullions; sunset sky, sun and a skyline outside
    fr = toon('win_frame', '#3a2418')
    for n, s, l in (('wf_l', (0.08, 0.16, 1.48), (0.35, 2.0, 1.65)), ('wf_r', (0.08, 0.16, 1.48), (1.45, 2.0, 1.65)),
                    ('wf_t', (1.18, 0.16, 0.08), (0.9, 2.0, 2.35)), ('wf_sill', (1.36, 0.3, 0.07), (0.9, 1.93, 0.93)),
                    ('wf_mv', (0.04, 0.08, 1.4), (0.9, 2.02, 1.65)), ('wf_mh', (1.1, 0.08, 0.04), (0.9, 2.02, 1.7))):
        box(n, s, l, fr, ink=0.008)
    sky = box('sky', (6, 0.05, 4), (0.9, 3.4, 1.8), sky_mat('sunset', [(0.0, '#ffb067'), (0.35, '#f08a6a'), (0.62, '#b0628a'), (1.0, '#4b3a78')]), ink=0)
    sun = cyl('sun', 0.2, 0.02, (1.15, 3.3, 1.3), emit('sun', '#ffe6b0', 2.0), ink=0, rot=(math.radians(90), 0, 0))
    city = toon('city', '#3a2a4a')
    for k, (x, w, h) in enumerate([(0.0, 0.35, 0.8), (0.4, 0.3, 1.25), (0.75, 0.4, 0.6), (1.2, 0.25, 1.45), (1.5, 0.35, 0.9), (1.9, 0.3, 1.15)]):
        box(f'tower{k}', (w, 0.3, h), (x, 3.1, h / 2 + 0.2), emit(f'tower{k}', '#2e2240', 1.0), ink=0)
    # rug under her feet
    cyl('rug', 1.25, 0.02, (0.05, -0.05, 0.01), toon('rug', '#e3cdb0'), ink=0.006).scale = (1, 0.62, 1)
    cyl('rug_in', 1.05, 0.022, (0.05, -0.05, 0.011), toon('rug_in', '#d0a982'), ink=0).scale = (1, 0.62, 1)
    # floor lamp (left, behind her): pole, base, glowing shade; its point light comes from apply_mood(lamp_at=LAMP_AT)
    metal = toon('lamp_metal', '#3a2c24')
    cyl('lamp_base', 0.17, 0.04, (LAMP_AT[0], LAMP_AT[1], 0.02), metal, ink=0.006)
    cyl('lamp_pole', 0.02, 1.5, (LAMP_AT[0], LAMP_AT[1], 0.78), metal, ink=0.005)
    cyl('lamp_shade', 0.26, 0.36, (LAMP_AT[0], LAMP_AT[1], LAMP_AT[2] + 0.1), emit('shade', '#ffd9a0', 2.2), r2=0.17, ink=0.008)
    # picture frames on the back wall
    for k, (x, z, w, h, art) in enumerate([(-0.75, 1.8, 0.62, 0.48, '#d38a52'), (-0.05, 1.86, 0.36, 0.36, '#6f8a86')]):
        box(f'frame{k}', (w, 0.04, h), (x, 1.98, z), toon(f'frame{k}', '#2a1a12'), ink=0.006)
        box(f'art{k}', (w - 0.09, 0.02, h - 0.09), (x, 1.955, z), toon(f'art{k}', art), ink=0)
    # library furniture, repainted
    furniture('Sofa_01', (1.55, 1.35, 0), 0, 1.0, tint='#5a78c0')
    furniture('GreenChair_01', (-2.0, 0.1, 0), 60, 1.0)
    furniture('side_table_01', (-0.95, 1.55, 0), 0, 1.0)
    furniture('potted_plant_04', (-0.95, 1.55, 0.5), 20, 0.9)
    furniture('potted_plant_01', (2.6, 1.55, 0), 0, 1.0)


def dumbbell(name, loc, rot=(0, 0, 0), scale=1.0, c='WORLD'):
    """A toon dumbbell (bar along x), built from primitives: no library model has one."""
    iron = toon(f'{name}_iron', '#3b3f4a'); bar = toon(f'{name}_bar', '#b9b4ac')
    e = bpy.data.objects.new(name, None); coll(c).objects.link(e); e.location = loc; e.rotation_euler = rot; e.scale = (scale,) * 3
    parts = [cyl(f'{name}_bar', 0.013, 0.24, (0, 0, 0), bar, ink=0.004, c=c, rot=(0, math.radians(90), 0))]
    for sx in (-1, 1):
        parts.append(cyl(f'{name}_plate{sx}', 0.045, 0.045, (0.09 * sx, 0, 0), iron, seg=6, ink=0.006, c=c, rot=(0, math.radians(90), 0)))
    for p in parts: p.parent = e
    return e


# a cosy sunset living room in the reference's palette: warm key, cool lilac fill, lamp and window as practicals
look.MOODS['living'] = dict(top=(0.40, 0.33, 0.38), hor=(0.62, 0.46, 0.40), wstr=0.5,
                            sun=((1.0, 0.8, 0.6), 0.0, (-40, 50)), fill=((0.70, 0.72, 1.0), 30.0), lamp=((1.0, 0.70, 0.42), 70.0),
                            exp=0.0, sat=1.12, con=0.30, gam=1.12, gain=(0.98, 0.95, 0.92), lift=(0.97, 0.975, 1.06), vig=0.38, haze=0.05)


def light(mood='living', f0=1, f1=250, lamp_at=LAMP_AT, key_at=(-1.9, -2.3, 2.9), key_to=(0.0, 0.0, 1.0), key_energy=500.0,
          window=(0.9, 1.75, 1.7), window_energy=90.0):
    """Mood rig from look.apply_mood, plus a warm key light. Only the key casts shadows (her shadow, the furniture
    shadows); the rest light without shadows, which keeps a frame at a few seconds. No fog (it is the slowest pass)."""
    sc = bpy.context.scene
    look.apply_mood(sc, mood, f0, f1, lamp_at=lamp_at, fill_x=0.0)
    w = sc.world; nt = w.node_tree
    for l in [l for l in nt.links if l.to_node.bl_idname == 'ShaderNodeOutputWorld' and l.to_socket.name == 'Volume']: nt.links.remove(l)
    kd = bpy.data.lights.new('key', 'AREA'); kd.size = 1.6; kd.energy = key_energy; kd.color = (1.0, 0.86, 0.70)
    k = bpy.data.objects.new('key', kd); sc.collection.objects.link(k); k.location = key_at
    k.rotation_euler = (Vector(key_to) - Vector(key_at)).to_track_quat('-Z', 'Y').to_euler()
    if window:                                           # warm sunset spilling in through the window
        ld = bpy.data.lights.new('win_light', 'AREA'); ld.shape = 'RECTANGLE'; ld.size, ld.size_y = 1.1, 1.4
        ld.energy = window_energy; ld.color = (1.0, 0.64, 0.40)
        o = bpy.data.objects.new('win_light', ld); sc.collection.objects.link(o)
        o.location = window; o.rotation_euler = (math.radians(-80), 0, 0)
    for o in sc.objects:
        if o.type == 'LIGHT':
            o.data.use_shadow = (o.name == 'key')
            if o.data.type == 'SUN' and o.data.energy == 0: o.hide_render = True
    for kname, v in dict(shadow_ray_count=1, shadow_step_count=4).items():
        try: setattr(sc.eevee, kname, v)
        except Exception: pass
    return sc


def grade():
    return look.setup_compositor(bpy.context.scene)


def set_kuwahara(size, frames):
    """look keys the painterly filter per mood (2 px); a 2D character keeps crisper eyes at 1. Call after light()."""
    nt = bpy.context.scene.compositing_node_group
    if nt is None or 'ku' not in nt.nodes: return
    s = nt.nodes['ku'].inputs['Size']
    for f in frames: s.default_value = size; s.keyframe_insert('default_value', frame=f)
