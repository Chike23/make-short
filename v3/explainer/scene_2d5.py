"""scene_2d5.py: the 5-second 2D test (flat2d + lady2d). Voice 3.3-8.3 s of the anatomy test:
"You lose about three to eight percent every decade. But muscle never stops listening."

Beats (frames at 30 fps, frame 1 = 3.3 s): admiring her arm -> "three" (27): X-ray on, shock, jump, muscles shrink
-> "every" (58): worried -> "But" (90): whip pan, determined flex, muscles grow back and glow -> "listening" (124):
hand to ear, muscle pulses. The camera moves on every frame (rig moves + punch-ins + Camera Shakify), then it is
baked to plain keys so the background render needs no add-on.

    build(); stills(out_dir, [1, 33, 62, 95, 130]); job = save_job(out_dir); launch(job, out_dir)
"""
import bpy, math, os, random, subprocess
import flat2d as F
import lady2d as L
import camera_rig as C

FR = 150


def room():
    S, E = F.shape, F.ellipse
    S('wall', [(-5, 0.3), (5, 0.3), (5, 4.5), (-5, 4.5)], '#3c2b22', None, 3.0, smooth=False)
    S('skirting', [(-5, 0.3), (5, 0.3), (5, 0.42), (-5, 0.42)], '#2b1f19', None, 2.995, smooth=False)
    S('floor', [(-5, -1.5), (5, -1.5), (5, 0.3), (-5, 0.3)], '#5a3a28', None, 2.99, smooth=False)
    for i in range(-12, 13):                                     # floor boards, a little lighter every other
        if i % 2: S(f'board{i}', [(i * 0.4, -1.5), (i * 0.4 + 0.2, -1.5), (i * 0.4 + 0.12, 0.3), (i * 0.4 + 0.08, 0.3)], '#603f2c', None, 2.989, smooth=False)
    # window with a sunset, sun and skyline
    F.rrect('win_frame', 0.22, 0.98, 1.08, 2.24, 0.03, '#22170f', None, 2.97)
    S('win_sky', F.rrect_pts(0.28, 1.04, 1.02, 2.18, 0.01), '#ff9d5c', None, 2.965, smooth=False,
      mat=F.vgrad_mat([(0.0, '#ffb067'), (0.45, '#f07a6a'), (1.0, '#5b3f73')]))
    E('win_sun', 0.78, 1.33, 0.11, 0.11, '#ffd892', None, 2.962)
    F.glow('win_sun_glow', 0.78, 1.33, 0.4, 0.4, '#ffd892', None, 2.963, power=1.4, alpha=0.8)
    for k, (x, w, h) in enumerate([(0.3, 0.12, 0.30), (0.42, 0.1, 0.48), (0.53, 0.14, 0.22), (0.68, 0.09, 0.56),
                                   (0.79, 0.12, 0.34), (0.92, 0.1, 0.44)]):
        F.rrect(f'tower{k}', x, 1.04, x + w, 1.04 + h, 0.004, '#2a1d2c', None, 2.958)
    F.rrect('win_mull_v', 0.635, 1.04, 0.665, 2.18, 0.003, '#22170f', None, 2.955)
    F.rrect('win_mull_h', 0.28, 1.62, 1.02, 1.65, 0.003, '#22170f', None, 2.955)
    F.glow('win_glow_wall', 0.65, 1.6, 1.3, 1.2, '#ff9d5c', None, 2.985, power=2.0, alpha=0.3)
    # picture frames
    F.rrect('frame0', -1.05, 1.55, -0.5, 2.0, 0.01, '#24180f', None, 2.97); F.rrect('art0', -1.0, 1.6, -0.55, 1.95, 0.005, '#c48a5c', None, 2.965)
    F.rrect('frame1', -0.4, 1.62, -0.1, 1.9, 0.01, '#24180f', None, 2.97); F.rrect('art1', -0.36, 1.66, -0.14, 1.86, 0.005, '#6e7d78', None, 2.965)
    # floor lamp (left) with a warm pool of light
    F.glow('lamp_glow', -1.3, 1.7, 1.0, 1.0, '#ffc777', None, 2.21, power=2.0, alpha=0.4)
    F.limb('lamp_pole', (-1.3, 0.3), (-1.3, 1.62), 0.025, 0.025, '#2b231d', None, 2.2)
    E('lamp_base', -1.3, 0.31, 0.14, 0.03, '#2b231d', None, 2.2)
    S('lamp_shade', [(-1.47, 1.58), (-1.13, 1.58), (-1.19, 1.86), (-1.41, 1.86)], '#ffe1ae', None, 2.19, smooth=False)
    # sofa (right), side table and plant (left)
    F.rrect('sofa_back', 0.5, 0.3, 1.7, 0.98, 0.1, '#4d6a4a', None, 1.6)
    F.rrect('sofa_seat', 0.45, 0.3, 1.75, 0.62, 0.08, '#5a7a56', None, 1.59)
    F.rrect('sofa_arm_l', 0.38, 0.3, 0.58, 0.76, 0.08, '#4d6a4a', None, 1.58)
    F.rrect('sofa_arm_r', 1.62, 0.3, 1.82, 0.76, 0.08, '#4d6a4a', None, 1.58)
    E('cushion', 0.8, 0.76, 0.14, 0.1, '#c87a4a', None, 1.585)
    F.rrect('table', -0.82, 0.3, -0.46, 0.62, 0.02, '#4a3021', None, 1.2)
    F.rrect('pot', -0.71, 0.62, -0.55, 0.78, 0.02, '#b5653f', None, 1.19)
    for k, (x, z, rx, rz) in enumerate([(-0.63, 0.92, 0.07, 0.16), (-0.72, 0.88, 0.06, 0.12), (-0.55, 0.88, 0.06, 0.12), (-0.63, 1.04, 0.05, 0.1)]):
        E(f'leaf{k}', x, z, rx, rz, '#3f6b45' if k % 2 else '#4f7f52', None, 1.185 - k * 0.001)
    # rug under her feet
    E('rug', 0, 0.02, 0.9, 0.14, '#b0967a', None, 0.08)


