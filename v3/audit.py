"""audit.py: check a finished Short against the measured reference style (references/reference-style.md).

    python audit.py [final.mp4]        run in the project folder P; default out/short-v3-final.mp4

Reads shots.json (the edit), voice/voice-timing.json (narration), voice/captions.ass (captions) and the final video.
Prints one PASS / FAIL / INFO line per parameter, with the reference target and range, and writes critic/audit.md.
A FAIL here is a measured gap, not taste: give the critic this file with the render (rubric items 8 and 9).
Needs: ffmpeg, python packages numpy + opencv-python.
"""
import json, os, re, subprocess, sys
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEO = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'out', 'short-v3-final.mp4')
if not os.path.exists(VIDEO) and len(sys.argv) == 1:      # no mix yet: audit the silent render (captions are then reported missing)
    VIDEO = os.path.join(HERE, 'out', 'short-v3-silent.mp4')
if not os.path.exists(VIDEO):
    sys.exit(f'audit.py: no video at {VIDEO}. Render (go.sh) and mix (voice/finish.mjs) first, or pass the mp4 path.')
FPS = 30

# ---------------------------------------------------------------- reference parameters (references/reference-style.md)
REF = {
    'shot_s':          (4.3, 3.1, 5.1),     # average shot (between real picture changes), seconds
    'longest_s':       (8.3, 7.9, 8.6),
    'trans_per_min':   (13.0, 10.7, 18.2),
    'dissolve_share':  (95, 78.6, 100),     # % of transitions
    'whips':           (0, 0, 0),
    'size_changes_ps': (0.73, 0.51, 0.78),  # on the 7-step scale (EWS WS FS MS MCU CU INS)
    'size_changes_ps_engine': (0.52, 0.43, 0.67),  # on the engine's 5 sizes (XW WIDE MED CU MACRO)
    'locations_per_min': (9 / 62 * 60, 7 / 65.2 * 60, 13 / 56.1 * 60),
    'still_pct':       (8, 4, 21),          # frames with a still camera
    'motion_px720':    (3.2, 2.9, 4.7),     # median optical flow, px/frame at 720 wide
    'luma':            (42, 40.0, 44.6),    # mean BT.709 luma, % of full scale
    'p5':              (13, 10.7, 15.2),
    'p95':             (79, 76.2, 80.9),
    'sat':             (51, 48, 65),        # mean HSV saturation %
    'a':               (18, 12.7, 21.33),
    'cap_top':         (1321, 1315, 1327),  # px at 1080x1920
    'cap_base':        (1376, 1370, 1382),
    'cap_h':           (54, 51, 57),
    'cap_cx':          (540, 534, 546),
    'words_ps':        (3.75, 3.345, 3.91),
    'cards_ps':        (2.9, 2.73, 3.025),
    'one_word':        (75, 73.2, 79.2),
    'cap_cover':       (100, 99, 100),
}
SIZE_SHARE = {   # engine size -> (pooled target %, low, high); EWS=XW, WS=WIDE, FS+MS=MED, MCU+CU=CU, INS=MACRO
    'XW': (19.0, 6.0, 36.9), 'WIDE': (16.9, 12.7, 24.7), 'MED': (39.7, 33.3, 48.0), 'CU': (13.5, 6.4, 29.8), 'MACRO': (11.0, 2.1, 19.6)}
TO_ENGINE = {'EWS': 'XW', 'WS': 'WIDE', 'FS': 'MED', 'MS': 'MED', 'MCU': 'CU', 'CU': 'CU', 'INS': 'MACRO',
             'XW': 'XW', 'WIDE': 'WIDE', 'MED': 'MED', 'MACRO': 'MACRO'}
BAND = {  # signalstats on 1080x1920 RGB frames: YAVG p10..p90, SATAVG p10..p90 of reference frames per mood
    'day': (99, 146, 22, 44), 'dusk': (114, 153, 18, 35), 'interior': (67, 139, 19, 35), 'night': (69, 118, 29, 61)}

