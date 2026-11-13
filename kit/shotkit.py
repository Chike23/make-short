"""shotkit.py: everything a film script needs to build one shot of a cut-out Short in Blender.

A film is one Python file, P/film.py, that does `from shotkit import *`, fills FILM (the voice timing, the cut
words, a place and a mood per shot) and defines one function per shot (S01, S02, ...). Each shot builds its set,
its cast, its acting and its camera keys, then calls finish(). The runner at the bottom renders it:

    blender -b --python film.py -- plan                        -> plan/film.json (shot ranges, places, moods)
    blender -b --python film.py -- S03 <out> preview           -> build + checks, 360x640 preview settings
    blender -b --python film.py -- S03 <out> preview 300 340   -> + stills of frames 300 and 340
    blender -b --python film.py -- S03 <out> render            -> + the clip <out>/S03_0290-0417.mp4 (720x1280)
Every build writes checks/S03.json (camera, clipping, outlines, camera motion) and prints CHECK lines.

What this file holds (the house rules live in SKILL/references/spec.md and acting.md):
- timing: wf(line, word) = the frame where a narration word starts; ranges() = each shot's frames
- setup(), light(): render settings, the set's light rig and the reference grade (rick_mood)
- cast(), big(), antic(), hop(), tremble(), blinks(), life(), on_twos(): the acting helpers
- camera(): the camera GRAMMAR. Each key is a framing the camera LANDS on at frame f. It gets there with a fast,
  eased move, then keeps drifting very slowly in the same direction (or a slow push-in) until the next move.
- finish(): blinks, life, on twos, shadows, bake the camera, face every character to it, run the checks, set the
  look (rick_look) and depth of field.
"""
import bpy, math, os, sys, json, random, time
KIT = os.path.dirname(os.path.abspath(__file__))
if KIT not in sys.path: sys.path.insert(0, KIT)
import flat2d as F
import lady2d as L
import world3d as W
import sets_lib as SL
import camera_rig as C
import checks as CK
import look
from mathutils import Vector

FPS, HANDLE = 30, 8                  # every shot renders HANDLE extra frames: the next shot dissolves over them
PREVIEW = False
PROJECT = os.environ.get('MAKESHORT_PROJECT') or os.path.dirname(KIT)    # P (kit/ sits inside it)
import style as STY
STYLE = STY.load(PROJECT)            # P/style/style.json: the look of a new style (palettes, shading, set colours, grade)
FILM = dict(timing=os.path.join(PROJECT, 'voice', 'voice-timing.json'),
            cuts=[],                 # [(line, word), ...]: shot N+1 starts 4 frames before that word
            loc=[], mood=[],         # one place and one mood (day, dusk, interior, night) per shot
            end=None,                # last frame of the film (the end of the voice plus a short tail)
            allow={})                # {'S05': {'june': ('sofa',)}}: contacts the clipping check accepts


# ---------------------------------------------------------------- timing
_T = None
def T():
    global _T
    if _T is None: _T = json.load(open(FILM['timing']))
    return _T


def wf(line, stem, end=False, off=0.0):
    """The frame where word `stem` (start of the word, case-insensitive) of narration line `line` starts (or ends)."""
    for l in T()['lines']:
        if l['line'] != line: continue
        for w in l['words']:
            if ''.join(c for c in w['w'] if c.isalnum() or c in "'-").lower().startswith(stem.lower()):
                return int(round((w['end' if end else 'start'] + off) * FPS)) + 1
    raise KeyError(f'{line}:{stem}')


def ranges():
    """{'S01': (f0, f1), ...}. A cut sits 4 frames before its word, so the 8-frame dissolve is half done on the word."""
    b = [1] + [wf(l, s) - 4 for l, s in FILM['cuts']] + [FILM['end'] + 1]
    return {f'S{i + 1:02d}': (b[i], b[i + 1] - 1) for i in range(len(b) - 1)}


def end_frame(tail=0.6):
    """The film's last frame: the end of the last word plus a short tail (default 0.6 s)."""
    return int(round((T()['lines'][-1]['words'][-1]['end'] + tail) * FPS)) + 1


# ---------------------------------------------------------------- scene setup, grade, light
_TEX_OK = False


