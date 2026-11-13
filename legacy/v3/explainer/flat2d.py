"""flat2d.py: flat 2D (vector, cut-out) animation inside Blender.

Every shape is a filled 2D curve in the picture plane (x right, z up), coloured with a flat emission material, so
renders are crisp, fast and exactly on palette (view transform Standard). Characters are cut-out puppets: shapes
hang on joints (empties) that rotate in the picture plane. Layers sit at small depth offsets (y, negative = nearer),
and backgrounds sit further back, so a moving perspective camera gives real parallax.

    import flat2d as F
    F.setup(frames=150)
    j = F.joint('hips', None, (0, 0.93))
    F.shape('torso', [(-0.2, 0.9), ...], '#2fa39a', j, depth=0.0)
    F.key_rot(j, 30, 12, interp='BACK')          # rotate the joint 12 degrees by frame 30, overshooting
"""
import bpy, math
from mathutils import Vector

_MATS = {}


# ------------------------------------------------------------------ scene
def setup(frames=150, fps=30, res=(1080, 1920), samples=16, bg='#120d0b', motion_blur=True):
    sc = bpy.context.scene
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    for c in list(bpy.data.collections): bpy.data.collections.remove(c)
    for blk in (bpy.data.curves, bpy.data.materials, bpy.data.actions, bpy.data.cameras, bpy.data.meshes):
        for x in list(blk):
            if x.users == 0: blk.remove(x)
    _MATS.clear()
    sc.render.engine = 'BLENDER_EEVEE'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.render.fps = fps; sc.frame_start, sc.frame_end = 1, frames
    for k, v in dict(taa_render_samples=samples, use_raytracing=False, use_gtao=False, use_shadows=False).items():
        try: setattr(sc.eevee, k, v)
        except Exception: pass
    sc.view_settings.view_transform = 'Standard'
    try: sc.view_settings.look = 'None'
    except Exception: pass
    sc.view_settings.exposure = 0.0; sc.view_settings.gamma = 1.0
    sc.render.use_motion_blur = motion_blur
    try: sc.render.motion_blur_shutter = 0.45
    except Exception: pass
    w = bpy.data.worlds.get('World') or bpy.data.worlds.new('World'); sc.world = w
    try: w.use_nodes = True
    except Exception: pass
    bgn = w.node_tree.nodes.get('Background')
    if bgn: bgn.inputs[0].default_value = (*lin(bg), 1); bgn.inputs[1].default_value = 1.0
    sc.render.film_transparent = False
    return sc


def lin(hexrgb):
    h = hexrgb.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)


# ------------------------------------------------------------------ materials
def _base_mat(name):
    m = bpy.data.materials.new(name)
    try: m.use_nodes = True
    except Exception: pass
    nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    try: m.surface_render_method = 'DITHERED'
    except Exception: pass
    return m, nt


def flat(hexrgb):
    """Flat colour; the object's alpha (obj.color[3]) fades it, so any shape can fade in and out."""
    key = ('flat', hexrgb)
    if key in _MATS: return _MATS[key]
    m, nt = _base_mat(f'flat_{hexrgb}')
    out = nt.nodes.new('ShaderNodeOutputMaterial'); em = nt.nodes.new('ShaderNodeEmission')
    tr = nt.nodes.new('ShaderNodeBsdfTransparent'); mix = nt.nodes.new('ShaderNodeMixShader'); oi = nt.nodes.new('ShaderNodeObjectInfo')
    em.inputs['Color'].default_value = (*lin(hexrgb), 1); em.inputs['Strength'].default_value = 1.0
    nt.links.new(oi.outputs['Alpha'], mix.inputs['Fac']); nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], out.inputs['Surface'])
    _MATS[key] = m; return m