def dust(n=26, seed=3):
    rnd = random.Random(seed)
    for i in range(n):
        x, z, d = rnd.uniform(-0.9, 0.7), rnd.uniform(0.7, 2.3), rnd.uniform(-0.4, 1.4)
        o = F.ellipse(f'dust{i}', x, z, 0.008, 0.008, '#ffe0b0', None, d, alpha=rnd.uniform(0.2, 0.5))
        F.key(o, 'location', o.location[0], 1, 'LINEAR', 'AUTO', 0); F.key(o, 'location', o.location[0] + rnd.uniform(0.03, 0.09), FR, 'LINEAR', 'AUTO', 0)
        F.key(o, 'location', o.location[2], 1, 'LINEAR', 'AUTO', 2); F.key(o, 'location', o.location[2] + rnd.uniform(0.02, 0.07), FR, 'LINEAR', 'AUTO', 2)


def muscles(R, f0, f1, sx, sz, interp='BEZIER'):
    for n in ('bicep_sl', 'bicep_sr', 'forem_sl', 'forem_sr', 'quad_sl', 'quad_sr'):
        j = R['j'][n]
        for i, v in ((0, sx), (2, sz)):
            F.key(j, 'scale', F.now(j, 'scale', f0, i), f0, interp, 'AUTO', i); F.key(j, 'scale', v, f1, 'BEZIER', 'AUTO', i)


def pulse(R, f, k):
    for side in ('sl', 'sr'):
        rj, rg = [r for r in R['rings'] if r[0].name.endswith(f'ringj{k}_{side}')][0]
        F.key(rj, 'scale', (0.3, 0.3, 0.3), f, 'BEZIER'); F.key(rj, 'scale', (2.3, 2.3, 2.3), f + 16, 'BEZIER')
        F.key(rg, 'color', 0.0, f - 1, 'CONSTANT', 'AUTO', 3); F.key(rg, 'color', 0.9, f, 'BEZIER', 'AUTO', 3); F.key(rg, 'color', 0.0, f + 16, 'BEZIER', 'AUTO', 3)
    for h in R['halos']:
        F.key(h, 'color', 0.6, f - 1, 'BEZIER', 'AUTO', 3); F.key(h, 'color', 1.0, f + 2, 'BEZIER', 'AUTO', 3); F.key(h, 'color', 0.6, f + 9, 'BEZIER', 'AUTO', 3)


