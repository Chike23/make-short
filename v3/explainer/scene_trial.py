"""scene_trial.py: ~24 s, 4 scenes. A 2D cut-out lead (lady2d) in painted 3D worlds (world3d, lib/look.py, lib/sets.py).

  s1 living room (sunset interior)  "After forty, your muscles start to quietly disappear. You lose up to eight percent
                                     every single decade."  walks in, admires her arm, X-ray, shock, backs away worried
  s2 park (day, Rick's world)       "You see, muscle isn't just for looks. It carries your shopping, climbs your stairs,
                                     and catches you when you trip."  walks toward camera with bags, climbs the steps, trips
  s3 gym (daylight)                 "But muscle never stops listening. Lift something heavy just twice a week, and it
                                     starts rebuilding, even in your seventies."  walks in, lifts, curls twice, X-ray rebuild
  s4 park (golden hour)             "So pick something heavy up today. Your future self will thank you."  jogs in, celebrates

House rules: library first; she reacts and acts (no lip-sync, no breathing); she moves around the set; the camera moves
on every frame; she is always head-on to the camera. Each scene renders as its own clip (+8 frames for the dissolve).

    build('s1'); stills([...]); job = save_job(out, 's1')   ... then launch(jobs, out)
"""
import bpy, math, os, sys, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flat2d as F
import lady2d as L
import world3d as W
import scene_2d5 as S5
import camera_rig as C
import look

FPS, HANDLE = 30, 8
HERE = os.path.dirname(os.path.abspath(__file__))
TIMING = os.path.join(HERE, '..', 'trial30', 'voice', 'voice-timing.json')


def _t():
    return json.load(open(TIMING))


def wf(line, stem, off=0.0, end=False):
    """Frame of a narration word (line number, word stem): its start, or its end."""
    for l in _t()['lines']:
        if l['line'] != line: continue
        for w in l['words']:
            if w['w'].lower().strip('.,!?').startswith(stem.lower()):
                return int(round((w['end' if end else 'start'] + off) * FPS)) + 1
    raise KeyError(f'{line}:{stem}')


def ranges():
    T = _t(); E = {l['line']: l['end'] for l in T['lines']}
    b = [1, int(round((E[2] + 0.22) * FPS)) + 1, int(round((E[3] + 0.2) * FPS)) + 1, int(round((E[5] + 0.2) * FPS)) + 1,
         int(round(T['duration'] * FPS))]
    return {'s1': (b[0], b[1] - 1), 's2': (b[1], b[2] - 1), 's3': (b[2], b[3] - 1), 's4': (b[3], b[4])}


# ---------------------------------------------------------------- shared
def setup(f0, f1):
    sc = F.setup(f1 + HANDLE, res=(720, 1280), samples=12)
    try: sc.render.image_settings.media_type = 'IMAGE'
    except Exception: pass
    look.setup_render(sc, 720, 1280)
    sc.eevee.taa_render_samples = 12; sc.render.use_motion_blur = True
    sc.frame_start, sc.frame_end = f0, f1 + HANDLE
    F.MODE = 'lit'
    W.grade()
    return sc


def lady(at, f0, f1):
    R = L.build('lady'); R['j']['root'].location = (at[0], at[1], 0.0); L.shadows(R)
    L.pose(R, f0 - 14, f0 - 12, {'arm_sl': (9, 10, 0), 'arm_sr': (9, 10, 0)})
    L.face(R, f0, eyes='open', mouth='smile', brows='neutral')
    for f in range(f0 + 40, f1, 95): L.blink(R, f)
    return R


