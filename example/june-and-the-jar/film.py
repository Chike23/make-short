"""film.py: "June and the jar", the 62 s example Short (16 shots, 8 places), built with the make-short kit.

Story: at 62 June can't open a pickle jar; muscle fades after 40; the stairs, the bags and the sofa get harder; a
fall; her doctor prescribes lifting; the gym; she rebuilds; at the end she opens the jar her son couldn't.

Read it as the worked example of every rule in SKILL/references: each shot function is one beat of the narration,
every key frame comes from a word (wf), the camera keys are the framings it lands on, each character acts with
big() and travels across the set, and finish() runs the checks.

    blender -b --python film.py -- plan
    blender -b --python film.py -- S08 preview_out preview 790 820      (build, checks, two preview stills)
    python3 tools/chain.py render                                       (every shot, two render chains)
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'kit'))
from shotkit import *                     # setup, light, cast, big, camera, finish, wf, F, L, W, look, Vector, ...
import sets_lib as S6

FILM['timing'] = os.path.join(HERE, 'voice', 'voice-timing.json')
FILM['cuts'] = [(3, 'You'), (5, 'Nobody'), (7, 'The'), (7, 'getting'), (8, 'Then'), (9, 'Three'), (10, 'Her'),
                (12, 'So'), (13, 'Two'), (15, 'But'), (18, 'The'), (19, 'The'), (20, 'The'), (21, 'By'), (22, 'And')]
FILM['loc'] = ['kitchen', 'bathroom', 'street', 'stairs', 'living', 'stairs', 'living', 'doctor', 'gym', 'gym', 'gym',
               'gym', 'street', 'stairs', 'park', 'kitchen']
FILM['mood'] = ['interior', 'interior', 'day', 'interior', 'interior', 'night', 'interior', 'interior', 'interior',
                'interior', 'interior', 'interior', 'day', 'interior', 'dusk', 'interior']
FILM['end'] = 1870
FILM['allow'] = {'S05': {'june': ('sofa',)}, 'S07': {'june': ('sofa',)},           # she sits IN the sofa seat
                 'S06': {'june': ('stair', 'landing', 'floor')},                    # the fall: she drops behind the edge
                 'S08': {'doc': ('desk',)},                                          # the doctor sits behind her desk
                 **{k: {'woman2': ('bench',)} for k in ('S09', 'S10', 'S11', 'S12')}}  # an extra sits on the bench



# ================================================================ the shots
def S01(f0, f1):                                    # kitchen: "At sixty-two, June couldn't open a jar of pickles. She blamed the lid."
    setup(f0, f1); S6.kitchen()
    J = cast('june', (1.4, 0.0), face=('open', 'flat', 'determined'), f0=f0, f1=f1)
    jar = S6.jar('jar'); hold_prop(J, jar, 'sr', (0.0, -0.075, -0.03))
    L.pose(J, f0 - 12, f0 - 10, {'ik_sr': (0.07, 1.08), 'ik_sl': (0.03, 1.27), 'front_sl': True, 'front_sr': True})
    L.walk(J, f0, f0 + 44, [(1.4, 0.0), (0.25, 1.1)], step=11, ease=(False, True), arms=None, bob=0.02, lift=0.86)  # walks in, twisting
    co = wf(1, "couldn't"); jr = wf(1, 'jar'); pk = wf(1, 'pickles'); b = wf(2, 'blamed'); ld = wf(2, 'lid')
    k = 0
    for f in range(f0, co, 8):                                   # the lid hand wrenches across the lid, the body pulls against it
        L.pose(J, f, f + 4, {'ik_sl': (-0.02, 1.27), 'ik_sr': (0.055, 1.08), 'torso': -5, 'head': 3})
        L.pose(J, f + 4, f + 8, {'ik_sl': (0.08, 1.25), 'ik_sr': (0.085, 1.08), 'torso': 5, 'head': -3})
        k += 1
    L.face(J, f0 + 8, eyes='closed', mouth='frown', brows='determined'); L.face(J, wf(1, 'June'), eyes='open', mouth='flat', brows='determined')
    L.look(J, f0 + 6, dx=0.004, dz=-0.009)
    L.pose(J, co, co + 3, {'torso': 0, 'head': 0})                                                 # hit-stop on "couldn't"
    L.pose(J, co + 3, co + 10, {'squash': (1.04, 0.95), 'head': 8, 'ik_sl': (-0.06, 1.16)})        # ...then a defeated slump
    L.face(J, co + 3, eyes='open', mouth='frown', brows='worried'); L.look(J, co + 1, dx=0.0, dz=-0.011)
    L.pose(J, pk, pk + 8, {'squash': (1.0, 1.0), 'head': 4})
    L.pose(J, jr - 6, jr, {'ik_sl': (-0.02, 1.27), 'front_sl': True})                                # one last twist in the insert...
    L.pose(J, jr, jr + 5, {'ik_sl': (0.08, 1.25), 'hand_sl': -30})
    L.pose(J, jr + 5, jr + 8, {'ik_sl': (0.17, 1.16), 'hand_sl': 25})                                # ...and her hand slips off the lid
    big(J, b, {'ik_sr': (0.2, 1.3), 'ik_sl': (-0.16, 1.05), 'front_sl': False, 'head': 6}, antic=6, move=8, settle=10, squash=0.1,
        face=('open', 'frown', 'determined'), look=(0.008, -0.004))                                 # holds the jar up, glares at it
    for k, f in enumerate(range(b + 8, b + 20, 4)):                                                  # shakes it at the lid
        L.pose(J, f, f + 2, {'ik_sr': (0.2 + (0.025 if k % 2 else -0.025), 1.3 + (0.015 if k % 2 else -0.015))})
    L.pose(J, b + 20, b + 24, {'ik_sr': (0.2, 1.3)})
    L.face(J, b + 12, eyes='open', mouth='flat', brows='determined'); L.look(J, b + 10, dx=0.009, dz=0.002)   # offended glare, held
    L.look(J, f1 - 2, dx=0.0, dz=0.0)                                                                # ...then a look to camera
    jp = objpos(jar, jr) + Vector((0, 0, 0.1)); P = lambda f: pos(J, f)
    cam = camera('S01', [
        dict(f=f0, size='WS', H=4.6, cz=1.1, at=P(f0), az=-6, el=4, lens=26),                            # open wide on the kitchen
        dict(f=co + 2, size='MS', at=P(co), az=1, el=3, lens=36),                                       # the struggle, jar at her chest
        dict(f=b - 3, size='MCU', at=P(b), az=8, el=3, lens=42)],                                       # the glare at the lid
        focus=J['j']['torso'])
    light('kitchen', f0, f1 + HANDLE)
    finish('S01', f0, f1, cam)


def S02(f0, f1):                                    # bathroom mirror: "You see, after forty, ... disappear. Up to eight percent, every single decade."
    setup(f0, f1); info = S6.bathroom()
    J = cast('june', (1.3, 0.6), face=('open', 'smile', 'neutral'), f0=f0, f1=f1)
    L.walk(J, f0, f0 + 36, [(1.3, 0.6), (0.0, 0.25)], step=10, ease=(False, True))               # in from the door to the mirror
    ft = wf(3, 'forty'); m = wf(3, 'muscles'); q = wf(3, 'quietly'); st = wf(3, 'start'); d = wf(3, 'disappear')
    e = wf(4, 'eight'); v = wf(4, 'every')
    L.look(J, f0 + 30, dx=0.0, dz=0.0)
    L.pose(J, ft - 2, ft + 6, {'torso': -6, 'head': -6})                                           # leans in to the mirror...
    L.pose(J, ft + 4, ft + 6, {'front_sr': True})
    L.pose(J, ft + 5, ft + 12, {'ik_sr': (0.12, 1.72), 'hand_sr': 20})                              # ...pats her hair
    L.pose(J, ft + 12, m - 1, {'arm_sr': (9, 10, 0), 'front_sr': False, 'torso': 0})
    L.face(J, ft + 4, eyes='happy', mouth='smile', brows='happy')
    big(J, m, {'arm_sl': (86, 108, 12), 'head': -6}, antic=7, move=6, settle=10, squash=0.12,
        face=('open', 'grin', 'happy'), look=(-0.008, 0.003))                                      # flexes at the mirror
    L.xray(J, m + 3, m + 5)
    for k, (f, sc_) in enumerate(((q, 0.85), (st, 0.7), (d, 0.5))):                                 # the bicep deflates in 3 steps
        muscles(J, f, f + 6, sc_, 0.88 + 0.04 * (2 - k)); pulse(J, f, k)
    L.face(J, q + 2, eyes='open', mouth='flat', brows='surprised'); L.face(J, d + 2, eyes='wide', mouth='O', brows='worried')
    L.look(J, q - 3, dx=-0.009, dz=0.0)
    L.pose(J, e - 9, e - 4, {'arm_sl': (40, 60, 0), 'head': 0})
    L.xray(J, e - 6, e - 4, on=False)                                                               # the shock in her own colours
    big(J, e - 2, {'ik_sl': (-0.30, 1.62), 'ik_sr': (0.30, 1.62), 'hand_sl': -35, 'hand_sr': -35, 'lift': 0.07},
        antic=6, move=5, settle=12, squash=0.12, hold=3, face=('wide', 'O', 'surprised'), look=(0.0, 0.0))   # "eight percent": shock
    L.pose(J, e + 10, e + 14, {'lift': 0.0}); L.pose(J, e + 14, e + 18, {'squash': (1.08, 0.92)}); L.pose(J, e + 18, e + 28, {'squash': (1.0, 1.0)})
    L.pose(J, v - 2, v + 2, {'ik_sl': (-0.11, 1.22), 'ik_sr': (0.11, 1.22), 'hand_sl': 10, 'hand_sr': -10})   # hands come down in front...
    L.pose(J, v + 2, v + 8, {'ik_sl': (-0.045, 1.0), 'ik_sr': (0.045, 1.0), 'hand_sl': 30, 'hand_sr': -30, 'head': 8})  # ...and wring
    L.face(J, v + 2, eyes='open', mouth='frown', brows='worried'); L.look(J, v - 1, dx=0.004, dz=-0.008)
    L.pose(J, v + 8, f1 + HANDLE, {'squash': (1.03, 0.96)})                                         # sinks a little under it
    L.sway(J, v, f1 + HANDLE, deg=1.5, period=40)
    p = pos(J, f0 + 36)
    cam = camera('S02', [
        dict(f=f0, size='FS', at=pos(J, f0), az=-9, el=2, lens=30),
        dict(f=ft, size='FS', at=p, az=-5, el=4, lens=30), dict(f=m + 4, size='MS', at=p, dx=-0.22, dz=0.14, az=-1, el=3, lens=38),
        dict(f=d + 6, size='FS', at=p, dx=-0.1, az=3, el=3, lens=31),                                   # the arm deflates: full figure
        dict(f=e, size='MS', H=1.25, cz=1.52, at=p, az=7, el=2, lens=40), dict(f=e + 30, size='FS', at=p, az=10, el=3, lens=32),
        dict(f=f1, size='MCU', at=p, az=13, el=1, lens=42, dz=-0.06)],
        focus=J['j']['torso'])
    light('bath', f0, f1 + HANDLE)
    finish('S02', f0, f1, cam)


def S03(f0, f1):                                    # high street: "Nobody notices at first. The shopping bags just feel a little heavier on the walk home."
    setup(f0, f1); info = S6.street()
    G = info['ground']
    J = cast('june', (0.2, 9.5, 0.12), face=('open', 'smile', 'neutral'), f0=f0, f1=f1)
    bl, br = S6.bag('bag_l'), S6.bag('bag_r'); L.hold(J, bl, 'sl', (-0.035, -0.07, -0.05)); L.hold(J, br, 'sr', (0.035, -0.07, -0.05))
    h = wf(6, 'heavier')
    L.walk(J, f0, h, [(0.2, 9.5), (0.22, 6.6)], step=14, ground=G, ease=(False, False), carry=True, arm_base=(2, 2), bob=0.035,
           lift=0.82, sway=4.0)
    L.walk(J, h, f1 + HANDLE, [(0.22, 6.6), (0.25, 4.6)], step=16, ground=G, ease=(False, True), carry=True, arm_base=(2, 2), bob=0.04,
           lift=0.84, sway=4.5)
    L.pose(J, f0, f0 + 2, {'head': 4})
    L.face(J, wf(6, 'bags'), eyes='open', mouth='flat', brows='worried'); L.look(J, wf(6, 'bags') - 3, dx=0.006, dz=-0.009)
    L.pose(J, h - 8, h - 3, {'squash': (0.97, 1.04), 'head': 0})                                      # hitches the bags up...
    L.pose(J, h, h + 4, {'squash': (1.08, 0.88), 'head': 12, 'torso': 4})                             # ...they yank her down
    L.pose(J, h + 4, h + 7, {'squash': (1.08, 0.88)})                                                  # hit-stop
    L.pose(J, h + 7, h + 19, {'squash': (1.02, 0.97), 'head': 7, 'torso': 2})
    L.face(J, h, eyes='closed', mouth='frown', brows='worried'); L.face(J, h + 12, eyes='open', mouth='frown', brows='worried')
    L.look(J, h + 11, dx=0.006, dz=-0.012)
    P = lambda f: pos(J, f)
    cam = camera('S03', [
        dict(f=f0 - 15, size='EWS', H=22, cz=1.2, at=P(f0), cam=(0.75, -1.6, 0.45), lens=22),
        dict(f=f0, size='EWS', H=22, cz=1.2, at=P(f0), cam=(0.75, -1.2, 0.5), lens=22),
        dict(f=f0 + 45, size='WS', H=7, cz=1.0, at=P(f0 + 45), cam=(0.7, 0.9, 0.8), lens=26),
        dict(f=f0 + 85, size='FS', at=P(f0 + 85), cam=(0.6, 2.4, 1.0), lens=30),
        dict(f=f1, size='FS', at=P(f1), cam=(0.5, 3.0, 1.25), lens=32)],
        focus=J['j']['torso'])
    light('street', f0, f1 + HANDLE)
    finish('S03', f0, f1, cam, grounds={'june': G})


def _stairs_climb(J, f0, f1, k0, n_treads, per=1, heavy=True, lean=-4):
    """Climb towards the camera, landing on tread centres: `per` treads a step (1 heavy, 2 bounding), a lift and bob
    each step, a lean into the climb."""
    g = S6.stairs_ground; root = J['j']['root']
    steps = max(1, n_treads // per); step = max(4, (f1 - f0) // steps)
    yc = lambda k: S6.STAIR_Y0 - (k + 0.5) * S6.GOING                   # centre of tread k (k = -1: hall floor)
    for i in range(steps):
        fa, fb = f0 + i * step, f0 + (i + 1) * step; ka, kb = k0 + i * per, k0 + (i + 1) * per
        ya, yb = yc(ka), yc(kb); za, zb = g(0, ya), g(0, yb)
        F.key(root, 'location', ya, fa, 'BEZIER', 'AUTO', 1); F.key(root, 'location', yb, fb, 'BEZIER', 'AUTO', 1)
        F.key(root, 'location', za, fa, 'BEZIER', 'AUTO', 2)
        F.key(root, 'location', zb + (0.05 if heavy else 0.14), fa + step // 2, 'BEZIER', 'AUTO', 2)
        F.key(root, 'location', zb, fb, 'BEZIER', 'AUTO', 2)
        up = 'sl' if i % 2 == 0 else 'sr'; jt = J['j'][f'thigh_{up}']
        F.key(jt, 'scale', 1.0, fa, 'BEZIER', 'AUTO', 2); F.key(jt, 'scale', 0.76 if heavy else 0.66, fa + step // 2, 'BEZIER', 'AUTO', 2)
        F.key(jt, 'scale', 1.0, fb, 'BEZIER', 'AUTO', 2)
        F.key(J['j']['hips'], 'rotation_euler', math.radians(3 if up == 'sl' else -3), fa + step // 2, 'BEZIER', 'AUTO', 1)
        F.key(J['j']['torso'], 'rotation_euler', math.radians(lean + (2 if up == 'sl' else -2)), fa + step // 2, 'BEZIER', 'AUTO', 1)
    end = f0 + steps * step
    F.key(J['j']['hips'], 'rotation_euler', 0.0, end, 'BEZIER', 'AUTO', 1); F.key(J['j']['torso'], 'rotation_euler', 0.0, end + 6, 'BEZIER', 'AUTO', 1)
    return end, yc(k0 + steps * per)


def S04(f0, f1):                                    # stairs, day: "The stairs feel a little steeper,"
    setup(f0, f1); S6.stairs(False)
    k0 = 3; y0 = S6.STAIR_Y0 - (k0 + 0.5) * S6.GOING
    J = cast('june', (0.0, y0, S6.stairs_ground(0, y0)), face=('open', 'flat', 'worried'), f0=f0, f1=f1)
    L.pose(J, f0 - 12, f0 - 10, {'ik_sr': (0.17, 0.95), 'hand_sr': -40, 'arm_sl': (10, 14, 0), 'head': 6})   # hand on her aching back
    end, _ = _stairs_climb(J, f0, f1 + HANDLE, k0, 4, per=1, heavy=True)
    L.face(J, f0 + 6, eyes='closed', mouth='frown', brows='worried'); L.face(J, f0 + 22, eyes='open', mouth='O', brows='worried')
    L.face(J, f0 + 40, mouth='frown'); L.look(J, f0 + 18, dx=0.0, dz=0.008)
    P = lambda f: pos(J, f)
    cam = camera('S04', [
        dict(f=f0 - 15, size='FS', at=P(f0), cam=(0.28, 1.0, 2.78), lens=26), dict(f=f0, size='FS', at=P(f0), cam=(0.25, 0.9, 2.75), lens=26),
        dict(f=f0 + 30, size='FS', at=P(f0 + 30), cam=(0.2, 0.55, 2.7), lens=28),
        dict(f=f1 + 8, size='FS', at=P(f1), cam=(0.15, 0.35, 2.66), lens=30)],
        focus=J['j']['torso'])
    light('hall', f0, f1 + HANDLE)
    finish('S04', f0, f1, cam, grounds={'june': lambda x, y: S6.stairs_ground(x, y)})


SOFA = (1.55, 1.45)              # inside the sofa: the seat front hides her legs; SIT = how far she sinks
SIT = -0.55


def S05(f0, f1):                                    # living room: "and getting up from the sofa needs a push."
    setup(f0, f1); W.living_room()
    J = cast('june', (SOFA[0], SOFA[1], SIT), face=('open', 'flat', 'determined'), f0=f0, f1=f1)
    L.pose(J, f0 - 12, f0 - 10, {'ik_sl': (-0.19, 0.78), 'ik_sr': (0.19, 0.78), 'head': 8})              # hands on her knees
    p_ = wf(7, 'needs') + 2; root = J['j']['root']
    # first try: pushes up hard... and drops back
    L.pose(J, f0 + 2, f0 + 6, {'squash': (1.05, 0.94), 'head': 12})
    L.pose(J, f0 + 6, f0 + 14, {'ik_sl': (-0.19, 0.92), 'ik_sr': (0.19, 0.92), 'head': -2, 'squash': (0.97, 1.03)})
    F.key(root, 'location', SIT, f0 + 6, 'BEZIER', 'AUTO', 2); F.key(root, 'location', SIT + 0.24, f0 + 14, 'BEZIER', 'AUTO', 2)
    F.key(root, 'location', SIT, f0 + 20, 'QUAD', 'EASE_IN', 2)
    L.pose(J, f0 + 20, f0 + 22, {'squash': (1.08, 0.92), 'ik_sl': (-0.19, 0.8), 'ik_sr': (0.19, 0.8), 'head': 8})
    L.pose(J, f0 + 22, f0 + 26, {'squash': (0.98, 1.02)}); L.pose(J, f0 + 26, f0 + 30, {'squash': (1.0, 1.0)})
    tremble(J, f0 + 6, f0 + 14, 'arm_sl', 6, 2); tremble(J, f0 + 6, f0 + 14, 'arm_sr', 6, 2)
    L.face(J, f0 + 6, eyes='closed', mouth='frown', brows='determined')
    L.face(J, f0 + 22, eyes='open', mouth='frown', brows='worried'); L.look(J, f0 + 19, dx=0.0, dz=-0.006)   # "ugh"
    # second try: rocks forward, and up she comes, off the sofa
    L.look(J, p_ - 5, dx=-0.006, dz=0.004)
    antic(J, p_ - 1, 6, 1.6, 14); L.pose(J, p_ - 4, p_ - 2, {'torso': 10})
    F.key(root, 'location', SIT, p_ - 2, 'BEZIER', 'AUTO', 2); F.key(root, 'location', 0.03, p_ + 5, 'BACK', 'EASE_OUT', 2)
    F.key(root, 'location', 0.0, p_ + 10, 'BEZIER', 'AUTO', 2)
    F.key(root, 'location', SOFA[1], p_ - 2, 'BEZIER', 'AUTO', 1); F.key(root, 'location', 0.8, p_ + 7, 'BEZIER', 'AUTO', 1)
    big(J, p_, {'ik_sr': (0.26, 0.95), 'hand_sr': -60, 'arm_sl': (40, 20, 0), 'torso': -3, 'head': -4}, antic=0, move=6, settle=8,
        squash=0.08, face=('closed', 'O', 'worried'))                                                   # "oof": a hand to her back
    L.pose(J, p_ + 14, p_ + 18, {'torso': 0})
    L.face(J, p_ + 12, eyes='open', mouth='flat', brows='worried')
    p = Vector((SOFA[0], SOFA[1], 0))
    cam = camera('S05', [
        dict(f=f0, size='FS', H=2.7, cz=0.9, at=p, az=-12, el=4, lens=30),
        dict(f=p_ - 2, size='MS', at=p, az=-5, el=2, lens=38, dz=SIT + 0.3),                        # in on 'push'
        dict(f=f1 + 8, size='FS', at=Vector((SOFA[0] - 0.15, 0.8, 0)), az=6, el=5, lens=30)],
        focus=J['j']['torso'])
    light('living', f0, f1 + HANDLE, key_at=(0.2, -0.9, 2.4), key_to=(SOFA[0], SOFA[1], 0.9), key_energy=600, key_size=0.6)
    finish('S05', f0, f1, cam)


def S06(f0, f1):                                    # stairs, night: "Then one night, June slipped on the landing, and her legs simply weren't there to catch her."
    setup(f0, f1); S6.stairs(True)
    LZ = S6.LANDING_Z
    J = cast('june', (0.0, -1.3, LZ), face=('open', 'smile', 'neutral'), f0=f0, f1=f1)
    s = wf(8, 'slipped'); lg = wf(8, 'legs'); c = wf(8, 'catch')
    L.walk(J, f0, s - 2, [(0.0, -1.3), (0.0, -0.15)], step=10, ground=lambda x, y: LZ, ease=(False, False))
    L.face(J, f0 + 2, eyes='open', mouth='flat', brows='neutral'); L.look(J, f0 + 4, dx=0.0, dz=-0.008)
    root = J['j']['root']
    L.face(J, s, eyes='wide', mouth='O', brows='surprised'); L.look(J, s - 3)
    big(J, s, {'arm_sl': (150, 40, 0), 'arm_sr': (70, 110, 0), 'torso': 14, 'head': -12}, antic=3, move=3, over=0.2, settle=4, squash=0.1)
    F.key(root, 'rotation_euler', 0.0, s - 1, 'BEZIER', 'AUTO', 1); F.key(root, 'rotation_euler', math.radians(-18), s + 5, 'BEZIER', 'AUTO', 1)
    F.key(root, 'rotation_euler', 0.0, s + 14, 'BEZIER', 'AUTO', 1)                                  # a lopsided flail, tipping back
    imp = s + 7
    F.key(root, 'location', LZ, s - 1, 'BEZIER', 'AUTO', 2); F.key(root, 'location', LZ + 0.1, s + 2, 'QUAD', 'EASE_IN', 2)
    F.key(root, 'location', LZ - 0.84, imp, 'CONSTANT', 'AUTO', 2)                                     # accelerating fall, then hit-stop
    L.pose(J, imp - 2, imp, {'squash': (1.15, 0.85), 'arm_sl': (70, 20, 0), 'arm_sr': (70, 20, 0), 'head': 6})
    L.pose(J, imp + 3, imp + 6, {'squash': (0.96, 1.04)}, interp='BACK', easing='EASE_OUT')
    L.pose(J, imp + 6, imp + 16, {'squash': (1.0, 1.0)})
    L.face(J, imp, eyes='closed', mouth='O', brows='worried')
    L.pose(J, lg - 4, lg + 6, {'ik_sr': (0.2, 0.92), 'hand_sr': -40, 'arm_sl': (25, 30, 0), 'head': 10})  # holds her hip
    L.face(J, lg, eyes='closed', mouth='frown', brows='worried')
    L.face(J, c, eyes='open', mouth='frown', brows='worried'); L.look(J, c - 3, dx=0.006, dz=-0.008)
    for k, f in enumerate(range(c + 4, f1 + HANDLE, 9)): L.pose(J, f, f + 5, {'head': 10 + (3 if k % 2 else -3)})
    sit = Vector((0, -0.15, LZ - 0.84))
    cam = camera('S06', [
        dict(f=f0 - 15, size='WS', at=pos(J, f0), cam=(0.35, 7.6, 1.5), lens=30), dict(f=f0, size='WS', at=pos(J, f0), cam=(0.33, 6.0, 1.55), lens=30),
        dict(f=s - 4, size='FS', at=pos(J, s - 4), cam=(0.25, 4.4, 1.8), lens=34),
        dict(f=imp + 8, size='FS', at=sit, cam=(0.2, 3.0, 2.8), lens=36, H=2.4, cz=1.2),
        dict(f=lg, size='MS', at=sit, cam=(0.18, 2.4, 3.0), lens=50, H=1.2, cz=1.5),
        dict(f=c, size='MCU', at=sit, cam=(0.15, 2.2, 3.1), lens=58, H=0.88, cz=1.5),
        dict(f=f1 + 8, size='MCU', at=sit, cam=(0.05, 1.7, 3.15), lens=72, H=0.88, cz=1.62),
        dict(f=f1 + 30, size='MCU', at=sit, cam=(0.0, 1.45, 3.17), lens=76, H=0.88, cz=1.62)],
        focus=J['j']['torso'], fstop=1.4)
    light('hall_night', f0, f1 + HANDLE)
    finish('S06', f0, f1, cam, grounds={'june': lambda x, y: LZ})


def S07(f0, f1):                                    # living room, evening: "Three weeks on the sofa, waiting for a bruised hip to heal."
    setup(f0, f1); W.living_room()
    J = cast('june', (SOFA[0], SOFA[1], SIT), face=('open', 'frown', 'worried'), f0=f0, f1=f1)
    L.pose(J, f0 - 12, f0 - 10, {'ik_sr': (0.19, 0.88), 'hand_sr': -40, 'arm_sl': (35, 70, 0), 'head': 7})
    w = wf(9, 'weeks'); so = wf(9, 'sofa'); wa = wf(9, 'waiting'); hip = wf(9, 'hip')
    root = J['j']['root']
    blanket = W.box('blanket', (0.7, 0.05, 0.42), (0, 0, 0), W.toon('blanket', '#d97a5a', 'canvas_green.png'), ink=0.004)
    L.hold(J, blanket, 'sr', (-0.17, -0.07, 0.24)); F.key(blanket, 'scale', (0, 0, 0), f0, 'CONSTANT')
    ice = W.box('icepack', (0.18, 0.05, 0.13), (0, 0, 0), W.toon('icepack', '#7fc8e8'), ink=0.004)
    L.hold(J, ice, 'sr', (0.0, -0.06, -0.03)); F.key(ice, 'scale', (0, 0, 0), f0, 'CONSTANT')
    L.look(J, f0 + 4, dx=-0.006, dz=-0.004)                                    # watching the TV, down and to the left
    # a time-lapse in one push: slumped with a blanket, lying back, upright with an ice pack
    for f, spec, fc in ((w, {'head': 12, 'torso': 0, 'arm_sl': (12, 20, 0)}, ('open', 'frown', 'worried')),
                        (so, {'torso': -15, 'head': -6, 'lift': SIT - 0.1, 'arm_sl': (60, 120, 0)}, ('closed', 'flat', 'neutral')),
                        (wa, {'torso': 0, 'head': 4, 'lift': SIT, 'arm_sl': (14, 40, 0), 'ik_sr': (0.22, 1.0), 'hand_sr': -40},
                         ('open', 'frown', 'determined'))):
        L.pose(J, f - 2, f, {'squash': (1.06, 0.94), **spec}); L.pose(J, f, f + 3, {'squash': (1.0, 1.0)})
        L.face(J, f, *fc)
    hide_until(blanket, w); F.key(blanket, 'scale', (1, 1, 1), wa - 1, 'CONSTANT'); F.key(blanket, 'scale', (0, 0, 0), wa, 'CONSTANT')
    hide_until(ice, wa)
    for k, f in enumerate(range(hip - 8, f1 + HANDLE, 6)): L.pose(J, f, f + 3, {'ik_sr': (0.22 + (0.015 if k % 2 else -0.015), 1.0)})
    L.look(J, wa + 2, dx=0.004, dz=-0.009)
    sc = bpy.context.scene
    td = bpy.data.lights.new('tv', 'AREA'); td.size = 0.6; td.color = (0.45, 0.62, 1.0)
    tv = bpy.data.objects.new('tv', td); sc.collection.objects.link(tv); tv.location = (SOFA[0] - 0.1, SOFA[1] - 1.4, 1.0)
    tv.rotation_euler = (math.radians(90), 0, 0); rnd = random.Random(3)
    for f in range(f0 - 2, f1 + HANDLE + 2, 3): td.energy = rnd.uniform(120, 320) * (1.6 if so <= f < wa else 1.0); td.keyframe_insert('energy', frame=f)
    p = Vector((SOFA[0], SOFA[1], 0))
    cam = camera('S07', [
        dict(f=f0, size='WS', H=4.4, cz=0.9, at=p, az=12, el=6, lens=28),                            # the room, weeks passing
        dict(f=w + 6, size='FS', at=p, dx=-0.05, az=6, el=3, lens=32, dz=SIT + 0.25),
        dict(f=hip, size='MCU', at=p, dx=-0.08, az=0, el=2, lens=42, H=1.15, cz=1.35, dz=SIT),
        dict(f=f1 + 8, size='MCU', at=p, dx=-0.18, az=-10, el=2, lens=44, H=1.1, cz=1.35, dz=SIT),
        dict(f=f1 + 30, size='MCU', at=p, dx=-0.28, az=-14, el=2, lens=46, H=1.05, cz=1.35, dz=SIT)],
        focus=J['j']['torso'])
    light('living_eve', f0, f1 + HANDLE)
    wl = bpy.data.objects.get('win_light')
    if wl:                                                                     # dusk, night, morning, dusk through the window
        for f, e, col in ((f0, 40, (1.0, 0.64, 0.4)), (so, 0, (1.0, 0.64, 0.4)), (wa, 200, (0.85, 0.92, 1.0)), (f1, 60, (1.0, 0.64, 0.4))):
            wl.data.energy = e; wl.data.color = col; wl.data.keyframe_insert('energy', frame=f); wl.data.keyframe_insert('color', frame=f)
    sun = bpy.data.objects.get('sun')
    if sun:                                                                    # the sun outside: sets, rises, a clock you can see
        for f, z in ((f0, 1.3), (so, 0.45), (wa, 1.9), (f1, 1.5)): F.key(sun, 'location', z, f, 'CONSTANT', 'AUTO', 2)
    finish('S07', f0, f1, cam)


def S08(f0, f1):                                    # doctor: "Her doctor wrote one prescription, and it wasn't a pill. Lift something heavy. Twice a week."
    setup(f0, f1); info = S6.doctor()
    J = cast('june', (-0.85, 0.3), face=('open', 'flat', 'worried'), f0=f0, f1=f1)
    D = cast('doc', (0.35, 1.45, -0.42), pal=L.DOCTOR, style='lady', face=('open', 'smile', 'neutral'), f0=f0, f1=f1)
    note = bpy.data.objects.new('note', None); W.coll('WORLD').objects.link(note)
    paper = W.box('note_paper', (0.17, 0.004, 0.22), (0, 0, 0.11), W.toon('note_paper', '#fbf8f0'), ink=0.002); paper.parent = note
    for k, (txt, sz, z) in enumerate((('Rx', 0.045, 0.19), ('Lift something', 0.019, 0.135), ('heavy.', 0.019, 0.11),
                                       ('Twice a week.', 0.019, 0.075))):
        t = S6.text(f'note_t{k}', txt, (0, -0.004, z), sz, '#2b3a66', rot=(90, 0, 0), emit=0.9); t.parent = note; t.location = (0, -0.004, z)
    L.hold(D, note, 'sr', (0.0, -0.05, 0.02)); hide_until(note, wf(10, 'prescription') + 4)
    pr = wf(10, 'prescription'); wn = wf(10, 'wasn'); pill = wf(10, 'pill'); li = wf(11, 'Lift'); tw = wf(11, 'Twice')
    for k, f in enumerate(range(f0, pr, 5)):                                    # the doctor writes on the desk, quick scribbles
        L.pose(D, f, f + 3, {'ik_sr': (0.05 + (0.04 if k % 2 else 0.0), 1.22), 'hand_sr': 10 if k % 2 else -10, 'head': 8})
    L.look(D, f0 + 2, dx=0.0, dz=-0.01); L.face(D, f0, eyes='open', mouth='flat', brows='determined')
    big(D, pr, {'ik_sr': (0.22, 1.34), 'hand_sr': 0, 'head': -4}, antic=5, move=6, settle=10, squash=0.08,
        face=('happy', 'grin', 'happy'), look=(-0.008, 0.0))                                        # holds it up beside her face, beaming
    L.look(J, pr - 3, dx=0.009, dz=-0.006)
    L.pose(J, pr + 2, pr + 10, {'torso': -6, 'head': -8, 'squash': (0.98, 1.02)})                   # June leans in, curious
    L.face(J, pr + 4, eyes='open', mouth='flat', brows='surprised')
    big(J, wn, {'head': 4, 'torso': 0, 'lift': 0.03}, antic=4, move=4, settle=8, squash=0.08, face=('wide', 'O', 'surprised'))   # 'wasn't a pill?!'
    L.pose(J, pill + 10, pill + 16, {'lift': 0.0})
    big(J, tw, {'arm_sl': (14, 30, 0), 'arm_sr': (40, 95, 0), 'head': 2, 'squash': (0.97, 1.03)}, antic=4, move=5, settle=8,
        squash=0.06, face=('open', 'flat', 'worried'), look=(0.0, 0.0))                             # "twice?!" she mimes a lift, gulps
    L.face(J, tw + 10, eyes='wide', mouth='flat', brows='worried')
    npos = objpos(note, li) + Vector((0, 0, 0.11))
    cam = camera('S08', [
        dict(f=f0, size='WS', H=4.2, cz=1.0, at=Vector((-0.2, 0.8, 0)), az=-10, el=6, lens=28),
        dict(f=wn + 3, size='FS', at=Vector((-0.3, 0.9, 0)), az=-12, el=3, lens=32, H=2.6, cz=1.15),      # two-shot: June's 'not a pill?!' take
        dict(f=li + 14, size='MS', at=Vector((0.35, 1.45, -0.42)), dx=0.12, H=1.5, cz=1.45, az=0, el=3, lens=42)],  # the note up by her face
        focus=note, fstop=5.6)
    light('clinic', f0, f1 + HANDLE, key_at=(-1.7, -1.0, 2.4), key_to=(0.2, 1.0, 0.9), key_size=0.7)
    ld = bpy.data.lights.new('desk_lamp', 'POINT'); ld.energy = 40; ld.color = (1.0, 0.75, 0.45); ld.use_shadow = False
    lo = bpy.data.objects.new('desk_lamp', ld); bpy.context.scene.collection.objects.link(lo); lo.location = (-0.15, 1.15, 1.15)
    finish('S08', f0, f1, cam)


GSPOT = (0.2, 0.45)
EXTRAS = (('woman2', (-1.6, 1.6), dict(L.SON, top='#f0b429', top_sh='#d39a1c', hair='#c9a46a'), 'lady'),
          ('kb_guy', (2.6, 2.1), dict(L.YOUNG_MAN, top='#3fae7a', top_sh='#2f9466', skin='#eab896', skin_sh='#d49a78', hair='#c98a3a'), 'man'),
          ('squat_gal', (-2.6, 1.2), dict(L.DOCTOR, top='#e86a9a', top_sh='#c9527e', trousers='#2e3550'), 'lady'))


def _gym_cast(f0, f1, man_at=(1.05, 0.85), small_on_box=False):   # 10 cm clear of the rack (clipping check)
    """The gym's people and props, the same in every gym shot: the young man at the rack, three gym-goers, the plyo box."""
    M = cast('man', man_at, pal=L.YOUNG_MAN, style='man', face=('open', 'smile', 'determined'), f0=f0, f1=f1)
    db = S6.dumbbell('db_man', 12, '#3b3f4a', 1.1); L.hold(M, db, 'sr', (0.0, -0.06, -0.055))
    X = []
    for k, (n, at, pal, st) in enumerate(EXTRAS):
        R = cast(n, at, pal=pal, style=st, face=('open', 'flat', 'determined'), f0=f0, f1=f1); X.append(R)
        if n == 'squat_gal':                                         # slow squats
            for f in range(f0 + 4 * k, f1 + HANDLE, 24):
                L.pose(R, f, f + 12, {'lift': -0.18, 'squash': (1.06, 0.9), 'arm_sl': (80, 0, 0), 'arm_sr': (80, 0, 0)})
                L.pose(R, f + 12, f + 24, {'lift': 0.0, 'squash': (1.0, 1.0), 'arm_sl': (70, 0, 0), 'arm_sr': (70, 0, 0)})
        else:
            d = S6.dumbbell(f'db_{n}', 6 + 2 * k, '#4f8fd8', 0.9); L.hold(R, d, 'sl' if k == 0 else 'sr', (0.0, -0.06, -0.05))
            _curls(R, f0 + 5 * k, f1 + HANDLE, 'sl' if k == 0 else 'sr', 18 + 2 * k)
    W.box('plyo', (0.36, 0.34, 0.69), (GSPOT[0] + 0.5, GSPOT[1] + 0.28, 0.345), W.toon('plyo', '#b07a4a', 'wood_crate.png'), ink=0.01)
    small = None
    if small_on_box:
        small = S6.dumbbell('db2_table', 2, '#e86a9a', 0.7); small.location = (GSPOT[0] + 0.44, GSPOT[1] + 0.14, 0.72)
    return M, X, small


