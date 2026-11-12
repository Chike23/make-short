"""kit.py: Blender kit for the anatomy-explainer style (references/styles/anatomy-explainer.md). Blender 5.x, EEVEE.

Run inside Blender (through the Blender MCP: exec this file's text, then call the functions).
Everything is built from code: no downloads. The look targets the measured reference: warm, very dark, soft
"illustrated 3D" (matte shapes, soft light, lamp pools), adults with realistic proportions, X-ray passes that line up
with the body because they are built from the same joints.

  reset()                          empty scene, render settings (1350x2400, EEVEE, AgX)
  living_room()                    floor lamp, sunset window, sofa, rug, frames, side table
  stage()                          dark sweep backdrop with a warm pool of light, for props and infographics
  person(pose, at, rot_z)          the lead (woman, 50s, grey bob, teal top); pose = 'stand' or 'curl'
  xray(pose, at, rot_z)            skeleton + muscles for the same pose (collection 'XRAY')
  dumbbell(at, rot)                prop
  camera(loc, target, lens)        the shot camera
  render(path)                     base pass;  render_layer(path) = X-ray pass on transparent film, body ghosted
"""
import bpy, bmesh, math
from mathutils import Vector, Matrix

RES = (1350, 2400)


# ------------------------------------------------------------------ scene
def reset():
    """Empty the scene's contents (not a factory reset: that would also unload the MCP add-on)."""
    sc = bpy.context.scene
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    for c in list(bpy.data.collections): bpy.data.collections.remove(c)
    for blocks in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras, bpy.data.worlds, bpy.data.images):
        for b in list(blocks):
            if b.users == 0: blocks.remove(b)
    sc.render.engine = 'BLENDER_EEVEE'
    sc.render.resolution_x, sc.render.resolution_y = RES
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    for k, v in dict(taa_render_samples=48, use_shadows=True, shadow_ray_count=2, shadow_step_count=8,
                     use_raytracing=True, use_gtao=True).items():
        try: setattr(sc.eevee, k, v)
        except Exception: pass
    sc.view_settings.view_transform = 'AgX'
    for look in ('AgX - Medium High Contrast', 'Medium High Contrast'):
        try: sc.view_settings.look = look; break
        except Exception: pass
    sc.view_settings.exposure = 0.3
    w = bpy.data.worlds.new('World'); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (0.012, 0.009, 0.007, 1); bg.inputs[1].default_value = 2.0
    for n in ('ROOM', 'STAGE', 'PERSON', 'XRAY', 'PROPS'):
        c = bpy.data.collections.new(n); sc.collection.children.link(c)
    return sc


def coll(name): return bpy.data.collections[name]


def link(o, c):
    for u in o.users_collection: u.objects.unlink(o)
    coll(c).objects.link(o); return o


# ------------------------------------------------------------------ materials
def mat(name, rgb, rough=0.8, noise=0.06, emit=None, strength=0.0, alpha=1.0, spec=0.25):
    if name in bpy.data.materials: return bpy.data.materials[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N, L = nt.nodes, nt.links
    p = N['Principled BSDF']
    p.inputs['Roughness'].default_value = rough
    for key in ('Specular IOR Level', 'Specular'):
        if key in p.inputs: p.inputs[key].default_value = spec; break
    col = (*rgb, 1.0)
    if noise:                                                         # painterly variation in the base colour
        tx = N.new('ShaderNodeTexNoise'); tx.inputs['Scale'].default_value = 9.0; tx.inputs['Detail'].default_value = 3.0
        mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'
        mx.inputs['Factor'].default_value = 1.0
        ramp = N.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].color = (1 - noise, 1 - noise, 1 - noise, 1); ramp.color_ramp.elements[1].color = (1 + noise, 1 + noise, 1 + noise, 1)
        L.new(tx.outputs['Fac'], ramp.inputs['Fac'])
        mx.inputs[6].default_value = col; L.new(ramp.outputs['Color'], mx.inputs[7]); L.new(mx.outputs[2], p.inputs['Base Color'])
    else:
        p.inputs['Base Color'].default_value = col
    if emit is not None:
        p.inputs['Emission Color'].default_value = (*emit, 1.0); p.inputs['Emission Strength'].default_value = strength
    if alpha < 1.0:
        p.inputs['Alpha'].default_value = alpha
        try: m.surface_render_method = 'BLENDED'
        except Exception: pass
    return m


