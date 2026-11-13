"""style_test.py: four test stills of a style (the cast, a day exterior, a night interior, a close-up), to compare
with the reference frames before a new style is used for a film (references/style-change.md).

    MAKESHORT_PROJECT=<P> blender -b --python kit/style_test.py -- <out_dir> [preview]
P/style/style.json is applied (it is the style under test). Then: python3 tools/style_compare.py <style-name> <out_dir>
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shotkit as K
from shotkit import *
import sets_lib as S6

a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
out = os.path.abspath(a[0] if a else 'style_test'); K.PREVIEW = 'preview' in a
os.makedirs(out, exist_ok=True)
F0, F1 = 1, 40


def shoot(name, keys, focus, frame=30):
    cam = camera(name, keys, focus)
    finish(name, F0, F1, cam, checks=False)
    stills(out, [frame])
    os.replace(os.path.join(out, f'still_{frame:04d}.png'), os.path.join(out, f'{name}.png'))


# 1. the cast in the kitchen: palettes, faces, cel shading, shadows
K.CAST.clear(); setup(F0, F1); S6.kitchen()
cast_ = [cast('lead', (-0.6, 0.3), face=('open', 'smile', 'happy'), f0=F0, f1=F1),
         cast('son', (0.05, 0.6), pal=L.SON, style='man', face=('wide', 'O', 'surprised'), f0=F0, f1=F1),
         cast('doc', (0.65, 0.3), pal=L.DOCTOR, face=('happy', 'grin', 'happy'), f0=F0, f1=F1),
         cast('young', (1.2, 0.7), pal=L.YOUNG_MAN, style='man', face=('open', 'flat', 'worried'), f0=F0, f1=F1)]
light('kitchen', F0, F1)
shoot('t1_cast', [dict(f=F0, size='FS', at=Vector((0.3, 0.45, 0)), H=3.3, az=-4, el=5, lens=30)], cast_[0]['j']['torso'])
# 2. a day exterior, wide: sky, haze, sun shadows, set colours
K.CAST.clear(); setup(F0, F1); info = S6.street()
J = cast('lead', (0.2, 3.0), face=('open', 'smile', 'neutral'), f0=F0, f1=F1)
light('street', F0, F1)
shoot('t2_day_wide', [dict(f=F0, size='WS', at=Vector((0.2, 3.0, 0.12)), az=-8, el=4, lens=26)], J['j']['torso'])
# 3. a night interior: the darkest mood, saturated blue, a warm lamp pool
K.CAST.clear(); setup(F0, F1); S6.stairs(night=True)
J = cast('lead', (0.0, -0.6, S6.LANDING_Z), face=('wide', 'O', 'worried'), f0=F0, f1=F1)          # on the landing
light('hall_night', F0, F1)
shoot('t3_night', [dict(f=F0, size='FS', at=Vector((0.0, -0.6, S6.LANDING_Z)), cam=(0.25, 4.4, 1.8), lens=34)], J['j']['torso'])   # from the foot of the stairs
# 4. a close-up: line weight, eyes, face shading
K.CAST.clear(); setup(F0, F1); S6.kitchen()
J = cast('lead', (0.3, 0.2), face=('open', 'smile', 'happy'), f0=F0, f1=F1)
light('kitchen', F0, F1)
shoot('t4_closeup', [dict(f=F0, size='CU', at=Vector((0.3, 0.2, 0)), az=4, el=3, lens=45)], J['j']['torso'])
print('STYLE_TEST', out, flush=True)
