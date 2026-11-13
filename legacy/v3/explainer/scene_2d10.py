"""scene_2d10.py: 10-second test, a 2D character in a painted 3D world (voice 3.3-13.3 s of the anatomy test).

"You lose about three to eight percent every decade. But muscle never stops listening. Lift something heavy just
twice a week, and it starts rebuilding, even in your seventies."

The lady is the flat cut-out puppet (lady2d), lit by the room's lights (flat2d MODE 'lit') and casting a shadow;
the room is 3D in the skill's own toon look (world3d + lib/look.py). Frames 1-150 replay scene_2d5's performance;
151-300: she lifts a dumbbell off a side table, curls it twice, the X-ray comes back as her muscles rebuild, and she
celebrates. The camera moves through the room on every frame (track-to moves, punch-ins, Camera Shakify), baked.
"""
import bpy, math, os, subprocess
from mathutils import Vector
import flat2d as F
import lady2d as L
import world3d as W
import scene_2d5 as S5
import look

FR = 300
HAND_AT = (0.44, 0.08, 0.74)        # where her reaching hand lands: the dumbbell sits there on the side table


def props():
    root = W.furniture('side_table_01', (HAND_AT[0] + 0.05, 0.22, 0), 0, 1.0)
    bpy.context.view_layer.update()
    top = max((o.matrix_world @ Vector(c)).z for o in root.children_recursive if o.type == 'MESH' for c in o.bound_box)
    sz = (HAND_AT[2] - 0.05) / max(top, 0.1); root.scale = (1, 1, sz)            # table top just under the dumbbell
    db_table = W.dumbbell('db_table', (HAND_AT[0], HAND_AT[1] + 0.02, HAND_AT[2] - 0.005), (0, 0, math.radians(8)))
    return db_table


def hand_dumbbell(R):
    j = R['j']['hand_sr']; px, pz = j['pivot']
    e = W.dumbbell('db_hand', (0, 0, 0), c='WORLD')
    e.parent = j; e.location = (0.2 - px, -0.06, 0.795 - pz); e.matrix_parent_inverse.identity()
    return e


def swap(a, b, f):
    """Hide a, show b from frame f (the dumbbell leaves the table and is in her hand)."""
    F.key(a, 'scale', (1, 1, 1), f - 1, 'CONSTANT'); F.key(a, 'scale', (0, 0, 0), f, 'CONSTANT')
    F.key(b, 'scale', (0, 0, 0), f - 1, 'CONSTANT'); F.key(b, 'scale', (1, 1, 1), f, 'CONSTANT')


def animate2(R, db_table, db_hand):
    S = S5
    # 146-152: X-ray and glow off, she turns to the table
    L.xray(R, 146, 152, on=False)
    for h in R['halos']: F.key(h, 'color', F.now(h, 'color', 146, 3), 146, 'BEZIER', 'AUTO', 3); F.key(h, 'color', 0.0, 152, 'BEZIER', 'AUTO', 3)
    L.face(R, 150, eyes='open', mouth='flat', brows='determined'); L.look(R, 150, dx=0.009, dz=-0.006)
    # 149 "Lift": lean over and reach for the dumbbell
    L.pose(R, 148, 157, {'ik_sr': (0.62, 0.66), 'hand_sr': 0, 'torso': 12, 'head': 8, 'squash': (1.05, 0.93),
                          'arm_sl': (14, 24, 0)})
    L.pose(R, 152, 153, {'front_sr': False})
    swap(db_table, db_hand, 158)
    # 158-172 "something heavy": hauls it up, straining
    L.pose(R, 158, 172, {'arm_sr': (9, 4, 0), 'torso': -3, 'head': -2, 'squash': (0.98, 1.02)}, interp='BACK', easing='EASE_OUT')
    L.face(R, 164, eyes='closed', mouth='flat', brows='determined'); L.face(R, 172, eyes='open')
    L.pose(R, 168, 172, {'squash': (1.06, 0.94)}); L.pose(R, 172, 177, {'squash': (1.0, 1.0)})
    L.look(R, 174, dx=0.007, dz=-0.004)
    # 178-200 "just twice a week": two curls, effort up, smile down
    for k, f in enumerate((177, 189)):
        L.pose(R, f, f + 6, {'arm_sr': (12, 138, -15)}, interp='BACK', easing='EASE_OUT')
        L.face(R, f + 2, eyes='open', mouth='grin', brows='determined')
        L.pose(R, f + 6, f + 12, {'arm_sr': (9, 6, 0)})
        L.face(R, f + 9, mouth='smile', brows='happy')
    L.pose(R, 200, 205, {'head': -6}); L.pose(R, 205, 210, {'head': 2})                 # proud nod
    # 209-236 "and it starts rebuilding": X-ray back on, muscles grow and glow, double flex
    L.xray(R, 211, 217)
    for h in R['halos']: F.key(h, 'color', 0.0, 214, 'BEZIER', 'AUTO', 3); F.key(h, 'color', 0.85, 224, 'BEZIER', 'AUTO', 3)
    S.muscles(R, 216, 238, 1.45, 1.12, interp='BACK')
    L.pose(R, 224, 232, {'arm_sl': (95, 112, 15), 'arm_sr': (95, 112, 15), 'squash': (0.97, 1.04), 'head': 0},
           interp='BACK', easing='EASE_OUT')
    L.face(R, 230, eyes='open', mouth='grin', brows='determined'); L.look(R, 230)
    for k, f in enumerate((222, 234, 246)): S.pulse(R, f, k)
    # 252-300 "even in your seventies": a little hop, delighted, sparkles
    L.pose(R, 252, 258, {'squash': (1.06, 0.92)})
    L.pose(R, 258, 265, {'lift': 0.08, 'squash': (0.95, 1.06)}, interp='BACK', easing='EASE_OUT')
    L.pose(R, 265, 272, {'lift': 0.0, 'squash': (1.05, 0.95)}); L.pose(R, 272, 280, {'squash': (1.0, 1.0)})
    L.face(R, 262, eyes='happy', mouth='grin', brows='happy')
    for k, f in enumerate(range(282, FR + 10, 10)):
        L.pose(R, f, f + 5, {'arm_sl': (95, 120 if k % 2 == 0 else 104, 15), 'arm_sr': (95, 104 if k % 2 == 0 else 120, 15)})
    for f, at in ((262, (-0.38, -0.12, 1.75)), (268, (0.42, -0.12, 1.85)), (276, (-0.3, -0.12, 2.0)), (284, (0.35, -0.12, 1.6))):
        look.fx_sparkle(at, f)