def hexrgb(h):
    h = h.lstrip('#'); s = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in s)    # sRGB -> linear


# ------------------------------------------------------------------ primitives
def _obj(name, me, c, m=None, smooth=True):
    o = bpy.data.objects.new(name, me); coll(c).objects.link(o)
    if m: me.materials.append(m)
    if smooth:
        for poly in me.polygons: poly.use_smooth = True
    return o


def box(name, size, loc, m, c='ROOM', bevel=0.0, rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    bm.to_mesh(me); bm.free()
    o = _obj(name, me, c, m, smooth=bevel > 0); o.location = loc; o.rotation_euler = rot
    if bevel:
        b = o.modifiers.new('bevel', 'BEVEL'); b.width = bevel; b.segments = 4; b.limit_method = 'NONE'
    return o


def cyl(name, r, depth, loc, m, c='ROOM', rot=(0, 0, 0), r2=None, seg=32, bevel=0.0):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=depth)
    bm.to_mesh(me); bm.free()
    o = _obj(name, me, c, m); o.location = loc; o.rotation_euler = rot
    if bevel:
        b = o.modifiers.new('bevel', 'BEVEL'); b.width = bevel; b.segments = 3; b.limit_method = 'ANGLE'
    return o


def sph(name, r, loc, m, c='PERSON', scale=(1, 1, 1), seg=32):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=r); bm.to_mesh(me); bm.free()
    o = _obj(name, me, c, m); o.location = loc; o.scale = scale; return o


def capsule(name, p0, p1, r, m, c='PERSON'):
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0
    o = cyl(name, r, d.length, (p0 + p1) / 2, m, c, seg=20)
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    sph(name + '_a', r, p0, m, c, seg=20); sph(name + '_b', r, p1, m, c, seg=20)
    return o


def plane(name, w, h, loc, m, c='ROOM', rot=(0, 0, 0)):
    return box(name, (w, 0.002, h), loc, m, c, rot=rot)


def light(name, kind, loc, energy, rgb, size=0.5, rot=(0, 0, 0), c='ROOM'):
    ld = bpy.data.lights.new(name, kind); ld.energy = energy; ld.color = rgb
    if kind == 'AREA': ld.size = size
    else: ld.shadow_soft_size = size
    o = bpy.data.objects.new(name, ld); coll(c).objects.link(o); o.location = loc; o.rotation_euler = rot; return o


