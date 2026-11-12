"""rig.py: the animated lead for the anatomy-explainer style. Needs kit.py loaded first (same namespace).

The skeleton and the motion come from the Quaternius Universal Animation Library (CC0, free): a 53-bone humanoid rig
in T-pose with 46 motions (Idle_Talking_Loop, Idle_Loop, Walk_Loop, Sitting_Talking_Loop, Interact, PickUp_Table, ...).
We build our own character around that rig (same look as kit.person: woman, 50s, grey bob, teal top), copy the bone
weights from the library's mannequin (nearest vertices), and parent face, hair, hands and shoes to their bones.
Life on top of the motion clips: blinks, a talking mouth driven by the voice, a custom arm curl, camera moves.

  rig = load_rig(glb)                              import once per scene; the library mannequin stays hidden (weight source)
  lead = build_lead(rig)                           our body on the rig (rest pose), weights copied, parts on bones
  build_xray_on(rig)                               skeleton + muscles parented to bones (collection XRAY)
  play(rig, 'Idle_Talking_Loop', start, end)       a looping clip on the NLA
  curl(rig, start, end, reps)                      right-arm biceps curls layered on top (COMBINE)
  blinks(lead, frames) / mouth(lead, cues)         face animation (object scale keys)
  place(rig, at, rot_z, scale)                     where she stands
"""
import bpy, math
from mathutils import Vector, Matrix, kdtree

FPS = 30


def load_rig(glb):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=glb)
    new = [o for o in bpy.data.objects if o not in before]
    rig = next(o for o in new if o.type == 'ARMATURE')
    for o in new:
        if o.type == 'MESH' and o.name.startswith('Icosphere'): bpy.data.objects.remove(o, do_unlink=True)
    man = next(o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith('Mannequin'))
    man.hide_render = True; man.hide_viewport = True
    for o in [rig, man]: link(o, 'PERSON')
    rig.animation_data_create(); rig.animation_data.action = None
    rig['mannequin'] = man.name
    return rig


def _b(rig, name, end='head'):
    b = rig.data.bones[name]; return rig.matrix_world @ (b.head_local if end == 'head' else b.tail_local)


def _copy_weights(obj, rig, k=6, allow=None):
    """Give obj the mannequin's bone weights, from its k nearest mannequin vertices (inverse-distance blend).
    allow: bone-name fragments this part may use (for example ('hips', 'thigh', 'shin', 'foot') for trousers).
    Left/right are kept apart: a vertex on the left of the body (rest pose, x > 0) never takes .R weights."""
    man = bpy.data.objects[rig['mannequin']]; mw = man.matrix_world
    kd = kdtree.KDTree(len(man.data.vertices))
    for i, v in enumerate(man.data.vertices): kd.insert(mw @ v.co, i)
    kd.balance()
    names = {g.index: g.name for g in man.vertex_groups if g.name.startswith('DEF-')}
    groups = {}
    ow = obj.matrix_world
    for v in obj.data.vertices:
        acc = {}
        hits = kd.find_n(ow @ v.co, k)
        tot = 0.0
        xl = (rig.matrix_world.inverted() @ (ow @ v.co)).x
        for co, idx, dist in hits:
            w0 = 1.0 / max(dist, 1e-4) ** 2; tot += w0
            for g in man.data.vertices[idx].groups:
                n = names.get(g.group)
                if not n: continue
                if allow and not any(a in n for a in allow): continue
                if (xl > 0.015 and n.endswith('.R')) or (xl < -0.015 and n.endswith('.L')): continue
                acc[n] = acc.get(n, 0.0) + g.weight * w0
        s = sum(acc.values())
        if s <= 0: continue
        for n, w in acc.items():
            if w / s < 0.02: continue
            if n not in groups: groups[n] = obj.vertex_groups.new(name=n)
            groups[n].add([v.index], w / s, 'REPLACE')
    mod = obj.modifiers.new('rig', 'ARMATURE'); mod.object = rig
    obj.parent = rig; obj.matrix_parent_inverse = rig.matrix_world.inverted()