def setup(f0, f1):
    global _TEX_OK
    if not _TEX_OK:                                   # the painted textures, generated once per computer (needs pillow)
        try:
            import sets as _S; _S.ensure_textures()
        except Exception as ex: print('shotkit: textures not generated:', ex)
        _TEX_OK = True
    w, h = (360, 640) if PREVIEW else (720, 1280)
    sc = F.setup(f1 + HANDLE, res=(w, h), samples=6 if PREVIEW else 12)
    try: sc.render.image_settings.media_type = 'IMAGE'
    except Exception: pass
    look.setup_render(sc, w, h)
    sc.eevee.taa_render_samples = 6 if PREVIEW else 12
    sc.render.use_motion_blur = True
    try: sc.render.motion_blur_position = 'START'           # a pose swap on a frame never shows as a double image
    except Exception: pass
    sc.frame_start, sc.frame_end = f0, f1 + HANDLE
    F.MODE = 'lit'
    W.grade()
    return sc


def rick_mood(m):
    """The reference grade on top of a set's mood: darker (mean luma 42%), a red push (a* about +18), more colour
    (HSV saturation about 51%), shadows lifted towards indigo, never black. Night keeps its saturated blue."""
    rm = STYLE.get('grade', {}).get('rick_mood', {})
    gm, sm, lift = rm.get('gain_mult', (0.97, 0.9, 0.9)), rm.get('sat_mult', 1.1), rm.get('lift', (1.0, 0.98, 1.05))
    P = dict(look.MOODS[m]); g = P['gain']
    if 'night' not in m: P['gain'] = (g[0] * gm[0], g[1] * gm[1], g[2] * gm[2])
    P['sat'] = P['sat'] * sm
    P['lift'] = tuple(lift)
    look.MOODS[m + '_r'] = P
    return m + '_r'


def light(key, f0, f1, **over):
    """The light rig of a set (sets_lib.LIGHT[key]) with the reference grade. One strong key that casts shadows, a fill
    at about a third of it. Environment SHOT_LIGHT='{"key_mult":1.3,"fill_mult":0.6}' tunes a test render."""
    sc = bpy.context.scene
    kw = dict(SL.LIGHT[key]); kw.update(over); kw['mood'] = rick_mood(kw['mood'])
    if kw.get('key_energy'): kw['key_size'] = min(kw.get('key_size', 1.6), 0.45)      # a hard key: shadows that read
    ov = json.loads(os.environ.get('SHOT_LIGHT', '{}'))
    if 'key_mult' in ov and kw.get('key_energy'): kw['key_energy'] *= ov['key_mult']
    W.light(f0=f0, f1=f1, **kw)
    fill = bpy.data.objects.get('LOOK_Fill')
    if fill:
        for fc in F._fcurves(fill.data):
            if fc.data_path == 'energy':
                for kp in fc.keyframe_points: kp.co.y *= ov.get('fill_mult', 0.45)
    if 'LOOK_Sun' in bpy.data.objects and kw.get('shadow') == 'LOOK_Sun':     # a stronger sun: cast shadows read
        for fc in F._fcurves(bpy.data.objects['LOOK_Sun'].data):
            if fc.data_path == 'energy':
                for kp in fc.keyframe_points: kp.co.y *= 1.6
    return sc


# ---------------------------------------------------------------- cast and acting
CAST = []


def cast(name, at, pal=L.PAL, style='lady', face=('open', 'smile', 'neutral'), f0=1, f1=None):
    """A cut-out character standing at at=(x, y[, z]). pal: a palette from lady2d (PAL, SON, DOCTOR, YOUNG_MAN) or
    your own dict; style 'lady' or 'man' (hair and brows). The film's style card can swap the whole builder."""
    R = L.build(name, pal=pal, style=style); R['j']['root'].location = (at[0], at[1], at[2] if len(at) > 2 else 0.0)
    L.shadows(R)
    L.pose(R, f0 - 16, f0 - 14, {'arm_sl': (9, 10, 0), 'arm_sr': (9, 10, 0)})
    L.face(R, f0, eyes=face[0], mouth=face[1], brows=face[2])
    R['f0'], R['f1'] = f0, (f1 if f1 is not None else FILM['end'])
    CAST.append(R)
    return R


def _eyes_at(R, f):
    bpy.context.scene.frame_set(f)
    for k, objs in R['eyes'].items():
        if objs and objs[0].scale[0] > 0.5: return k
    return 'open'


