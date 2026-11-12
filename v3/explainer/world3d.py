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
                            exp=0.0, sat=0.85, con=0.30, gam=1.0, gain=(0.9, 0.86, 0.84), lift=(0.9, 0.9, 0.98), vig=0.38, haze=0.05)


# the park at golden hour: the skill's dusk with the saturation the 2D lead can take (her skin went red at 1.95) and a
# brighter grade (Rick's dusk band is YAVG 114-153)
look.MOODS['park_dusk'] = dict(look.MOODS['dusk'], sat=1.25, gain=(0.98, 0.9, 0.85))

look.MOODS['gym'] = dict(top=(0.52, 0.58, 0.72), hor=(0.78, 0.74, 0.70), wstr=0.55,
                         sun=((1.0, 0.95, 0.9), 0.0, (-40, 50)), fill=((1.0, 0.86, 0.72), 25.0), lamp=((1.0, 0.8, 0.6), 0.0),
                         exp=0.0, sat=1.1, con=0.30, gam=1.12, gain=(0.96, 0.97, 1.0), lift=(0.97, 0.98, 1.06), vig=0.38, haze=0.04)


def light(mood='living', f0=1, f1=250, lamp_at=LAMP_AT, key_at=(-1.9, -2.3, 2.9), key_to=(0.0, 0.0, 1.0), key_energy=500.0,
          key_color=(1.0, 0.86, 0.70), key_size=1.6, window=(0.9, 1.75, 1.7), window_energy=90.0, shadow='key'):
    """Mood rig from look.apply_mood, plus an optional key light. Only ONE light casts shadows (`shadow`: 'key'
    indoors, 'LOOK_Sun' outdoors); the rest light without shadows, which keeps a frame at a few seconds. No fog
    (it was most of the frame time; the compositor haze still gives depth)."""
    sc = bpy.context.scene
    look.apply_mood(sc, mood, f0, f1, lamp_at=lamp_at, fill_x=0.0)
    w = sc.world; nt = w.node_tree
    for l in [l for l in nt.links if l.to_node.bl_idname == 'ShaderNodeOutputWorld' and l.to_socket.name == 'Volume']: nt.links.remove(l)
    if key_energy:
        kd = bpy.data.lights.new('key', 'AREA'); kd.size = key_size; kd.energy = key_energy; kd.color = key_color
        k = bpy.data.objects.new('key', kd); sc.collection.objects.link(k); k.location = key_at
        k.rotation_euler = (Vector(key_to) - Vector(key_at)).to_track_quat('-Z', 'Y').to_euler()
    if window:                                           # warm sunset spilling in through the window
        ld = bpy.data.lights.new('win_light', 'AREA'); ld.shape = 'RECTANGLE'; ld.size, ld.size_y = 1.1, 1.4
        ld.energy = window_energy; ld.color = (1.0, 0.64, 0.40)
        o = bpy.data.objects.new('win_light', ld); sc.collection.objects.link(o)
        o.location = window; o.rotation_euler = (math.radians(-80), 0, 0)
    for o in sc.objects:
        if o.type == 'LIGHT':
            o.data.use_shadow = (o.name == shadow)
            if o.data.energy == 0 and not (o.animation_data and o.animation_data.action): o.hide_render = True
    for kname, v in dict(shadow_ray_count=1, shadow_step_count=4).items():
        try: setattr(sc.eevee, kname, v)
        except Exception: pass
    return sc


def grade():
    return look.setup_compositor(bpy.context.scene)


