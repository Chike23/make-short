"""checks.py: the checks every shot runs before anything renders (shotkit.finish calls run_all).

They catch in seconds what used to cost a re-render:
  camera     the view of the subject is blocked, the lens is pressed against something (the laptop in S08 of the
             June example filled the frame for 20 frames), the camera is inside an object, the head is cut, the
             face leaves the frame or sits in the caption band, the subject drifts off-centre
  clipping   a character's cut-out passes through a set object (a sofa arm through her body, a rail across her
             chest). Each event comes with a suggested fix: the smallest move of the character (left/right/
             towards/away from the camera) that clears it at the worst frame and keeps the face in frame
  outlines   every text object has its black outline twin (house rule: outlines on all text)
  motion     how fast the picture moves because of the camera, frame by frame, in px/frame at 720 wide:
             median, % still (< 0.5), % fast (> 10), whips (> 45) and still runs (6+ frames)
The report goes to checks/<sid>.json (the judge agent reads it) and CHECK lines are printed for the log.
"""
import bpy, math, json, os
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view as w2c

W_PX, H_PX = 720, 1280
SKIP_NAMES = ('blob', 'shadow', 'LOOK_', 'cam', 'sky', 'dome', 'haze', 'glow', 'halo', 'ring')


# ---------------------------------------------------------------- helpers
def _cast_names(cast): return tuple(R['name'] + '_' for R in cast)


def _owned_by(o, prefixes):
    """True when o belongs to a character: its name, a parent's name, or a constraint target (held props)."""
    seen = 0
    while o is not None and seen < 20:
        if o.name.startswith(prefixes): return True
        for c in getattr(o, 'constraints', ()):
            t = getattr(c, 'target', None)
            if t is not None and t.name.startswith(prefixes): return True
        o = o.parent; seen += 1
    return False


def _aabb(o):
    m = o.matrix_world; pts = [m @ Vector(c) for c in o.bound_box]
    return (Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
            Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))))


def _overlap(a, b, pad=0.02):
    return all(a[0][i] - pad <= b[1][i] and b[0][i] - pad <= a[1][i] for i in range(3))


def _visible(o):
    return not o.hide_render and min(abs(v) for v in o.matrix_world.to_scale()) > 1e-4


def _depth_inside(o, p):
    """How far point p (world) is inside mesh o (0 when outside). Uses the plain mesh, so the ink-outline hull
    modifier doesn't count."""
    mi = o.matrix_world.inverted(); lp = mi @ p
    try: ok, loc, nrm, _ = o.closest_point_on_mesh(lp)
    except Exception: return 0.0
    if not ok: return 0.0
    if (lp - loc).dot(nrm) >= 0: return 0.0
    return ((o.matrix_world @ loc) - p).length


def _set_objects(prefixes):
    return [o for o in bpy.context.scene.objects
            if o.type == 'MESH' and _visible(o) and not _owned_by(o, prefixes) and not any(s in o.name for s in SKIP_NAMES)]


def _groundlike(o):
    """Floors, ground, rugs and ground scatter (pebbles, tufts): big, low and flat. Characters stand and sit on them."""
    a = _aabb(o); d = a[1] - a[0]
    return d.z < 0.4 and d.x * d.y > 4.0