def animate(R):
    L.sway(R, 1, FR)
    # 1-26 "You lose about": admiring her flexed arm, pleased
    L.pose(R, -12, -10, {'arm_sl': (78, 100, 10), 'arm_sr': (8, 6, 0), 'head': -5})
    L.face(R, 1, eyes='open', mouth='smile', brows='happy'); L.look(R, 1, dx=-0.007, dz=0.004)
    L.pose(R, 7, 13, {'arm_sl': (84, 114, 14)}); L.pose(R, 13, 19, {'arm_sl': (78, 98, 8)})
    L.blink(R, 15)
    L.pose(R, 21, 26, {'squash': (1.03, 0.97), 'head': -2})                      # anticipation
    L.face(R, 25, brows='neutral'); L.look(R, 25)
    # 27 "three": X-ray, shock (hands to cheeks), jump with stretch, muscles shrink
    L.xray(R, 27, 32)
    L.pose(R, 26, 27, {'front_sl': True, 'front_sr': True})
    L.pose(R, 27, 33, {'ik_sl': (-0.175, 1.47), 'ik_sr': (0.175, 1.47), 'hand_sl': -35, 'hand_sr': -35,
                       'lift': 0.075, 'squash': (0.95, 1.06), 'head': 0}, interp='BACK', easing='EASE_OUT')
    L.face(R, 29, eyes='wide', mouth='O', brows='surprised')
    L.pose(R, 38, 44, {'lift': 0.0, 'squash': (1.05, 0.95)})
    L.pose(R, 44, 50, {'squash': (1.0, 1.0)})
    muscles(R, 30, 64, 0.55, 0.9)
    # 58 "every decade": worried, hands wringing in front, head down
    L.pose(R, 52, 60, {'ik_sl': (-0.045, 1.0), 'ik_sr': (0.045, 1.0), 'hand_sl': 30, 'hand_sr': -30, 'head': 7,
                       'squash': (1.02, 0.97)})
    L.pose(R, 57, 58, {'front_sl': False, 'front_sr': False})
    L.face(R, 59, eyes='open', mouth='frown', brows='worried'); L.look(R, 59, dx=0.004, dz=-0.008)
    L.pose(R, 66, 74, {'ik_sl': (-0.03, 1.03), 'ik_sr': (0.06, 0.98)}); L.pose(R, 74, 82, {'ik_sl': (-0.05, 0.99), 'ik_sr': (0.04, 1.01)})
    L.blink(R, 72)
    L.pose(R, 83, 89, {'squash': (1.05, 0.94), 'head': 2})                      # anticipation
    # 90 "But": determined flex, hand on hip, muscles grow back with overshoot and glow
    L.pose(R, 89, 96, {'arm_sl': (95, 108, 15), 'ik_sr': (0.2, 0.99), 'hand_sr': -40, 'squash': (0.97, 1.04), 'head': -6},
           interp='BACK', easing='EASE_OUT')
    L.pose(R, 96, 104, {'squash': (1.0, 1.0)})
    L.face(R, 91, eyes='open', mouth='grin', brows='determined'); L.look(R, 91, dx=-0.007, dz=0.004)
    muscles(R, 90, 100, 1.25, 1.08, interp='BACK')
    for h in R['halos']:
        F.key(h, 'color', 0.0, 90, 'BEZIER', 'AUTO', 3); F.key(h, 'color', 0.9, 96, 'BEZIER', 'AUTO', 3); F.key(h, 'color', 0.6, 104, 'BEZIER', 'AUTO', 3)
    # 107 "never": a firm nod
    L.pose(R, 104, 108, {'head': -1}); L.pose(R, 108, 113, {'head': -7})
    # 118-124 "listening": right hand cups her ear, head tilts to it, delighted; the flexed arm pumps
    L.pose(R, 114, 115, {'front_sr': True})
    L.pose(R, 115, 123, {'ik_sr': (0.168, 1.63), 'hand_sr': 30, 'head': 8}, interp='BACK', easing='EASE_OUT')
    L.face(R, 121, eyes='happy', mouth='grin', brows='happy')
    for k, f in enumerate(range(124, FR, 8)):
        L.pose(R, f, f + 4, {'arm_sl': (95, 120 if k % 2 == 0 else 104, 15)})
    for k, f in enumerate((124, 134, 144)): pulse(R, f, k)