def rick_look(keep=('lady',), world_ink=False, depth_ink=0.6, smooth=True):
    """Rick's world, studied frame by frame on R1 (2026-11): the SET is smoothly lit 3D (sun and sky light roll
    across surfaces; no cel steps), it has NO outlines (only the 2D characters are drawn with lines), cast shadows
    from one strong sun, haze to a bright horizon, and shallow depth of field on medium and close shots (the
    camera's job: see scene_trial.finish). Call after the set, the character and the lights exist.
      - smooth: the skill's toon ramp (cel steps) becomes a soft shadow -> mid -> lit gradient on the set
      - world_ink False: the inverted-hull outlines on set objects are switched off
      - depth_ink: strength of the compositor's depth lines (1 = off, 0.15 = the skill's full ink)"""
    sc = bpy.context.scene; n_ink = n_ramp = 0
    for o in sc.objects:
        if o.name.startswith(keep) or o.type != 'MESH': continue
        md = o.modifiers.get('LOOK_ink')
        if md and not world_ink: md.show_render = False; md.show_viewport = False; n_ink += 1
    if smooth:
        for m in bpy.data.materials:
            if not m.node_tree or m.name.startswith(keep): continue
            for n in m.node_tree.nodes:
                if n.bl_idname != 'ShaderNodeValToRGB': continue
                els = n.color_ramp.elements
                if len(els) != 5 or abs(els[2].position - 0.27) > 0.01: continue      # only look.py's toon ramp
                sh, mid, lit = tuple(els[0].color), tuple(els[2].color), tuple(els[4].color)
                while len(els) > 3: els.remove(els[-1])
                for e, (p, c) in zip(els, ((0.0, sh), (0.32, mid), (0.72, lit))): e.position = p; e.color = c
                n.color_ramp.interpolation = 'EASE'; n_ramp += 1
    nt = sc.compositing_node_group
    if nt is not None and 'inkmap' in nt.nodes: nt.nodes['inkmap'].inputs['To Max'].default_value = depth_ink
    return {'ink_off': n_ink, 'ramps_smoothed': n_ramp}


def set_kuwahara(size, frames):
    """look keys the painterly filter per mood (2 px); a 2D character keeps crisper eyes at 1. Call after light()."""
    nt = bpy.context.scene.compositing_node_group
    if nt is None or 'ku' not in nt.nodes: return
    s = nt.nodes['ku'].inputs['Size']
    for f in frames: s.default_value = size; s.keyframe_insert('default_value', frame=f)


# ---------------------------------------------------------------- the park: Rick's riverside world (lib/sets.py builders)
PARK_PATH = [(-0.55, 4.4), (-0.75, 2.2), (-0.78, 0.6), (-0.72, -0.9)]


def park_ground(x, y):
    """Floor height in the park: three stone steps up to a low terrace on the path ("climbs your stairs")."""
    if abs(x + 0.75) > 1.25: return 0.0
    if y > 1.75: return 0.0
    if y > 1.45: return 0.12
    if y > 1.15: return 0.24
    if y > -1.9: return 0.36
    return 0.0