# ------------------------------------------------------------------ sets
def living_room():
    wood = mat('wood_floor', hexrgb('#5b3b27'), 0.7, 0.12)
    wall = mat('wall', hexrgb('#30231c'), 0.95, 0.08)
    wall2 = mat('wall_side', hexrgb('#2c201a'), 0.95, 0.08)
    box('floor', (12, 12, 0.02), (0, 0, -0.01), wood)
    for i in range(-20, 21):                                            # board seams
        box(f'seam{i}', (12, 0.006, 0.003), (0, i * 0.18, 0.001), mat('seam', hexrgb('#3e271a'), 0.9, 0))
    box('wall_back', (12, 0.1, 4), (0, 1.8, 2), wall)
    box('wall_left', (0.1, 8, 4), (-2.6, -1, 2), wall2)
    box('skirting', (12, 0.04, 0.1), (0, 1.74, 0.05), mat('skirting', hexrgb('#2a1d16'), 0.8, 0))
    # sunset window (right of the back wall), skyline in front of a glowing gradient
    sky = bpy.data.materials.new('sky'); sky.use_nodes = True; N, L = sky.node_tree.nodes, sky.node_tree.links
    em = N.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 0.9
    tc = N.new('ShaderNodeTexCoord'); sep = N.new('ShaderNodeSeparateXYZ'); ramp = N.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*hexrgb('#f2a25c'), 1); ramp.color_ramp.elements[1].color = (*hexrgb('#5a3f6b'), 1)
    L.new(tc.outputs['Generated'], sep.inputs[0]); L.new(sep.outputs['Z'], ramp.inputs['Fac']); L.new(ramp.outputs['Color'], em.inputs['Color'])
    L.new(em.outputs[0], N['Material Output'].inputs['Surface']); N.remove(N['Principled BSDF'])
    box('window_glow', (1.3, 0.02, 1.5), (1.45, 1.86, 1.55), sky)
    sil = mat('skyline', hexrgb('#1c1520'), 0.9, 0)
    for k, (x, h) in enumerate([(0.95, 0.35), (1.15, 0.55), (1.32, 0.3), (1.5, 0.7), (1.7, 0.42), (1.9, 0.5)]):
        box(f'tower{k}', (0.16, 0.01, h), (x, 1.84, 0.8 + h / 2), sil)
    frame = mat('window_frame', hexrgb('#24180f'), 0.7, 0)
    box('wf_l', (0.06, 0.08, 1.6), (0.8, 1.76, 1.55), frame); box('wf_r', (0.06, 0.08, 1.6), (2.1, 1.76, 1.55), frame)
    box('wf_t', (1.36, 0.08, 0.06), (1.45, 1.76, 2.33), frame); box('wf_b', (1.5, 0.14, 0.06), (1.45, 1.74, 0.77), frame)
    box('wf_m', (0.04, 0.06, 1.5), (1.45, 1.77, 1.55), frame); box('wf_h', (1.3, 0.06, 0.04), (1.45, 1.77, 1.62), frame)
    light('window_light', 'AREA', (1.45, 1.65, 1.6), 80, hexrgb('#ffb070'), 1.4, rot=(math.radians(90), 0, 0))
    # floor lamp (left)
    brass = mat('lamp_metal', hexrgb('#3b3128'), 0.5, 0, spec=0.5)
    cyl('lamp_base', 0.16, 0.03, (-1.35, 1.0, 0.015), brass, bevel=0.01)
    cyl('lamp_pole', 0.012, 1.55, (-1.35, 1.0, 0.8), brass)
    shade = mat('lamp_shade', hexrgb('#f1d9b0'), 0.9, 0, emit=hexrgb('#ffc98a'), strength=2.2)
    cyl('lamp_shade', 0.24, 0.32, (-1.35, 1.0, 1.66), shade, r2=0.16)
    light('lamp_bulb', 'POINT', (-1.35, 1.0, 1.62), 160, hexrgb('#ffbe7a'), 0.12)
    light('lamp_pool', 'SPOT', (-1.35, 1.0, 1.5), 260, hexrgb('#ffb46e'), 0.2, rot=(0, 0, 0))
    bpy.data.objects['lamp_pool'].data.spot_size = math.radians(110)
    # sofa (back right), rug, frames, side table
    sofa = mat('sofa', hexrgb('#4c5f45'), 0.95, 0.1)
    box('sofa_base', (1.9, 0.75, 0.38), (1.15, 1.25, 0.25), sofa, bevel=0.08)
    box('sofa_back', (1.9, 0.22, 0.55), (1.15, 1.55, 0.6), sofa, bevel=0.08)
    box('sofa_arm_l', (0.2, 0.75, 0.55), (0.25, 1.25, 0.38), sofa, bevel=0.08)
    box('sofa_arm_r', (0.2, 0.75, 0.55), (2.05, 1.25, 0.38), sofa, bevel=0.08)
    box('cushion', (0.38, 0.14, 0.3), (0.65, 1.32, 0.6), mat('cushion', hexrgb('#b4683f'), 0.95, 0.1), bevel=0.06, rot=(0.25, 0, 0.12))
    cyl('rug', 1.35, 0.012, (0.15, -0.1, 0.006), mat('rug', hexrgb('#a68f73'), 0.98, 0.15), seg=64)
    cyl('rug_ring', 1.2, 0.014, (0.15, -0.1, 0.006), mat('rug_ring', hexrgb('#8a7359'), 0.98, 0.1), seg=64)
    cyl('rug_in', 1.12, 0.016, (0.15, -0.1, 0.006), mat('rug', hexrgb('#a68f73'), 0.98, 0.15), seg=64)
    fr = mat('frame', hexrgb('#1f1610'), 0.6, 0)
    for k, (x, z, w, h, art) in enumerate([(-0.35, 2.0, 0.55, 0.42, '#c48a5c'), (0.25, 1.95, 0.32, 0.32, '#6e7d78')]):
        box(f'frame{k}', (w, 0.04, h), (x, 1.74, z), fr)
        box(f'art{k}', (w - 0.08, 0.01, h - 0.08), (x, 1.715, z), mat(f'art{k}', hexrgb(art), 0.9, 0.2))
    # people light: a soft warm key from front left, a dim lilac fill, a little bounce from above
    light('key', 'AREA', (-1.6, -2.6, 2.5), 220, hexrgb('#ffd9b5'), 2.2, rot=(math.radians(55), 0, math.radians(-32)))
    light('fill', 'AREA', (2.4, -2.2, 1.6), 40, hexrgb('#c9b6d6'), 2.0, rot=(math.radians(70), 0, math.radians(45)))
    light('bounce', 'AREA', (0, -1.0, 3.6), 30, hexrgb('#ffc999'), 4.0)
    cyl('table_top', 0.22, 0.03, (-0.85, 1.25, 0.55), mat('table', hexrgb('#4a3021'), 0.6, 0.05), bevel=0.01)
    cyl('table_leg', 0.025, 0.54, (-0.85, 1.25, 0.27), mat('table', hexrgb('#4a3021'), 0.6, 0.05))


