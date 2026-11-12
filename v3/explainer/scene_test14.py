"""The 14 s test Short: 4 shots. Run in Blender after kit.py:  exec(kit); exec(this); shoot('s01') ... or shoot_all().
Writes renders/<id>.png (+ <id>_xray.png) at 1350x2400 into OUT."""
import os, math, time
OUT = os.path.expanduser('~/Downloads/make-short-test/renders')
AT, ROT = (-0.25, -0.15, 0.0), 0.35            # where the lead stands in the living room


def _room(pose):
    sc = reset(); living_room(); person(pose, AT, ROT); xray(pose, AT, ROT, muscles=('thigh', 'arm') if pose == 'stand' else ('arm',))
    return sc


def shoot(sid, pct=100):
    t = time.time()
    if sid == 's01':                                   # FS in the living room
        sc = _room('stand'); camera((0.3, -3.1, 1.3), (-0.2, 0.0, 1.0), 34)
    elif sid == 's02':                                 # MS, X-ray layer
        sc = _room('stand'); camera((0.05, -1.9, 1.38), (-0.22, -0.1, 1.34), 40)
    elif sid == 's03':                                 # the dumbbell on the dark stage
        sc = reset(); stage((30, 0, 0)); dumbbell((30, 0.0, 0.06), (0, 0, math.radians(-25)), c='STAGE')
        camera((30.05, -0.85, 0.62), (30.0, 0.02, 0.1), 42)
    elif sid == 's04':                                 # MS, curl with the dumbbell, X-ray arm
        sc = _room('curl'); hp = hand_pos('curl', AT, ROT, 'R')
        dumbbell(tuple(hp), (0, 0, ROT), c='PERSON', scale=0.8)
        camera((0.0, -1.75, 1.32), (-0.25, -0.1, 1.33), 40)
    sc.render.resolution_percentage = pct
    render(f'{OUT}/{sid}.png')
    if sid in ('s02', 's04'): render_layer(f'{OUT}/{sid}_xray.png')
    return round(time.time() - t, 1)


def shoot_all(pct=100):
    return {s: shoot(s, pct) for s in ('s01', 's02', 's03', 's04')}
