import json, re, sys, numpy as np, pandas as pd, cv2
from PIL import Image, ImageDraw, ImageFont
D = sys.argv[1]

A = json.load(open(f'{D}/analysis.json'))
S, SH = A['summary'], A['shots']
pf = pd.read_csv(f'{D}/per_frame_full.csv')
cards = pd.read_csv(f'{D}/caption_cards.csv')
bar = np.load(f'{D}/colour_samples.npz')['barcode']           # (N,64,3) RGB
occ = np.load(f'{D}/caption_occupancy.npy')
N = len(pf)

import os as _os
_CANDS = {'Bold': ['/usr/share/fonts/opentype/inter/Inter-Bold.otf', '/System/Library/Fonts/Supplemental/Arial Bold.ttf', 'C:/Windows/Fonts/arialbd.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'],
          'SemiBold': ['/usr/share/fonts/opentype/inter/Inter-SemiBold.otf', '/System/Library/Fonts/Supplemental/Arial Bold.ttf', 'C:/Windows/Fonts/arialbd.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'],
          'Regular': ['/usr/share/fonts/opentype/inter/Inter-Regular.otf', '/System/Library/Fonts/Supplemental/Arial.ttf', 'C:/Windows/Fonts/arial.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']}
def font(w, s):
    for f in _CANDS.get(w, _CANDS['Regular']):
        if _os.path.exists(f): return ImageFont.truetype(f, s)
    return ImageFont.load_default(s)
f_title, f_h2, f_b, f_r, f_s, f_xs = font('Bold', 46), font('SemiBold', 30), font('SemiBold', 22), font('Regular', 22), font('Regular', 19), font('Regular', 16)
f_big = font('Bold', 40)
SURF, INK, INK2, MUTED, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#8a8984', '#e4e3df'
BLUE, ORANGE = '#2a78d6', '#eb6834'

W = 2400; M = 60
img = Image.new('RGB', (W, 5200), SURF); d = ImageDraw.Draw(img, 'RGBA')

def frame(i):
    return Image.open(f'{D}/frames/f_{i + 1:05d}.jpg').convert('RGB')

# ---------------- header ----------------
y = 50
d.text((M, y), f"{S['title']} — contact sheet", font=f_title, fill=INK); y += 64
d.text((M, y), f"720×1280 · 30 fps · {N:,} frames · {S['duration']:.2f} s · every frame decoded and measured (BT.709)", font=f_r, fill=INK2); y += 50
tiles = [
    (f"{S['shots']}", 'shots', f"{S['transitions']} transitions: " + ', '.join(x for x in [f"{S['dissolves']} dissolves" if S['dissolves'] else '', f"{S['hard_cuts']} hard cuts" if S['hard_cuts'] else '', f"{S['hidden_cuts']} hidden cuts" if S['hidden_cuts'] else '', f"{len(S['other_transitions'])} other" if S['other_transitions'] else ''] if x)),
    (f"{S['asl']:.2f} s", 'average shot', f"median {S['shot_len_median']:.2f} s · range {S['shot_len_min']:.2f}–{S['shot_len_max']:.2f} s"),
    (f"{S['size_changes']}", 'shot-size changes', f"{S['size_changes_per_sec']:.2f}/s · a new size every {S['size_hold_mean']:.2f} s on average"),
    (f"{S['locations']}", 'locations', f"{S['location_changes']} location changes"),
    (f"{S['luma_mean']:.1f}%", 'mean brightness', f"p5 {S['p5']:.0f}% · p95 {S['p95']:.0f}% · contrast SD {S['contrast_sd']:.1f}%"),
    (f"{S['sat']:.0f}%", 'mean saturation', f"colourfulness {S['colourfulness']:.0f} · {S['warm_frames_pct']:.0f}% of frames warm (b*>0)"),
]
tw = (W - 2 * M - 5 * 16) / 6
for k, (big, lab, sub) in enumerate(tiles):
    x = M + k * (tw + 16)
    d.rounded_rectangle([x, y, x + tw, y + 128], 10, fill='#f1f0ec')
    d.text((x + 18, y + 12), big, font=f_big, fill=INK)
    d.text((x + 18, y + 62), lab, font=f_b, fill=INK)
    # wrap sub
    words, line, ly = sub.split(), '', y + 92
    for wd in words:
        t = (line + ' ' + wd).strip()
        if d.textlength(t, font=f_xs) > tw - 30:
            d.text((x + 18, ly), line, font=f_xs, fill=INK2); ly += 19; line = wd
        else:
            line = t
    d.text((x + 18, ly), line, font=f_xs, fill=INK2)
y += 128 + 50