def glow_mat(hexrgb, power=1.6):
    """Soft radial glow (bright centre fading to nothing at the shape's edge), times the object's alpha."""
    key = ('glow', hexrgb, power)
    if key in _MATS: return _MATS[key]
    m, nt = _base_mat(f'glow_{hexrgb}')
    N, L = nt.nodes, nt.links
    out = N.new('ShaderNodeOutputMaterial'); em = N.new('ShaderNodeEmission'); tr = N.new('ShaderNodeBsdfTransparent')
    mix = N.new('ShaderNodeMixShader'); oi = N.new('ShaderNodeObjectInfo'); tc = N.new('ShaderNodeTexCoord')
    mp = N.new('ShaderNodeMapping'); mp.inputs['Location'].default_value = (-1, -1, 0); mp.inputs['Scale'].default_value = (2, 2, 1)
    gr = N.new('ShaderNodeTexGradient'); gr.gradient_type = 'SPHERICAL'
    pw = N.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = power
    mul = N.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'
    em.inputs['Color'].default_value = (*lin(hexrgb), 1)
    L.new(tc.outputs['Generated'], mp.inputs['Vector']); L.new(mp.outputs[0], gr.inputs['Vector'])
    L.new(gr.outputs['Fac'], pw.inputs[0]); L.new(pw.outputs[0], mul.inputs[0]); L.new(oi.outputs['Alpha'], mul.inputs[1])
    L.new(mul.outputs[0], mix.inputs['Fac']); L.new(tr.outputs[0], mix.inputs[1]); L.new(em.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], out.inputs['Surface'])
    _MATS[key] = m; return m


MODE = 'flat'          # 'flat' = pure flat colour (2D world); 'lit' = takes the 3D world's lights (2D character in a 3D world)
LIT = dict(shadow=(0.58, 0.55, 0.80), mid=(0.88, 0.85, 0.94), lit=(1.08, 1.0, 0.88), steps=(0.12, 0.2, 0.42, 0.5),
           tint=0.35, self_em=0.14, gain=1.0)


def lit(hexrgb):
    """Flat colour that takes the scene's light like the skill's toon materials (look.toon_mat): the light level picks
    one of three cel steps (cool purple shadow, neutral mid, warm lit), tinted by the light's colour, plus a little
    self-light so faces stay readable. The object's alpha fades it."""
    key = ('lit', hexrgb)
    if key in _MATS: return _MATS[key]
    m, nt = _base_mat(f'lit_{hexrgb}')
    N, Ln = nt.nodes, nt.links
    out = N.new('ShaderNodeOutputMaterial'); em = N.new('ShaderNodeEmission'); tr = N.new('ShaderNodeBsdfTransparent')
    mix = N.new('ShaderNodeMixShader'); oi = N.new('ShaderNodeObjectInfo')
    dif = N.new('ShaderNodeBsdfDiffuse'); dif.inputs['Color'].default_value = (1, 1, 1, 1)
    s2r = N.new('ShaderNodeShaderToRGB'); bw = N.new('ShaderNodeRGBToBW')
    g = N.new('ShaderNodeMath'); g.operation = 'MULTIPLY'; g.inputs[1].default_value = LIT['gain']
    ramp = N.new('ShaderNodeValToRGB'); els = ramp.color_ramp.elements
    a, b, c, d = LIT['steps']
    spec = [(0.0, LIT['shadow']), (a, LIT['shadow']), (b, LIT['mid']), (c, LIT['mid']), (d, LIT['lit'])]
    while len(els) < len(spec): els.new(0.5)
    for e, (p, col) in zip(els, spec): e.position = p; e.color = (*col, 1)
    # light colour tint = lit white diffuse / its luminance
    mx = N.new('ShaderNodeMath'); mx.operation = 'MAXIMUM'; mx.inputs[1].default_value = 0.02
    inv = N.new('ShaderNodeMath'); inv.operation = 'DIVIDE'; inv.inputs[0].default_value = 1.0
    sc = N.new('ShaderNodeVectorMath'); sc.operation = 'SCALE'
    tn = N.new('ShaderNodeMix'); tn.data_type = 'RGBA'; tn.inputs[0].default_value = LIT['tint']; tn.inputs[6].default_value = (1, 1, 1, 1)
    base = N.new('ShaderNodeRGB'); base.outputs[0].default_value = (*lin(hexrgb), 1)
    m1 = N.new('ShaderNodeMix'); m1.data_type = 'RGBA'; m1.blend_type = 'MULTIPLY'; m1.inputs[0].default_value = 1.0
    m2 = N.new('ShaderNodeMix'); m2.data_type = 'RGBA'; m2.blend_type = 'MULTIPLY'; m2.inputs[0].default_value = 1.0
    se = N.new('ShaderNodeMix'); se.data_type = 'RGBA'; se.blend_type = 'ADD'; se.inputs[0].default_value = LIT['self_em']
    Ln.new(dif.outputs[0], s2r.inputs[0]); Ln.new(s2r.outputs[0], bw.inputs[0]); Ln.new(bw.outputs[0], g.inputs[0]); Ln.new(g.outputs[0], ramp.inputs['Fac'])
    Ln.new(bw.outputs[0], mx.inputs[0]); Ln.new(mx.outputs[0], inv.inputs[1]); Ln.new(s2r.outputs[0], sc.inputs[0]); Ln.new(inv.outputs[0], sc.inputs['Scale'])
    Ln.new(sc.outputs[0], tn.inputs[7])
    Ln.new(base.outputs[0], m1.inputs[6]); Ln.new(ramp.outputs['Color'], m1.inputs[7])
    Ln.new(m1.outputs[2], m2.inputs[6]); Ln.new(tn.outputs[2], m2.inputs[7])
    Ln.new(m2.outputs[2], se.inputs[6]); Ln.new(base.outputs[0], se.inputs[7])
    Ln.new(se.outputs[2], em.inputs['Color'])
    Ln.new(oi.outputs['Alpha'], mix.inputs['Fac']); Ln.new(tr.outputs[0], mix.inputs[1]); Ln.new(em.outputs[0], mix.inputs[2])
    Ln.new(mix.outputs[0], out.inputs['Surface'])
    _MATS[key] = m; return m


