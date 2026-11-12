"""compose.py: the anatomy-explainer shot builder. Still renders -> a moving, silent 1080x1920 30 fps video.

The reference (references/styles/anatomy-explainer.md, sections 2 and 4b) animates mostly in the edit:
  - a still per shot, often with extra layers (X-ray organs, labels, sweat) that fade in on a spoken word
  - the camera is locked off about half the time, otherwise a slow push-in or pull-out (2-6 % zoom a second)
  - transitions: 3-frame crossfade (most), vertical push with motion blur, 1-2 frame cut, slow fade, dip through dark
Blender renders the stills (base + layers from the same camera, a bit larger than 1080x1920 so the zoom has room);
this script moves them. Then voice/finish.mjs adds voice, music, captions and callouts.

  python3 explainer/compose.py                  # in P: explainer/shots.json -> out/short-v3-silent.mp4
  python3 explainer/compose.py --stills         # one still per shot (middle) + one per transition -> gate/explainer/
  python3 explainer/compose.py --from 4 --to 7  # only shots 4..7 (1-based), for a quick look -> out/part.mp4

explainer/shots.json (see explainer/README.md):
{"duration": 45.0,                      # optional; default = voice length + 0.6 s
 "vignette": 0.35,                      # optional dark edges, 0 = off
 "shots": [
  {"id": "s01", "at": 0, "base": "renders/s01.png",
   "camera": {"from": [1.0, 0.5, 0.5], "to": [1.08, 0.5, 0.42], "ease": "inout"},   # [zoom, centre x, centre y], 0..1 of the image
   "layers": [{"img": "renders/s01_xray.png", "in": "2:bones", "fade": 0.3, "out": "3:then", "mode": "normal", "glow": 0.8},
              {"dim": 0.45, "in": "4:percent", "fade": 0.2}],                         # darken the shot under a stat callout
   "transition_in": {"type": "crossfade", "frames": 3}}]}
"at", "in" and "out" are seconds or "line:wordStem" (that word's start in voice/voice-timing.json).
transition types: crossfade (3 f), fade (8 f, slow crossfade), push_up / push_down (4 f, with motion blur), dip (6 f), cut.
"""
import json, os, subprocess, sys
import numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(HERE)
W, H, FPS = 1080, 1920, 30
DEFAULT_FRAMES = {'crossfade': 3, 'fade': 8, 'push_up': 4, 'push_down': 4, 'dip': 6, 'cut': 0}


def load_json(p):
    return json.load(open(p, encoding='utf-8-sig'))


SPEC = load_json(os.path.join(HERE, 'shots.json'))
TIMING = os.path.join(P, 'voice', 'voice-timing.json')
WORDS = []
if os.path.exists(TIMING):
    T = load_json(TIMING)
    WORDS = [dict(w, line=l['line']) for l in T['lines'] for w in l['words']]
    VOICE_END = T['duration']
else:
    VOICE_END = None


def when(spec, default=None):
    if spec is None: return default
    if isinstance(spec, (int, float)): return float(spec)
    line, stem = str(spec).split(':', 1)
    for w in WORDS:
        bare = ''.join(ch for ch in w['w'] if ch.isalnum() or ch == "'").lower()
        if w['line'] == int(line) and bare.startswith(stem.lower()): return float(w['start'])
    raise SystemExit(f'"{spec}": word not found in voice/voice-timing.json (use "line:wordStem" or seconds)')


def ease(t, kind='inout'):
    t = min(max(t, 0.0), 1.0)
    if kind == 'linear': return t
    if kind == 'out': return 1 - (1 - t) ** 2
    if kind == 'in': return t * t
    return t * t * (3 - 2 * t)


_clip_cache = {}
def clip_frame(spec, t):
    """A frame from a rendered clip: spec = {"video": "renders/anim/s01_0001-0110.mp4", "first": 1}. "first" is the
    Blender frame of the clip's first frame; time t maps to Blender frame round(t * 30) + 1 (held at the ends).
    The clip is unpacked once to PNGs next to it (alpha kept for QuickTime RLE / PNG clips)."""
    path = spec['video'] if os.path.isabs(spec['video']) else os.path.join(P, spec['video'])
    d = os.path.splitext(path)[0] + '_frames'
    if not os.path.isdir(d) or not os.listdir(d):
        os.makedirs(d, exist_ok=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-start_number', '0', '-pix_fmt', 'rgba', os.path.join(d, '%05d.png')], check=True)
    n = len([x for x in os.listdir(d) if x.endswith('.png')])
    k = min(max(int(round(t * FPS)) + 1 - int(spec.get('first', 1)), 0), n - 1)
    key = (d, k)
    if key not in _clip_cache:
        if len(_clip_cache) > 24: _clip_cache.pop(next(iter(_clip_cache)))
        im = cv2.imread(os.path.join(d, f'{k:05d}.png'), cv2.IMREAD_UNCHANGED)
        if im.shape[2] == 3: im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
        _clip_cache[key] = im.astype(np.float32) / 255.0
    return _clip_cache[key]


def source(spec, t):
    """A shot base or layer: a still (path) or a clip ({"video": ..., "first": ...})."""
    return clip_frame(spec, t) if isinstance(spec, dict) else img(spec)


_img_cache = {}
def img(path):
    if path not in _img_cache:
        full = path if os.path.isabs(path) else os.path.join(P, path)
        im = cv2.imread(full, cv2.IMREAD_UNCHANGED)
        if im is None: raise SystemExit(f'missing image: {full}')
        if im.ndim == 2: im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGRA)
        if im.shape[2] == 3: im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
        if im.dtype != np.uint8: im = (im / 257).astype(np.uint8)          # 16-bit PNG from Blender
        _img_cache[path] = im.astype(np.float32) / 255.0
    return _img_cache[path]


