"""camera_rig.py: cameras that never stop (house rule: the camera moves on every frame).

Every shot camera gets a planned move (push, pull, orbit, crane, pan) keyed with smooth ease, plus recorded handheld
shake from the Camera Shakify add-on on top, plus optional punch-ins (a quick lens push) on key words.

    from camera_rig import shot_cam
    cam = shot_cam('s01', target=(0, 0, 1.4), f0=1, f1=66, move='orbit', dist=2.2, height=1.5, lens=50,
                   swing=25, punch=[30], shake='THE_WEDDING')

Moves (all relative to `target`, the point the camera looks at):
  push   dolly in by `amount` of the distance      pull   dolly out by `amount`
  orbit  swing `swing` degrees around the target   crane  rise by `rise` metres while pushing a little
  pan    slide sideways by `slide` metres
Before saving a render job, call prep_for_background() so the shake renders without the add-on UI.
"""
import bpy, math
from mathutils import Vector


def _look(cam, target):
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat('-Z', 'Y').to_euler()


def _ease_keys(obj):
    ad = obj.animation_data
    if not ad or not ad.action: return
    try:
        curves = ad.action.fcurves
    except AttributeError:                                  # Blender 5 layered actions
        curves = [c for l in ad.action.layers for s in l.strips for b in s.channelbags for c in b.fcurves]
    for fc in curves:
        for k in fc.keyframe_points:
            k.interpolation = 'BEZIER'; k.easing = 'AUTO'; k.handle_left_type = k.handle_right_type = 'AUTO_CLAMPED'


def shot_cam(name, target, f0, f1, move='push', dist=2.5, height=None, lens=50, angle=0.0, amount=0.18, swing=20,
             rise=0.4, slide=0.5, punch=(), punch_amount=0.18, shake='THE_WEDDING', shake_scale=1.0, steps=6):
    """One camera for frames f0..f1. angle: degrees around the target (0 = from the front, -Y). Returns the camera."""
    sc = bpy.context.scene
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 36
    cam = bpy.data.objects.new(name, cd); sc.collection.objects.link(cam)
    tgt = Vector(target); h = tgt.z if height is None else height
    for i in range(steps + 1):
        u = i / steps; f = round(f0 + (f1 - f0) * u)
        a, d, z, sx = angle, dist, h, 0.0
        if move == 'push': d = dist * (1 - amount * u)
        elif move == 'pull': d = dist * (1 - amount) + dist * amount * u
        elif move == 'orbit': a = angle - swing / 2 + swing * u; d = dist * (1 - 0.06 * u)
        elif move == 'crane': z = h + rise * u; d = dist * (1 - 0.08 * u)
        elif move == 'pan': sx = -slide / 2 + slide * u
        r = math.radians(a)
        cam.location = (tgt.x + d * math.sin(r) + sx * math.cos(r), tgt.y - d * math.cos(r) + sx * math.sin(r), z)
        _look(cam, (tgt.x + sx * math.cos(r), tgt.y + sx * math.sin(r), tgt.z))
        cam.keyframe_insert('location', frame=f); cam.keyframe_insert('rotation_euler', frame=f)
    _ease_keys(cam)
    # punch-ins: the lens jumps in over 4 frames on a key word and settles back over 14
    cd.keyframe_insert('lens', frame=f0); cd.keyframe_insert('lens', frame=f1)
    for p in punch:
        cd.lens = lens; cd.keyframe_insert('lens', frame=p - 2)
        cd.lens = lens * (1 + punch_amount); cd.keyframe_insert('lens', frame=p + 3)
        cd.lens = lens * (1 + punch_amount * 0.7); cd.keyframe_insert('lens', frame=p + 16)
    cd.lens = lens
    if shake: add_shake(cam, shake, shake_scale)
    return cam


def add_shake(cam, kind='THE_WEDDING', scale=1.0, speed=1.0):
    for o in bpy.context.selected_objects: o.select_set(False)
    bpy.context.view_layer.objects.active = cam; cam.select_set(True)
    bpy.ops.object.camera_shake_add()
    s = cam.camera_shakes[len(cam.camera_shakes) - 1]
    s.shake_type = kind; s.scale = scale; s.speed = speed
    return s


def prep_for_background():
    """Camera Shakify's own 'prep file for render farm': the shake then renders in `blender -b` without the add-on."""
    try: bpy.ops.wm.camera_shakify_prep_file_for_farm()
    except Exception as e: print('camera_rig: prep_for_background:', e)


def use_camera_at(cams):
    """Switch the scene camera per shot with timeline markers: cams = [(frame, camera), ...]."""
    sc = bpy.context.scene
    for m in [m for m in sc.timeline_markers if m.name.startswith('cam_')]: sc.timeline_markers.remove(m)
    for f, cam in cams:
        m = sc.timeline_markers.new(f'cam_{cam.name}', frame=f); m.camera = cam