def park(mood='day'):
    """Rick's world: sky dome with clouds (or a sunset sky), three rows of hills and a tree line, the river, a winding
    path and grass patches (sets.terrain), far, framing and foreground trees (sets._dep_trees), dense ink-outlined
    tufts, pebbles and flowers (sets._surface_ground). Plus a stone terrace with steps on the path, Poly Haven benches
    and street lamps repainted toon, closer framing trees and edge bushes so wides never show bare ground."""
    import sets as S
    o = (0, 0, 0); c = coll('WORLD')
    S._DUSK = (mood == 'dusk')
    try:
        if mood == 'dusk':
            st = [(0.0, (1.0, 0.8, 0.5)), (0.12, (1.0, 0.66, 0.44)), (0.36, (0.82, 0.66, 0.74)), (0.68, (0.46, 0.54, 0.8)), (1.0, (0.3, 0.38, 0.68))]
            d = S.sph(c, 'skydome', 140.0, o, S.sky_mat('sky_dusk', st, 140.0), (1, 1, 1), 24); d.visible_shadow = False
            S.sph(c, 'sundisc', 8.0, (6, 118, 7), S.glow('sundisc', (1.0, 0.82, 0.5), 3.0), (1, 1, 1), 16)
            S._surface_sky(c, o)
        else:
            S.sky(c, o, False)
        S.hills(c, o, False)
        S.terrain(c, o)
        S._dep_trees(c, o, False)
        S.tree(c, 'tree_n1', (-3.8, 3.2, 0), 5.2, 31); S.tree(c, 'tree_n2', (3.6, 5.0, 0), 5.8, 32); S.tree(c, 'tree_n3', (-6.5, 8.5, 0), 6.0, 33)
        for i, (x, y, k) in enumerate(((-2.3, -4.6, 1.1), (2.4, -4.2, 1.2), (-3.2, -2.6, 0.9), (3.1, -2.2, 1.0))):   # frame-edge bushes
            S.inked(S.sph(c, 'ebush', 0.75 * k, (x, y, 0.3 * k), S.M('leaf'), (1.3, 1.0, 0.8), 10, 0.14, 50 + i), 0.025)
        stone = S.M('stone')
        for i, (y, h) in enumerate(((1.6, 0.12), (1.3, 0.24), (1.0, 0.36))):
            S.inked(S.box(c, f'step{i}', (2.5, 0.32, h), (-0.75, y, h / 2), stone, tile=0.45), 0.012)
        S.inked(S.box(c, 'terrace', (2.5, 2.9, 0.36), (-0.75, -0.45, 0.18), stone, tile=0.45), 0.014)
        for sx in (-1, 1):
            for k in range(4): S.rock(c, 'trock', (-0.75 + sx * 1.42, 0.9 - k * 0.75, 0.1), 0.22 + 0.04 * (k % 2), 60 + k)
        cols = dict(tl=(0.36, 0.52, 0.14), td=(0.14, 0.3, 0.14), peb=(0.66, 0.64, 0.6), flw=(1.0, 0.95, 0.55), patch=(0.5, 0.72, 0.38))
        if mood == 'dusk': cols = dict(tl=(0.42, 0.48, 0.16), td=(0.16, 0.24, 0.12), peb=(0.6, 0.56, 0.58), flw=(1.0, 0.8, 0.45), patch=(0.3, 0.38, 0.14))
        avoid = [(-0.75, y, 1.15) for y in (5.0, 3.5, 2.0, 0.5, -1.0, -2.0)]
        S._surface_ground(c, o, 'pk', cols, avoid, (-8, 8, -6, 10), n_t=1100, n_p=140, n_f=70, patches=10, seed=81)
    finally:
        S._DUSK = False
    furniture('painted_wooden_bench', (2.3, 1.6, 0), -20, 1.0)
    furniture('painted_wooden_bench', (-3.0, -0.2, 0), 35, 1.0)
    furniture('street_lamp_01', (1.9, 3.6, 0), 0, 1.0)
    furniture('street_lamp_01', (-2.6, 5.8, 0), 0, 1.0)


# ---------------------------------------------------------------- the gym: daylight from a window wall, rack, bench, mirror
GYM_RACK = (1.35, 1.25)