def camera():
    sc = bpy.context.scene
    rig = bpy.data.objects.new('cam_rig', None); sc.collection.objects.link(rig); rig.rotation_mode = 'XYZ'
    cd = bpy.data.cameras.new('cam2d'); cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 36; cd.lens = 50; cd.clip_start = 0.05
    cam = bpy.data.objects.new('cam2d', cd); sc.collection.objects.link(cam)
    cam.parent = rig; cam.rotation_euler = (math.pi / 2, 0, 0); sc.camera = cam
    def at(f, x, y, z, roll=None, interp='BEZIER', easing='AUTO'):
        for i, v in enumerate((x, y, z)): F.key(rig, 'location', v, f, interp, easing, i)
        if roll is not None: F.key(rig, 'rotation_euler', math.radians(roll), f, interp, easing, 1)
    def lens(f, v, interp='BEZIER', easing='AUTO'): F.key(cd, 'lens', v, f, interp, easing)
    at(-15, -0.10, -2.8, 1.36, 0); at(1, -0.12, -2.75, 1.36, 0); lens(1, 50)   # already moving on frame 1
    at(26, -0.15, -2.63, 1.35)
    lens(27, 50); lens(31, 57); lens(46, 55)                                  # punch-in on "three"
    at(33, -0.155, -2.6, 1.38, -0.5); at(46, -0.16, -2.58, 1.34)               # rides the jump
    at(86, -0.16, -2.5, 1.33, -1.8, interp='BEZIER', easing='EASE_IN')        # slow push while she worries
    lens(86, 56, easing='EASE_IN')
    at(90, 0.06, -2.5, 1.32, 3.0, interp='BACK', easing='EASE_OUT')           # whip pan on "But"
    lens(93, 61); lens(106, 58)
    at(100, -0.03, -2.52, 1.32, 0.5)
    at(150, 0.0, -2.62, 1.35, 1.5)                                          # slow pull out to the end
    lens(150, 55)
    C.add_shake(cam, 'THE_WEDDING', 0.6)
    return cam


def build():
    sc = F.setup(FR)
    room(); dust()
    R = L.build('lady', at=(0.0, 0.0))
    animate(R)
    cam = camera()
    baked = F.bake_camera(cam, 'cam2d_baked')
    sc.camera = baked
    return R


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


def save_job(out):
    sc = bpy.context.scene; os.makedirs(out, exist_ok=True)
    for n in ('cam2d', 'cam_rig'):                       # the shaky source camera stays out of the job file
        o = bpy.data.objects.get(n)
        if o: bpy.data.objects.remove(o, do_unlink=True)
    s = sc.render.image_settings
    try: s.media_type = 'VIDEO'
    except Exception: pass
    s.file_format = 'FFMPEG'; s.color_mode = 'RGB'
    f = sc.render.ffmpeg; f.format = 'MPEG4'; f.codec = 'H264'; f.constant_rate_factor = 'HIGH'; f.ffmpeg_preset = 'GOOD'; f.audio_codec = 'NONE'
    sc.render.filepath = os.path.join(out, 'lady2d_')
    job = os.path.join(out, 'job_2d5.blend'); bpy.ops.wm.save_as_mainfile(filepath=job, copy=True)
    return job


def launch(job, out):
    log = os.path.join(out, 'render.log')
    cmd = f'"{bpy.app.binary_path}" -b "{job}" -a > "{log}" 2>&1 ; echo ALL_DONE >> "{log}"'
    subprocess.Popen(['/bin/bash', '-c', cmd], start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return log