_glow_cache = {}
def glow_img(li, radius):
    key = (id(li), radius)
    hit = _glow_cache.get(key)
    if hit is None or hit[0] is not li:                                # keep li alive in the cache so its id stays unique
        if len(_glow_cache) > 8: _glow_cache.pop(next(iter(_glow_cache)))
        bright = li[..., :3] * li[..., 3:4]
        lum = bright.max(axis=2, keepdims=True); bright = bright * np.clip((lum - 0.45) / 0.4, 0, 1)
        small = cv2.resize(bright, (bright.shape[1] // 4, bright.shape[0] // 4), interpolation=cv2.INTER_AREA)
        hit = (li, cv2.resize(cv2.GaussianBlur(small, (0, 0), radius / 4), (bright.shape[1], bright.shape[0])))
        _glow_cache[key] = hit
    return hit[1]


# ------------------------------------------------------------------ timeline
shots = SPEC['shots']
for s in shots: s['_t0'] = when(s.get('at'), 0.0)
shots[0]['_t0'] = 0.0
if any(b['_t0'] <= a['_t0'] for a, b in zip(shots, shots[1:])): raise SystemExit('shot "at" times must increase')
DUR = float(SPEC.get('duration') or ((VOICE_END + 0.6) if VOICE_END else shots[-1]['_t0'] + 3.0))
for a, b in zip(shots, shots[1:]): a['_t1'] = b['_t0']
shots[-1]['_t1'] = DUR
NF = int(round(DUR * FPS))
for s in shots:
    tr = s.get('transition_in') or {'type': 'crossfade'}
    if isinstance(tr, str): tr = {'type': tr}
    if tr['type'] not in DEFAULT_FRAMES: raise SystemExit(f"{s['id']}: unknown transition {tr['type']}")
    tr.setdefault('frames', DEFAULT_FRAMES[tr['type']]); s['_tr'] = tr
    base = source(s['base'], s['_t0']); s['_size'] = base.shape[1], base.shape[0]
    for L in s.get('layers', []):
        L['_in'] = when(L.get('in'), s['_t0']); L['_out'] = when(L.get('out'), None)
        if 'img' in L and source(L['img'], L['_in']).shape[:2] != base.shape[:2]:
            raise SystemExit(f"{s['id']}: layer {L['img']} is not the same size as the base (render both from the same camera)")


def shot_frame(s, t):
    """The shot at time t (seconds), 1080x1920 BGR float, camera and layers applied."""
    comp = source(s['base'], t)[..., :3].copy()
    for L in s.get('layers', []):
        fade = max(L.get('fade', 0.3), 1e-3)
        a = ease((t - L['_in']) / fade, 'linear')
        if L['_out'] is not None: a *= 1 - ease((t - L['_out']) / fade, 'linear')
        a *= L.get('opacity', 1.0)
        if a <= 0: continue
        if 'dim' in L:
            comp *= 1 - L['dim'] * a; continue
        li = source(L['img'], t); rgb, al = li[..., :3], li[..., 3:4] * a
        if L.get('glow'):                                              # soft bloom around bright parts (bones, muscles)
            comp = np.minimum(comp + glow_img(li, L.get('glow_radius', 18)) * L['glow'] * a, 1.0)
        mode = L.get('mode', 'normal')
        if mode == 'add': comp = np.minimum(comp + rgb * al, 1.0)
        elif mode == 'screen': comp = 1 - (1 - comp) * (1 - rgb * al)
        else: comp = comp * (1 - al) + rgb * al
    cam = s.get('camera') or {}
    z0, x0, y0 = cam.get('from', [1.0, 0.5, 0.5]); z1, x1, y1 = cam.get('to', [z0, x0, y0])
    span = max(s['_t1'] - s['_t0'], 1e-3)
    k = ease((t - s['_t0']) / span, cam.get('ease', 'inout'))
    z = z0 + (z1 - z0) * k; cx = x0 + (x1 - x0) * k; cy = y0 + (y1 - y0) * k
    iw, ih = s['_size']
    fit = min(iw / W, ih / H)                                          # source px per output px at zoom 1
    sc = 1 / (fit / z)                                                 # output px per source px
    cw, ch = W / sc, H / sc                                            # crop size in source px
    cxp = min(max(cx * iw, cw / 2), iw - cw / 2); cyp = min(max(cy * ih, ch / 2), ih - ch / 2)
    M = np.float32([[sc, 0, W / 2 - sc * cxp], [0, sc, H / 2 - sc * cyp]])
    return cv2.warpAffine(comp, M, (W, H), flags=cv2.INTER_AREA if sc < 1 else cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


VIG = None
def vignette(fr):
    global VIG
    amt = SPEC.get('vignette', 0.35)
    if not amt: return fr
    if VIG is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / np.sqrt(2)
        VIG = (1 - amt * np.clip((r - 0.35) / 0.65, 0, 1) ** 1.6)[..., None]
    return fr * VIG


def frame(f):
    t = f / FPS
    i = max(k for k, s in enumerate(shots) if s['_t0'] <= t + 1e-9)
    cur = shots[i]
    # is a transition into the next shot (or from the previous one) running at frame f?
    for j in (i, i + 1):
        if j == 0 or j >= len(shots): continue
        s, prev = shots[j], shots[j - 1]; tr = s['_tr']; n = tr['frames']; f0 = int(round(s['_t0'] * FPS))
        if n == 0: continue
        a0 = f0 - n // 2                                               # centred on the cut point
        if not (a0 <= f < a0 + n): continue
        p = (f - a0 + 0.5) / n
        if tr['type'] in ('crossfade', 'fade'):
            return prev_and_next(prev, s, t, lambda A, B: A * (1 - ease(p, 'linear')) + B * ease(p, 'linear'))
        if tr['type'] == 'dip':
            src = prev if p < 0.5 else s
            depth = 1 - 0.92 * (1 - abs(p - 0.5) * 2)                   # down to 8 % brightness at the middle
            return shot_frame(src, t) * depth
        if tr['type'] in ('push_up', 'push_down'):
            A, B = shot_frame(prev, t), shot_frame(s, t); sign = -1 if tr['type'] == 'push_up' else 1
            acc = np.zeros_like(A)
            for sub in range(4):                                       # motion blur: 4 samples across the frame time
                q = ease((f - a0 + (sub + 0.5) / 4) / n, 'inout'); off = int(round(q * H))
                out = np.empty_like(A)
                if sign < 0: out[:H - off] = A[off:]; out[H - off:] = B[:off]
                else: out[off:] = A[:H - off]; out[:off] = B[H - off:]
                acc += out
            return acc / 4
    return shot_frame(cur, t)


def prev_and_next(prev, s, t, mix):
    return mix(shot_frame(prev, t), shot_frame(s, t))


def to8(fr):
    return (np.clip(vignette(fr), 0, 1) * 255 + 0.5).astype(np.uint8)


def main():
    args = sys.argv[1:]
    if '--stills' in args:
        out = os.path.join(P, 'gate', 'explainer'); os.makedirs(out, exist_ok=True)
        for k, s in enumerate(shots):
            mid = int(round((s['_t0'] + s['_t1']) / 2 * FPS)); cv2.imwrite(os.path.join(out, f"{k + 1:02d}_{s['id']}_mid.png"), to8(frame(mid)))
            if k: cv2.imwrite(os.path.join(out, f"{k + 1:02d}_{s['id']}_in.png"), to8(frame(int(round(s['_t0'] * FPS)))))
        print(f'wrote {len(shots)} shot stills to {out}'); return
    f_a, f_b, dst = 0, NF, os.path.join(P, 'out', 'short-v3-silent.mp4')
    if '--from' in args:
        a = int(args[args.index('--from') + 1]) - 1; b = int(args[args.index('--to') + 1]) - 1 if '--to' in args else a
        f_a = int(round(shots[a]['_t0'] * FPS)); f_b = int(round(shots[b]['_t1'] * FPS)); dst = os.path.join(P, 'out', 'part.mp4')
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', dst], stdin=subprocess.PIPE)
    for f in range(f_a, f_b):
        ff.stdin.write(to8(frame(f)).tobytes())
        if (f - f_a) % 150 == 0: print(f'  frame {f - f_a}/{f_b - f_a}', flush=True)
    ff.stdin.close(); ff.wait()
    print(f'wrote {dst}: {(f_b - f_a) / FPS:.2f} s, {len(shots)} shots')


if __name__ == '__main__':
    main()