def _to_bone(obj, rig, bone):
    """Rigid child of a bone that keeps its current world position. The parent inverse is computed from the bone's
    rest matrix (world = rig @ bone rest @ tail offset), so it does not depend on the depsgraph or the current pose."""
    w = obj.matrix_basis.copy() if obj.parent is None else obj.matrix_world.copy()   # new objects: matrix_world is not computed yet
    b = rig.data.bones[bone]
    pm = rig.matrix_world @ b.matrix_local @ Matrix.Translation((0, b.length, 0))
    obj.parent = rig; obj.parent_type = 'BONE'; obj.parent_bone = bone
    obj.matrix_parent_inverse = pm.inverted()
    obj.matrix_basis = w


def build_lead(rig, name='lead'):
    rig.data.pose_position = 'REST'; bpy.context.view_layer.update()
    m_skin, m_top = mat('skin', hexrgb(SKIN), 0.6, 0.04, spec=0.3), mat('top', hexrgb(TOP), 0.9, 0.08)
    m_tr, m_hair = mat('trousers', hexrgb(TROUSERS), 0.9, 0.06), mat('hair', hexrgb(HAIR), 0.55, 0.1, spec=0.4)
    m_dark, m_shoe = mat('features', hexrgb('#2a1c18'), 0.5, 0), mat('shoes', hexrgb('#e8e2d8'), 0.8, 0.04)
    B = lambda n, e='head': _b(rig, n, e)
    hips, waist, chest, upper, neck0, head0 = B('DEF-hips'), B('DEF-spine.001'), B('DEF-spine.003'), B('DEF-spine.003', 'tail'), B('DEF-neck'), B('DEF-head')
    deform = []
    # top: hem -> waist -> chest -> collar, sleeves to 60% of the upper arm
    sh = {s: B(f'DEF-upper_arm.{s}') for s in 'LR'}; el = {s: B(f'DEF-forearm.{s}') for s in 'LR'}; wr = {s: B(f'DEF-hand.{s}') for s in 'LR'}
    inner = {s: chest.lerp(sh[s], 0.45) + Vector((0, 0, 0.1)) for s in 'LR'}
    pts = [waist + Vector((0, 0, -0.085)), waist, chest, upper - Vector((0, 0, 0.02)), inner['L'], sh['L'], sh['L'].lerp(el['L'], 0.6), inner['R'], sh['R'], sh['R'].lerp(el['R'], 0.6)]
    deform.append(_skin_obj(name + '_top', pts, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (3, 7), (7, 8), (8, 9)],
                            [(0.19, 0.145), (0.165, 0.125), (0.18, 0.13), (0.11, 0.08), (0.08, 0.075), (0.07, 0.07), (0.06, 0.06), (0.08, 0.075), (0.07, 0.07), (0.06, 0.06)], m_top, levels=2))
    # trousers
    th = {s: B(f'DEF-thigh.{s}') for s in 'LR'}; kn = {s: B(f'DEF-shin.{s}') for s in 'LR'}; an = {s: B(f'DEF-foot.{s}') for s in 'LR'}
    pts = [waist + Vector((0, 0, -0.06)), hips, th['L'], kn['L'], an['L'] + Vector((0, 0, 0.005)), th['R'], kn['R'], an['R'] + Vector((0, 0, 0.005))]
    deform.append(_skin_obj(name + '_trousers', pts, [(0, 1), (1, 2), (2, 3), (3, 4), (1, 5), (5, 6), (6, 7)],
                            [(0.165, 0.122), (0.172, 0.13), (0.097, 0.097), (0.074, 0.074), (0.066, 0.066), (0.097, 0.097), (0.074, 0.074), (0.066, 0.066)], m_tr, levels=2))
    # skin: neck and forearms
    deform.append(_skin_obj(name + '_neck', [upper - Vector((0, 0, 0.04)), neck0, head0 + Vector((0, 0, 0.02))], [(0, 1), (1, 2)],
                            [(0.05, 0.05), (0.047, 0.047), (0.045, 0.045)], m_skin))
    for s in 'LR':
        deform.append(_skin_obj(f'{name}_arm{s}', [sh[s].lerp(el[s], 0.5), el[s], wr[s]], [(0, 1), (1, 2)], [(0.046, 0.046), (0.043, 0.043), (0.031, 0.028)], m_skin))
    allow = {name + '_top': ('spine', 'hips', 'shoulder', 'upper_arm', 'neck'), name + '_trousers': ('hips', 'spine.001', 'thigh', 'shin', 'foot'),
             name + '_neck': ('spine.003', 'neck', 'head'), name + '_armL': ('upper_arm', 'forearm', 'hand'), name + '_armR': ('upper_arm', 'forearm', 'hand')}
    for o in deform: _copy_weights(o, rig, allow=allow.get(o.name))
    # head, face, hair: rigid on the head bone
    hc = head0 + Vector((0, -0.012, 0.085))
    rigid = [sph(name + '_head', 0.104, hc, m_skin, scale=(0.93, 1.0, 1.1))]
    for sx in (-1, 1):
        rigid.append(sph(f'{name}_ear{sx}', 0.022, hc + Vector((0.097 * sx, 0.005, -0.005)), m_skin, scale=(0.5, 1, 1)))
        rigid.append(sph(f'{name}_eye{sx}', 0.0125, hc + Vector((0.035 * sx, -0.092, 0.012)), m_dark))
        rigid.append(sph(f'{name}_hl{sx}', 0.0035, hc + Vector((0.035 * sx + 0.004, -0.104, 0.017)), mat('eye_hl', (1, 1, 1), 0.3, 0)))
        b = sph(f'{name}_brow{sx}', 0.02, hc + Vector((0.037 * sx, -0.093, 0.045)), mat('brow', hexrgb('#7d746f'), 0.8, 0), scale=(1.25, 0.35, 0.3))
        b.rotation_euler = (0, math.radians(8 * sx), 0); rigid.append(b)
        rigid.append(sph(f'{name}_cheek{sx}', 0.02, hc + Vector((0.054 * sx, -0.083, -0.022)), mat('blush', hexrgb('#d98a78'), 0.7, 0), scale=(1, 0.4, 0.7)))
    rigid.append(sph(name + '_nose', 0.0135, hc + Vector((0, -0.104, -0.008)), mat('nose', hexrgb('#cf9177'), 0.6, 0), scale=(0.8, 0.9, 1.25)))
    rigid.append(sph(name + '_mouth', 0.017, hc + Vector((0, -0.097, -0.048)), mat('lips', hexrgb('#9d4f4b'), 0.6, 0), scale=(1.2, 0.35, 0.34)))
    rigid.append(_hair_bob(name + '_hair', hc, m_hair))
    for o in rigid: _to_bone(o, rig, 'DEF-head')
    # hands (mitten + thumb) and shoes
    for s, sx in (('L', 1), ('R', -1)):
        d = (B(f'DEF-hand.{s}', 'tail') - wr[s]).normalized()
        hand = sph(f'{name}_hand{s}', 0.038, wr[s] + d * 0.05, m_skin, scale=(1.25, 0.6, 0.95)); _to_bone(hand, rig, f'DEF-hand.{s}')
        thumb = sph(f'{name}_thumb{s}', 0.014, wr[s] + d * 0.035 + Vector((0, -0.03, -0.012)), m_skin, scale=(1.6, 1, 1)); _to_bone(thumb, rig, f'DEF-hand.{s}')
        shoe = box(f'{name}_shoe{s}', (0.105, 0.26, 0.09), an[s] + Vector((0, -0.075, -0.045)), m_shoe, c='PERSON', bevel=0.035)
        _to_bone(shoe, rig, f'DEF-foot.{s}')
    rig.data.pose_position = 'POSE'
    return rig