def blinks(R, sid):
    """Blinks every 2-4 s at irregular times (seeded per shot), never within 8 frames of a face change, and back to
    whatever eyes she had: a blink never resets an expression."""
    keys = set()
    for o in R['eyes_all'] + R['mouth_all']:
        for fc in F._fcurves(o):
            for kp in fc.keyframe_points: keys.add(int(kp.co.x))
    rnd = random.Random(sum(map(ord, R['name'] + sid))); f = R['f0'] + rnd.randint(14, 40)
    while f < R['f1'] + HANDLE - 4:
        if all(abs(f - k) > 8 for k in keys) and all(abs(f + 3 - k) > 8 for k in keys):
            back = _eyes_at(R, f)
            if back in ('open', 'wide'): L.blink(R, f, back=back)
            f += rnd.randint(60, 115)
        else: f += 3


def pos(R, f):
    bpy.context.scene.frame_set(f); return R['j']['root'].matrix_world.translation.copy()


def objpos(o, f):
    bpy.context.scene.frame_set(f); return o.matrix_world.translation.copy()


def life(R, amount=1.0):
    """Holds never freeze: a slow, irregular drift on the head and torso (not breathing)."""
    for n, st, sc_ in (('head', 0.018, 23), ('torso', 0.01, 31)):
        j = R['j'][n]
        F.key(j, 'rotation_euler', F.now(j, 'rotation_euler', bpy.context.scene.frame_start, 1), bpy.context.scene.frame_start, 'BEZIER', 'AUTO', 1)
        for fc in F._fcurves(j):
            if fc.data_path == 'rotation_euler' and fc.array_index == 1:
                m = fc.modifiers.new('NOISE'); m.strength = st * amount; m.scale = sc_; m.phase = random.random() * 50


def on_twos(R):
    """Characters are drawn on twos (a new pose every 2 frames). The camera, the world and the character's travel
    across the set (root x/y) stay on ones: stepping the travel made her size pulse as the camera tracked her."""
    pre = R['name'] + '_'; root = R['j']['root']
    for o in bpy.data.objects:
        if not o.name.startswith(pre): continue
        for fc in F._fcurves(o):
            if o is root and fc.data_path == 'location' and fc.array_index in (0, 1): continue
            if any(m.type == 'STEPPED' for m in fc.modifiers): continue
            m = fc.modifiers.new('STEPPED'); m.frame_step = 2.0; m.frame_offset = 0.0


def antic(R, f, n=6, k=1.0, head=-3):
    """Anticipation: a small squash down before a big move that starts at f."""
    L.pose(R, f - n, f, {'squash': (1 + 0.05 * k, 1 - 0.06 * k), 'head': head})


def big(R, f, spec, antic=6, move=6, over=0.15, settle=10, squash=0.1, hold=0, face=None, look=None):
    """One big readable move by the acting rules: an eased anticipation (a squash and a small counter-move), a move
    that overshoots the target by `over`, an optional hold at the peak, then a settle onto the target. face and
    look land with the move; the eyes lead by 3 frames. spec: lady2d pose targets plus 'lift' and 'squash'."""
    J = R['j']; tg = L._target(R, spec); fa = f - antic
    for j, v1 in tg.items():
        v0 = F.now(j, 'rotation_euler', fa, 1)
        F.key(j, 'rotation_euler', v0, fa, 'BEZIER', 'AUTO', 1)
        if antic: F.key(j, 'rotation_euler', v0 - 0.08 * (v1 - v0), f, 'BEZIER', 'AUTO', 1)
        F.key(j, 'rotation_euler', v0 + (1 + over) * (v1 - v0), f + move, 'BEZIER', 'AUTO', 1)
        if hold: F.key(j, 'rotation_euler', v0 + (1 + over) * (v1 - v0), f + move + hold, 'BEZIER', 'AUTO', 1)
        F.key(j, 'rotation_euler', v1, f + move + hold + settle, 'BEZIER', 'AUTO', 1)
    root = J['root']
    sx, sz = spec.get('squash', (1.0, 1.0))
    for i, v in ((0, sx), (2, sz)):
        v0 = F.now(root, 'scale', fa, i)
        F.key(root, 'scale', v0, fa, 'BEZIER', 'AUTO', i)
        if antic: F.key(root, 'scale', (1 + 0.6 * squash) if i == 0 else (1 - squash), f, 'BEZIER', 'AUTO', i)
        F.key(root, 'scale', (1 - 0.5 * squash) if i == 0 else (1 + 0.7 * squash), f + move, 'BEZIER', 'AUTO', i)
        F.key(root, 'scale', v, f + move + hold + settle, 'BEZIER', 'AUTO', i)
    if 'lift' in spec:
        z0 = F.now(root, 'location', fa, 2); z1 = spec['lift']
        F.key(root, 'location', z0, f, 'BEZIER', 'AUTO', 2)
        F.key(root, 'location', z0 + (1 + over) * (z1 - z0), f + move, 'BEZIER', 'AUTO', 2)
        if hold: F.key(root, 'location', z0 + (1 + over) * (z1 - z0), f + move + hold, 'BEZIER', 'AUTO', 2)
        F.key(root, 'location', z1, f + move + hold + settle, 'BEZIER', 'AUTO', 2)
    for s_ in ('sl', 'sr'):
        if f'front_{s_}' in spec: L.pose(R, f - 1, f, {f'front_{s_}': spec[f'front_{s_}']})
    if look is not None: L.look(R, f - 3, *look)
    if face: L.face(R, f + 1, *face)