def camera(shots, punch=()):
    """shots = [(frame, position, look-at, lens or None), ...]; keys before/after the clip keep it moving on every frame."""
    sc = bpy.context.scene
    tgt = bpy.data.objects.new('cam_target', None); sc.collection.objects.link(tgt)
    cd = bpy.data.cameras.new('cam3d'); cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 36; cd.clip_start = 0.05; cd.clip_end = 400
    cam = bpy.data.objects.new('cam3d', cd); sc.collection.objects.link(cam)
    tc = cam.constraints.new('TRACK_TO'); tc.target = tgt; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
    for f, p, t, lens in shots:
        for i in range(3): F.key(cam, 'location', p[i], f, 'BEZIER', 'AUTO', i); F.key(tgt, 'location', t[i], f, 'BEZIER', 'AUTO', i)
        if lens: F.key(cd, 'lens', lens, f)
    for f, add in punch:
        base = F.now(cd, 'lens', f)
        F.key(cd, 'lens', base, f - 1); F.key(cd, 'lens', base + add, f + 4); F.key(cd, 'lens', base + add * 0.6, f + 16)
    sc.camera = cam
    try:
        import addon_utils                                  # a background Blender loads only saved prefs: enable it here
        if not hasattr(bpy.types.Object, 'camera_shakes'):
            for m in ('bl_ext.user_default.camera_shakify', 'camera_shakify'):
                try: addon_utils.enable(m, default_set=False); break
                except Exception: pass
        C.add_shake(cam, 'THE_WEDDING', 0.6)
    except Exception as ex:                                 # no Camera Shakify (e.g. a fresh install): handheld noise
        print('scene_trial: Camera Shakify unavailable, noise shake instead:', ex)
        for fc in F._fcurves(cam):
            if fc.data_path == 'location':
                m = fc.modifiers.new('NOISE'); m.scale = 28 + 6 * fc.array_index; m.strength = 0.022; m.phase = 7 * fc.array_index
    return cam


RICK = True          # Rick's world look: smooth sunlit set, no outlines on the set, shallow depth of field


def finish(R, cam, f0, f1, ground=None):
    sc = bpy.context.scene
    L.blob_shadow(R, frames=(f0 - 2, f1 + HANDLE + 2), ground=ground)
    baked = F.bake_camera(cam, 'cam3d_baked'); sc.camera = baked
    L.face_camera(R, baked)
    W.set_kuwahara(1, (f0, f1 + HANDLE))
    if RICK:
        print('rick_look', W.rick_look(), flush=True)
        d = baked.data.dof; d.use_dof = True; d.focus_object = R['j']['torso']; d.aperture_fstop = 1.4
    return baked


def bag(name):
    """A paper shopping bag (toon box + handle), built from primitives."""
    e = bpy.data.objects.new(name, None); W.coll('WORLD').objects.link(e)
    b = W.box(f'{name}_b', (0.2, 0.11, 0.24), (0, 0, -0.17), W.toon(f'{name}_paper', '#c99a62'), ink=0.006)
    h = W.box(f'{name}_h', (0.12, 0.012, 0.012), (0, 0, -0.04), W.toon(f'{name}_hd', '#7a4a2a'), ink=0.003)
    g = W.box(f'{name}_g', (0.08, 0.02, 0.06), (0, -0.056, -0.15), W.toon(f'{name}_lbl', '#4f6fb0'), ink=0)
    for o in (b, h, g): o.parent = e
    return e


def swap(a, b, f):
    F.key(a, 'scale', (1, 1, 1), f - 1, 'CONSTANT'); F.key(a, 'scale', (0, 0, 0), f, 'CONSTANT')
    F.key(b, 'scale', (0, 0, 0), f - 1, 'CONSTANT'); F.key(b, 'scale', (1, 1, 1), f, 'CONSTANT')


def plyo(spot, top=0.69):
    """A wooden plyo box behind her right hand; the dumbbell sits on its front edge, where her reaching hand lands
    (hand target ik_sr (0.62, 0.66) + torso tilt 12 deg puts the hand at about x +0.44, z 0.74 from her feet)."""
    x, y = spot
    W.box('plyo', (0.38, 0.36, top), (x + 0.5, y + 0.28, top / 2), W.toon('plyo', '#b07a4a', 'wood_crate.png'), ink=0.01)
    return W.dumbbell('db_table', (x + 0.44, y + 0.14, top + 0.045), (0, 0, math.radians(6)))