# ---------------- every-frame timeline ----------------
d.text((M, y), f'Every frame, 0–{N - 1}', font=f_h2, fill=INK); y += 46
X0, X1 = M + 270, W - M
sc = (X1 - X0) / N
fx = lambda f: X0 + f * sc
starts = [s['start'] for s in SH]

def row_label(yy, h, title, sub=None):
    d.text((M, yy + h / 2 - (20 if sub else 11)), title, font=f_b, fill=INK)
    if sub: d.text((M, yy + h / 2 + 4), sub, font=f_xs, fill=INK2)

# 1 colour barcode
h = 120
bc = Image.fromarray(np.transpose(bar, (1, 0, 2)).astype(np.uint8)).resize((int(X1 - X0), h), Image.NEAREST)
img.paste(bc, (int(X0), int(y)))
row_label(y, h, 'Colour', 'frame avg, top→bottom')
y += h + 14

# 2 shots
h = 40
for k, s in enumerate(SH):
    d.rectangle([fx(s['start']), y, fx(s['end'] + 1), y + h], fill='#ecebe7' if k % 2 == 0 else '#dcdbd6')
for s in SH:
    if s['transition_span'] and s['transition_in'].startswith('Dissolve'):
        a, b = map(int, s['transition_span'].split('–'))
        d.rectangle([fx(a), y, fx(b + 1), y + h], fill='#a9a8a3')
    elif s['transition_in'] != 'Start':
        d.rectangle([fx(s['start']) - 1, y - 4, fx(s['start']) + 1, y + h + 4], fill=INK)
for s in SH:
    cx = (fx(s['start']) + fx(s['end'] + 1)) / 2
    t = str(s['shot'])
    if d.textlength(t, font=f_b) + 4 <= fx(s['end'] + 1) - fx(s['start']):
        d.text((cx - d.textlength(t, font=f_b) / 2, y + 7), t, font=f_b, fill=INK)
row_label(y, h, 'Shots', 'grey dissolve, black cut')
y += h + 18

# 3 shot size (ordinal step)
levels = ['EWS', 'WS', 'FS', 'MS', 'MCU', 'CU', 'INS']
h = 175; step = h / (len(levels) - 1)
ly = {L: y + h - i * step for i, L in enumerate(levels)}
for L in levels:
    d.line([X0, ly[L], X1, ly[L]], fill=GRID, width=1)
    d.text((X0 - 44, ly[L] - 9), L, font=f_xs, fill=INK2)
pts = []
for i, s in enumerate(pf.shot_size):
    pts += [(fx(i), ly[s]), (fx(i + 1), ly[s])]
d.line(pts, fill=BLUE, width=3, joint='curve')
d.text((M, y + 6), 'Shot size', font=f_b, fill=INK)
d.text((M, y + 34), 'coded per frame', font=f_xs, fill=INK2)
d.text((M, y + 54), f"{S['size_changes']} changes", font=f_xs, fill=INK2)
y += h + 40

# 4 brightness
h = 130
def yv(v, top, hh): return top + hh - v / 100 * hh
for v in (0, 50, 100):
    d.line([X0, yv(v, y, h), X1, yv(v, y, h)], fill=GRID, width=1)
    d.text((X0 - 44, yv(v, y, h) - 9), f'{v}%', font=f_xs, fill=INK2)
p5 = pf.luma_p5.values / 2.55; p95 = pf.luma_p95.values / 2.55; mu = pf.luma_mean.values / 2.55
poly = [(fx(i), yv(p95[i], y, h)) for i in range(N)] + [(fx(i), yv(p5[i], y, h)) for i in range(N - 1, -1, -1)]
d.polygon(poly, fill=(42, 120, 214, 46))
d.line([(fx(i), yv(mu[i], y, h)) for i in range(N)], fill=BLUE, width=2)
row_label(y, h, 'Brightness', 'mean luma; band p5–p95')
y += h + 34

# 5 saturation
h = 110
for v in (0, 50, 100):
    d.line([X0, yv(v, y, h), X1, yv(v, y, h)], fill=GRID, width=1)
    d.text((X0 - 44, yv(v, y, h) - 9), f'{v}%', font=f_xs, fill=INK2)
d.line([(fx(i), yv(pf.sat_mean.values[i], y, h)) for i in range(N)], fill=ORANGE, width=2)
row_label(y, h, 'Saturation', 'mean HSV S')
y += h + 22

# 6 location
h = 40
segs = []
for i, l in enumerate(pf.location):
    if not segs or segs[-1][2] != l: segs.append([i, i, l])
    else: segs[-1][1] = i