def surface(hexrgb):
    return lit(hexrgb) if MODE == 'lit' else flat(hexrgb)


def glow(name, cx, cz, rx, rz, hexrgb, parent=None, depth=0.0, power=1.6, alpha=1.0):
    """A soft radial glow centred on (cx, cz): bright in the middle, nothing at the rim. Blended (no dither noise)."""
    m, nt = _base_mat(f'glow_{name}')
    try: m.surface_render_method = 'BLENDED'
    except Exception: pass
    N, L = nt.nodes, nt.links
    out = N.new('ShaderNodeOutputMaterial'); em = N.new('ShaderNodeEmission'); tr = N.new('ShaderNodeBsdfTransparent')
    mix = N.new('ShaderNodeMixShader'); oi = N.new('ShaderNodeObjectInfo'); tc = N.new('ShaderNodeTexCoord')
    mp = N.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (1 / rx, 1 / rz, 1); mp.inputs['Location'].default_value = (-cx / rx, -cz / rz, 0)
    gr = N.new('ShaderNodeTexGradient'); gr.gradient_type = 'SPHERICAL'
    pw = N.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = power
    mul = N.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'
    em.inputs['Color'].default_value = (*lin(hexrgb), 1)
    L.new(tc.outputs['Object'], mp.inputs['Vector']); L.new(mp.outputs[0], gr.inputs['Vector'])
    L.new(gr.outputs['Fac'], pw.inputs[0]); L.new(pw.outputs[0], mul.inputs[0]); L.new(oi.outputs['Alpha'], mul.inputs[1])
    L.new(mul.outputs[0], mix.inputs['Fac']); L.new(tr.outputs[0], mix.inputs[1]); L.new(em.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], out.inputs['Surface'])
    return shape(name, ellipse_pts(cx, cz, rx, rz, 24), hexrgb, parent, depth, smooth=False, mat=m, alpha=alpha)


def vgrad_mat(stops):
    """Vertical gradient for skies and windows: stops = [(0.0, '#hex'), (1.0, '#hex')], 0 = bottom of the shape."""
    key = ('vgrad', tuple(stops))
    if key in _MATS: return _MATS[key]
    m, nt = _base_mat('vgrad')
    N, L = nt.nodes, nt.links
    out = N.new('ShaderNodeOutputMaterial'); em = N.new('ShaderNodeEmission'); tc = N.new('ShaderNodeTexCoord')
    sep = N.new('ShaderNodeSeparateXYZ'); ramp = N.new('ShaderNodeValToRGB')
    els = ramp.color_ramp.elements
    while len(els) < len(stops): els.new(0.5)
    for e, (p, h) in zip(els, stops): e.position = p; e.color = (*lin(h), 1)
    L.new(tc.outputs['Generated'], sep.inputs[0]); L.new(sep.outputs['Y'], ramp.inputs['Fac'])
    L.new(ramp.outputs['Color'], em.inputs['Color']); L.new(em.outputs[0], out.inputs['Surface'])
    _MATS[key] = m; return m


# ------------------------------------------------------------------ geometry
def joint(name, parent, pivot, depth=0.0):
    """An empty at `pivot` (x, z, in the character's rest coordinates) that rotates in the picture plane."""
    e = bpy.data.objects.new(name, None); bpy.context.scene.collection.objects.link(e)
    e.empty_display_size = 0.03; e.rotation_mode = 'XYZ'
    e['pivot'] = pivot
    if parent:
        e.parent = parent; pp = parent['pivot']
        e.location = (pivot[0] - pp[0], depth, pivot[1] - pp[1])
    else:
        e.location = (pivot[0], depth, pivot[1])
    e.matrix_parent_inverse.identity()
    return e