def tremble(R, f0, f1, joint='fore_sr', amp=4.0, every=4):
    """A shaking limb (strain): +-amp degrees every `every` frames, then back."""
    j = R['j'][joint]; base = F.now(j, 'rotation_euler', f0, 1); s = 1
    for f in range(f0, f1, every):
        F.key(j, 'rotation_euler', base + math.radians(amp) * s, f, 'LINEAR', 'AUTO', 1); s = -s
    F.key(j, 'rotation_euler', base, f1, 'BEZIER', 'AUTO', 1)


def hop(R, f, h=0.08, n=7):
    """A small happy hop: anticipation, up with overshoot, land with a squash, settle."""
    antic(R, f, 5, 1.0, 0)
    L.pose(R, f, f + n, {'lift': h, 'squash': (0.94, 1.07)}, interp='BACK', easing='EASE_OUT')
    L.pose(R, f + n, f + 2 * n, {'lift': 0.0, 'squash': (1.06, 0.94)})
    L.pose(R, f + 2 * n, f + 3 * n, {'squash': (1.0, 1.0)})


def hold_point(R, side, f):
    return objpos(R['j'][f'hand_{side}'], f)


def hold_prop(R, obj, side, off):
    """A prop in a hand; it stays upright (COPY_ROTATION to the root) however the arm turns."""
    return L.hold(R, obj, side, off)


def muscles(R, f0, f1, sx, sz, interp='BEZIER'):
    """X-ray muscles grow (sx, sz > 1) or shrink between f0 and f1."""
    for n in ('bicep_sl', 'bicep_sr', 'forem_sl', 'forem_sr', 'quad_sl', 'quad_sr'):
        j = R['j'][n]
        for i, v in ((0, sx), (2, sz)):
            F.key(j, 'scale', F.now(j, 'scale', f0, i), f0, interp, 'AUTO', i); F.key(j, 'scale', v, f1, 'BEZIER', 'AUTO', i)


def pulse(R, f, k):
    """An X-ray glow ring pulses out from the muscles at frame f (k = ring 0, 1 or 2)."""
    for side in ('sl', 'sr'):
        rj, rg = [r for r in R['rings'] if r[0].name.endswith(f'ringj{k}_{side}')][0]
        F.key(rj, 'scale', (0.3, 0.3, 0.3), f, 'BEZIER'); F.key(rj, 'scale', (2.3, 2.3, 2.3), f + 16, 'BEZIER')
        F.key(rg, 'color', 0.0, f - 1, 'CONSTANT', 'AUTO', 3); F.key(rg, 'color', 0.9, f, 'BEZIER', 'AUTO', 3); F.key(rg, 'color', 0.0, f + 16, 'BEZIER', 'AUTO', 3)
    for h in R['halos']:
        F.key(h, 'color', 0.6, f - 1, 'BEZIER', 'AUTO', 3); F.key(h, 'color', 1.0, f + 2, 'BEZIER', 'AUTO', 3); F.key(h, 'color', 0.6, f + 9, 'BEZIER', 'AUTO', 3)