def _curls(R, fa, fb, side='sr', every=14, easy=True):
    """A curl up the centre line, in front of the chest (it reads head-on and stays inside every framing)."""
    for f in range(fa, fb - every + 1, every):
        L.pose(R, f, f + every // 2, {f'arm_{side}': (4, -125, 0), f'front_{side}': True})
        L.pose(R, f + every // 2, f + every, {f'arm_{side}': (6, -8, 0)})


def S09(f0, f1):                                    # gym, wide: "So June walked into a gym full of people half her age and picked up the smallest dumbbell in the room."
    setup(f0, f1); W.gym()
    pk = wf(12, 'picked'); sm = wf(12, 'smallest'); hf = wf(12, 'half'); ag = wf(12, 'age'); fu = wf(12, 'full')
    J = cast('june', (-2.4, -0.5), face=('open', 'smile', 'determined'), f0=f0, f1=f1)
    M, X, small = _gym_cast(f0, f1, small_on_box=True); _curls(M, f0, sm - 8, every=16)
    held = S6.dumbbell('db2_hand', 2, '#e86a9a', 0.7); L.hold(J, held, 'sr', (0.0, -0.06, -0.05)); F.key(held, 'scale', (0, 0, 0), f0, 'CONSTANT')
    L.walk(J, f0, pk - 6, [(-2.4, -0.5), (-1.1, 0.0), GSPOT], step=9, ease=(False, True), lift=0.84, bob=0.03)
    L.face(J, hf, eyes='open', mouth='flat', brows='worried'); L.look(J, hf - 3, dx=0.008, dz=0.002)
    for R in X[:2]: L.look(R, hf - 3, dx=-0.01, dz=0.0); L.look(R, ag + 9, dx=0.0, dz=0.0)          # two of them glance at her
    L.look(J, ag - 3, dx=-0.008, dz=0.0); L.face(J, ag + 4, mouth='smile', brows='determined')
    L.look(J, pk - 9, dx=0.009, dz=-0.007)
    big(J, pk - 4, {'ik_sr': (0.62, 0.66), 'hand_sr': 0, 'torso': 12, 'head': 6}, antic=4, move=6, over=0.1, settle=4, squash=0.08)
    swap(small, held, pk + 3)
    L.pose(J, pk + 3, pk + 11, {'arm_sr': (10, 6, 0), 'torso': 0, 'head': -2})
    big(J, sm + 2, {'ik_sr': (0.17, 1.74), 'hand_sr': 15, 'head': 6, 'torso': -3}, antic=5, move=6, over=0.15, settle=10,
        squash=0.08, face=('happy', 'grin', 'happy'), look=(0.008, 0.007))                          # holds it up like a trophy
    L.look(J, wf(12, 'room') - 3, 0.0, 0.0)                                                         # ...proud, to the lens
    big(M, sm + 8, {'arm_sr': (165, 10, 0), 'head': -4}, antic=6, move=6, over=0.08, hold=4, settle=10, squash=0.08)   # his 12 kg press behind her
    G = Vector((GSPOT[0], GSPOT[1], 0))
    cam = camera('S09', [
        dict(f=f0, size='EWS', H=9.0, cz=1.4, at=Vector((-1.6, 0.2, 0)), cam=(-1.6, -4.4, 1.3), lens=22),   # the whole gym
        dict(f=f0 + 30, size='WS', H=5.0, cz=1.2, at=pos(J, f0 + 30), cam=(-1.0, -3.2, 1.2), lens=24),
        dict(f=fu, size='WS', H=5.0, cz=1.4, at=Vector((-0.3, 0.9, 0)), cam=(-0.6, -3.6, 1.5), lens=22),
        dict(f=ag, size='FS', at=pos(J, ag), az=-10, el=4, lens=28),
        dict(f=pk - 4, size='MS', at=G, dx=0.15, az=-22, el=3, lens=32),
        dict(f=sm + 4, size='FS', H=2.7, cz=1.1, at=G, dx=0.3, az=-35, el=3, lens=30)],
        focus=J['j']['torso'])
    light('gym', f0, f1 + HANDLE)
    finish('S09', f0, f1, cam)


def S10(f0, f1):                                    # gym: "Two kilos. She could barely lift it, and the young man at the rack tried very hard not to stare."
    setup(f0, f1); W.gym()
    J = cast('june', GSPOT, face=('open', 'smile', 'determined'), f0=f0, f1=f1)
    M, X, _ = _gym_cast(f0, f1, (1.15, 0.9))
    held = S6.dumbbell('db2_hand', 2, '#e86a9a', 0.7); L.hold(J, held, 'sr', (0.0, -0.06, -0.05))
    L.pose(J, f0 - 12, f0 - 10, {'ik_sr': (0.1, 1.48), 'hand_sr': 0, 'front_sr': True})                # the dumbbell up by her face
    L.look(J, f0, dx=0.006, dz=-0.004)
    ke = wf(13, 'kilos', end=True); bl = wf(14, 'barely'); it_ = wf(14, 'it'); ym = wf(14, 'young'); st = wf(14, 'tried'); stare = wf(14, 'stare')
    L.pose(J, ke - 2, bl - 6, {'arm_sr': (6, -8, 0), 'front_sr': False})                               # lowers it to her side
    big(J, bl, {'arm_sr': (4, -55, 0), 'front_sr': True, 'torso': -5, 'head': 8}, antic=6, move=8, over=0.1, settle=6,
        squash=0.1, face=('closed', 'grin', 'determined'), look=(0.0, -0.006))                          # halfway up... stuck
    tremble(J, bl + 10, it_ - 2, 'arm_sr', 3, 2); tremble(J, bl + 10, it_ - 2, 'head', 2, 2)
    big(J, it_ - 2, {'arm_sr': (4, -125, 0), 'torso': 0, 'head': -4}, antic=3, move=5, over=0.12, settle=8, squash=0.06,
        face=('wide', 'O', 'surprised'))                                                               # one last heave: it's up
    tremble(J, it_ + 12, st + 6, 'arm_sr', 2, 2)
    L.pose(J, st + 6, st + 16, {'arm_sr': (6, -10, 0)}); L.face(J, st + 8, eyes='happy', mouth='grin', brows='happy')
    _curls(M, f0, ym - 4, every=16)
    L.pose(M, ym - 4, ym + 4, {'arm_sr': (6, -8, 0), 'head': -6})                                      # he freezes, staring
    L.face(M, ym, eyes='wide', mouth='O', brows='surprised'); L.look(M, ym - 3, dx=-0.01, dz=0.0)
    big(M, st, {'head': 10, 'torso': 4}, antic=3, move=5, over=0.2, settle=8, squash=0.04, look=(0.006, 0.012),
        face=('open', 'O', 'neutral'))                                                                 # snaps away, eyes on the ceiling
    _curls(M, st + 8, stare - 4, every=10)                                                             # busy pretend curls
    L.look(M, stare - 3, dx=-0.012, dz=0.0)
    big(M, stare, {'head': -6}, antic=2, move=3, over=0.2, settle=5, squash=0.03, face=('wide', 'flat', 'surprised'))
    big(M, stare + 8, {'head': 10}, antic=0, move=3, over=0.15, settle=6, squash=0.03, look=(0.006, 0.012), face=('open', 'O', 'neutral'))
    hp = hold_point(J, 'sr', f0 + 2)
    fo = bpy.data.objects.new('S10_focus', None); bpy.context.scene.collection.objects.link(fo)
    for f, p_ in ((f0 - 15, hp), (ke, hp), (bl - 2, pos(J, bl) + Vector((0, 0, 1.3)))):
        for i in range(3): F.key(fo, 'location', p_[i], f, 'BEZIER', 'AUTO', i)
    cam = camera('S10', [
        dict(f=f0 - 15, size='INS', at=hp, H=0.5, cz=0.03, dx=-0.03, az=-4, el=2, lens=55),
        dict(f=f0, size='INS', at=hp, H=0.48, cz=0.03, dx=-0.02, az=-3, el=2, lens=55),
        dict(f=bl + 2, size='MS', H=1.15, cz=1.35, at=pos(J, bl), az=-10, el=2, lens=44),
        dict(f=ym - 2, size='WS', H=4.0, cz=1.05, at=Vector((0.7, 1.0, 0)), cam=(-1.2, -2.6, 1.35), lens=26),  # the two-shot gag, wide
        dict(f=st + 8, size='FS', H=2.5, cz=1.1, at=Vector((0.75, 1.0, 0)), cam=(-0.6, -1.15, 1.35), lens=30)],
        focus=fo)
    light('gym', f0, f1 + HANDLE)
    finish('S10', f0, f1, cam)


def S11(f0, f1):                                    # gym X-ray: "But muscle never stops listening. Week by week, it started to rebuild ... Four kilos. Then six. Then eight."
    setup(f0, f1); W.gym()
    sp = GSPOT
    J = cast('june', sp, face=('open', 'flat', 'determined'), f0=f0, f1=f1)
    M, X, _ = _gym_cast(f0, f1, (1.2, 0.92)); _curls(M, f0, f1 + HANDLE, every=16)   # clear of the rack
    dbs = [S6.dumbbell('db2', 2, '#e86a9a', 0.7), S6.dumbbell('db4', 4, '#4f8fd8', 0.8), S6.dumbbell('db6', 6, '#3fae7a', 0.9),
           S6.dumbbell('db8', 8, '#e08a3a', 1.0)]
    for d in dbs: L.hold(J, d, 'sr', (0.0, -0.06, -0.05))
    li = wf(15, 'listening'); wk = wf(16, 'Week'); rb = wf(16, 'rebuild'); tw = wf(16, 'twenty')
    k4, k6, k8 = wf(17, 'Four'), wf(17, 'six'), wf(17, 'eight')
    for d in dbs[1:]: F.key(d, 'scale', (0, 0, 0), f0, 'CONSTANT')
    for a, b, f in ((dbs[0], dbs[1], k4), (dbs[1], dbs[2], k6), (dbs[2], dbs[3], k8 - 7)): swap(a, b, f)
    L.look(J, li - 6, dx=0.008, dz=0.004)
    big(J, li - 1, {'ik_sl': (-0.168, 1.63), 'hand_sl': -30, 'head': -8, 'front_sl': True}, antic=4, move=5, over=0.12,
        settle=8, squash=0.06, face=('happy', 'grin', 'happy'))                                     # cups her ear: listening
    L.pose(J, wk - 4, wk + 2, {'arm_sl': (9, 10, 0), 'head': 0, 'front_sl': False})
    L.xray(J, wk - 1, wk + 1)                                                                          # a hard switch reads as a scan
    muscles(J, f0, f0 + 1, 0.5, 0.88)                                                              # start small (after the decline)
    for k, f in enumerate((wk, rb, tw, k4, k6, k8 - 4)):                                              # rebuild in steps, with pulses
        s_ = 0.5 + 0.11 * (k + 1)
        muscles(J, f, f + 8, s_ * 1.05, 0.88 + 0.04 * (k + 1), interp='BACK')
        pulse(J, f + 1, k % 3)
    for h in J['halos']: F.key(h, 'color', 0.0, wk, 'BEZIER', 'AUTO', 3); F.key(h, 'color', 0.85, wk + 10, 'BEZIER', 'AUTO', 3)
    L.face(J, rb, eyes='open', mouth='grin', brows='determined')
    L.walk(J, rb + 4, k4 - 2, [sp, (sp[0] - 0.55, sp[1] - 0.3), (0.35, 0.1)], step=12, lift=0.84, bob=0.03, carry=True)   # struts a loop
    for f in (k4 + 2, k6):                                                                            # curls get easier
        big(J, f, {'arm_sr': (4, -128, 0), 'front_sr': True}, antic=4, move=5, over=0.12, settle=6, squash=0.05)
        L.pose(J, f + 11, f + 16, {'arm_sr': (6, -8, 0)})
    big(J, k8 - 4, {'arm_sr': (4, -128, 0), 'front_sr': True, 'ik_sl': (-0.2, 1.8), 'hand_sl': -20, 'head': -6},
        antic=3, move=5, over=0.15, hold=3, settle=8, squash=0.1, face=('happy', 'grin', 'happy'), look=(0.0, 0.0))   # 8 kg up, fist up
    P = lambda f: pos(J, f)
    cam = camera('S11', [
        dict(f=f0, size='WS', H=4.6, cz=1.1, at=P(f0), az=-6, el=4, lens=28),
        dict(f=li + 2, size='MCU', at=P(li), az=-2, el=2, lens=48),
        dict(f=wk + 6, size='FS', at=P(wk + 6), az=2, el=3, lens=31),
        dict(f=rb + 8, size='FS', at=P(rb + 8), az=7, el=5, lens=30),
        dict(f=tw + 4, size='FS', at=P(tw + 4), az=10, el=3, lens=31),
        dict(f=k4 + 4, size='MS', at=P(k4 + 4), dz=0.1, az=6, el=2, lens=42),
        dict(f=k6 + 4, size='MS', H=1.2, cz=1.36, at=P(k6 + 4), az=2, el=2, lens=44),
        dict(f=k8, size='MCU', H=1.0, cz=1.42, at=P(k8), az=-2, el=2, lens=46),
        dict(f=f1 + 8, size='MCU', H=0.95, cz=1.44, at=P(f1), az=-4, el=2, lens=46)],
        focus=J['j']['torso'])
    light('gym', f0, f1 + HANDLE)
    finish('S11', f0, f1, cam)


def S12(f0, f1):                                    # gym: "The young man started asking her for tips."
    setup(f0, f1); W.gym()
    sp = (0.35, 0.1)
    J = cast('june', sp, face=('open', 'grin', 'happy'), f0=f0, f1=f1)
    d8 = S6.dumbbell('db8', 8, '#e08a3a', 1.0); L.hold(J, d8, 'sr', (0.0, -0.06, -0.05))
    M, X, _ = _gym_cast(f0, f1, (1.4, 0.9))
    a = wf(18, 'asking'); tp = wf(18, 'tips')
    L.walk(M, f0, a - 6, [(1.4, 0.9), (0.95, 0.45)], step=8, ease=(False, True))
    big(M, a - 2, {'ik_sr': (0.1, 1.82), 'hand_sr': -20, 'ik_sl': (-0.28, 1.15), 'head': -6}, antic=4, move=5, over=0.12,
        settle=8, squash=0.05, face=('open', 'grin', 'surprised'), look=(-0.01, 0.0))                 # scratches his head, points at hers
    L.look(J, a - 2, dx=0.01, dz=0.0)
    big(J, a + 6, {'arm_sr': (4, -128, 0), 'front_sr': True, 'arm_sl': (14, 30, 0), 'head': -5}, antic=5, move=5, over=0.15,
        settle=8, squash=0.08, face=('happy', 'grin', 'happy'))                                       # "like this"
    big(M, tp - 6, {'arm_sl': (4, -128, 0), 'front_sl': True, 'ik_sr': (0.2, 0.95), 'head': 4}, antic=4, move=5, over=0.15,
        settle=8, squash=0.08, face=('open', 'smile', 'determined'), look=(-0.01, 0.0))               # he copies with an empty fist
    L.look(J, tp + 2, 0.0, 0.0)                                                                       # her proud look to the lens
    q = Vector(((sp[0] + 0.95) / 2, (sp[1] + 0.45) / 2, 0))
    cam = camera('S12', [
        dict(f=f0, size='WS', at=q, az=14, el=5, lens=28, H=4.2, cz=1.0),
        dict(f=a + 4, size='FS', at=q, az=8, el=4, lens=32, H=2.7, cz=1.05),
        dict(f=tp, size='MS', at=q, az=1, el=4, lens=33, H=2.05, cz=1.15),
        dict(f=f1 + 8, size='FS', at=q, az=-6, el=4, lens=31, H=2.7, cz=1.05)],
        focus=J['j']['torso'])
    light('gym', f0, f1 + HANDLE, key_color=(1.0, 0.78, 0.55))
    finish('S12', f0, f1, cam)


def S13(f0, f1):                                    # high street again: "The shopping bags got lighter."
    setup(f0, f1); info = S6.street()
    J = cast('june', (0.2, 6.2, 0.12), face=('happy', 'grin', 'happy'), f0=f0, f1=f1)
    bl, br = S6.bag('bag_l'), S6.bag('bag_r'); L.hold(J, bl, 'sl', (-0.035, -0.07, -0.05)); L.hold(J, br, 'sr', (0.035, -0.07, -0.05))
    L.walk(J, f0, f1 + HANDLE, [(0.2, 6.2), (0.25, 3.8)], step=7, ground=info['ground'], ease=(False, False), arms=24.0,
           arm_base=(14, 14), fore=10, bob=0.04, lift=0.82)                                               # swings the bags, a spring in her step
    cam = camera('S13', [
        dict(f=f0, size='EWS', H=10.0, cz=1.3, at=pos(J, f0), az=22, el=9, lens=24),
        dict(f=f0 + 20, size='WS', H=5.0, cz=1.1, at=pos(J, f0 + 20), az=14, el=5, lens=28),
        dict(f=f1 + 8, size='FS', at=pos(J, f1), az=8, el=4, lens=34)],
        focus=J['j']['torso'])
    light('street', f0, f1 + HANDLE)
    finish('S13', f0, f1, cam, grounds={'june': info['ground']})


def S14(f0, f1):                                    # stairs, day: "The stairs got shorter, and she started taking them two at a time."
    setup(f0, f1); S6.stairs(False)
    J = cast('june', (0.0, 4.5, 0.0), face=('happy', 'grin', 'determined'), f0=f0, f1=f1)
    tw = wf(20, 'two'); tm = wf(20, 'time')
    L.walk(J, f0, f0 + 14, [(0.0, 4.5), (0.0, 4.1)], step=7, ease=(False, False))
    _stairs_climb(J, f0 + 14, tm - 2, -1, 16, per=2, heavy=False, lean=-6)                               # two treads a bound
    L.pose(J, f0 + 14, f0 + 16, {'arm_sl': (30, 60, 0), 'arm_sr': (30, 60, 0)})
    for k, f in enumerate(range(f0 + 14, tm - 2, 8)):
        L.pose(J, f, f + 4, {'arm_sl': (30 + (20 if k % 2 else 0), 60, 0), 'arm_sr': (30 + (0 if k % 2 else 20), 60, 0)})
    L.face(J, tw, eyes='open', mouth='grin', brows='determined')
    big(J, tm + 2, {'arm_sr': (25, 125, -10), 'arm_sl': (14, 20, 0), 'head': -8, 'torso': 5}, antic=4, move=4, over=0.2, hold=3,
        settle=10, squash=0.1, face=('happy', 'grin', 'happy'))                                       # "Yes!" pull on the landing
    L.face(J, tm + 3, eyes='happy', mouth='grin', brows='happy')
    LZ = S6.LANDING_Z
    cam = camera('S14', [
        dict(f=f0 - 15, size='WS', at=pos(J, f0), cam=(-0.45, -3.3, LZ + 2.15), lens=26), dict(f=f0, size='WS', at=pos(J, f0), cam=(-0.42, -3.0, LZ + 2.02), lens=27),
        dict(f=f0 + 40, size='FS', at=pos(J, f0 + 40), cam=(-0.2, -2.4, LZ + 1.75), lens=34),
        dict(f=tm, size='FS', at=pos(J, tm), cam=(0.2, -2.3, LZ + 1.4), lens=32),
        dict(f=f1 + 8, size='FS', at=pos(J, f1), cam=(0.4, -2.6, LZ + 1.3), lens=32)],
        focus=J['j']['torso'])
    light('hall', f0, f1 + HANDLE)
    finish('S14', f0, f1, cam, grounds={'june': S6.stairs_ground})


def S15(f0, f1):                                    # park at sunset: "By summer she was jogging through the park at sunset, past people half her age, walking."
    setup(f0, f1); W.park('dusk')
    G = W.park_ground
    F.LIT = dict(F.LIT, tint=0.12)
    J = cast('june', (-0.6, 7.2), face=('happy', 'grin', 'happy'), f0=f0, f1=f1)
    A = cast('walk1', (0.2, 4.6), pal=dict(L.YOUNG_MAN, top='#7a5ab0', top_sh='#634894'), style='man', face=('open', 'flat', 'neutral'), f0=f0, f1=f1)
    B = cast('walk2', (-0.15, 4.3), pal=dict(L.SON, top='#e2574c', top_sh='#c2443b', hair='#2a1d18'), style='lady', face=('open', 'flat', 'neutral'), f0=f0, f1=f1)
    L.jog(J, f0, f1 + HANDLE, [(-0.6, 7.2), (-0.72, 4.4), (-0.75, 2.2)], ground=G, ease=(False, False))
    L.walk(A, f0, f1 + HANDLE, [(0.2, 4.6), (0.18, 3.6)], step=12, ground=G, ease=(False, False), bob=0.012, lift=0.95)
    L.walk(B, f0, f1 + HANDLE, [(-0.15, 4.3), (-0.17, 3.4)], step=12, ground=G, ease=(False, False), bob=0.012, lift=0.95)
    ps = wf(21, 'past')
    L.face(A, ps + 4, eyes='wide', mouth='O', brows='surprised'); L.face(B, ps + 8, eyes='wide', mouth='O', brows='surprised')
    L.look(A, ps + 1, dx=-0.01, dz=0.0); L.look(B, ps + 5, dx=-0.01, dz=0.0)
    L.look(J, ps - 2, dx=0.0, dz=0.0); L.face(J, ps + 2, eyes='open', mouth='grin', brows='determined')
    cam = camera('S15', [
        dict(f=f0 - 15, size='EWS', at=pos(J, f0), az=-14, el=18, lens=24), dict(f=f0, size='EWS', at=pos(J, f0), az=-13, el=17, lens=24),
        dict(f=f0 + 50, size='WS', at=pos(J, f0 + 50), az=-7, el=9, lens=28),
        dict(f=ps, size='FS', at=pos(J, ps), az=-2, el=4, lens=30),
        dict(f=f1 + 8, size='FS', at=pos(J, f1), az=5, el=3, lens=32)],
        focus=J['j']['torso'])
    light('park_dusk', f0, f1 + HANDLE)
    finish('S15', f0, f1, cam, grounds={'june': G, 'walk1': G, 'walk2': G})


def S16(f0, f1):                                    # kitchen: "And the jar of pickles? Her son, thirty-five, couldn't open it. June did. First try."
    setup(f0, f1); S6.kitchen()
    J = cast('june', (-0.3, 1.05), face=('open', 'smile', 'happy'), f0=f0, f1=f1)
    Sn = cast('son', (0.33, 1.0), pal=L.SON, style='man', face=('open', 'flat', 'determined'), f0=f0, f1=f1)
    jar_s = S6.jar('jar_son'); L.hold(Sn, jar_s, 'sr', (0.0, -0.075, -0.03))
    jar_j = S6.jar('jar_june'); L.hold(J, jar_j, 'sr', (0.0, -0.075, -0.03))
    lid = bpy.data.objects['jar_june_lid']
    so = wf(23, 'son'); co = wf(23, "couldn't"); jd = wf(24, 'June'); ft = wf(24, 'First'); tr = wf(24, 'try')
    give = jd - 2
    swap(jar_s, jar_j, give); F.key(jar_j, 'scale', (0, 0, 0), f0, 'CONSTANT'); F.key(jar_j, 'scale', (0, 0, 0), give - 1, 'CONSTANT')
    L.pose(Sn, f0 - 12, f0 - 10, {'ik_sr': (0.07, 1.08), 'ik_sl': (0.03, 1.27), 'front_sl': True, 'front_sr': True})
    for f in range(f0, give - 4, 8):                                                                     # he wrenches at it
        L.pose(Sn, f, f + 4, {'hand_sl': -30, 'torso': -5, 'squash': (1.04, 0.96)}, interp='BACK', easing='EASE_OUT')
        L.pose(Sn, f + 4, f + 8, {'hand_sl': 24, 'torso': 3, 'squash': (0.99, 1.01)})
    tremble(Sn, f0 + 4, give - 4, 'fore_sr', 4, 4)
    L.face(Sn, f0 + 4, eyes='closed', mouth='frown', brows='determined'); L.face(Sn, co, eyes='open', mouth='frown', brows='worried')
    L.look(J, f0 + 2, dx=0.01, dz=0.0); L.face(J, so, eyes='open', mouth='smile', brows='surprised')
    L.pose(Sn, give - 4, give + 2, {'ik_sr': (-0.12, 1.15), 'ik_sl': (-0.1, 1.0), 'front_sl': False, 'hand_sl': 0}, interp='BACK', easing='EASE_OUT')
    L.pose(J, give - 6, give, {'ik_sr': (0.12, 1.1), 'front_sr': True}, interp='BACK', easing='EASE_OUT')   # she takes it
    L.pose(J, give + 2, give + 6, {'ik_sl': (0.03, 1.27), 'front_sl': True})
    L.face(J, give + 2, eyes='open', mouth='flat', brows='determined'); L.look(J, give, dx=0.006, dz=-0.009)
    antic(J, ft - 2, 5, 1.2)
    L.pose(J, ft - 2, ft + 2, {'hand_sl': -50, 'squash': (1.03, 0.97)})
    pop = ft + 3                                                                                          # POP: the lid flies off
    big(J, pop, {'ik_sl': (-0.22, 1.55), 'hand_sl': 30, 'head': -6}, antic=4, move=4, over=0.15, hold=3, settle=10, squash=0.1)
    bpy.context.scene.frame_set(pop); lw = lid.matrix_world.translation.copy()
    free = W.cyl('lid_free', 0.058, 0.03, tuple(lw), W.toon('jar_june_lid', '#c8402f'), ink=0.003)
    hide_until(free, pop); F.key(lid, 'scale', (1, 1, 1), pop - 1, 'CONSTANT'); F.key(lid, 'scale', (0, 0, 0), pop, 'CONSTANT')
    for f, dz, dx, r in ((pop, 0, 0, 0), (pop + 6, 0.35, -0.12, 200), (pop + 12, 0.45, -0.22, 400), (pop + 20, 0.2, -0.32, 560)):
        for i, v in ((0, lw.x + dx), (1, lw.y), (2, lw.z + dz)): F.key(free, 'location', v, f, 'BEZIER', 'AUTO', i)
        F.key(free, 'rotation_euler', math.radians(r), f, 'BEZIER', 'AUTO', 1)
    L.face(J, tr, eyes='happy', mouth='grin', brows='happy')
    L.face(Sn, pop + 12, eyes='wide', mouth='O', brows='surprised'); L.look(Sn, pop + 9, dx=-0.01, dz=0.006)
    L.pose(Sn, pop + 12, pop + 19, {'lift': 0.05, 'squash': (0.95, 1.06), 'head': -6})
    L.pose(Sn, pop + 19, pop + 26, {'lift': 0.0, 'squash': (1.0, 1.0)})
    look.fx_sparkle((lw.x - 0.15, lw.y - 0.1, lw.z + 0.3), pop + 4)
    q = Vector((0.02, 1.02, 0))
    cam = camera('S16', [
        dict(f=f0, size='WS', at=q, az=-10, el=5, lens=26, H=4.4, cz=1.0),
        dict(f=so - 4, size='FS', at=q, dx=0.12, az=-6, el=3, lens=31, H=2.7, cz=1.05),
        dict(f=give, size='FS', at=q, az=-2, el=3, lens=32, H=2.7, cz=1.05),
        dict(f=pop, size='MCU', at=Vector((-0.3, 1.05, 0)), dx=0.1, az=2, el=2, lens=42, H=1.15, cz=1.38),
        dict(f=pop + 24, size='FS', at=q, az=10, el=6, lens=29, H=3.0, cz=1.0)],
        focus=J['j']['torso'])
    light('kitchen', f0, f1 + HANDLE)
    finish('S16', f0, f1, cam)


if __name__ == '__main__':
    run(globals())