def _curve(name, splines, smooth):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '2D'; cu.fill_mode = 'BOTH'; cu.resolution_u = 14
    for pts in splines:
        if smooth:
            sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
            for bp, (x, z) in zip(sp.bezier_points, pts):
                bp.co = (x, z, 0); bp.handle_left_type = bp.handle_right_type = 'AUTO'
        else:
            sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
            for p, (x, z) in zip(sp.points, pts): p.co = (x, z, 0, 1)
        sp.use_cyclic_u = True
    return cu


def shape(name, pts, color, parent=None, depth=0.0, smooth=True, holes=(), mat=None, alpha=1.0):
    """A filled shape through `pts` [(x, z), ...] in absolute rest coordinates, hung on joint `parent`."""
    cu = _curve(name, [pts, *holes], smooth)
    cu.materials.append(mat or surface(color))
    ob = bpy.data.objects.new(name, cu); bpy.context.scene.collection.objects.link(ob)
    ob['hex'] = color
    ob.rotation_euler = (math.pi / 2, 0, 0)
    if parent is not None:
        ob.parent = parent; px, pz = parent['pivot']
        ob.location = (-px, depth, -pz); ob.matrix_parent_inverse.identity()
    else:
        ob.location = (0, depth, 0)
    ob.color = (1, 1, 1, alpha)
    return ob


def copy_shape(src, name, color, parent, depth, alpha=1.0):
    """Same outline as src, another colour, hung on `parent` at `depth` (e.g. an X-ray ghost of a body part)."""
    cu = src.data.copy(); cu.materials.clear(); cu.materials.append(flat(color))
    ob = bpy.data.objects.new(name, cu); bpy.context.scene.collection.objects.link(ob)
    ob.rotation_euler = (math.pi / 2, 0, 0)
    ob.parent = parent; px, pz = parent['pivot']; ob.location = (-px, depth, -pz); ob.matrix_parent_inverse.identity()
    ob.color = (1, 1, 1, alpha)
    return ob


def ellipse_pts(cx, cz, rx, rz, n=16, a0=0.0):
    return [(cx + rx * math.cos(a0 + 2 * math.pi * i / n), cz + rz * math.sin(a0 + 2 * math.pi * i / n)) for i in range(n)]


def ellipse(name, cx, cz, rx, rz, color, parent=None, depth=0.0, **kw):
    return shape(name, ellipse_pts(cx, cz, rx, rz, 8), color, parent, depth, **kw)


def rrect_pts(x0, z0, x1, z1, r, n=5):
    r = min(r, (x1 - x0) / 2, (z1 - z0) / 2); pts = []
    for cx, cz, a in ((x1 - r, z1 - r, 0), (x0 + r, z1 - r, 90), (x0 + r, z0 + r, 180), (x1 - r, z0 + r, 270)):
        for i in range(n + 1):
            t = math.radians(a + 90 * i / n); pts.append((cx + r * math.cos(t), cz + r * math.sin(t)))
    return pts


def rrect(name, x0, z0, x1, z1, r, color, parent=None, depth=0.0, **kw):
    return shape(name, rrect_pts(x0, z0, x1, z1, r), color, parent, depth, smooth=False, **kw)


def limb_pts(p0, p1, w0, w1, n=8):
    """A tapered capsule from p0 (width w0) to p1 (width w1)."""
    (x0, z0), (x1, z1) = p0, p1; dx, dz = x1 - x0, z1 - z0; L = math.hypot(dx, dz) or 1e-6
    ux, uz = dx / L, dz / L; nx, nz = -uz, ux; a = math.atan2(uz, ux); pts = []
    for i in range(n + 1):                                     # end cap at p1
        t = a - math.pi / 2 + math.pi * i / n; pts.append((x1 + w1 / 2 * math.cos(t), z1 + w1 / 2 * math.sin(t)))
    for i in range(n + 1):                                     # start cap at p0
        t = a + math.pi / 2 + math.pi * i / n; pts.append((x0 + w0 / 2 * math.cos(t), z0 + w0 / 2 * math.sin(t)))
    return pts


def limb(name, p0, p1, w0, w1, color, parent=None, depth=0.0, **kw):
    return shape(name, limb_pts(p0, p1, w0, w1), color, parent, depth, smooth=False, **kw)