def swap(a, b, f):
    """Object a disappears and b appears at frame f (a prop swap)."""
    F.key(a, 'scale', (1, 1, 1), f - 1, 'CONSTANT'); F.key(a, 'scale', (0, 0, 0), f, 'CONSTANT')
    F.key(b, 'scale', (0, 0, 0), f - 1, 'CONSTANT'); F.key(b, 'scale', (1, 1, 1), f, 'CONSTANT')


def hide_until(o, f):
    F.key(o, 'scale', (0, 0, 0), f - 1, 'CONSTANT'); F.key(o, 'scale', (1, 1, 1), f, 'CONSTANT')


# ---------------------------------------------------------------- camera: the grammar
SIZE = {'EWS': (22.0, 4.0), 'WS': (7.0, 1.6), 'FS': (2.9, 1.0), 'MS': (1.45, 1.2), 'MCU': (0.88, 1.47), 'CU': (0.5, 1.62)}
#        frame height H at the subject (m), look-at height above its feet (m)
SHOT_KEYS = {}                       # sid -> [{'f', 'size', 'move', 'drift'}]
MOVE_MIN, MOVE_MAX = 10, 48          # a move lasts 10-48 frames: long enough that it never whips
PEAK = 34                            # fastest picture speed in a move, px/frame at 720x1280 (the check calls > 45 a whip)
PX_PER_CHANGE = 600                  # measured: a change of 1.0 frame height moves the median pixel about 600 px
DRIFT = 0.0035                       # drift speed between moves, frame heights per frame (about 1.5-2 px/frame at 720)
DRIFT_CAP = 0.18                     # a drift never travels more than 18% of a frame
CAM_NOTES = {}                       # sid -> warnings from camera() (keys too close for a smooth move)


def _framing(k):
    lens = k.get('lens', 35)
    H, cz = (k['H'], k.get('cz', 0.0)) if 'H' in k else SIZE[k['size']]
    t = Vector(k['at']) + Vector((k.get('dx', 0.0), 0, cz + k.get('dz', 0.0)))
    if 'cam' in k:
        v = Vector(k['cam']) - t; d = max(v.length, 0.05)
        az, el = math.atan2(v.x, -v.y), math.asin(max(-1.0, min(1.0, v.z / d)))
    else:
        d = H * lens / 36.0; az, el = math.radians(k.get('az', 0.0)), math.radians(k.get('el', 5.0))
    return dict(t=t, d=d, az=az, el=el, lens=float(lens), H=d * 36.0 / lens)


def _cam_pos(fr):
    az, el = fr['az'], fr['el']
    return fr['t'] + fr['d'] * Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))


def _mix(a, b, u):
    """Framing between a (u=0) and b (u=1): target and angles linear, distance and lens on a log scale (an even zoom).
    u outside 0..1 extrapolates (used for the drift)."""
    return dict(t=a['t'].lerp(b['t'], u), d=a['d'] * (b['d'] / a['d']) ** u, az=a['az'] + (b['az'] - a['az']) * u,
                el=a['el'] + (b['el'] - a['el']) * u, lens=a['lens'] * (b['lens'] / a['lens']) ** u,
                H=a['H'] * (b['H'] / a['H']) ** u)


def _change(a, b):
    """How much the picture changes from framing a to b, in frame heights: the subject sliding across the frame, the
    zoom (log of the frame-height ratio) and the background swinging past on an orbit or tilt."""
    Hm = math.sqrt(a['H'] * b['H'])
    lat = (b['t'] - a['t']).length / Hm
    zoom = abs(math.log(b['H'] / a['H']))
    orbit = (abs(b['az'] - a['az']) + abs(b['el'] - a['el'])) * math.sqrt(a['lens'] * b['lens']) / 36.0
    return lat + zoom + orbit


