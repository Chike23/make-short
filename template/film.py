"""film.py: <TITLE>. One function per shot; each shot is one beat of the narration.

How to write a shot (the full rules: SKILL/references/planning.md, acting.md, spec.md):
  1. setup(f0, f1); build the set (S6.kitchen(), S6.street(), W.living_room(), W.gym(), W.park('dusk') ...)
  2. cast the characters where they start; light('<set>', f0, f1)
  3. take every key frame from a word: a = wf(line, 'word')
  4. act: travel (L.walk / L.jog / L.travel) in EVERY shot, one big() per beat, a face per beat, eyes lead
  5. camera keys = the framings the camera LANDS on, each on its word. Follow the size mix: open wide (EWS/WS)
     on new places, FS is home, MS is passed through, MCU/CU only for the big reactions. Between moves the
     camera drifts slowly by itself (push-in by default after the first key, then "follow").
  6. finish('Sxx', f0, f1, cam) runs the checks; read the CHECK lines.
Run:  blender -b --python film.py -- S01 preview_out preview 40 90     (build + checks + 2 preview stills)
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'kit'))
from shotkit import *
import sets_lib as S6

FILM['timing'] = os.path.join(HERE, 'voice', 'voice-timing.json')
FILM['cuts'] = [(2, 'First')]               # shot 2 starts on the first word of narration line 2, and so on
FILM['loc'] = ['kitchen', 'street']         # one place per shot
FILM['mood'] = ['interior', 'day']          # day, dusk, interior or night per shot
FILM['end'] = end_frame()                   # the last word plus 0.6 s
FILM['allow'] = {}                          # {'S03': {'hero': ('sofa',)}}: overlaps the clipping check accepts


def S01(f0, f1):                            # kitchen: "<the narration of this beat>"
    setup(f0, f1); S6.kitchen()
    H = cast('hero', (1.4, 0.0), face=('open', 'flat', 'neutral'), f0=f0, f1=f1)
    light('kitchen', f0, f1)
    a = wf(1, 'Word')                       # TODO: the word this beat reacts to
    L.walk(H, f0, a - 4, [(1.4, 0.0), (0.5, 0.15)])                       # she travels: never one spot all shot
    big(H, a, {'arm_sr': (70, 90, 0), 'head': -5}, face=('wide', 'O', 'surprised'), look=(0.0, 0.004))
    cam = camera('S01', [
        dict(f=f0, size='WS', at=Vector((1.1, 0.1, 0)), az=-10, el=6, lens=28),         # wide on the new place
        dict(f=a, size='MS', at=Vector((0.5, 0.15, 0)), az=8, el=4, lens=40),           # fast move in, lands on the word
        dict(f=a + 36, size='FS', at=Vector((0.5, 0.15, 0)), az=14, el=5, lens=35),     # back to FS as she reacts
    ], H['j']['torso'])
    finish('S01', f0, f1, cam)


def S02(f0, f1):                            # street: "<the narration of this beat>"
    setup(f0, f1); info = S6.street()
    H = cast('hero', (0.2, 6.0), face=('open', 'smile', 'happy'), f0=f0, f1=f1)
    light('street', f0, f1)
    G = info['ground']
    L.walk(H, f0, f1 + HANDLE, [(0.2, 6.0), (0.0, 2.0)], ground=G)
    cam = camera('S02', [
        dict(f=f0, size='EWS', at=Vector((0.1, 5.0, 0)), az=-6, el=4, lens=24),
        dict(f=f0 + 45, size='FS', at=Vector((0.0, 3.0, 0)), az=4, el=5, lens=32),
    ], H['j']['torso'])
    finish('S02', f0, f1, cam, grounds={'hero': G})


if __name__ == '__main__':
    run(globals())