# per-style targets: critic/targets.json overrides the numbers above for a style measured from other references
# (written from references/styles/<style>.md). {"ref": {key: [target, low, high]}, "size_share": {...}, "band": {mood: [ylo, yhi, slo, shi]},
#  "skip": ["caption_geometry", "caption_cards"]}. Missing file = the bean-world reference above.
SKIP = set()
_TGT = os.path.join(HERE, 'critic', 'targets.json')
if os.path.exists(_TGT):
    _t = json.load(open(_TGT, encoding='utf-8-sig'))
    REF.update({k: tuple(v) for k, v in _t.get('ref', {}).items()})
    SIZE_SHARE.update({k: tuple(v) for k, v in _t.get('size_share', {}).items()})
    BAND.update({k: tuple(v) for k, v in _t.get('band', {}).items()})
    SKIP = set(_t.get('skip', []))

rows = []
def check(name, val, key=None, rng=None, unit='', info=False, fmt='{:.2f}'):
    t, lo, hi = REF[key] if key else rng
    tol = max(0.03 * abs(t), 0.1 * (hi - lo))        # sampling noise: frames are subsampled and resized for speed
    ok = lo - tol <= val <= hi + tol
    status = 'INFO' if info else ('PASS' if ok else 'FAIL')
    rows.append((status, name, fmt.format(val) + unit, f'{fmt.format(t)}{unit} ({fmt.format(lo)}–{fmt.format(hi)})'))


# ---------------------------------------------------------------- edit (shots.json)
shots = json.load(open(os.path.join(HERE, 'shots.json')))
N = max(s['f_out'] for s in shots)
dur = N / FPS
picture = [s for s in shots[1:] if s.get('transition_in', 'cut') != 'travel']          # travel = same camera move, no picture change
cuts = [s['f_in'] for s in picture]
segs = np.diff([0] + cuts + [N]) / FPS
check('Average shot (between picture changes)', float(np.mean(segs)), 'shot_s', unit=' s')
check('Longest shot', float(segs.max()), 'longest_s', unit=' s')
check('Transitions per minute', len(cuts) / dur * 60, 'trans_per_min')
kinds = [s.get('transition_in', 'cut') for s in picture]
if kinds:
    check('Dissolve share of transitions', 100 * sum(k == 'dissolve' for k in kinds) / len(kinds), 'dissolve_share', unit='%', fmt='{:.0f}')
check('Whip transitions', sum(k == 'whip' for k in kinds), 'whips', fmt='{:.0f}')
cross = os.path.isdir(os.path.join(HERE, 'render', 'pre_dissolve'))     # dissolve.py ran on the last render
rendered = os.path.isdir(os.path.join(HERE, 'render'))
rows.append(('INFO' if not rendered else 'PASS' if cross or 'dissolve' not in kinds else 'FAIL', 'Dissolves rendered as crossfades',
             'yes' if cross else 'no (dip to ink)' if rendered else 'no render/ folder',
             '8-frame crossfade, no dip (DISSOLVE=cross bash go.sh)'))

# shot size per frame: shot size, overridden by camera keys that carry "size" (held until the next key)
size = [None] * N
for s in shots:
    for f in range(s['f_in'], s['f_out']): size[f] = TO_ENGINE.get(s.get('size'), s.get('size'))
    keys = [k for k in s.get('camera', []) if k.get('size')]
    for i, k in enumerate(keys):
        end = keys[i + 1]['f'] if i + 1 < len(keys) else s['f_out']
        for f in range(max(k['f'], s['f_in']), min(end, s['f_out'])): size[f] = TO_ENGINE.get(k['size'], k['size'])