def _drifted(fr, prev, mode, frames, amt=None):
    """Where the camera has drifted to after `frames` frames of drift from framing fr. prev = the framing it moved
    from (None for the first key). mode: follow (keep going the way the last move went), push, pull, left, right,
    up, down, orbit_l, orbit_r, hold."""
    total = min(DRIFT_CAP, (amt if amt is not None else DRIFT) * frames)
    if mode == 'hold' or total <= 0: return dict(fr)
    if mode == 'follow' and prev is not None and _change(prev, fr) > 0.03:
        return _mix(prev, fr, 1.0 + total / _change(prev, fr))
    if mode in ('follow', 'push', 'pull'):
        k = math.exp(-total if mode != 'pull' else total)
        return dict(fr, d=fr['d'] * k, H=fr['H'] * k)
    right = Vector((math.cos(fr['az']), math.sin(fr['az']), 0.0))
    step = total * fr['H']
    if mode in ('left', 'right'): return dict(fr, t=fr['t'] + right * (step if mode == 'right' else -step))
    if mode in ('up', 'down'): return dict(fr, t=fr['t'] + Vector((0, 0, step if mode == 'up' else -step)))
    if mode in ('orbit_l', 'orbit_r'):
        da = total * 36.0 / fr['lens']; return dict(fr, az=fr['az'] + (da if mode == 'orbit_r' else -da))
    raise ValueError(f'unknown drift {mode}')


def _ease(u):                       # smootherstep: a quick move that starts and lands softly
    u = max(0.0, min(1.0, u)); return u * u * u * (u * (u * 6 - 15) + 10)


def camera(sid, keys, focus, fstop=1.6, shake=0.55, grammar='move_drift'):
    """keys: dicts {f, size, at, az, el, lens, dx, dz, H, cz, cam, move, drift}, one per framing.
      f      the frame the camera LANDS on this framing (put it on the word the framing is for)
      size   EWS, WS, FS, MS, MCU, CU or INS (sets the frame height H and look-at height, and the audit's shot size)
      at     the subject's feet (Vector); dx/dz shift the look-at point; H/cz override the size's values
      az, el the camera's angle round and above the subject (degrees; az 0 = from -y, looking towards +y)
      lens   mm (35 default); cam = an explicit camera position instead of az/el/distance
      move   frames for the move into this framing (default: from the size of the change, 10-32)
      drift  what happens after landing until the next move: follow (default: keep going the same way, slowly),
             push (slow zoom in; default for the first key), pull, left, right, up, down, orbit_l, orbit_r, hold
    grammar='spline' gives the old behaviour (one smooth curve through every key)."""
    sc = bpy.context.scene
    tgt = bpy.data.objects.new('cam_target', None); sc.collection.objects.link(tgt)
    cd = bpy.data.cameras.new('cam3d'); cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 36; cd.clip_start = 0.03; cd.clip_end = 500
    cam = bpy.data.objects.new('cam3d', cd); sc.collection.objects.link(cam)
    tc = cam.constraints.new('TRACK_TO'); tc.target = tgt; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
    keys = sorted(keys, key=lambda k: k['f'])
    frs = [_framing(k) for k in keys]
    rec = []
    if grammar == 'spline':
        for k, fr in zip(keys, frs):
            p = _cam_pos(fr)
            for i in range(3):
                F.key(cam, 'location', p[i], k['f'], 'BEZIER', 'AUTO', i); F.key(tgt, 'location', fr['t'][i], k['f'], 'BEZIER', 'AUTO', i)
            F.key(cd, 'lens', fr['lens'], k['f'], 'BEZIER', 'AUTO')
            rec.append({'f': k['f'], 'size': k.get('size'), 'move': 0, 'drift': 'spline'})
        for ob in (cam, tgt, cd):
            for fc in F._fcurves(ob):
                for kp in fc.keyframe_points: kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
                fc.extrapolation = 'LINEAR'
    else:
        f_end = sc.frame_end + 2; f_start = min(sc.frame_start, keys[0]['f']) - 2
        # moves: key i is reached at f_i after a move of m_i frames that starts from where key i-1 had drifted to
        segs = []                                           # (frame, framing) anchors, in order
        land = [frs[0]]                                     # framing at each landing
        starts = []; CAM_NOTES[sid] = []
        for i, k in enumerate(keys):
            if i == 0: starts.append(None); continue
            # long enough that the fastest frame of the eased move stays under PEAK (smootherstep peaks at 1.875x average)
            need = int(math.ceil(1.875 * PX_PER_CHANGE * _change(frs[i - 1], frs[i]) / PEAK))
            m = k.get('move') or min(MOVE_MAX, max(MOVE_MIN, need))
            s = k['f'] - m
            if s < keys[i - 1]['f'] + 6: s = max(keys[i - 1]['f'], s)     # eat the drift before eating the move
            if k['f'] - s < min(m, need) - 2:
                CAM_NOTES[sid].append(f"key at {k['f']} ({k.get('size')}) needs {min(m, need)} frames to move, has {k['f'] - s}: "
                                      f"move it later or drop the key before it")
            starts.append(s)
        drifted = []
        for i, k in enumerate(keys):
            nxt = starts[i + 1] if i + 1 < len(keys) else f_end
            mode = k.get('drift') or ('push' if i == 0 else 'follow')
            drifted.append(_drifted(frs[i], frs[i - 1] if i else None, mode, max(0, nxt - k['f']), k.get('drift_amt')))
            rec.append({'f': k['f'], 'size': k.get('size'), 'move': 0 if i == 0 else k['f'] - starts[i], 'drift': mode})

        def at_frame(f):
            i = 0
            for j in range(1, len(keys)):
                if f >= starts[j]: i = j
            k = keys[i]
            if i > 0 and f < k['f']:                         # inside the move into key i
                u = (f - starts[i]) / max(1, k['f'] - starts[i]); return _mix(drifted[i - 1], frs[i], _ease(u))
            nxt = starts[i + 1] if i + 1 < len(keys) else f_end
            span = max(1, nxt - k['f'])
            return _mix(frs[i], drifted[i], (f - k['f']) / span)    # the drift: steady and slow (u<0 before key 0)
        for f in range(f_start, f_end + 1):
            fr = at_frame(f); p = _cam_pos(fr)
            for i in range(3):
                F.key(cam, 'location', p[i], f, 'LINEAR', 'AUTO', i); F.key(tgt, 'location', fr['t'][i], f, 'LINEAR', 'AUTO', i)
            F.key(cd, 'lens', fr['lens'], f, 'LINEAR', 'AUTO')
    sc.camera = cam
    try:
        import addon_utils
        if not hasattr(bpy.types.Object, 'camera_shakes'):
            for m in ('bl_ext.user_default.camera_shakify', 'camera_shakify'):
                try: addon_utils.enable(m, default_set=False); break
                except Exception: pass
        C.add_shake(cam, 'THE_WEDDING', shake)
    except Exception as ex:
        print('shotkit: no Camera Shakify, noise shake instead:', ex)
        for fc in F._fcurves(cam):
            if fc.data_path == 'location':
                m = fc.modifiers.new('NOISE'); m.scale = 28 + 6 * fc.array_index; m.strength = 0.02
    SHOT_KEYS[sid] = rec
    for n in CAM_NOTES.get(sid, []): print(f'CHECK {sid} camera keys too close: {n}', flush=True)
    return cam, focus, fstop