def gym():
    floor = toon('gym_floor', '#9a6a44', 'wood_deck.png'); mat = toon('gym_mat', '#56657e')
    wall = toon('gym_wall', '#e3d6c4'); band = toon('gym_band', '#4f6fb0'); steel = toon('gym_steel', '#3b3f4a'); trim = toon('gym_trim', '#f2ebe0')
    box('floor', (14, 12, 0.1), (0, -1.0, -0.05), floor, ink=0)
    box('mat', (4.4, 3.4, 0.03), (0.2, 0.4, 0.015), mat, ink=0.006)
    box('ceiling', (14, 12, 0.1), (0, -1.0, 3.6), toon('gym_ceiling', '#cfc3b4'), ink=0)
    box('wall_back', (14, 0.2, 3.6), (0, 3.1, 1.8), wall, ink=0)
    box('band_back', (14, 0.05, 1.0), (0, 2.99, 0.5), band, ink=0); box('rail_back', (14, 0.06, 0.05), (0, 2.97, 1.02), trim, ink=0.005)
    # left wall: tall windows with a bright sky behind them (the daylight key comes from here)
    for n, sz, l in (('wl_a', (0.2, 6, 0.8), (-3.6, -0.5, 0.4)), ('wl_b', (0.2, 6, 0.6), (-3.6, -0.5, 3.3)),
                     ('wl_c', (0.2, 0.5, 2.2), (-3.6, -3.25, 1.9)), ('wl_d', (0.2, 0.5, 2.2), (-3.6, 2.25, 1.9))):
        box(n, sz, l, wall, ink=0)
    for k, y in enumerate((-1.75, 0.0, 1.75)):
        box(f'mull{k}', (0.12, 0.08, 2.2), (-3.55, y + 0.85, 1.9), steel, ink=0.006)
    box('gym_sky', (0.05, 8, 4), (-4.6, -0.5, 1.9), sky_mat('gym_sky', [(0.0, '#d9ecff'), (0.5, '#9cc8f5'), (1.0, '#5d93e0')]), ink=0)
    for k, (y, h) in enumerate(((-2.2, 1.1), (-1.2, 1.6), (0.4, 0.9), (1.5, 1.4))):
        box(f'bld{k}', (0.3, 0.9, h), (-4.4, y, 0.8 + h / 2), emit(f'bld{k}', '#b8c6d8', 1.0), ink=0)
    # right wall: a mirror
    box('wall_right', (0.2, 12, 3.6), (4.2, -1.0, 1.8), wall, ink=0)
    box('mirror', (0.04, 3.0, 1.8), (4.08, 0.9, 1.5), emit('mirror', '#cfe0ee', 0.85), ink=0.01)
    # dumbbell rack (two tiers) with dumbbells
    rx, ry = GYM_RACK
    for x in (rx - 0.75, rx + 0.75):
        box(f'rack_leg{x}', (0.06, 0.5, 0.95), (x, ry + 0.1, 0.475), steel, ink=0.006)
    for z, yy in ((0.55, ry - 0.05), (0.88, ry + 0.22)):
        box(f'rack_tier{z}', (1.6, 0.34, 0.05), (rx, yy, z), steel, ink=0.006)
    for k in range(5):
        dumbbell(f'db_rk_lo{k}', (rx - 0.6 + k * 0.3, ry - 0.05, 0.62), (0, 0, math.radians(90)), 0.9)
        dumbbell(f'db_rk_hi{k}', (rx - 0.6 + k * 0.3, ry + 0.22, 0.95), (0, 0, math.radians(90)), 0.85)
    # bench, kettlebells, plants, posters
    pad = toon('pad', '#b5463c')
    box('bench_pad', (1.3, 0.34, 0.1), (-1.5, 1.6, 0.48), pad, ink=0.008)
    for x in (-2.0, -1.0): box(f'bench_leg{x}', (0.08, 0.3, 0.43), (x, 1.6, 0.215), steel, ink=0.005)
    for k, x in enumerate((2.9, 3.25, 3.6)):
        kb = cyl(f'kb{k}', 0.13 + 0.02 * k, 0.24 + 0.03 * k, (x, 2.5, 0.13 + 0.015 * k), toon(f'kb{k}', '#2f3540'), ink=0.006)
    for k, (x, art) in enumerate(((-1.6, '#f0b04a'), (-0.6, '#6f8a86'), (0.6, '#d36b4a'))):
        box(f'poster{k}', (0.6, 0.03, 0.8), (x, 2.98, 2.1), toon(f'poster_fr{k}', '#2a2a30'), ink=0.006)
        box(f'poster_art{k}', (0.5, 0.02, 0.7), (x, 2.96, 2.1), toon(f'poster{k}', art), ink=0)
    furniture('potted_plant_01', (-3.0, 2.5, 0), 0, 1.0)
    furniture('potted_plant_04', (3.7, -1.6, 0), 0, 1.4)