for k, (a, b, l) in enumerate(segs):
    d.rectangle([fx(a), y, fx(b + 1), y + h], fill='#ecebe7' if k % 2 == 0 else '#dcdbd6')
    t = f'L{l}'; cx = (fx(a) + fx(b + 1)) / 2
    if d.textlength(t, font=f_s) + 4 <= fx(b + 1) - fx(a):   # skip labels wider than their segment
        d.text((cx - d.textlength(t, font=f_s) / 2, y + 9), t, font=f_s, fill=INK)
row_label(y, h, 'Location', 'see key below')
y += h + 18

# 7 caption changes
h = 30
for s in cards.start:
    d.line([fx(s), y, fx(s), y + h], fill=INK, width=1)
row_label(y, h, 'Caption cards', f"{len(cards)} · tick = new card")
y += h + 10

# x axis
for sec in range(0, int(N / 30) + 1, 5):
    x = fx(sec * 30)
    d.line([x, y, x, y + 8], fill=INK2, width=1)
    t = f'{sec}s'; d.text((x - d.textlength(t, font=f_xs) / 2, y + 10), t, font=f_xs, fill=INK2)
y += 40
# location key
lk = A['LOC']
keytxt = '   '.join(f"L{k} {v}" for k, v in lk.items())
words, line = keytxt.split('   '), ''
for wd in words:
    t = (line + '   ' + wd) if line else wd
    if d.textlength(t, font=f_s) > W - 2 * M - 210:
        d.text((X0, y), line, font=f_s, fill=INK2); y += 26; line = wd
    else:
        line = t
d.text((X0, y), line, font=f_s, fill=INK2); y += 26
d.text((X0, y), 'Sizes: EWS extreme wide/no figure · WS figure small · FS whole figure · MS knees/waist up · MCU chest up · CU head/close body · INS object detail',
       font=f_s, fill=INK2)
y += 60

