"""dissolve.py: turn every dissolve in shots.json into a true crossfade, as in the reference (references/reference-style.md section 1).

    python dissolve.py [render_dir] [handles_dir] [H]      defaults: render  render/handles  4

The reference crossfades over 8 frames (6-10): frame = a * outgoing + (1 - a) * incoming, a falling linearly from about
0.94 to 0.06, so the incoming shot dominates from the cut frame f on. Brightness never dips. Inputs:
  render/fNNNN.png                 the normal render (outgoing shot before f, incoming shot from f)
  render/handles/out_FFFF_i.png    outgoing camera continued to frame f+i     (scene.py handles mode)
  render/handles/in_FFFF_i.png     incoming camera run back to frame f-H+i    (scene.py handles mode)
Blended frames replace render/fNNNN.png; the originals are kept in render/pre_dissolve/.
Needs: python packages numpy + pillow.
"""
import json, os, shutil, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
R = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'render')
HD = sys.argv[2] if len(sys.argv) > 2 else os.path.join(R, 'handles')
H = int(sys.argv[3]) if len(sys.argv) > 3 else 4
shots = json.load(open(os.path.join(HERE, 'shots.json')))
keep = os.path.join(R, 'pre_dissolve'); os.makedirs(keep, exist_ok=True)


def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.float32)


n = 0
for s in shots[1:]:
    if s.get('transition_in') != 'dissolve':
        continue
    f = s['f_in']
    for t in range(f - H, f + H):
        dst = os.path.join(R, f'f{t:04d}.png')
        if not os.path.exists(dst):
            continue
        if t < f:
            out_p, in_p = dst, os.path.join(HD, f'in_{f:04d}_{t - (f - H)}.png')
        else:
            out_p, in_p = os.path.join(HD, f'out_{f:04d}_{t - f}.png'), dst
        if not (os.path.exists(out_p) and os.path.exists(in_p)):
            print(f'skip frame {t}: missing handle for the dissolve at {f}')
            continue
        a = 1.0 - (t - (f - H) + 0.5) / (2 * H)          # weight of the outgoing shot: 0.94 ... 0.06 for H = 4
        src = os.path.join(keep, f'f{t:04d}.png')
        if not os.path.exists(src):
            shutil.copy(dst, src)                           # keep the original once
        A = load(out_p if t >= f else src)
        B = load(in_p if t < f else src)
        Image.fromarray(np.clip(a * A + (1 - a) * B + 0.5, 0, 255).astype(np.uint8)).save(dst)
        n += 1
print(f'dissolve.py: blended {n} frames ({2 * H}-frame crossfades)')