def build_xray_on(rig, muscles=('thigh', 'arm'), name='lead'):
    """Glowing skeleton + muscles, each piece a rigid child of its bone (so it moves with the motion)."""
    rig.data.pose_position = 'REST'; bpy.context.view_layer.update()
    bone = mat('xray_bone', hexrgb('#fff0d6'), 0.5, 0, emit=hexrgb('#ffe2b0'), strength=2.6)
    musc = mat('xray_muscle', hexrgb('#d8473f'), 0.6, 0, emit=hexrgb('#ff4a3c'), strength=2.4, alpha=0.85)
    B = lambda n, e='head': _b(rig, n, e)
    def cap(n, a, b, r, m, parent):
        before = set(coll('XRAY').objects)
        capsule(f'{name}_x_{n}', a, b, r, m, 'XRAY')
        for o in set(coll('XRAY').objects) - before: _to_bone(o, rig, parent)
    hc = B('DEF-head') + Vector((0, -0.005, 0.085))
    sk = sph(f'{name}_x_skull', 0.075, hc, bone, 'XRAY', scale=(0.88, 1.0, 1.05)); _to_bone(sk, rig, 'DEF-head')
    for bn in ('DEF-spine.001', 'DEF-spine.002', 'DEF-spine.003', 'DEF-neck'):
        cap(bn, B(bn) + Vector((0, 0.035, 0)), B(bn, 'tail') + Vector((0, 0.035, 0)), 0.014, bone, bn)
    for k in range(5):
        z = B('DEF-spine.003').z + 0.1 - k * 0.045; me = bpy.data.meshes.new(f'rib{k}')
        import bmesh as _bm
        bm = _bm.new(); _bm.ops.create_circle(bm, cap_ends=False, radius=1.0, segments=28)
        for v in bm.verts: v.co = Vector((v.co.x * (0.12 - k * 0.006), v.co.y * 0.08, 0))
        bm.to_mesh(me); bm.free()
        o = _obj(f'{name}_x_rib{k}', me, 'XRAY', bone); o.location = (0, 0.01, z)
        o.modifiers.new('skin', 'SKIN')
        for v in o.data.skin_vertices[0].data: v.radius = (0.006, 0.006)
        _to_bone(o, rig, 'DEF-spine.003' if k < 3 else 'DEF-spine.002')
    cap('pelvis', B('DEF-thigh.L') + Vector((0.02, 0, 0.06)), B('DEF-thigh.R') + Vector((-0.02, 0, 0.06)), 0.03, bone, 'DEF-hips')
    for s in 'LR':
        cap(f'clav{s}', B('DEF-spine.003', 'tail') + Vector((0, 0, -0.04)), B(f'DEF-upper_arm.{s}'), 0.012, bone, f'DEF-shoulder.{s}')
        cap(f'hum{s}', B(f'DEF-upper_arm.{s}'), B(f'DEF-forearm.{s}'), 0.016, bone, f'DEF-upper_arm.{s}')
        cap(f'rad{s}', B(f'DEF-forearm.{s}'), B(f'DEF-hand.{s}'), 0.012, bone, f'DEF-forearm.{s}')
        cap(f'fem{s}', B(f'DEF-thigh.{s}'), B(f'DEF-shin.{s}'), 0.02, bone, f'DEF-thigh.{s}')
        cap(f'tib{s}', B(f'DEF-shin.{s}'), B(f'DEF-foot.{s}'), 0.016, bone, f'DEF-shin.{s}')
        if 'thigh' in muscles:
            cap(f'quad{s}', B(f'DEF-thigh.{s}').lerp(B(f'DEF-shin.{s}'), 0.12), B(f'DEF-thigh.{s}').lerp(B(f'DEF-shin.{s}'), 0.88), 0.05, musc, f'DEF-thigh.{s}')
        if 'arm' in muscles:
            cap(f'bic{s}', B(f'DEF-upper_arm.{s}').lerp(B(f'DEF-forearm.{s}'), 0.18), B(f'DEF-upper_arm.{s}').lerp(B(f'DEF-forearm.{s}'), 0.85), 0.034, musc, f'DEF-upper_arm.{s}')
    coll('XRAY').hide_render = True
    rig.data.pose_position = 'POSE'