def stage(origin=(30, 0, 0)):
    """Dark stage, built away from the room (origin): floor and back wall in near-black brown, a warm pool of light."""
    dark = mat('stage', hexrgb('#1d1612'), 0.95, 0.06)
    box('stage_floor', (14, 12, 0.02), (0, -2, -0.01), dark, c='STAGE')
    box('stage_wall', (14, 0.05, 6), (0, 3.0, 3), dark, c='STAGE')
    light('stage_key', 'SPOT', (0.3, -0.6, 3.2), 520, hexrgb('#ffbf80'), 0.4, rot=(math.radians(8), 0, 0), c='STAGE')
    bpy.data.objects['stage_key'].data.spot_size = math.radians(55); bpy.data.objects['stage_key'].data.spot_blend = 0.9
    light('stage_fill', 'AREA', (-2, -3, 2), 40, hexrgb('#ffd6a8'), 3, rot=(math.radians(70), 0, math.radians(-30)), c='STAGE')
    for o in coll('STAGE').objects:
        if o.parent is None: o.location += Vector(origin)


# ------------------------------------------------------------------ the lead: woman, 50s, grey bob, teal top
POSES = {
    'stand': dict(pelvis=(0, 0, 0.93), waist=(0, 0, 1.07), chest=(0, 0, 1.25), neck=(0, 0, 1.42), nectop=(0, -0.005, 1.48),
                  L_sh=(0.155, 0, 1.335), L_el=(0.205, 0.01, 1.09), L_wr=(0.235, -0.02, 0.86),
                  R_sh=(-0.155, 0, 1.335), R_el=(-0.205, 0.01, 1.09), R_wr=(-0.235, -0.02, 0.86),
                  L_hip=(0.09, 0, 0.90), L_kn=(0.1, -0.015, 0.5), L_an=(0.1, 0.01, 0.09),
                  R_hip=(-0.09, 0, 0.90), R_kn=(-0.1, -0.015, 0.5), R_an=(-0.1, 0.01, 0.09)),
}
POSES['curl'] = dict(POSES['stand'], R_el=(-0.2, -0.02, 1.09), R_wr=(-0.21, -0.24, 1.22))
EDGES = [('pelvis', 'waist'), ('waist', 'chest'), ('chest', 'neck'), ('neck', 'nectop'),
         ('chest', 'L_sh'), ('L_sh', 'L_el'), ('L_el', 'L_wr'), ('chest', 'R_sh'), ('R_sh', 'R_el'), ('R_el', 'R_wr'),
         ('pelvis', 'L_hip'), ('L_hip', 'L_kn'), ('L_kn', 'L_an'), ('pelvis', 'R_hip'), ('R_hip', 'R_kn'), ('R_kn', 'R_an')]