changes = sum(1 for f in range(1, N) if size[f] != size[f - 1])
fine = any(k.get('size') in ('EWS', 'WS', 'FS', 'MS', 'MCU', 'INS') for s in shots for k in s.get('camera', []))
if fine:   # keys use the 7-step reference scale: count on it before mapping to engine sizes
    FINE = {'XW': 'EWS', 'WIDE': 'WS', 'MED': 'FS', 'MACRO': 'INS'}   # a shot's engine size, read on the 7-step scale
    fsz = [None] * N
    for s in shots:
        for f in range(s['f_in'], s['f_out']): fsz[f] = FINE.get(s.get('size'), s.get('size'))
        ks = [k for k in s.get('camera', []) if k.get('size')]
        for i, k in enumerate(ks):
            end = ks[i + 1]['f'] if i + 1 < len(ks) else s['f_out']
            for f in range(max(k['f'], s['f_in']), min(end, s['f_out'])): fsz[f] = k['size']
    check('Shot-size changes per second (7-step scale)', sum(1 for f in range(1, N) if fsz[f] != fsz[f - 1]) / dur, 'size_changes_ps')
else:
    check('Shot-size changes per second (engine sizes)', changes / dur, 'size_changes_ps_engine')
for z, (t, lo, hi) in SIZE_SHARE.items():
    check(f'Time in {z}', 100 * sum(1 for x in size if x == z) / N, rng=(t, lo, hi), unit='%', fmt='{:.1f}')
loc = [None] * N     # location per frame: the shot's set, or a camera key's "loc" when the camera travels to another place
for s in shots:
    for f in range(s['f_in'], s['f_out']): loc[f] = s.get('loc') or s['set']
    ks = [k for k in s.get('camera', []) if k.get('loc')]
    for i, k in enumerate(ks):
        end = ks[i + 1]['f'] if i + 1 < len(ks) else s['f_out']
        for f in range(max(k['f'], s['f_in']), min(end, s['f_out'])): loc[f] = k['loc']
loc_changes = sum(1 for f in range(1, N) if loc[f] != loc[f - 1])
check('Locations per minute', len(set(loc)) / dur * 60, 'locations_per_min')
rows.append(('INFO', 'Location changes', str(loc_changes), '14 per ~62 s (6–15)'))

# ---------------------------------------------------------------- picture (final video)
def frames(path, step, w, h):
    """yield every step-th frame as an RGB array (streamed: a 60 s Short at 1080x1920 never sits in memory at once)"""
    cmd = ['ffmpeg', '-v', 'error', '-i', path, '-vf',
           f"select=not(mod(n\\,{step})),scale={w}:{h}:in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb24",
           '-vsync', '0', '-f', 'rawvideo', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = w * h * 3
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n: break
        yield np.frombuffer(buf, np.uint8).reshape(h, w, 3)
    p.wait()

probe = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', VIDEO],
                       capture_output=True, text=True).stdout.strip().split(',')
VW, VH = int(probe[0]), int(probe[1])
k = 1920 / VH
y0b, y1b = int(1250 / k), int(1450 / k)
lum, p5, p95, sat, aa, BANDS = [], [], [], [], [], []
for rgb in frames(VIDEO, 5, VW, VH):
    BANDS.append(rgb[y0b:y1b].copy())                     # keep only the caption band for the caption check
    sm = cv2.resize(rgb, (360, 640), interpolation=cv2.INTER_AREA).astype(np.float32)
    Y = 0.2126 * sm[..., 0] + 0.7152 * sm[..., 1] + 0.0722 * sm[..., 2]
    lum.append(Y.mean() / 2.55); p5.append(np.percentile(Y, 5) / 2.55); p95.append(np.percentile(Y, 95) / 2.55)
    sat.append(cv2.cvtColor(sm.astype(np.uint8), cv2.COLOR_RGB2HSV)[..., 1].mean() / 2.55)
    aa.append(cv2.cvtColor(sm / 255, cv2.COLOR_RGB2Lab)[..., 1].mean())
check('Mean luma', float(np.mean(lum)), 'luma', unit='%', fmt='{:.1f}')
check('Darkest 5% of pixels', float(np.mean(p5)), 'p5', unit='%', fmt='{:.1f}')
check('Brightest 5% of pixels', float(np.mean(p95)), 'p95', unit='%', fmt='{:.1f}')
check('Mean saturation (HSV)', float(np.mean(sat)), 'sat', unit='%', fmt='{:.1f}')
check('Red push, a*', float(np.mean(aa)), 'a', fmt='{:+.1f}')