# ---------------------------------------------------------------- s1 living room
def build_s1():
    f0, f1 = ranges()['s1']; sc = setup(f0, f1)
    W.living_room()
    R = lady((-1.45, 0.8), f0, f1)
    L.sway(R, f0, f1 + HANDLE)
    L.walk(R, f0, 46, [(-1.45, 0.8), (-0.75, 0.28), (0.0, 0.0)], step=8, ease=(False, True))    # walks in
    L.face(R, 30, brows='happy'); L.look(R, 30, dx=0.006)
    m = wf(1, 'muscles'); d = wf(1, 'disappear')
    L.pose(R, 48, 58, {'arm_sl': (80, 104, 10), 'arm_sr': (9, 8, 0), 'head': -5}, interp='BACK', easing='EASE_OUT')   # admires her arm
    L.look(R, 52, dx=-0.007, dz=0.004); L.face(R, 52, mouth='smile', brows='happy')
    L.pose(R, 60, 66, {'arm_sl': (84, 116, 14)}); L.pose(R, 66, 72, {'arm_sl': (80, 102, 10)})
    L.xray(R, d - 2, d + 4)                                                                        # "disappear": X-ray
    S5.muscles(R, d, d + 34, 0.55, 0.9)
    L.face(R, d + 2, eyes='open', mouth='frown', brows='worried'); L.look(R, d + 2, dx=-0.007, dz=-0.002)
    L.pose(R, d + 4, d + 14, {'arm_sl': (40, 70, 0), 'head': -8})
    e = wf(2, 'eight')                                                                             # "eight": shock
    L.pose(R, e - 6, e - 1, {'squash': (1.04, 0.95), 'head': -2})
    L.pose(R, e - 2, e - 1, {'front_sl': True, 'front_sr': True})
    L.pose(R, e - 1, e + 5, {'ik_sl': (-0.175, 1.47), 'ik_sr': (0.175, 1.47), 'hand_sl': -35, 'hand_sr': -35,
                             'lift': 0.075, 'squash': (0.95, 1.06), 'head': 0}, interp='BACK', easing='EASE_OUT')
    L.face(R, e + 1, eyes='wide', mouth='O', brows='surprised'); L.look(R, e + 1)
    L.pose(R, e + 10, e + 16, {'lift': 0.0, 'squash': (1.05, 0.95)}); L.pose(R, e + 16, e + 22, {'squash': (1.0, 1.0)})
    v = wf(2, 'every')                                                                             # "every single decade": worried, backs away
    L.pose(R, v - 4, v + 4, {'ik_sl': (-0.045, 1.0), 'ik_sr': (0.045, 1.0), 'hand_sl': 30, 'hand_sr': -30, 'head': 7})
    L.pose(R, v + 1, v + 2, {'front_sl': False, 'front_sr': False})
    L.face(R, v + 3, eyes='open', mouth='frown', brows='worried'); L.look(R, v + 3, dx=0.004, dz=-0.008)
    L.travel(R, v + 8, f1 + HANDLE, [(0.0, 0.0), (0.12, 0.45)])
    L.cycle(R, v + 8, f1 + HANDLE, step=10, bob=0.012, lift=0.94, sway=1.5, arms=None)
    cam = camera([(f0 - 15, (-1.35, -4.3, 1.25), (-1.4, 0.8, 1.0), 32), (f0, (-1.2, -4.1, 1.25), (-1.3, 0.7, 1.0), 32),
                  (46, (-0.3, -3.3, 1.3), (-0.05, 0.0, 1.15), 36), (75, (0.1, -2.9, 1.36), (0.0, 0.0, 1.25), 38),
                  (e + 20, (0.15, -2.85, 1.36), (0.02, 0.0, 1.25), 38), (f1 - 5, (0.55, -3.2, 1.3), (0.1, 0.25, 1.2), 38),
                  (f1 + 25, (0.75, -3.4, 1.3), (0.12, 0.3, 1.18), 37)], punch=[(e, 4)])
    W.light('living', f0, f1 + HANDLE)
    finish(R, cam, f0, f1)
    return R