def size_at(sid, f):
    """The shot size at frame f: a size counts from the middle of the move into it."""
    ks = [k for k in SHOT_KEYS.get(sid, []) if k.get('size') and k['f'] - k['move'] // 2 <= f]
    return ks[-1]['size'] if ks else next((k['size'] for k in SHOT_KEYS.get(sid, []) if k.get('size')), 'FS')


# ---------------------------------------------------------------- finish
def finish(sid, f0, f1, camspec, grounds=None, allow=None, checks=True):
    """Blinks, life, on twos and a soft shadow for every character; bake the camera and turn everyone to face it;
    run the checks (camera, clipping, outlines, motion: checks/<sid>.json); the reference look; depth of field.
    allow: {'june': ('sofa',)}: objects this character may overlap on purpose (sitting in a sofa, sunk behind a desk)."""
    sc = bpy.context.scene; cam, focus, fstop = camspec
    for R in CAST:
        g = (grounds or {}).get(R['name'])
        blinks(R, sid); life(R); on_twos(R)
        L.blob_shadow(R, frames=(f0 - 2, f1 + HANDLE + 2), ground=g, alpha=0.75)
    baked = F.bake_camera(cam, 'cam3d_baked'); sc.camera = baked
    for R in CAST: L.face_camera(R, baked)
    if checks:
        main = next((R for R in CAST if R['j']['torso'] is focus), CAST[0] if CAST else None)
        rep = CK.run_all(sid, baked, CAST, main, f0, f1 + HANDLE, lambda f: size_at(sid, f),
                         allow=dict(FILM.get('allow', {}).get(sid, {}), **(allow or {})),
                         sizes=SHOT_KEYS.get(sid, []))
        rep['camera_keys_too_close'] = CAM_NOTES.get(sid, [])
        CK.write(rep, os.path.join(PROJECT, 'checks'))
    W.set_kuwahara(1, (f0, f1 + HANDLE))
    W.rick_look(keep=tuple(R['name'] for R in CAST), depth_ink=1.0)
    d = baked.data.dof; d.use_dof = True; d.focus_object = focus; d.aperture_fstop = fstop
    for n in ('cam3d', 'cam_target'):
        o = bpy.data.objects.get(n)
        if o: bpy.data.objects.remove(o, do_unlink=True)
    return baked


# ---------------------------------------------------------------- runner
def stills(out, frames):
    sc = bpy.context.scene; os.makedirs(out, exist_ok=True); paths = []
    s = sc.render.image_settings
    try: s.media_type = 'IMAGE'
    except Exception: pass
    s.file_format = 'PNG'; s.color_mode = 'RGB'
    for f in frames:
        sc.frame_set(f); p = os.path.join(out, f'still_{f:04d}.png'); sc.render.filepath = p
        bpy.ops.render.render(write_still=True); paths.append(p)
    return paths


def save_job(out, sid):
    sc = bpy.context.scene; os.makedirs(out, exist_ok=True)
    s = sc.render.image_settings
    try: s.media_type = 'VIDEO'
    except Exception: pass
    s.file_format = 'FFMPEG'; s.color_mode = 'RGB'
    f = sc.render.ffmpeg; f.format = 'MPEG4'; f.codec = 'H264'; f.constant_rate_factor = 'HIGH'; f.ffmpeg_preset = 'GOOD'; f.audio_codec = 'NONE'
    sc.render.filepath = os.path.join(out, f'{sid}_')
    job = os.path.join(out, f'job_{sid}.blend'); bpy.ops.wm.save_as_mainfile(filepath=job, copy=True)
    return job


def write_plan(path):
    """plan/film.json: every shot's frames, place and mood (the tools read it)."""
    rg = ranges(); ids = sorted(rg)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump({'fps': FPS, 'handle': HANDLE, 'end': FILM['end'],
               'shots': [{'id': s, 'f0': rg[s][0], 'f1': rg[s][1], 'loc': FILM['loc'][i] if i < len(FILM['loc']) else '',
                          'mood': FILM['mood'][i] if i < len(FILM['mood']) else 'interior'} for i, s in enumerate(ids)]},
              open(path, 'w'), indent=1)


def run(ns):
    """Call at the bottom of film.py: `if __name__ == '__main__': run(globals())`."""
    global PREVIEW
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    if not a: print('usage: film.py -- plan | SID OUT [preview] [frames...] [render]'); return
    n = len(FILM['cuts']) + 1
    assert len(FILM['loc']) == n and len(FILM['mood']) == n, f"FILM['loc'] and FILM['mood'] need {n} entries"
    if a[0] == 'plan':
        p = os.path.join(PROJECT, 'plan', 'film.json'); write_plan(p); print('PLAN', p, flush=True); return
    sid, out = a[0], os.path.abspath(a[1]); rest = a[2:]
    PREVIEW = 'preview' in rest; go = 'render' in rest; frames = [int(x) for x in rest if x.isdigit()]
    os.makedirs(out, exist_ok=True)
    CAST.clear(); f0, f1 = ranges()[sid]
    t0 = time.time(); ns[sid](f0, f1); print(f'BUILT {sid} {f0}-{f1} {time.time() - t0:.1f}s', flush=True)
    json.dump(SHOT_KEYS.get(sid, []), open(os.path.join(out, f'{sid}_camkeys.json'), 'w'))
    if frames:
        t0 = time.time(); stills(os.path.join(out, f'stills_{sid}'), frames)
        print(f'STILLS {sid} {(time.time() - t0) / len(frames):.1f}s/frame', flush=True)
    if go:
        save_job(out, sid)
        bpy.context.scene.render.filepath = os.path.join(out, f'{sid}_')
        bpy.ops.render.render(animation=True)
        print(f'RENDERED {sid}', flush=True)