RADII = dict(pelvis=(0.175, 0.13), waist=(0.155, 0.115), chest=(0.172, 0.12), neck=(0.05, 0.05), nectop=(0.047, 0.047),
             L_sh=(0.068, 0.068), L_el=(0.05, 0.05), L_wr=(0.034, 0.03), R_sh=(0.068, 0.068), R_el=(0.05, 0.05), R_wr=(0.034, 0.03),
             L_hip=(0.1, 0.1), L_kn=(0.075, 0.075), L_an=(0.066, 0.066), R_hip=(0.1, 0.1), R_kn=(0.075, 0.075), R_an=(0.066, 0.066))
ZONE = {('chest', 'neck'): 'skin', ('neck', 'nectop'): 'skin', ('L_el', 'L_wr'): 'skin', ('R_el', 'R_wr'): 'skin',
        ('L_hip', 'L_kn'): 'trousers', ('L_kn', 'L_an'): 'trousers', ('R_hip', 'R_kn'): 'trousers', ('R_kn', 'R_an'): 'trousers',
        ('pelvis', 'L_hip'): 'trousers', ('pelvis', 'R_hip'): 'trousers'}
SKIN, TOP, TROUSERS, HAIR = '#d9a184', '#2e8b88', '#34343f', '#a9a4a2'
HEAD_UP = 0.078                     # head centre above the neck top (lower = shorter neck)


def _xf(p, at, rot_z):
    return Matrix.Translation(Vector(at)) @ Matrix.Rotation(rot_z, 4, 'Z') @ Vector(p)


def _skin_obj(name, pts, edges, radii, m, root=0, levels=2):
    """Smooth tube body from joint points + radii (Skin + Subdivision), applied to a plain mesh."""
    me = bpy.data.meshes.new(name); me.from_pydata(pts, edges, [])
    o = _obj(name, me, 'PERSON', smooth=False)
    o.modifiers.new('skin', 'SKIN'); o.modifiers.new('sub', 'SUBSURF').levels = levels
    for i, r in enumerate(radii):
        o.data.skin_vertices[0].data[i].radius = r; o.data.skin_vertices[0].data[i].use_root = (i == root)
    dg = bpy.context.evaluated_depsgraph_get()
    new = bpy.data.meshes.new_from_object(o.evaluated_get(dg)); o.modifiers.clear(); o.data = new
    o.data.materials.append(m)
    for poly in o.data.polygons: poly.use_smooth = True
    return o


def _hair_bob(name, hc, m):
    """An open shell (not a solid ball): sphere minus the face opening and everything below the jaw, then thickened."""
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=32, radius=1.0)
    kill = []
    for v in bm.verts:
        x, y, z = v.co
        face_hole = y < -0.25 and z < 0.45 and abs(x) < 0.62            # face opening below the fringe
        below_jaw = z < -0.78 + 0.25 * max(0.0, y)                       # bob length: jaw at the front, a touch longer at the back
        if face_hole or below_jaw: kill.append(v)
    bmesh.ops.delete(bm, geom=kill, context='VERTS')
    for v in bm.verts: v.co = Vector((v.co.x * 0.122, v.co.y * 0.128, v.co.z * 0.132))
    bm.to_mesh(me); bm.free()
    o = _obj(name, me, 'PERSON', m); o.location = hc + Vector((0, 0.012, 0.006))
    so = o.modifiers.new('solid', 'SOLIDIFY'); so.thickness = 0.014; so.offset = -1
    o.modifiers.new('sub', 'SUBSURF').levels = 1
    return o