def place(rig, at=(0, 0, 0), rot_z=0.0, scale=0.92):
    rig.location = at; rig.rotation_euler = (0, 0, rot_z); rig.scale = (scale,) * 3


def _strip(rig, action, start, end, blend='REPLACE', track=None, speed=1.0):
    ad = rig.animation_data or rig.animation_data_create()
    tr = ad.nla_tracks.new() if track is None else track
    a = bpy.data.actions[action]
    st = tr.strips.new(action, int(start), a)
    try:
        if a.slots and hasattr(st, 'action_slot'): st.action_slot = a.slots[0]
    except Exception: pass
    st.blend_type = blend
    st.extrapolation = 'NOTHING'                    # a later clip must not hold its first pose over earlier frames
    span = (a.frame_range[1] - a.frame_range[0]) / speed
    st.scale = 1.0 / speed
    st.repeat = max(1.0, (end - start) / max(span, 1))
    st.frame_end = end
    st.blend_in = st.blend_out = 0
    return tr, st


def play(rig, action, start, end, speed=1.0):
    """A clip from the library, looped from start to end (frames)."""
    return _strip(rig, action, start, end, speed=speed)


CURL_AXIS, CURL_SIGN = 'X', 1                     # elbow hinge of the library rig's forearm (checked on test renders)


