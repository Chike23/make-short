"""The 14 s test, animated. Run in Blender after kit.py and rig.py (same namespace):
    build(P, glb)     -> the whole scene: room, stage, the rigged lead, X-ray, cameras, motion, face
    jobs = save_jobs(P)  -> one .blend per shot (+ X-ray passes), each with its camera and frame range
    launch(jobs, P)   -> renders them one after another in a background Blender (videos in P/renders/anim/)
Frames are global (Blender frame = 1 + video frame at 30 fps). Shots (from the voice timing):
  s01 1-110 FS living room, talking | s02 101-194 MS, X-ray from ~3.8 s | s03 184-253 the dumbbell on the stage |
  s04 243-421 MS, curls with the dumbbell, X-ray arm from ~10.9 s.  A few frames overlap at each cut for crossfades."""
import bpy, os, json, math, subprocess

AT, ROT, SCALE = (-0.25, -0.15, 0.0), 0.35, 0.92
SHOTS = {
    's01': dict(frames=(1, 110), cam=((0.3, -3.1, 1.3), (-0.2, 0.0, 1.0), (0.15, -2.6, 1.3), (-0.22, -0.05, 1.08), 34)),
    's02': dict(frames=(101, 194), cam=((0.05, -1.95, 1.36), (-0.22, -0.1, 1.33), (0.0, -1.72, 1.37), (-0.23, -0.1, 1.35), 40), xray=(110, 194)),
    's03': dict(frames=(184, 253), cam=((30.05, -0.85, 0.62), (30.0, 0.02, 0.1), (30.04, -0.68, 0.52), (30.0, 0.02, 0.1), 42)),
    's04': dict(frames=(243, 421), cam=((0.0, -1.7, 1.3), (-0.25, -0.1, 1.3), (0.02, -1.95, 1.31), (-0.25, -0.1, 1.28), 40), xray=(320, 421)),
}


def build(P, glb, cues_json):
    sc = reset()
    for a in list(bpy.data.actions): bpy.data.actions.remove(a)
    sc.render.fps = 30; sc.frame_start, sc.frame_end = 1, 421
    # animation renders at the reference's own size (Instagram serves 720x1280); compose.py scales to 1080x1920.
    # About 8 s a frame at 1080x1920 with ray tracing on an M1, so: 720x1280, 12 samples, no ray tracing.
    for k, v in dict(taa_render_samples=12, use_raytracing=False, shadow_ray_count=1, shadow_step_count=6).items():
        try: setattr(sc.eevee, k, v)
        except Exception: pass
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 720, 1280, 100
    living_room(); stage((30, 0, 0))
    rig = load_rig(glb)
    for tr in list(rig.animation_data.nla_tracks): rig.animation_data.nla_tracks.remove(tr)
    build_lead(rig); build_xray_on(rig)
    place(rig, AT, ROT, SCALE)
    # motion: talking while she explains, then curls in s04
    play(rig, 'Idle_Talking_Loop', 1, 250)
    play(rig, 'Idle_Loop', 243, 421)
    curl(rig, 250, 421, 3)
    # dumbbell: on the stage (s03) and in her right hand (s04)
    db = dumbbell((30, 0.0, 0.06), (0, 0, math.radians(-25)), name='db_stage', c='STAGE')
    db.keyframe_insert('rotation_euler', frame=184); db.rotation_euler = (0, 0, math.radians(-8)); db.keyframe_insert('rotation_euler', frame=253)
    rig.data.pose_position = 'REST'; bpy.context.view_layer.update()
    hb = rig.data.bones['DEF-hand.R']; hp = rig.matrix_world @ hb.tail_local
    hand_db = dumbbell(tuple(hp), (0, 0, math.radians(90)), name='db_hand', c='PROPS', scale=0.75)   # bar across the grip
    _to_bone(hand_db, rig, 'DEF-hand.R')
    rig.data.pose_position = 'POSE'
    # face: talking mouth from the voice, blinks
    cj = json.load(open(cues_json))
    mouth('lead', cj['cues']); blinks('lead', cj['blinks'])
    # cameras, one per shot, each with a slow move
    for sid, s in SHOTS.items():
        l0, t0, l1, t1, lens = s['cam']
        cam = camera(l0, t0, lens, name='cam_' + sid)
        cam_move(cam, s['frames'][0], s['frames'][1], l0, l1, t0, t1)
    return rig


def _video(sc, path, alpha=False):
    s = sc.render.image_settings
    try: s.media_type = 'VIDEO'
    except Exception: pass
    s.file_format = 'FFMPEG'
    f = sc.render.ffmpeg
    if alpha:
        f.format = 'QUICKTIME'; f.codec = 'QTRLE'; s.color_mode = 'RGBA'
    else:
        f.format = 'MPEG4'; f.codec = 'H264'; f.constant_rate_factor = 'HIGH'; f.ffmpeg_preset = 'GOOD'; s.color_mode = 'RGB'
    f.audio_codec = 'NONE'
    sc.render.filepath = path


def save_jobs(P):
    sc = bpy.context.scene; out = os.path.join(P, 'renders', 'anim'); os.makedirs(out, exist_ok=True)
    jobs = []
    for sid, s in SHOTS.items():
        sc.camera = bpy.data.objects['cam_' + sid]
        sc.frame_start, sc.frame_end = s['frames']
        bpy.data.objects['db_hand'].hide_render = sid != 's04'
        for ch in bpy.data.objects['db_hand'].children: ch.hide_render = sid != 's04'
        sc.render.film_transparent = False
        _video(sc, os.path.join(out, f'{sid}_'))
        f = os.path.join(out, f'job_{sid}.blend'); bpy.ops.wm.save_as_mainfile(filepath=f, copy=True); jobs.append(f)
        if 'xray' in s:                       # X-ray pass: same camera, transparent, room hidden, body ghosted, face/hair hidden
            sc.frame_start, sc.frame_end = s['xray']
            saved = {n: coll(n).hide_render for n in ('ROOM', 'STAGE', 'PROPS', 'XRAY')}
            for n in ('ROOM', 'STAGE', 'PROPS'): coll(n).hide_render = True
            coll('XRAY').hide_render = False
            ghost = mat('ghost', hexrgb('#3a4660'), 0.6, 0, alpha=0.38)
            swaps, hidden = [], []
            for o in coll('PERSON').objects:
                if o.type != 'MESH' or o.hide_render: continue
                if any(k in o.name for k in FACE_PARTS): o.hide_render = True; hidden.append(o); continue
                swaps.append((o, list(o.data.materials)))
                for i in range(len(o.data.materials)): o.data.materials[i] = ghost
            sc.render.film_transparent = True
            _video(sc, os.path.join(out, f'{sid}x_'), alpha=True)
            f = os.path.join(out, f'job_{sid}x.blend'); bpy.ops.wm.save_as_mainfile(filepath=f, copy=True); jobs.append(f)
            for o, ms in swaps:
                for i, m in enumerate(ms): o.data.materials[i] = m
            for o in hidden: o.hide_render = False
            for n, v in saved.items(): coll(n).hide_render = v
            sc.render.film_transparent = False
    return jobs


def launch(jobs, P):
    bl = bpy.app.binary_path; log = os.path.join(P, 'renders', 'anim', 'render.log')
    chain = ' ; '.join(f'"{bl}" -b "{j}" -a >> "{log}" 2>&1 ; echo DONE {os.path.basename(j)} >> "{log}"' for j in jobs)
    subprocess.Popen(['/bin/bash', '-c', chain + f' ; echo ALL_DONE >> "{log}"'], start_new_session=True,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return log