def ring(name, cx, cz, r, width, color, parent=None, depth=0.0, **kw):
    return shape(name, ellipse_pts(cx, cz, r, r, 24), color, parent, depth, smooth=False,
                 holes=[ellipse_pts(cx, cz, r - width, r - width, 24)[::-1]], **kw)


# ------------------------------------------------------------------ keys
def _fcurves(obj):
    ad = obj.animation_data
    if not ad or not ad.action: return []
    try: return list(ad.action.fcurves)
    except AttributeError:
        from bpy_extras import anim_utils
        cb = anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot)
        return list(cb.fcurves) if cb else []


def key(obj, path, value, frame, interp='BEZIER', easing='AUTO', index=-1):
    """Set obj.<path> (or one index of it) and key it; interp/easing shape the segment that STARTS at this key."""
    if index >= 0:
        getattr(obj, path)[index] = value
    else:
        setattr(obj, path, value)
    obj.keyframe_insert(path, index=index, frame=frame)
    for fc in _fcurves(obj):
        if fc.data_path == path and (index < 0 or fc.array_index == index):
            for kp in fc.keyframe_points:
                if abs(kp.co.x - frame) < 0.01: kp.interpolation = interp; kp.easing = easing


def now(obj, path, frame, index=None):
    bpy.context.scene.frame_set(frame)
    v = getattr(obj, path)
    return v[index] if index is not None else v


def key_rot(j, frame, deg, f0=None, interp='BEZIER', easing='AUTO'):
    """Rotate joint j (picture plane) to `deg` at `frame`; if f0, hold its value at f0 and move from there."""
    if f0 is not None: key(j, 'rotation_euler', now(j, 'rotation_euler', f0, 1), f0, interp, easing, 1)
    key(j, 'rotation_euler', math.radians(deg), frame, 'BEZIER', 'AUTO', 1)


def key_alpha(obj, frame, a, f0=None, interp='BEZIER'):
    if f0 is not None: key(obj, 'color', now(obj, 'color', f0, 3), f0, interp, 'AUTO', 3)
    key(obj, 'color', a, frame, 'BEZIER', 'AUTO', 3)


def show_only(objs, visible, frame):
    """Swap drawings (eyes, mouths): `visible` gets scale 1, the rest scale 0, from `frame` on (no in-betweens)."""
    for o in objs:
        s = 1.0 if o is visible or (isinstance(visible, (list, tuple)) and o in visible) else 0.0
        key(o, 'scale', (s, s, s), frame, 'CONSTANT')


def ik2(shoulder, l1, l2, target, outward=-1):
    """2-bone IK in the picture plane. Returns (upper, fore) joint angles in degrees for this rig's convention
    (a joint angle rotates the hanging-down direction; +90 points the limb to -x). outward: -1 = the elbow bends
    towards -x (screen-left arm), +1 = towards +x."""
    sx, sz = shoulder; tx, tz = target
    d = min(max(math.hypot(tx - sx, tz - sz), 1e-4), l1 + l2 - 1e-4)
    a = math.atan2(tz - sz, tx - sx)
    b = math.acos(max(-1, min(1, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))))
    p1 = max((a + b, a - b), key=lambda p: outward * math.cos(p))
    ex, ez = sx + l1 * math.cos(p1), sz + l1 * math.sin(p1)
    p2 = math.atan2(tz - ez, tx - ex)
    up = -(math.degrees(p1) + 90); fore = -(math.degrees(p2) + 90) - up
    wrap = lambda x: (x + 180) % 360 - 180
    return wrap(up), wrap(fore)


def bake_camera(src, name='cam_baked'):
    """Copy an animated camera (moves + Camera Shakify shake) into plain keys, so a background render needs no add-on."""
    sc = bpy.context.scene
    cd = bpy.data.cameras.new(name)
    for a in ('sensor_fit', 'sensor_height', 'sensor_width', 'clip_start', 'clip_end', 'lens'):
        setattr(cd, a, getattr(src.data, a))
    cam = bpy.data.objects.new(name, cd); sc.collection.objects.link(cam)
    prev = None
    for f in range(sc.frame_start - 1, sc.frame_end + 2):      # one frame either side, for motion blur
        sc.frame_set(f)
        loc, rot, _ = src.matrix_world.decompose()
        e = rot.to_euler('XYZ', prev) if prev else rot.to_euler('XYZ'); prev = e
        cam.location = loc; cam.rotation_euler = e
        cam.keyframe_insert('location', frame=f); cam.keyframe_insert('rotation_euler', frame=f)
        cd.lens = src.data.lens; cd.keyframe_insert('lens', frame=f)
    sc.camera = cam
    return cam