# ---------------------------------------------------------------- s2 park, day
def build_s2(mood='day'):
    f0, f1 = ranges()['s2']; sc = setup(f0, f1)
    W.park(mood)
    G = W.park_ground
    R = lady((-0.55, 4.4), f0, f1)
    bl, br = bag('bag_l'), bag('bag_r'); L.hold(R, bl, 'sl', (-0.035, -0.07, -0.05)); L.hold(R, br, 'sr', (0.035, -0.07, -0.05))
    c = wf(3, 'climbs'); t = wf(3, 'trip')
    L.walk(R, f0, c, [(-0.55, 4.4), (-0.75, 2.6), (-0.75, 1.9)], step=8, ground=G, ease=(False, False), carry=True)
    L.walk(R, c, c + 26, [(-0.75, 1.9), (-0.77, 0.85)], step=7, ground=G, ease=(False, False), carry=True, lift=0.8, bob=0.03)
    L.walk(R, c + 26, t - 2, [(-0.77, 0.85), (-0.75, -0.25)], step=8, ground=G, ease=(False, True), carry=True)
    L.face(R, f0 + 2, eyes='open', mouth='smile', brows='happy'); L.look(R, f0 + 2)
    L.face(R, c, mouth='flat', brows='determined'); L.face(R, c + 28, mouth='smile', brows='happy')
    # "trip": she pitches toward the camera, arms fly up, then catches herself
    L.pose(R, t - 2, t + 3, {'arm_sl': (68, 25, 0), 'arm_sr': (68, 25, 0), 'head': 10, 'torso': -6, 'squash': (1.06, 0.92)},
           interp='BACK', easing='EASE_OUT')
    L.face(R, t, eyes='wide', mouth='O', brows='surprised')
    L.travel(R, t - 2, t + 6, [(-0.75, -0.25), (-0.72, -0.62)], ground=G, ease=(False, True))
    L.pose(R, t + 6, t + 14, {'arm_sl': (30, 12, 0), 'arm_sr': (30, 12, 0), 'head': -3, 'torso': 2, 'squash': (0.98, 1.02)},
           interp='BACK', easing='EASE_OUT')
    L.pose(R, t + 14, f1 + HANDLE, {'arm_sl': (12, 8, 0), 'arm_sr': (12, 8, 0), 'head': 0, 'torso': 0, 'squash': (1, 1)})
    L.face(R, t + 12, eyes='open', mouth='grin', brows='happy')
    cam = camera([(f0 - 15, (0.45, 0.75, 1.15), (-0.55, 4.6, 1.0), 32), (f0, (0.4, 0.55, 1.15), (-0.57, 4.3, 1.0), 32),
                  (f0 + 60, (0.25, -0.5, 1.1), (-0.7, 3.1, 1.0), 33), (c, (0.35, -1.5, 1.95), (-0.75, 1.6, 0.75), 30),
                  (c + 26, (0.1, -2.4, 1.9), (-0.77, 0.9, 1.0), 32), (t - 8, (-0.2, -3.5, 1.65), (-0.75, -0.2, 1.4), 34),
                  (f1, (-0.4, -3.4, 1.7), (-0.74, -0.5, 1.4), 36), (f1 + 25, (-0.46, -3.35, 1.72), (-0.74, -0.55, 1.4), 36)],
                 punch=[(t, 4)])
    W.light(mood, f0, f1 + HANDLE, lamp_at=(0, 40, -5), key_energy=0, window=None, shadow='LOOK_Sun')
    finish(R, cam, f0, f1, ground=G)
    return R