# camera: (frame, position, look-at, lens); keys before 1 and after the end keep it moving on every frame
SHOT = [(-15, (0.40, -4.7, 1.30), (0.06, 0, 1.05), 30), (1, (0.30, -4.4, 1.30), (0.0, 0, 1.05), 30),
        (26, (0.02, -3.2, 1.36), (-0.02, 0, 1.25), 38), (33, (-0.10, -3.0, 1.38), (0.0, 0, 1.3), None),
        (86, (-0.45, -2.85, 1.35), (-0.05, 0, 1.28), 44), (90, (0.45, -2.8, 1.33), (0.15, 0, 1.28), None),
        (100, (0.25, -2.75, 1.33), (0.05, 0, 1.28), 46), (122, (0.12, -2.55, 1.36), (0.02, 0, 1.32), 48),
        (146, (0.25, -2.7, 1.30), (0.06, 0, 1.25), 46), (166, (0.60, -3.35, 0.98), (0.22, 0, 0.95), 35),
        (185, (0.48, -3.05, 1.05), (0.2, 0, 1.0), None), (209, (0.22, -2.9, 1.2), (0.05, 0, 1.2), 40),
        (236, (0.05, -2.5, 1.32), (0.0, 0, 1.3), 46), (252, (0.02, -2.6, 1.33), (0.0, 0, 1.28), None),
        (300, (-0.35, -4.2, 1.6), (0.0, 0, 1.1), 30), (315, (-0.42, -4.35, 1.66), (0.0, 0, 1.08), 29)]
PUNCH = [(27, 6), (185, 6), (234, 4)]          # (frame, lens mm added) quick push-ins on key words


def camera():
    sc = bpy.context.scene
    tgt = bpy.data.objects.new('cam_target', None); sc.collection.objects.link(tgt)
    cd = bpy.data.cameras.new('cam3d'); cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 36; cd.clip_start = 0.05
    cam = bpy.data.objects.new('cam3d', cd); sc.collection.objects.link(cam)
    tc = cam.constraints.new('TRACK_TO'); tc.target = tgt; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
    for f, p, t, lens in SHOT:
        interp, ease = ('BACK', 'EASE_OUT') if f == 90 else ('BEZIER', 'AUTO')
        for i in range(3):
            F.key(cam, 'location', p[i], f, interp, ease, i); F.key(tgt, 'location', t[i], f, interp, ease, i)
        if lens: F.key(cd, 'lens', lens, f)
    for f, add in PUNCH:
        base = F.now(cd, 'lens', f)
        F.key(cd, 'lens', base, f - 1); F.key(cd, 'lens', base + add, f + 4); F.key(cd, 'lens', base + add * 0.6, f + 16)
    sc.camera = cam
    import camera_rig as C
    C.add_shake(cam, 'THE_WEDDING', 0.6)
    return cam


def build():
    sc = F.setup(FR, res=(720, 1280), samples=12)
    try: sc.render.image_settings.media_type = 'IMAGE'      # Blender 5: a video output left from a job blocks PNG
    except Exception: pass
    look.setup_render(sc, 720, 1280)
    sc.eevee.taa_render_samples = 12
    sc.render.use_motion_blur = True; sc.frame_start, sc.frame_end = 1, FR
    F.MODE = 'lit'
    W.grade(); W.living_room()
    db_table = props()
    R = L.build('lady', at=(0.0, 0.0)); L.shadows(R)
    db_hand = hand_dumbbell(R); F.key(db_hand, 'scale', (0, 0, 0), 1, 'CONSTANT')
    S5.animate(R)
    animate2(R, db_table, db_hand)
    L.blob_shadow(R, frames=(1, FR))
    W.light('living', 1, FR)
    W.set_kuwahara(1, (1, FR))
    cam = camera()
    baked = F.bake_camera(cam, 'cam3d_baked'); sc.camera = baked
    L.face_camera(R, baked)                    # always head-on to the camera
    return R


def save_job(out):
    sc = bpy.context.scene; os.makedirs(out, exist_ok=True)
    for n in ('cam3d', 'cam_target'):
        o = bpy.data.objects.get(n)
        if o: bpy.data.objects.remove(o, do_unlink=True)
    s = sc.render.image_settings
    try: s.media_type = 'VIDEO'
    except Exception: pass
    s.file_format = 'FFMPEG'; s.color_mode = 'RGB'
    f = sc.render.ffmpeg; f.format = 'MPEG4'; f.codec = 'H264'; f.constant_rate_factor = 'HIGH'; f.ffmpeg_preset = 'GOOD'; f.audio_codec = 'NONE'
    sc.render.filepath = os.path.join(out, 'lady3d_')
    job = os.path.join(out, 'job_2d10.blend'); bpy.ops.wm.save_as_mainfile(filepath=job, copy=True)
    return job


stills = S5.stills
launch = S5.launch