def curl(rig, start, end, reps=3, side='R', name='Curl', axis=None, sign=None):
    """Biceps curls with the right arm, layered on the base motion (COMBINE keeps the rest of the body moving)."""
    act = bpy.data.actions.new(name); pb = rig.pose.bones
    rig.animation_data.action = act
    fa, ua = pb[f'DEF-forearm.{side}'], pb[f'DEF-upper_arm.{side}']
    for b in (fa, ua): b.rotation_mode = 'QUATERNION'
    n = end - start; per = n / reps
    for r in range(reps + 1):
        for phase, bend in ((0.0, 0.0), (0.5, 1.0)):
            f = start + r * per + phase * per
            if f > end: continue
            ax, sg = axis or CURL_AXIS, sign if sign is not None else CURL_SIGN
            q_fa = Matrix.Rotation(math.radians(100 * sg * bend), 4, ax).to_quaternion()
            q_ua = Matrix.Rotation(math.radians(12 * sg * bend), 4, ax).to_quaternion()
            fa.rotation_quaternion = q_fa; ua.rotation_quaternion = q_ua
            fa.keyframe_insert('rotation_quaternion', frame=f); ua.keyframe_insert('rotation_quaternion', frame=f)
    rig.animation_data.action = None
    fa.rotation_quaternion = (1, 0, 0, 0); ua.rotation_quaternion = (1, 0, 0, 0)
    for fc in _fcurves(act):
        for kp in fc.keyframe_points: kp.interpolation = 'BEZIER'; kp.easing = 'EASE_IN_OUT'
    return _strip(rig, name, start, end, blend='COMBINE')


def _fcurves(act):
    try:
        return list(act.fcurves)
    except Exception:
        out = []
        for layer in act.layers:
            for strip in layer.strips:
                for bag in strip.channelbags: out += list(bag.fcurves)
        return out


def blinks(name, frames, dur=4):
    """Eyes close briefly at each frame given (scale the eye spheres flat)."""
    for sx in (-1, 1):
        for part in ('eye', 'hl'):
            o = bpy.data.objects.get(f'{name}_{part}{sx}')
            if not o: continue
            base = o.scale.copy()
            for f in frames:
                for df, k in ((-1, 1.0), (1, 0.1), (dur - 1, 0.1), (dur + 1, 1.0)):
                    o.scale = (base.x, base.y, base.z * k); o.keyframe_insert('scale', frame=f + df)
            o.scale = base


def mouth(name, cues):
    """cues: [(frame, open 0..1, wide 0..1)], from the voice (mouth_cues.json). Scales the lips object."""
    o = bpy.data.objects[f'{name}_mouth']; base = o.scale.copy()
    for f, op, wd in cues:
        o.scale = (base.x * (0.85 + 0.35 * wd), base.y, base.z * (1.0 + 2.6 * op)); o.keyframe_insert('scale', frame=f)
    o.scale = base


def cam_move(cam, f0, f1, loc0, loc1, tgt0, tgt1):
    """Camera glides from (loc0, looking at tgt0) to (loc1, tgt1) between frames f0 and f1."""
    for f, l, t in ((f0, loc0, tgt0), (f1, loc1, tgt1)):
        cam.location = l; cam.rotation_euler = (Vector(t) - Vector(l)).to_track_quat('-Z', 'Y').to_euler()
        cam.keyframe_insert('location', frame=f); cam.keyframe_insert('rotation_euler', frame=f)