# ---------------------------------------------------------------- s3 gym
def build_s3():
    f0, f1 = ranges()['s3']; sc = setup(f0, f1)
    W.gym()
    spot = (0.15, 0.3)
    db_table = plyo(spot)
    R = lady((1.45, -0.15), f0, f1)
    db_hand = W.dumbbell('db_hand', (0, 0, 0)); L.hold(R, db_hand, 'sr'); F.key(db_hand, 'scale', (0, 0, 0), f0, 'CONSTANT')
    li = wf(4, 'listening'); lf = wf(4, 'lift'); tw = wf(4, 'twice'); rb = wf(5, 'rebuilding'); sv = wf(5, 'seventies')
    L.walk(R, f0, li - 4, [(1.45, -0.15), (0.8, 0.12), spot], step=7, ease=(False, True))
    L.face(R, f0 + 2, eyes='open', mouth='smile', brows='determined'); L.look(R, f0 + 2, dx=0.006)
    L.pose(R, li - 4, li + 6, {'ik_sr': (0.168, 1.63), 'hand_sr': 30, 'head': 8, 'front_sr': True}, interp='BACK', easing='EASE_OUT')
    L.face(R, li + 4, eyes='happy', mouth='grin', brows='happy')
    L.pose(R, lf - 6, lf + 3, {'ik_sr': (0.62, 0.66), 'hand_sr': 0, 'torso': 12, 'head': 6, 'squash': (1.05, 0.93),
                               'arm_sl': (14, 24, 0), 'front_sr': False})
    L.face(R, lf - 4, eyes='open', mouth='flat', brows='determined'); L.look(R, lf - 4, dx=0.009, dz=-0.006)
    swap(db_table, db_hand, lf + 4)
    L.pose(R, lf + 4, lf + 16, {'arm_sr': (9, 4, 0), 'torso': -3, 'head': -2, 'squash': (0.98, 1.02)}, interp='BACK', easing='EASE_OUT')
    L.face(R, lf + 8, eyes='closed', mouth='flat', brows='determined'); L.face(R, lf + 15, eyes='open')
    L.pose(R, lf + 16, lf + 22, {'squash': (1.0, 1.0)})
    for f in (tw - 4, tw + 8):                                                                     # "twice": two curls
        L.pose(R, f, f + 6, {'arm_sr': (12, 138, -15)}, interp='BACK', easing='EASE_OUT')
        L.face(R, f + 2, mouth='grin', brows='determined')
        L.pose(R, f + 6, f + 12, {'arm_sr': (9, 6, 0)}); L.face(R, f + 9, mouth='smile', brows='happy')
    L.xray(R, rb - 2, rb + 4)                                                                      # "rebuilding"
    for h in R['halos']: F.key(h, 'color', 0.0, rb, 'BEZIER', 'AUTO', 3); F.key(h, 'color', 0.85, rb + 10, 'BEZIER', 'AUTO', 3)
    S5.muscles(R, rb + 2, rb + 24, 1.45, 1.12, interp='BACK')
    L.pose(R, rb + 8, rb + 16, {'arm_sl': (95, 112, 15), 'arm_sr': (95, 112, 15), 'squash': (0.97, 1.04), 'head': 0},
           interp='BACK', easing='EASE_OUT')
    L.face(R, rb + 12, eyes='open', mouth='grin', brows='determined'); L.look(R, rb + 12)
    for k, f in enumerate((rb + 6, rb + 18, rb + 30)): S5.pulse(R, f, k)
    L.pose(R, sv - 6, sv, {'squash': (1.06, 0.92)})                                                # "seventies": hop
    L.pose(R, sv, sv + 7, {'lift': 0.08, 'squash': (0.95, 1.06)}, interp='BACK', easing='EASE_OUT')
    L.pose(R, sv + 7, sv + 14, {'lift': 0.0, 'squash': (1.05, 0.95)}); L.pose(R, sv + 14, sv + 22, {'squash': (1.0, 1.0)})
    L.face(R, sv + 3, eyes='happy', mouth='grin', brows='happy')
    for f, (dx, z) in ((sv + 4, (-0.62, 1.7)), (sv + 10, (0.66, 1.95)), (sv + 18, (-0.5, 2.15))):
        look.fx_sparkle((spot[0] + dx, spot[1] - 0.12, z), f)
    L.sway(R, f0, f1 + HANDLE, deg=0.8)
    cam = camera([(f0 - 15, (1.95, -3.9, 1.3), (1.5, -0.1, 1.0), 32), (f0, (1.85, -3.8, 1.3), (1.4, -0.1, 1.0), 32),
                  (li, (0.75, -3.3, 1.3), (0.35, 0.3, 1.12), 36), (lf + 2, (0.85, -3.0, 1.08), (0.55, 0.3, 0.95), 36),
                  (rb, (0.35, -2.65, 1.35), (0.25, 0.3, 1.3), 44), (sv - 4, (0.3, -2.5, 1.4), (0.2, 0.3, 1.35), 46),
                  (f1, (0.05, -3.5, 1.45), (0.2, 0.3, 1.12), 34), (f1 + 25, (-0.05, -3.7, 1.47), (0.2, 0.3, 1.1), 33)],
                 punch=[(tw, 6), (rb, 4)])
    W.light('gym', f0, f1 + HANDLE, lamp_at=(0, 0, -10), key_at=(-3.3, 0.6, 2.5), key_to=(0.3, 0.3, 1.0), key_energy=650,
            key_color=(0.95, 0.97, 1.0), key_size=2.0, window=None, shadow='key')
    finish(R, cam, f0, f1)
    return R