def person(pose='stand', at=(0, 0, 0), rot_z=0.0, name='lead'):
    J = {k: Vector(v) for k, v in POSES[pose].items()}
    m_skin, m_top = mat('skin', hexrgb(SKIN), 0.6, 0.04, spec=0.3), mat('top', hexrgb(TOP), 0.9, 0.08)
    m_tr, m_hair = mat('trousers', hexrgb(TROUSERS), 0.9, 0.06), mat('hair', hexrgb(HAIR), 0.55, 0.1, spec=0.4)
    m_dark, m_shoe = mat('features', hexrgb('#2a1c18'), 0.5, 0), mat('shoes', hexrgb('#e8e2d8'), 0.8, 0.04)
    parts = []
    # top: hem -> waist -> chest -> neck base, with short sleeves; slightly bigger than the trousers so it covers the waistband
    sl = {s: J[s + '_sh'].lerp(J[s + '_el'], 0.6) for s in ('L', 'R')}
    pts = [J['waist'] + Vector((0, 0, -0.085)), J['waist'], J['chest'], J['chest'] + Vector((0, 0, 0.115)),
           J['L_sh'], sl['L'], J['R_sh'], sl['R']]
    parts.append(_skin_obj(name + '_top', pts, [(0, 1), (1, 2), (2, 3), (2, 4), (4, 5), (2, 6), (6, 7)],
                           [(0.185, 0.14), (0.16, 0.12), (0.17, 0.122), (0.06, 0.05), (0.066, 0.066), (0.057, 0.057), (0.066, 0.066), (0.057, 0.057)], m_top))
    # trousers: waistband -> pelvis -> legs (relaxed straight leg)
    pts = [J['waist'] + Vector((0, 0, -0.06)), J['pelvis'], J['L_hip'], J['L_kn'], J['L_an'] + Vector((0, 0, 0.03)),
           J['R_hip'], J['R_kn'], J['R_an'] + Vector((0, 0, 0.03))]
    parts.append(_skin_obj(name + '_trousers', pts, [(0, 1), (1, 2), (2, 3), (3, 4), (1, 5), (5, 6), (6, 7)],
                           [(0.165, 0.122), (0.175, 0.13), (0.1, 0.1), (0.078, 0.078), (0.07, 0.07), (0.1, 0.1), (0.078, 0.078), (0.07, 0.07)], m_tr))
    # skin: neck, forearms (start inside the sleeves)
    pts = [J['chest'] + Vector((0, 0, 0.1)), J['neck'], J['nectop']]
    parts.append(_skin_obj(name + '_neck', pts, [(0, 1), (1, 2)], [(0.046, 0.046), (0.044, 0.044), (0.042, 0.042)], m_skin))
    for s in ('L', 'R'):
        pts = [J[s + '_sh'].lerp(J[s + '_el'], 0.5), J[s + '_el'], J[s + '_wr']]
        parts.append(_skin_obj(f'{name}_arm{s}', pts, [(0, 1), (1, 2)], [(0.045, 0.045), (0.043, 0.043), (0.031, 0.028)], m_skin))
    # head + face (looks toward -Y)
    hc = J['nectop'] + Vector((0, -0.005, HEAD_UP))
    parts.append(sph(name + '_head', 0.104, hc, m_skin, scale=(0.93, 1.0, 1.1)))
    for sx in (-1, 1):
        parts.append(sph(f'{name}_ear{sx}', 0.022, hc + Vector((0.097 * sx, 0.005, -0.005)), m_skin, scale=(0.5, 1, 1)))
        parts.append(sph(f'{name}_eye{sx}', 0.0125, hc + Vector((0.035 * sx, -0.092, 0.012)), m_dark))
        parts.append(sph(f'{name}_hl{sx}', 0.0035, hc + Vector((0.035 * sx + 0.004, -0.104, 0.017)), mat('eye_hl', (1, 1, 1), 0.3, 0)))
        b = sph(f'{name}_brow{sx}', 0.02, hc + Vector((0.037 * sx, -0.093, 0.045)), mat('brow', hexrgb('#7d746f'), 0.8, 0), scale=(1.25, 0.35, 0.3))
        b.rotation_euler = (0, math.radians(8 * sx), 0); parts.append(b)
        parts.append(sph(f'{name}_cheek{sx}', 0.02, hc + Vector((0.054 * sx, -0.083, -0.022)), mat('blush', hexrgb('#d98a78'), 0.7, 0), scale=(1, 0.4, 0.7)))
    parts.append(sph(name + '_nose', 0.0135, hc + Vector((0, -0.104, -0.008)), mat('nose', hexrgb('#cf9177'), 0.6, 0), scale=(0.8, 0.9, 1.25)))
    parts.append(sph(name + '_mouth', 0.017, hc + Vector((0, -0.097, -0.048)), mat('lips', hexrgb('#9d4f4b'), 0.6, 0), scale=(1.2, 0.35, 0.34)))
    parts.append(_hair_bob(name + '_hair', hc, m_hair))
    # hands and shoes
    for s in ('L', 'R'):
        d = (J[s + '_wr'] - J[s + '_el']).normalized()
        parts.append(sph(f'{name}_hand{s}', 0.037, J[s + '_wr'] + d * 0.045, m_skin, scale=(0.8, 0.8, 1.2)))
        parts.append(box(f'{name}_shoe{s}', (0.105, 0.25, 0.08), J[s + '_an'] + Vector((0, -0.07, -0.05)), m_shoe, c='PERSON', bevel=0.035))
    root = bpy.data.objects.new(name, None); coll('PERSON').objects.link(root)
    for p in parts: p.parent = root
    root.location = at; root.rotation_euler = (0, 0, rot_z)
    return root