# camera motion: median optical flow on 90x160 frames, every frame
G = [cv2.cvtColor(f, cv2.COLOR_RGB2GRAY) for f in frames(VIDEO, 1, 90, 160)]
mag = np.array([np.median(np.hypot(*np.moveaxis(cv2.calcOpticalFlowFarneback(G[i - 1], G[i], None, 0.5, 3, 9, 3, 5, 1.1, 0), 2, 0)))
                for i in range(1, len(G))]) * 8
check('Frames with a still camera', float((mag < 0.5).mean() * 100), 'still_pct', unit='%', fmt='{:.1f}')
check('Median camera motion (px/frame at 720 wide)', float(np.median(mag)), 'motion_px720')

# brightness/saturation per mood, signalstats units (same as gate.py)
moods = {}
for s in shots:
    m = {'night_in': 'night', 'night_card': 'night', 'night_warm': 'night', 'day_in': 'day', 'day_hot': 'day',
         'interior_in': 'interior', 'interior_lid': 'interior'}.get(s.get('mood', 'day'), s.get('mood', 'day'))
    moods.setdefault(m, []).append((s['f_in'], s['f_out']))
ss = subprocess.run(['ffmpeg', '-v', 'error', '-i', VIDEO, '-vf',
                     "select=not(mod(n\\,10)),scale=1080:1920:in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb24,signalstats,metadata=print:file=-",
                     '-vsync', '0', '-f', 'null', '-'], capture_output=True, text=True).stdout
vals, cur, n = {}, {}, 0
for line in ss.splitlines() + ['frame:end']:
    if line.startswith('frame:'):
        if cur:
            f = n * 10; n += 1
            m = next((k for k, spans in moods.items() if any(a <= f < b for a, b in spans)), 'day')
            vals.setdefault(m, []).append(cur)
        cur = {}
    mm = re.match(r'lavfi\.signalstats\.(YAVG|SATAVG)=([\d.]+)', line)
    if mm: cur[mm.group(1)] = float(mm.group(2))
for m, v in vals.items():
    if m not in BAND: continue
    ylo, yhi, slo, shi = BAND[m]
    y = float(np.median([x['YAVG'] for x in v])); s_ = float(np.median([x['SATAVG'] for x in v]))
    check(f'{m}: YAVG (signalstats, median)', y, rng=((ylo + yhi) / 2, ylo, yhi), fmt='{:.0f}')
    check(f'{m}: SATAVG (signalstats, median)', s_, rng=((slo + shi) / 2, slo, shi), fmt='{:.0f}')

# caption geometry: glyphs = near-white pixels next to a black outline, in the band around 70% of the height
if 'caption_geometry' in SKIP:
    rows.append(('INFO', 'Caption geometry', 'not checked (critic/targets.json "skip")', 'check the gate stills by eye'))
    BANDS = []