# ---------------- shot-by-shot ----------------
d.text((M, y), 'Shot by shot — one frame per shot-size segment (middle frame of each)', font=f_h2, fill=INK); y += 52
colw = (W - 2 * M - 40) / 2
tw_, th_ = 72, 128
rowh = 226
size_spans = A['size_spans']
per_col = (len(SH) + 1) // 2
for k, s in enumerate(SH):
    col, r = (0, k) if k < per_col else (1, k - per_col)
    x = M + col * (colw + 40); yy = y + r * rowh
    d.line([x, yy - 10, x + colw, yy - 10], fill=GRID, width=1)
    d.text((x, yy), f"Shot {s['shot']}", font=f_h2, fill=INK)
    tin = s['transition_in']
    lines = [f"{s['tc_in']}–{s['tc_out']} · {s['secs']:.2f} s",
             f"frames {s['start']}–{s['end']} ({s['frames']})",
             f"in: {tin}" + (f" {s['transition_span']}" if s['transition_span'] else ''),
             f"location L{s['locations'].replace(' → ', ' → L')}",
             f"luma {s['luma_mean']:.0f}% · sat {s['sat']:.0f}%",
             f"b* {s['b']:+.1f} · a* {s['a']:+.1f}",
             f"{s['captions']} caption cards"]
    for j, t in enumerate(lines):
        d.text((x, yy + 40 + j * 24), t, font=f_xs, fill=INK2)
    tx = x + 240
    segs = [(max(a, s['start']), min(b, s['end']), z) for a, b, z in size_spans if b >= s['start'] and a <= s['end']]
    avail = colw - 240 - 150
    tw2 = int(min(tw_, avail / max(1, len(segs)) - 7)); th2 = int(tw2 * 16 / 9)
    for j, (a, b, z) in enumerate(segs):
        xx = tx + j * (tw2 + 7)
        th = frame((a + b) // 2).resize((tw2, th2), Image.LANCZOS)
        d.text((xx, yy + 2), z, font=font('SemiBold', 17), fill=INK)
        img.paste(th, (int(xx), int(yy + 26)))
        lab = f'{a}–{b}'
        d.text((xx, yy + 26 + th2 + 4), lab, font=font('Regular', 12 if tw2 >= 60 else 10), fill=INK2)
    # palette
    px = x + colw - 140
    d.text((px, yy + 2), 'palette', font=font('SemiBold', 17), fill=INK)
    for j, (hx, share) in enumerate(s['palette']):
        d.rectangle([px, yy + 28 + j * 34, px + 44, yy + 28 + j * 34 + 28], fill=hx)
        d.text((px + 52, yy + 28 + j * 34 + 4), f'{hx} {share * 100:.0f}%', font=font('Regular', 14), fill=INK2)
y += per_col * rowh + 30

# ---------------- captions ----------------
d.line([M, y - 10, W - M, y - 10], fill=GRID, width=1)
d.text((M, y), f'Caption position — all {N:,} frames overlaid', font=f_h2, fill=INK); y += 52
fw, fh = 324, 576
base = frame(N // 2).resize((fw, fh), Image.LANCZOS)
base = Image.blend(base, Image.new('RGB', base.size, '#ffffff'), 0.55)
heat = cv2.resize(occ, (fw, fh), interpolation=cv2.INTER_AREA)
heat = np.clip(heat / heat.max(), 0, 1)
ov = np.array(base).astype(np.float32)
blue = np.array([42, 120, 214], np.float32)
a_ = np.clip(heat * 2.2, 0, 1)[..., None] * 0.95
ov = ov * (1 - a_) + blue * a_
img.paste(Image.fromarray(ov.astype(np.uint8)), (M, int(y)))
d.rectangle([M, y, M + fw, y + fh], outline=INK, width=2)
cg = S['captions']
def ypx(v): return y + v / 1280 * fh
for v, lab in ((cg['cap_top_px'], 'cap top'), (cg['baseline_px'], 'baseline')):
    d.line([M + fw, ypx(v), M + fw + 14, ypx(v)], fill=INK, width=2)
    d.line([M, ypx(v), M + fw, ypx(v)], fill=(11, 11, 11, 120), width=1)
d.line([M + fw / 2, y, M + fw / 2, y + fh], fill=(11, 11, 11, 90), width=1)
tx = M + fw + 60; ty = y
facts = [
    ('Vertical', f"cap top {cg['cap_top_px']:.0f} px ({cg['cap_top_px'] / 12.8:.1f}%) · baseline {cg['baseline_px']:.0f} px ({cg['baseline_px'] / 12.8:.1f}%) · line centre {cg['line_centre_y_px']:.0f} px = {cg['line_centre_y_px'] / 12.8:.1f}% from top"),
    ('', f"descenders to {cg['descender_px']:.0f} px ({cg['descender_px'] / 12.8:.1f}%) · {1280 - cg['baseline_px']:.0f} px ({(1280 - cg['baseline_px']) / 12.8:.1f}%) clear below the baseline · {cg['cards_within_3px_of_centre']} of {cg['cards']} cards within 3 px of centre"),
    ('Horizontal', f"centred: median box centre x = {cg['centre_x_px']:.1f} px of 720 ({cg['centre_x_px'] / 7.2:.1f}%)"),
    ('', f"width {cg['min_w_px']:.0f}–{cg['max_w_px']:.0f} px ({cg['min_w_px'] / 7.2:.0f}–{cg['max_w_px'] / 7.2:.0f}% of frame width), median {cg['med_w_px']:.0f} px ({cg['med_w_px'] / 7.2:.0f}%)"),
    ('Size', f"cap height {cg['cap_height_px']:.0f} px = {cg['cap_height_px'] / 12.8:.1f}% of frame height ({cg['cap_height_px'] * 1.5:.0f} px at 1080×1920) · x-height {cg['xheight_px']:.0f} px"),
    ('Style', cg.get('style', '')),
    ('Cards', f"{cg['cards']} cards · {cg['words']} words · {cg['one_word_cards']} one-word, {cg['two_word_cards']} two-word, {cg['three_word_cards']} three-word"),
    ('', f"on screen {cg['min_card_frames']}–{cg['max_card_frames']} frames, median {cg['median_card_frames']:.0f} frames ({cg['median_card_frames'] / 30:.2f} s) · {cg['words'] / S['duration']:.2f} words/s · caption on 100% of frames"),
]
for lab, t in facts:
    if lab: d.text((tx, ty), lab, font=f_b, fill=INK)
    d.text((tx + 150, ty + 2), t, font=f_s, fill=INK2); ty += 40
_c = cards.loc[cards.frames.idxmax()]
_cy = int(cg['line_centre_y_px'])
ex = frame(int((_c.start + _c.end) // 2)).crop((180, _cy - 45, 540, _cy + 45)).resize((540, 135), Image.LANCZOS)
img.paste(ex, (int(tx + 150), int(ty + 70)))
d.text((tx, ty + 70), 'Sample', font=f_b, fill=INK)
d.text((tx, ty + 96), f'frame {int((_c.start + _c.end) // 2)}, 1.5×', font=f_xs, fill=INK2)
d.text((tx, ty + 20), 'Blue = how often a caption pixel occupied that spot (darker = more frames). Lines = measured cap top and baseline.', font=f_s, fill=MUTED)
y += fh + 50
img = img.crop((0, 0, W, int(y)))
slug = re.sub(r'[^a-z0-9]+', '_', S['title'].lower()).strip('_')
out = f"{D}/contact_sheet_{S['key']}_{slug}.png"
img.save(out, optimize=True); print(out)
print(img.size)