# ---------------------------------------------------------------- s4 park, golden hour
def build_s4():
    f0, f1 = ranges()['s4']; sc = setup(f0, f1)
    W.park('dusk')
    G = W.park_ground
    F.LIT = dict(F.LIT, tint=0.12)               # low golden sun: keep her skin her own colour (it went orange-red)
    R = lady((-0.6, 4.6), f0, f1)
    td = wf(6, 'today'); th = wf(6, 'thank')
    L.jog(R, f0, td, [(-0.6, 4.6), (-0.72, 3.0), (-0.75, 2.05)], ground=G)
    L.face(R, f0 + 2, eyes='happy', mouth='grin', brows='happy')
    L.pose(R, td, td + 8, {'arm_sr': (100, 112, 15), 'arm_sl': (12, 10, 0), 'head': -5}, interp='BACK', easing='EASE_OUT')   # flex at the camera
    L.face(R, td + 4, eyes='open', mouth='grin', brows='determined'); L.look(R, td + 4)
    L.pose(R, th - 8, th - 2, {'squash': (1.06, 0.92), 'arm_sl': (30, 20, 0)})                      # "thank you": a jump for joy
    L.pose(R, th - 2, th + 6, {'lift': 0.12, 'squash': (0.94, 1.08), 'arm_sl': (150, 10, 0), 'arm_sr': (150, 10, 0)},
           interp='BACK', easing='EASE_OUT')
    L.pose(R, th + 6, th + 14, {'lift': 0.0, 'squash': (1.06, 0.94)})
    L.pose(R, th + 14, f1 + HANDLE, {'squash': (1, 1), 'arm_sl': (95, 112, 15), 'arm_sr': (95, 112, 15)})
    L.face(R, th, eyes='happy', mouth='grin', brows='happy')
    for f, at in ((th, (-1.15, 1.95, 1.9)), (th + 6, (-0.3, 1.95, 2.05)), (th + 12, (-1.0, 1.95, 2.25))): look.fx_sparkle(at, f)
    L.sway(R, td + 10, f1 + HANDLE, deg=0.8)
    cam = camera([(f0 - 15, (0.5, 0.9, 1.05), (-0.6, 4.9, 1.0), 32), (f0, (0.45, 0.6, 1.05), (-0.6, 4.6, 1.0), 32),
                  (td, (0.1, -1.1, 1.2), (-0.74, 2.05, 1.15), 38), (th, (-0.15, -1.4, 1.35), (-0.75, 2.05, 1.25), 36),
                  (f1, (-0.4, -3.6, 2.3), (-0.72, 2.6, 1.5), 28), (f1 + 25, (-0.48, -3.9, 2.45), (-0.72, 2.7, 1.55), 27)],
                 punch=[(td, 5)])
    W.light('park_dusk', f0, f1 + HANDLE, lamp_at=(0, 40, -5), key_energy=0, window=None, shadow='LOOK_Sun')
    finish(R, cam, f0, f1, ground=G)
    return R


BUILD = {'s1': build_s1, 's2': build_s2, 's3': build_s3, 's4': build_s4}


def build(sid):
    return BUILD[sid]()


stills = S5.stills


def save_job(out, sid):
    sc = bpy.context.scene; os.makedirs(out, exist_ok=True)
    for n in ('cam3d', 'cam_target'):
        o = bpy.data.objects.get(n)
        if o: bpy.data.objects.remove(o, do_unlink=True)
    s = sc.render.image_settings
    try: s.media_type = 'VIDEO'
    except Exception: pass
    s.file_format = 'FFMPEG'; s.color_mode = 'RGB'
    f = sc.render.ffmpeg; f.format = 'MPEG4'; f.codec = 'H264'; f.constant_rate_factor = 'HIGH'; f.ffmpeg_preset = 'GOOD'; f.audio_codec = 'NONE'
    sc.render.filepath = os.path.join(out, f'{sid}_')
    job = os.path.join(out, f'job_{sid}.blend'); bpy.ops.wm.save_as_mainfile(filepath=job, copy=True)
    return job


def launch(jobs, out):
    log = os.path.join(out, 'render.log')
    parts = [f'"{bpy.app.binary_path}" -b "{j}" -a >> "{log}" 2>&1 ; echo "DONE {os.path.basename(j)}" >> "{log}"' for j in jobs]
    cmd = ' ; '.join(parts) + f' ; echo ALL_DONE >> "{log}"'
    subprocess.Popen(['/bin/bash', '-c', cmd], start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return log


if __name__ == '__main__':
    # blender -b --python scene_trial.py -- <sid> <out> [still frames...]   build one scene, save its render job, render
    # a few test stills (no MCP time limit).  Add 'render' after the frames to also render the whole clip.
    import sys, time
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    sid, out = a[0], a[1]; rest = a[2:]
    go = 'render' in rest; frames = [int(x) for x in rest if x.isdigit()]
    t0 = time.time(); build(sid); print(f'BUILT {sid} {time.time() - t0:.1f}s', flush=True)
    sc = bpy.context.scene
    print(f'RANGE {sid} {sc.frame_start} {sc.frame_end}', flush=True)
    if frames:
        t0 = time.time(); S5.stills(os.path.join(out, f'stills_{sid}'), frames)
        print(f'STILLS {sid} {(time.time() - t0) / len(frames):.1f}s/frame', flush=True)
    job = save_job(out, sid); print(f'JOB {job}', flush=True)
    if go:
        sc.render.filepath = os.path.join(out, f'{sid}_'); bpy.ops.render.render(animation=True)
        print(f'RENDERED {sid}', flush=True)