def xray(pose='stand', at=(0, 0, 0), rot_z=0.0, name='lead', muscles=('thigh', 'arm')):
    """Skeleton + muscles built from the same joints as person(), so they line up with the body."""
    J = {k: Vector(v) for k, v in POSES[pose].items()}
    bone = mat('xray_bone', hexrgb('#fff0d6'), 0.5, 0, emit=hexrgb('#ffe2b0'), strength=2.6)
    musc = mat('xray_muscle', hexrgb('#d8473f'), 0.6, 0, emit=hexrgb('#ff4a3c'), strength=2.4, alpha=0.85)
    parts = []
    def b(n, a, c, r=0.016): parts.append(capsule(f'{name}_x_{n}', a, c, r, bone, 'XRAY'))
    hc = J['nectop'] + Vector((0, -0.005, HEAD_UP))
    parts.append(sph(f'{name}_x_skull', 0.085, hc + Vector((0, 0.005, 0.01)), bone, 'XRAY', scale=(0.9, 1.0, 1.05)))
    for k in range(6): b(f'spine{k}', J['pelvis'].lerp(J['nectop'], k / 6) + Vector((0, 0.03, 0)), J['pelvis'].lerp(J['nectop'], (k + 0.7) / 6) + Vector((0, 0.03, 0)), 0.014)
    for k in range(5):                                                   # ribs as flat rings
        z = J['chest'].z + 0.09 - k * 0.045
        tor = bpy.data.meshes.new(f'rib{k}'); bm = bmesh.new()
        bmesh.ops.create_circle(bm, cap_ends=False, radius=1.0, segments=28)
        for v in bm.verts: v.co = Vector((v.co.x * (0.12 - k * 0.006), v.co.y * 0.08, 0))
        bm.to_mesh(tor); bm.free()
        o = _obj(f'{name}_x_rib{k}', tor, 'XRAY', bone); o.location = (0, 0.01, z)
        sk = o.modifiers.new('skin', 'SKIN'); parts.append(o)
        for v in o.data.skin_vertices[0].data: v.radius = (0.006, 0.006)
    b('clav_L', J['neck'] + Vector((0, 0, -0.04)), J['L_sh'], 0.012); b('clav_R', J['neck'] + Vector((0, 0, -0.04)), J['R_sh'], 0.012)
    b('pelvis', J['L_hip'] + Vector((0.02, 0, 0.06)), J['R_hip'] + Vector((-0.02, 0, 0.06)), 0.03)
    for s in ('L', 'R'):
        b(f'hum{s}', J[s + '_sh'], J[s + '_el']); b(f'rad{s}', J[s + '_el'], J[s + '_wr'], 0.012)
        b(f'fem{s}', J[s + '_hip'], J[s + '_kn'], 0.02); b(f'tib{s}', J[s + '_kn'], J[s + '_an'], 0.016)
        if 'thigh' in muscles:
            parts.append(capsule(f'{name}_x_quad{s}', J[s + '_hip'].lerp(J[s + '_kn'], 0.12), J[s + '_hip'].lerp(J[s + '_kn'], 0.88), 0.05, musc, 'XRAY'))
        if 'arm' in muscles:
            parts.append(capsule(f'{name}_x_bic{s}', J[s + '_sh'].lerp(J[s + '_el'], 0.18), J[s + '_sh'].lerp(J[s + '_el'], 0.85), 0.032, musc, 'XRAY'))
    root = bpy.data.objects.new(name + '_xray', None); coll('XRAY').objects.link(root)
    for p in parts:
        if p.parent is None: p.parent = root
    for o in list(coll('XRAY').objects):
        if o.parent is None and o is not root: o.parent = root
    root.location = at; root.rotation_euler = (0, 0, rot_z)
    coll('XRAY').hide_render = True
    return root