tops, bases, cxs, hs = [], [], [], []
for band in BANDS:
    band = band.astype(np.int16)
    mn, mx = band.min(2), band.max(2)
    txt = ((mn >= 200) & (mx - mn <= 40) & (cv2.dilate((mx <= 70).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0)).astype(np.uint8)
    n_, lbl, st, cen = cv2.connectedComponentsWithStats(txt, 8)
    comps = [tuple(st[i]) for i in range(1, n_) if 12 / k <= st[i][3] <= 80 / k and st[i][2] <= 140 / k and st[i][4] >= 30 / k]
    if not comps: continue
    comps.sort(); c = np.array([x + w / 2 for x, y, w, h, a in comps]); i0 = int(np.argmin(abs(c - VW / 2)))
    if abs(c[i0] - VW / 2) > VW * 0.28: continue
    L = R = i0
    while L > 0 and comps[L - 1][0] + comps[L - 1][2] >= comps[L][0] - 30 / k: L -= 1
    while R < len(comps) - 1 and comps[R + 1][0] <= comps[R][0] + comps[R][2] + 30 / k: R += 1
    g = comps[L:R + 1]
    tops.append((min(x[1] for x in g) + y0b) * k); bases.append((max(x[1] + x[3] for x in g) + y0b) * k)
    cxs.append((min(x[0] for x in g) + max(x[0] + x[2] for x in g)) / 2 * k)
if tops:
    top, base = float(np.percentile(tops, 25)), float(np.percentile(bases, 25))   # the 25th percentile = caps / no descenders
    check('Caption cap top (px at 1080x1920)', top, 'cap_top', fmt='{:.0f}')
    check('Caption baseline (px at 1080x1920)', base, 'cap_base', fmt='{:.0f}')
    check('Caption cap height (px at 1080x1920)', base - top, 'cap_h', fmt='{:.0f}')
    check('Caption centre x (px at 1080x1920)', float(np.median(cxs)), 'cap_cx', fmt='{:.0f}')
elif 'caption_geometry' not in SKIP:
    rows.append(('FAIL', 'Captions', 'none found near 70% of the height', 'every frame has a caption'))

# ---------------------------------------------------------------- captions + narration (captions.ass, voice-timing.json)
ass = os.path.join(HERE, 'voice', 'captions.ass')
tm = os.path.join(HERE, 'voice', 'voice-timing.json')
def secs(t):
    h, m, s = t.split(':'); return int(h) * 3600 + int(m) * 60 + float(s)
if os.path.exists(ass) and 'caption_cards' not in SKIP:
    ev = []
    for line in open(ass, encoding='utf-8-sig'):
        if not line.startswith('Dialogue:'): continue
        p = line.rstrip('\n').split(',', 9)
        if p[3] != 'W': continue                                    # main text layer only
        txt = re.sub(r'\{[^}]*\}', '', p[9]); ev.append((secs(p[1]), secs(p[2]), txt, p[9]))
    if ev:
        nw = [len(t.split()) for _, _, t, _ in ev]
        check('Caption cards per second', len(ev) / dur, 'cards_ps')
        check('One-word cards', 100 * sum(w == 1 for w in nw) / len(nw), 'one_word', unit='%', fmt='{:.0f}')
        cover = np.zeros(N, bool)
        for a, b, _, _ in ev: cover[int(round(a * FPS)):int(round(b * FPS))] = True
        check('Frames with a caption', 100 * cover.mean(), 'cap_cover', unit='%', fmt='{:.1f}')
        anim = sum(1 for *_, raw_ in ev if re.search(r'\\t\(|\\fad|\\move', raw_))
        rows.append(('PASS' if not anim else 'FAIL', 'Caption entry animation', f'{anim} animated cards', 'none (cards cut on one frame)'))
if os.path.exists(tm):
    T = json.load(open(tm, encoding='utf-8-sig'))
    words = sum(len(l['words']) for l in T['lines'])
    check('Narration words per second', words / dur, 'words_ps')

# ---------------------------------------------------------------- report
w = max(len(r[1]) for r in rows)
lines = [f'{st:4}  {name:<{w}}  {val:>14}   ref {ref}' for st, name, val, ref in rows]
nf = sum(r[0] == 'FAIL' for r in rows)
lines.append(f'\n{sum(r[0] == "PASS" for r in rows)} PASS, {nf} FAIL, {sum(r[0] == "INFO" for r in rows)} INFO  ({os.path.basename(VIDEO)}, {dur:.2f} s)')
print('\n'.join(lines))
os.makedirs(os.path.join(HERE, 'critic'), exist_ok=True)
with open(os.path.join(HERE, 'critic', 'audit.md'), 'w') as fh:
    fh.write('# Style audit against references/reference-style.md\n\n| Result | Parameter | Ours | Reference target (range) |\n|---|---|---|---|\n')
    fh.writelines(f'| {st} | {name} | {val} | {ref} |\n' for st, name, val, ref in rows)