# ---------------------------------------------------------------- camera
def camera(sid, cam, R, f0, f1, size_at, step=2):
    sc = bpy.context.scene; names = (R['name'],)
    def mine(o):
        while o is not None:
            if o.name.startswith(names): return True
            o = o.parent
        return False
    world = _set_objects(_cast_names([R]))
    probs = {}
    for f in range(f0, f1 + 1, step):
        sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get()
        cpos = cam.matrix_world.translation.copy(); size = size_at(f)
        root = R['j']['root'].matrix_world
        tgt = root @ Vector((0, 0, 1.2)); d = cpos - tgt; dist = d.length; dn = d.normalized(); o = tgt + dn * 0.1
        while True:                                            # the subject's view of the camera
            hit, loc, nrm, idx, ob, mw = sc.ray_cast(dg, o, dn, distance=max(0.01, dist - (o - tgt).length - 0.1))
            if not hit: break
            if mine(ob) or not ob.visible_camera: o = loc + dn * 0.01; continue
            probs.setdefault(f'blocked by {ob.name}', []).append(f); break
        fwd = (cam.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized()
        hit, loc, nrm, idx, ob, mw = sc.ray_cast(dg, cpos + fwd * 0.03, fwd, distance=0.35)
        if hit and not mine(ob) and ob.visible_camera and not ob.name.startswith(tuple(SKIP_NAMES)):
            probs.setdefault(f'lens against {ob.name} ({(loc - cpos).length:.2f} m)', []).append(f)
        for w in world:                                        # the camera inside an object
            a = _aabb(w)
            if all(a[0][i] < cpos[i] < a[1][i] for i in range(3)) and _depth_inside(w, cpos) > 0.01:
                probs.setdefault(f'camera inside {w.name}', []).append(f); break
        if size == 'INS': continue
        top = w2c(sc, cam, root @ Vector((0, 0, 1.86)))
        face = w2c(sc, cam, root @ Vector((0, 0, 1.62)))
        mid = w2c(sc, cam, root @ Vector((0, 0, 1.2)))
        if top.y > 0.985 and size not in ('MCU', 'CU'): probs.setdefault('head cut', []).append(f)
        if face.y > 1.0 or face.y < 0.0 or face.x < 0.05 or face.x > 0.95: probs.setdefault('face out of frame', []).append(f)
        elif 0.26 <= face.y <= 0.34: probs.setdefault('face in caption band', []).append(f)
        if size not in ('EWS',) and (mid.x < 0.08 or mid.x > 0.92): probs.setdefault('subject off-centre', []).append(f)
    return {k: {'frames': len(fs) * step, 'from': fs[0], 'to': fs[-1]} for k, fs in probs.items()}


# ---------------------------------------------------------------- clipping
# A cut-out passes through an object when its flat shapes CROSS the object's surface. Testing surface crossings
# (BVH overlap) works on open library meshes too, where an "is this point inside?" test gave nonsense depths.
from mathutils.bvhtree import BVHTree
FEET = ('shoe', 'shinp', 'foot')


def _parts(R):
    pre = R['name'] + '_'; skip = set(id(o) for o in R.get('xray', []))
    return [o for o in bpy.data.objects if o.name.startswith(pre) and o.type in ('CURVE', 'MESH', 'FONT')
            and id(o) not in skip and 'blob' not in o.name and 'shadow' not in o.name and not o.name.endswith('_cast')]


def _geo(o, dg):
    """A part's triangles in its own space, read once (the cut-out shapes never deform)."""
    try:
        ev = o.evaluated_get(dg); me = ev.to_mesh()
        vs = [v.co.copy() for v in me.vertices]; ps = [tuple(p.vertices) for p in me.polygons]
        ev.to_mesh_clear(); return vs, ps
    except Exception:
        return [], []


def _char_bvh(geo, off=None):
    off = off or Vector(); verts, polys, owner = [], [], []
    for o, (vs, ps) in geo:
        if not ps or not _visible(o) or (len(o.color) > 3 and o.color[3] < 0.1): continue
        m = o.matrix_world; base = len(verts)
        verts += [m @ v + off for v in vs]; polys += [tuple(base + i for i in p) for p in ps]; owner += [o.name] * len(ps)
    if not polys: return None, [], None
    lo = Vector((min(v.x for v in verts), min(v.y for v in verts), min(v.z for v in verts)))
    hi = Vector((max(v.x for v in verts), max(v.y for v in verts), max(v.z for v in verts)))
    return BVHTree.FromPolygons(verts, polys, all_triangles=False), owner, (lo, hi)


def _animated(o):
    while o is not None:
        if (o.animation_data and o.animation_data.action) or len(o.constraints): return True
        o = o.parent
    return False


_OBJ = {}
def _obj_bvh(o, f):
    """An object's surface in world space (plain mesh: the ink-outline hull doesn't count). Static ones are cached."""
    key = (o.name, f if _animated(o) else None)
    if key not in _OBJ:
        me = o.data; m = o.matrix_world
        _OBJ[key] = BVHTree.FromPolygons([m @ v.co for v in me.vertices], [tuple(p.vertices) for p in me.polygons], all_triangles=False) \
            if len(me.polygons) else None
    return _OBJ[key]


def _hits(cb, owner, box, objs, f, allow, root_z):
    hits = {}
    for w in objs:
        if w.name.lower().startswith(tuple(x.lower() for x in allow)) or _groundlike(w): continue
        a = _aabb(w)
        if not _overlap(box, a): continue
        ob = _obj_bvh(w, f)
        if ob is None: continue
        grounded = a[0].z <= root_z + 0.1                          # stands on the ground (grass, steps, mats): feet and shins may cross it
        parts = set()
        for ci, _ in cb.overlap(ob):
            n = owner[ci]
            if grounded and any(t in n for t in FEET): continue
            parts.add(n.split('_', 1)[-1])
        if parts: hits[w.name] = parts
    return hits


def _face_ok(sc, cam, root, off):
    v = w2c(sc, cam, root.matrix_world.translation + off + Vector((0, 0, 1.62)))
    return 0.08 < v.x < 0.92 and 0.05 < v.y < 0.95


def suggest(sc, cam, R, geo, allow, world, f):
    """The smallest move (5-60 cm) of the character that clears every crossing at frame f and keeps the face in
    frame. Directions are in screen terms: left/right across the frame, towards/away from the camera."""
    m3 = cam.matrix_world.to_3x3()
    r = m3 @ Vector((1, 0, 0)); r.z = 0; r.normalize()
    fw = m3 @ Vector((0, 0, -1)); fw.z = 0; fw.normalize()
    dirs = [('left', -r), ('right', r), ('away from camera', fw), ('towards camera', -fw),
            ('left and away', (-r + fw).normalized()), ('right and away', (r + fw).normalized()),
            ('left and towards', (-r - fw).normalized()), ('right and towards', (r - fw).normalized())]
    root = R['j']['root']; rz = root.matrix_world.translation.z
    for k in range(1, 13):
        mag = 0.05 * k
        for name, d in dirs:
            off = d * mag
            cb, owner, box = _char_bvh(geo, off)
            if cb is None: return None
            if not _hits(cb, owner, box, world, f, allow, rz) and _face_ok(sc, cam, root, off):
                return {'move': name, 'metres': round(mag, 2), 'dx': round(off.x, 2), 'dy': round(off.y, 2)}
    return None


def clipping(cast, cam, f0, f1, allow=None, step=4):
    """Every character against every set object, every `step` frames. allow = {'june': ('sofa',)} lists object-name
    starts a character may cross on purpose (sitting in a sofa, sunk behind a desk, a fall behind a floor edge)."""
    sc = bpy.context.scene; allow = allow or {}; _OBJ.clear()
    if not cast: return []
    prefixes = _cast_names(cast); world = _set_objects(prefixes)
    sc.frame_set(f0); dg = bpy.context.evaluated_depsgraph_get()
    geo = {R['name']: [(o, _geo(o, dg)) for o in _parts(R)] for R in cast}
    ev = {}
    for f in range(f0, f1 + 1, step):
        sc.frame_set(f)
        for R in cast:
            cb, owner, box = _char_bvh(geo[R['name']])
            if cb is None: continue
            al = tuple(allow.get(R['name'], ()))
            for obj, parts in _hits(cb, owner, box, world, f, al, R['j']['root'].matrix_world.translation.z).items():
                e = ev.setdefault((R['name'], obj), {'frames': [], 'parts': set(), 'worst': f, 'n': 0})
                e['frames'].append(f); e['parts'] |= parts
                if len(parts) > e['n']: e['n'] = len(parts); e['worst'] = f
    out = []
    for (name, obj), e in ev.items():
        R = next(r for r in cast if r['name'] == name)
        sc.frame_set(e['worst'])
        fix = suggest(sc, cam, R, geo[name], tuple(allow.get(name, ())), world, e['worst'])
        out.append({'character': name, 'object': obj, 'from': e['frames'][0], 'to': e['frames'][-1],
                    'frames': len(e['frames']) * step, 'worst': e['worst'], 'parts': sorted(e['parts'])[:8], 'fix': fix})
    return sorted(out, key=lambda e: -e['frames'])


# ---------------------------------------------------------------- outlines
def outlines():
    """House rule: every text object has a black outline twin (sets_lib.text makes one)."""
    miss = []
    for o in bpy.context.scene.objects:
        if o.type != 'FONT' or o.name.endswith('_ol') or o.hide_render: continue
        tw = o.get('outline'); tw = bpy.data.objects.get(tw) if tw else bpy.data.objects.get(o.name + '_ol')
        if tw is None: miss.append(o.name)
    return miss


# ---------------------------------------------------------------- camera motion
def motion(cam, f0, f1, grid=(9, 16)):
    """Picture motion caused by the camera: a grid of points on the set, seen at frame f and f+1, in px/frame at
    720x1280. Characters add their own motion on top, so the real film measures a little higher."""
    sc = bpy.context.scene; per = []; prev = None
    for f in range(f0, f1 + 1):
        sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get()
        if prev is not None:                                   # last frame's points, seen from this frame
            pts, b = prev; a = [w2c(sc, cam, p) for p in pts]
            dpx = sorted(math.hypot((x.x - y.x) * W_PX, (x.y - y.y) * H_PX) for x, y in zip(a, b) if y.z > 0 and x.z > 0)
            per.append(dpx[len(dpx) // 2] if dpx else 0.0)
        m = cam.matrix_world.copy(); o = m.translation.copy()
        tr, br, bl, tl = [Vector(c) for c in cam.data.view_frame(scene=sc)]     # camera-space corners
        pts = []
        for i in range(grid[0]):
            for j in range(grid[1]):
                u, v = (i + 0.5) / grid[0], (j + 0.5) / grid[1]
                d = (m.to_3x3() @ (bl.lerp(br, u)).lerp(tl.lerp(tr, u), v)).normalized()
                hit, loc, *_ = sc.ray_cast(dg, o, d, distance=80.0)
                pts.append(loc if hit else o + d * 80.0)
        prev = (pts, [w2c(sc, cam, p) for p in pts])
    if not per: return {}
    s = sorted(per); n = len(per)
    runs, run = [], 0
    for i, v in enumerate(per + [99]):
        if v < 0.5: run += 1
        else:
            if run >= 6: runs.append([f0 + i - run, f0 + i - 1])
            run = 0
    return {'median': round(s[n // 2], 2), 'still_pct': round(100 * sum(v < 0.5 for v in per) / n, 1),
            'fast_pct': round(100 * sum(v > 10 for v in per) / n, 1), 'max': round(s[-1], 1),
            'whip_frames': [f0 + i for i, v in enumerate(per) if v > 45], 'still_runs': runs,
            'per_frame': [round(v, 2) for v in per]}


# ---------------------------------------------------------------- all of it
def run_all(sid, cam, cast, main, f0, f1, size_at, allow=None, sizes=None):
    rep = {'sid': sid, 'f0': f0, 'f1': f1, 'sizes': sizes or []}
    rep['camera'] = camera(sid, cam, main, f0, f1, size_at) if main else {}
    rep['clipping'] = clipping(cast, cam, f0, f1, allow)
    rep['outlines_missing'] = outlines()
    rep['motion'] = motion(cam, f0, f1)
    for k, v in rep['camera'].items(): print(f"CHECK {sid} {k}: {v['frames']} frames, {v['from']}-{v['to']}", flush=True)
    for e in rep['clipping']:
        fx = e['fix']; tip = f"move {e['character']} {fx['metres']} m {fx['move']} (dx {fx['dx']}, dy {fx['dy']})" if fx else 'no simple move clears it'
        print(f"CHECK {sid} clipping: {e['character']} through {e['object']} {e['from']}-{e['to']} "
              f"(worst {e['worst']}, {', '.join(e['parts'][:4])}): {tip}", flush=True)
    if rep['outlines_missing']: print(f"CHECK {sid} text without outline: {', '.join(rep['outlines_missing'])}", flush=True)
    mo = rep['motion']
    if mo:
        print(f"CHECK {sid} camera motion: median {mo['median']} px/f, still {mo['still_pct']}%, fast {mo['fast_pct']}%, "
              f"max {mo['max']}" + (f", WHIP at {mo['whip_frames'][:6]}" if mo['whip_frames'] else '')
              + (f", still runs {mo['still_runs']}" if mo['still_runs'] else ''), flush=True)
    if not rep['camera'] and not rep['clipping'] and not rep['outlines_missing']: print(f'CHECK {sid} ok', flush=True)
    return rep


def write(rep, folder):
    os.makedirs(folder, exist_ok=True)
    json.dump(rep, open(os.path.join(folder, f"{rep['sid']}.json"), 'w'), indent=1, default=list)