def hand_pos(pose, at, rot_z, side='R'):
    J = POSES[pose]; el, wr = Vector(J[side + '_el']), Vector(J[side + '_wr'])
    return (_xf(wr + (wr - el).normalized() * 0.045, at, rot_z)).to_3d()


def dumbbell(at=(0, 0, 0), rot=(0, 0, 0), name='dumbbell', c='PROPS', scale=1.0):
    iron, grip = mat('iron', hexrgb('#3b3d44'), 0.45, 0.04, spec=0.5), mat('grip', hexrgb('#9a9ca3'), 0.35, 0, spec=0.6)
    root = bpy.data.objects.new(name, None); coll(c).objects.link(root)
    for p in (cyl(name + '_bar', 0.016, 0.34, (0, 0, 0), grip, c, rot=(0, math.radians(90), 0)),
              cyl(name + '_hl', 0.06, 0.075, (-0.13, 0, 0), iron, c, rot=(0, math.radians(90), 0), seg=6, bevel=0.008),
              cyl(name + '_hr', 0.06, 0.075, (0.13, 0, 0), iron, c, rot=(0, math.radians(90), 0), seg=6, bevel=0.008)):
        p.parent = root
    root.location = at; root.rotation_euler = rot; root.scale = (scale,) * 3
    return root


# ------------------------------------------------------------------ camera + render
def camera(loc, target, lens=35.0, name='cam'):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 36
    o = bpy.data.objects.new(name, cd); bpy.context.scene.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = o; return o


def render(path):
    sc = bpy.context.scene; sc.render.film_transparent = False; sc.render.filepath = path
    bpy.ops.render.render(write_still=True); return path


FACE_PARTS = ('_eye', '_hl', '_brow', '_cheek', '_nose', '_mouth', '_hair', '_ear')


def render_layer(path, ghost_rgb='#3a4660', ghost_alpha=0.5, hide=('ROOM', 'STAGE', 'PROPS')):
    """X-ray pass: same camera, transparent film, room hidden, body ghosted (see-through), face and hair hidden so the
    skull reads, skeleton and muscles shown."""
    sc = bpy.context.scene
    saved = {n: coll(n).hide_render for n in ('ROOM', 'STAGE', 'PROPS', 'XRAY')}
    hidden = [o for o in coll('PERSON').objects if any(k in o.name for k in FACE_PARTS) and not o.hide_render]
    for o in hidden: o.hide_render = True
    for n in hide: coll(n).hide_render = True
    coll('XRAY').hide_render = False
    ghost = mat('ghost', hexrgb(ghost_rgb), 0.6, 0, alpha=ghost_alpha)
    swaps = []
    for o in coll('PERSON').objects:
        if o.type == 'MESH' and not o.hide_render:
            swaps.append((o, list(o.data.materials)))
            for i in range(len(o.data.materials)): o.data.materials[i] = ghost
            if not o.data.materials: o.data.materials.append(ghost)
    sc.render.film_transparent = True; sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    for o, ms in swaps:
        for i, m in enumerate(ms): o.data.materials[i] = m
    for n, v in saved.items(): coll(n).hide_render = v
    for o in hidden: o.hide_render = False
    sc.render.film_transparent = False
    return path
