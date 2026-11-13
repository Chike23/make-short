"""Frame-accurate reference measurement (make-short/measure).  Usage:  python3 -I pipeline.py <step> <video_dir> [args]
Folder layout: <dir>/source.<ext> (the download, any size or frame rate), <dir>/video.mp4 (720x1280, 30 fps, made by prep),
<dir>/frames/f_00001.jpg (= frame 0) ...
Steps (in order): prep [file], measure, small, sheets, capband, captions, [agent writes caption_cards.csv + annotations.json],
capbox, capstyle, assemble, contact.   Helpers: strip <a> <b> [name], blendfit <a> <b>, grid <name> <a:b:step>...
"""
import sys, os, json, subprocess, collections
import numpy as np, pandas as pd, cv2

W, H, FPS = 720, 1280, 30


SOURCE_EXTS = ('.mp4', '.mov', '.m4v', '.webm', '.mkv')


def _probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                          'stream=width,height,r_frame_rate,avg_frame_rate,nb_frames:format=duration',
                          '-of', 'json', path], capture_output=True, text=True, check=True).stdout
    j = json.loads(out); s = j['streams'][0]
    rate = lambda r: (lambda a, b: float(a) / float(b) if float(b) else 0.0)(*r.split('/'))
    return dict(width=int(s['width']), height=int(s['height']), r_fps=rate(s['r_frame_rate']), avg_fps=rate(s['avg_frame_rate']),
                nb_frames=int(s.get('nb_frames') or 0), duration=float(j.get('format', {}).get('duration') or 0))


def _need_prep(d):
    """Every step reads <dir>/video.mp4 as 720x1280 at exactly 30 fps. Stop with a clear message if prep was skipped."""
    v = f'{d}/video.mp4'
    if not os.path.exists(v):
        raise SystemExit(f'{d}: no video.mp4. Put the reference in the folder (any name, any frame rate) and run: pipeline.py prep {d}')
    p = _probe(v)
    if (p['width'], p['height']) != (W, H) or abs(p['r_fps'] - FPS) > 0.01 or abs(p['avg_fps'] - FPS) > 0.05:
        raise SystemExit(f"{d}/video.mp4 is {p['width']}x{p['height']} at {p['avg_fps']:.3f} fps. Run: pipeline.py prep {d} "
                         f"(it keeps the original and writes a {W}x{H}, {FPS} fps video.mp4)")


# ------------------------------------------------------------------ prep: any reference -> 720x1280 at 30 fps
def prep(d, src=None):
    """Normalise one reference to the format every other step expects, then extract every frame.
    Instagram / TikTok / YouTube downloads come at 24, 25, 30, 50 or 60 fps and 720 or 1080 wide; all measuring is done at 30 fps.
    The original stays in the folder (an old video.mp4 is renamed source.mp4); source_meta.json records its real size and frame rate."""
    os.makedirs(d, exist_ok=True)
    if src is None:
        found = sorted(f for f in os.listdir(d) if f.lower().endswith(SOURCE_EXTS) and f != 'video.mp4' and not f.startswith('.'))
        src_name = next((f for f in found if f.startswith('source.')), found[0] if found else None)
        if src_name is None and os.path.exists(f'{d}/video.mp4'):
            src_name = 'source.mp4'; os.rename(f'{d}/video.mp4', f'{d}/source.mp4')
        if src_name is None:
            raise SystemExit(f'{d}: no video found. Put the downloaded reference (.mp4/.mov/.webm) in this folder first.')
        src = f'{d}/{src_name}'
    else:
        ext = os.path.splitext(src)[1].lower() or '.mp4'
        dst = f'{d}/source{ext}'
        if os.path.abspath(src) != os.path.abspath(dst):
            subprocess.run(['cp', src, dst], check=True)
        src = dst
    meta = _probe(src); meta['source'] = os.path.basename(src)
    fps = meta['avg_fps'] or meta['r_fps']
    vf = (f'fps={FPS},scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos:out_color_matrix=bt709,'
          f'pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black,setsar=1,format=yuv420p')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', src, '-vf', vf, '-r', str(FPS), '-fps_mode', 'cfr',
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', '12',
                    '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv',
                    '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', f'{d}/video.mp4'], check=True)
    fr = f'{d}/frames'
    if os.path.isdir(fr):
        for f in os.listdir(fr):
            if f.endswith('.jpg'): os.remove(os.path.join(fr, f))
    os.makedirs(fr, exist_ok=True)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', f'{d}/video.mp4', '-fps_mode', 'passthrough', '-q:v', '3',
                    f'{fr}/f_%05d.jpg'], check=True)
    out = _probe(f'{d}/video.mp4'); n = nframes(d)
    meta.update(measured_fps=FPS, measured_size=[W, H], measured_frames=n, measured_duration=n / FPS)
    note = ''
    if abs(fps - FPS) > 0.05:
        if fps < FPS:
            note = (f'{fps:g} fps source: ffmpeg repeats about {FPS - fps:.0f} frames a second to reach {FPS} fps, '
                    f'so evenly spaced zero-difference frames are repeats, not holds.')
        else:
            note = (f'{fps:g} fps source: ffmpeg keeps {FPS} of every {fps:g} frames, so a dissolve or flash shorter than '
                    f'{1000 / FPS:.0f} ms can lose a frame. Check short transitions in source.* if they matter.')
    if abs(meta['width'] / meta['height'] - W / H) > 0.01:
        note += (f" Not 9:16 ({meta['width']}x{meta['height']}): prep added black bars, which raise pct_black and lower luma_mean; "
                 f"crop them out of colour numbers or use a 9:16 download.")
    meta['note'] = note.strip()
    json.dump(meta, open(f'{d}/source_meta.json', 'w'), indent=1)
    if (out['width'], out['height']) != (W, H) or abs(out['avg_fps'] - FPS) > 0.05:
        raise SystemExit(f'prep failed: video.mp4 is {out}')
    print(f"{d}: {meta['source']} {meta['width']}x{meta['height']} at {fps:.3f} fps -> video.mp4 {W}x{H} at {FPS} fps, "
          f"{n} frames ({n / FPS:.2f} s). {meta['note']}".rstrip())


def nframes(d):
    return len([f for f in os.listdir(f'{d}/frames') if f.endswith('.jpg')])


def frame_path(d, i):
    return f'{d}/frames/f_{i + 1:05d}.jpg'


# ------------------------------------------------------------------ measure
def measure(d):
    _need_prep(d)
    cmd =['ffmpeg', '-v', 'error', '-i', f'{d}/video.mp4', '-vf',
           'scale=in_color_matrix=bt709:in_range=tv:out_range=pc:flags=neighbor+full_chroma_int,format=rgb24',
           '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    rows, samples, bar = [], [], []
    i = 0
    while True:
        buf = p.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        rgb = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        f = rgb.astype(np.float32)
        R, G, B = f[..., 0], f[..., 1], f[..., 2]
        Y = 0.2126 * R + 0.7152 * G + 0.0722 * B
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV_FULL).astype(np.float32)
        h = hsv[..., 0] * (2 * np.pi / 256); s = hsv[..., 1] / 255; v = hsv[..., 2] / 255
        w = s * v
        sx, cx = (w * np.sin(h)).sum(), (w * np.cos(h)).sum()
        lab = cv2.cvtColor((f / 255).astype(np.float32), cv2.COLOR_RGB2Lab)
        rg = R - G; yb = 0.5 * (R + G) - B
        rows.append(dict(frame=i, t=i / FPS,
                         luma_mean=Y.mean(), luma_std=Y.std(), luma_p5=np.percentile(Y, 5), luma_p50=np.percentile(Y, 50),
                         luma_p95=np.percentile(Y, 95), pct_black=(Y < 10).mean() * 100, pct_white=(Y > 245).mean() * 100,
                         sat_mean=s.mean() * 100, sat_p90=np.percentile(s, 90) * 100,
                         colourfulness=np.sqrt(rg.std() ** 2 + yb.std() ** 2) + 0.3 * np.sqrt(rg.mean() ** 2 + yb.mean() ** 2),
                         hue_deg=(np.degrees(np.arctan2(sx, cx)) + 360) % 360, hue_strength=np.hypot(sx, cx) / (w.sum() + 1e-9),
                         L=lab[..., 0].mean(), a=lab[..., 1].mean(), b=lab[..., 2].mean(),
                         R=R.mean(), G=G.mean(), B=B.mean(),
                         luma_top=Y[:427].mean(), luma_mid=Y[427:853].mean(), luma_bot=Y[853:].mean()))
        samples.append(cv2.resize(rgb, (36, 64), interpolation=cv2.INTER_AREA).reshape(-1, 3))
        bar.append(cv2.resize(rgb, (1, 64), interpolation=cv2.INTER_AREA)[:, 0, :])
        i += 1
    pd.DataFrame(rows).to_csv(f'{d}/per_frame.csv', index=False)
    np.savez_compressed(f'{d}/colour_samples.npz', samples=np.array(samples), barcode=np.array(bar))
    print(d, 'measured', i, 'frames')


# ------------------------------------------------------------------ small frames + diffs
def small(d):
    _need_prep(d)
    cmd =['ffmpeg', '-v', 'error', '-i', f'{d}/video.mp4', '-vf', 'scale=90:160:flags=area,format=bgr24', '-f', 'rawvideo', '-']
    raw = subprocess.run(cmd, capture_output=True).stdout
    sm = np.frombuffer(raw, np.uint8).reshape(-1, 160, 90, 3)
    N = len(sm)
    hs = []
    for f in sm:
        hh = cv2.calcHist([cv2.cvtColor(f, cv2.COLOR_BGR2HSV)], [0, 1, 2], None, [18, 6, 6], [0, 180, 0, 256, 0, 256])
        hs.append((hh / hh.sum()).flatten())
    hs = np.array(hs, np.float32)
    band = None
    if os.path.exists(f'{d}/caption_band.json'):
        band = json.load(open(f'{d}/caption_band.json'))
    mask = np.ones(160, bool)
    if band:
        mask[int((band['y_centre'] - 50) / 8): int((band['y_centre'] + 50) / 8) + 1] = False
    g = sm[:, mask].astype(np.float32).mean(axis=3)
    mad = np.r_[np.nan, np.abs(np.diff(g, axis=0)).mean(axis=(1, 2))]
    bh = np.r_[np.nan, [cv2.compareHist(hs[i - 1], hs[i], cv2.HISTCMP_BHATTACHARYYA) for i in range(1, N)]]
    def nc(a, b):
        a = a - a.mean(); b = b - b.mean(); return (a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum() + 1e-9)
    corr = np.r_[np.nan, [nc(g[i - 1], g[i]) for i in range(1, N)]]
    def spike(x):
        out = np.full(N, np.nan)
        for i in range(1, N):
            nb = np.r_[x[max(1, i - 4):i], x[i + 1:i + 5]]
            out[i] = x[i] / (np.nanmedian(nb) + 1e-3)
        return out
    df = pd.DataFrame(dict(frame=np.arange(N), mad=mad, bhatt=bh, corr=corr, mad_spike=spike(mad), bh_spike=spike(bh)))
    df.to_csv(f'{d}/diffs.csv', index=False)
    np.savez_compressed(f'{d}/small.npz', small=sm, hists=hs)
    cand = df[((df.mad_spike > 2.5) & (df.mad > 8)) | (df.bhatt > 0.35) | ((df['corr'] < 0.5) & (df.mad_spike > 1.8))]
    print(d, N, 'frames; cut candidates (frame = first frame after the change):')
    print(cand.round(3).to_string())
    # plot
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    rows = int(np.ceil(N / 490))
    fig, ax = plt.subplots(rows, 1, figsize=(22, 3 * rows))
    ax = np.atleast_1d(ax)
    for k in range(rows):
        s = df.iloc[k * 490:(k + 1) * 490]
        ax[k].plot(s.frame, s.mad, lw=.8, label='mean abs diff'); ax[k].plot(s.frame, s.bhatt * 50, lw=.8, label='hist dist x50')
        ax[k].plot(s.frame, (1 - s['corr']) * 50, lw=.8, label='(1-corr) x50')
        ax[k].set_xticks(range(k * 490, (k + 1) * 490, 10)); ax[k].tick_params(axis='x', labelsize=6, rotation=90); ax[k].grid(alpha=.3); ax[k].set_ylim(0, 50)
    ax[0].legend(); plt.tight_layout(); plt.savefig(f'{d}/diffplot.png', dpi=75)


# ------------------------------------------------------------------ review grids
def sheets(d, per=240, cols=20):
    from PIL import Image, ImageDraw
    sm = np.load(f'{d}/small.npz')['small']
    N = len(sm); rows = per // cols; tw, th, lab = 90, 160, 14
    os.makedirs(f'{d}/sheets', exist_ok=True)
    for s in range(0, N, per):
        im = Image.new('RGB', (cols * (tw + 2), rows * (th + lab + 2)), 'white'); dr = ImageDraw.Draw(im)
        for k in range(per):
            i = s + k
            if i >= N: break
            x = (k % cols) * (tw + 2); y = (k // cols) * (th + lab + 2)
            im.paste(Image.fromarray(sm[i][..., ::-1]), (x, y + lab)); dr.text((x + 2, y + 1), str(i), fill='black')
        im.save(f'{d}/sheets/sheet_{s:04d}.png')
    print('sheets in', f'{d}/sheets')


def strip(d, a, b, name=None, w=150):
    from PIL import Image, ImageDraw
    fr = list(range(a, b + 1)); h = int(w * H / W)
    im = Image.new('RGB', (len(fr) * (w + 3), h + 14), 'white'); dr = ImageDraw.Draw(im)
    for k, i in enumerate(fr):
        im.paste(Image.open(frame_path(d, i)).resize((w, h)), (k * (w + 3), 14)); dr.text((k * (w + 3) + 3, 1), str(i), fill='black')
    os.makedirs(f'{d}/strips', exist_ok=True)
    out = f'{d}/strips/{name or f"s{a}_{b}"}.jpg'; im.save(out, quality=86); print(out)


def grid(d, name, specs, cols=14, w=110):
    """specs like '0:112:3' '410:650:4' -> frames range(a,b,step)"""
    from PIL import Image, ImageDraw
    frames = []
    for s in specs:
        a, b, st = (int(x) for x in s.split(':')); frames += list(range(a, b, st))
    h = int(w * H / W); rows = (len(frames) + cols - 1) // cols
    im = Image.new('RGB', (cols * (w + 3), rows * (h + 15)), 'white'); dr = ImageDraw.Draw(im)
    for k, i in enumerate(frames):
        x = (k % cols) * (w + 3); y = (k // cols) * (h + 15)
        im.paste(Image.open(frame_path(d, i)).resize((w, h)), (x, y + 14)); dr.text((x + 3, y + 1), str(i), fill='black')
    os.makedirs(f'{d}/strips', exist_ok=True)
    out = f'{d}/strips/{name}.jpg'; im.save(out, quality=82); print(out)


def blendfit(d, a, b):
    """alpha per frame for F_i ~ alpha*F_a + (1-alpha)*F_b (1 = pure outgoing, 0 = pure incoming)."""
    sm = np.load(f'{d}/small.npz')['small'].astype(np.float32)
    A = sm[a].ravel(); B = sm[b].ravel(); dAB = A - B
    print(' '.join(f'{i}:{np.dot(sm[i].ravel() - B, dAB) / np.dot(dAB, dAB):.2f}' for i in range(a, b + 1)))


# ------------------------------------------------------------------ captions
def _textmask(bgr, y0, y1):
    band = bgr[y0:y1].astype(np.int16)
    mn = band.min(2); mx = band.max(2)
    white = ((mn >= 200) & (mx - mn <= 40)).astype(np.uint8)
    near = cv2.dilate((mx <= 70).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    return (white.astype(bool) & near).astype(np.uint8)


def capband(d):
    """Find the caption line: glyph-sized white-with-black-outline components, every 5th frame, whole frame."""
    N = nframes(d); hist = np.zeros(H); heights = []
    for i in range(0, N, 5):
        bgr = cv2.imread(frame_path(d, i))
        txt = _textmask(bgr, 0, H)
        n, lbl, st, cen = cv2.connectedComponentsWithStats(txt, 8)
        for k in range(1, n):
            x, y, w, h, a = st[k]
            if 10 <= h <= 90 and w <= 160 and a >= 30:
                hist[int(cen[k][1])] += a; heights.append((cen[k][1], h))
    sm = np.convolve(hist, np.ones(31), 'same')
    yc = int(np.argmax(sm))
    hh = np.array([h for c, h in heights if abs(c - yc) <= 25])
    capH = float(np.percentile(hh, 80)) if len(hh) else 36.0
    share = sm[yc] / sm.sum()
    out = dict(y_centre=yc, cap_height_est=capH, share_of_glyph_area_on_this_line=float(share))
    json.dump(out, open(f'{d}/caption_band.json', 'w')); print(out)
    # second peak report
    sm2 = sm.copy(); sm2[max(0, yc - 120): yc + 120] = 0
    print('next strongest glyph row', int(np.argmax(sm2)), 'relative strength', round(float(sm2.max() / sm[yc]), 3))


def _glyphs(bgr, band):
    yc, ch = band['y_centre'], band['cap_height_est']
    y0, y1 = int(yc - 1.6 * ch), int(yc + 1.6 * ch)
    txt = _textmask(bgr, y0, y1)
    n, lbl, st, cen = cv2.connectedComponentsWithStats(txt, 8)
    comps, keep = [], np.zeros_like(txt)
    for k in range(1, n):
        x, y, w, h, a = st[k]
        top, bot = y + y0, y + h - 1 + y0
        if 0.22 * ch <= h <= 1.45 * ch and w <= 2.6 * ch and a >= 30 and top >= yc - 0.8 * ch and bot <= yc + 1.2 * ch:
            comps.append((x, x + w - 1, top, bot)); keep[lbl == k] = 1
    return comps, keep, y0


def captions(d):
    band = json.load(open(f'{d}/caption_band.json'))
    cap = cv2.VideoCapture(f'{d}/video.mp4'); masks, KEEP = [], []
    while True:
        ok, bgr = cap.read()
        if not ok: break
        comps, keep, y0 = _glyphs(bgr, band)
        KEEP.append(keep); masks.append(cv2.resize(keep, (180, 22), interpolation=cv2.INTER_AREA) > 0)
    N = len(masks)
    iou = [np.nan] + [((masks[i - 1] & masks[i]).sum() / max(1, (masks[i - 1] | masks[i]).sum())) for i in range(1, N)]
    seg, segs = 0, []
    for i in range(N):
        if i > 0 and iou[i] < 0.5: seg += 1
        segs.append(seg)
    try:
        import pytesseract
    except ImportError:          # OCR is optional: the reviewer types the text into caption_cards.csv
        pytesseract = None
    cfg = "--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?-"
    def ocr(k):
        if pytesseract is None: return ''
        img = ((1 - k) * 255).astype(np.uint8)
        img = cv2.copyMakeBorder(img, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=255)
        img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
        return pytesseract.image_to_string(img, config=cfg).strip()
    df = pd.DataFrame(dict(frame=range(N), iou_prev=iou, seg=segs, glyph_px=[int(k.sum()) for k in KEEP]))
    rows = []
    for s, g in df.groupby('seg'):
        fr = g.frame.values
        picks = fr[np.linspace(0, len(fr) - 1, min(5, len(fr))).astype(int)]
        votes = collections.Counter(ocr(KEEP[i]) for i in picks)
        rows.append(dict(seg=s, start=int(fr.min()), end=int(fr.max()), frames=len(fr), text=votes.most_common(1)[0][0],
                         min_glyph_px=int(g.glyph_px.min())))
    df.to_csv(f'{d}/captions.csv', index=False)
    out = pd.DataFrame(rows); out.to_csv(f'{d}/caption_cards_auto.csv', index=False)
    pd.set_option('display.width', 200); print(out.to_string())
    print('frames with almost no glyph pixels (possible no-caption frames):', df[df.glyph_px < 100].frame.tolist()[:200])


def capbox(d):
    """After the agent writes caption_cards.csv (start,end,text): per-card median box + occupancy map + words."""
    band = json.load(open(f'{d}/caption_band.json'))
    cards = pd.read_csv(f'{d}/caption_cards.csv')
    cap = cv2.VideoCapture(f'{d}/video.mp4'); rows = []; occ = np.zeros((H, W), np.float32); i = 0
    while True:
        ok, bgr = cap.read()
        if not ok: break
        comps, keep, y0 = _glyphs(bgr, band)
        box = (np.nan,) * 4
        if comps:
            comps.sort(); c = np.array([(a + b) / 2 for a, b, _, _ in comps]); s = int(np.argmin(abs(c - W / 2)))
            if abs(c[s] - W / 2) < 200:
                Lh = R = s; gap = 0.85 * band['cap_height_est']
                while Lh > 0 and comps[Lh - 1][1] >= comps[Lh][0] - gap: Lh -= 1
                while R < len(comps) - 1 and comps[R + 1][0] <= max(cc[1] for cc in comps[Lh:R + 1]) + gap: R += 1
                g = comps[Lh:R + 1]
                box = (min(x[0] for x in g), min(x[2] for x in g), max(x[1] for x in g), max(x[3] for x in g))
                for (a, b, t, bt) in g:
                    occ[t:bt + 1, a:b + 1] += keep[t - y0:bt + 1 - y0, a:b + 1]
        rows.append((i, *box)); i += 1
    N = i
    pf = pd.DataFrame(rows, columns=['frame', 'x0', 'y0', 'x1', 'y1'])
    has = np.zeros(N, bool)
    for n, r in cards.iterrows():
        has[int(r.start):int(r.end) + 1] = True
    for c in ['x0', 'y0', 'x1', 'y1']:
        cards[c] = [pf.iloc[int(r.start):int(r.end) + 1][c].median() for _, r in cards.iterrows()]
    cards['frames'] = cards.end - cards.start + 1
    cards['words'] = cards.text.astype(str).str.split().str.len()
    cards['cx'] = (cards.x0 + cards.x1) / 2
    cards.to_csv(f'{d}/caption_cards.csv', index=False)
    np.save(f'{d}/caption_occupancy.npy', occ / N)
    print(cards[['start', 'end', 'text', 'x0', 'y0', 'x1', 'y1', 'cx']].describe().round(1))
    print('frames with no caption card:', int((~has).sum()))
    print('cards off-centre > 8 px:'); print(cards[abs(cards.cx - W / 2) > 8][['start', 'end', 'text', 'x0', 'x1', 'cx']])


def capstyle(d, frames):
    band = json.load(open(f'{d}/caption_band.json'))
    for fr in frames:
        bgr = cv2.imread(frame_path(d, fr))
        comps, keep, y0 = _glyphs(bgr, band)
        y1 = int(band['y_centre'] + 1.6 * band['cap_height_est'])
        sub = bgr[y0:y1].astype(np.int16)
        fill = cv2.morphologyEx(keep, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        fillcol = sub[fill > 0].mean(0)[::-1] if fill.sum() else None
        dark = sub.max(2) <= 60
        prev = fill.copy(); out = []
        for k in range(1, 13):
            dd = cv2.dilate(fill, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * k + 1, 2 * k + 1)))
            ring = (dd > 0) & ~(prev > 0); prev = dd
            out.append(f'{k}:{dark[ring].mean():.2f}/{sub[ring].max(1).mean():.0f}')
        print(fr, 'fill RGB', None if fillcol is None else fillcol.round(0), '| ring px: dark-fraction/brightness', ' '.join(out))


# ------------------------------------------------------------------ assemble
def circ_mean(deg, wts):
    r = np.radians(deg); return float((np.degrees(np.arctan2((wts * np.sin(r)).sum(), (wts * np.cos(r)).sum())) + 360) % 360)


def hue_name(h):
    for lim, n in [(15, 'red'), (45, 'orange'), (70, 'yellow'), (160, 'green'), (200, 'cyan'), (255, 'blue'), (290, 'violet'), (340, 'magenta'), (361, 'red')]:
        if h < lim: return n


def tc(f):
    s = f / FPS; return f"{int(s // 60)}:{s % 60:05.2f}"


def assemble(d):
    an = json.load(open(f'{d}/annotations.json'))
    pf = pd.read_csv(f'{d}/per_frame.csv'); N = len(pf)
    shots = an['shots']; starts = [s[0] for s in shots] + [N]
    LOC = {int(k): v for k, v in an['LOC'].items()}
    size = np.empty(N, object); loc = np.zeros(N, int); sid = np.zeros(N, int)
    for a, b, s in an['size_spans']: size[a:b + 1] = s
    for a, b, l in an['loc_spans']: loc[a:b + 1] = l
    for k in range(len(shots)): sid[starts[k]:starts[k + 1]] = k + 1
    assert all(x is not None for x in size), 'size_spans must cover every frame'
    assert (loc > 0).all(), 'loc_spans must cover every frame'
    assert all(shots[k][0] < shots[k + 1][0] for k in range(len(shots) - 1)) and shots[0][0] == 0
    pf['shot'] = sid; pf['shot_size'] = size; pf['location'] = loc
    chg = np.r_[False, size[1:] != size[:-1]]; pf['size_change'] = chg
    cs = pd.read_csv(f'{d}/caption_cards.csv')
    smp = np.load(f'{d}/colour_samples.npz')['samples']
    def palette(frames, k=4):
        px = smp[frames].reshape(-1, 3).astype(np.float32)
        if len(px) > 60000: px = px[np.random.default_rng(1).choice(len(px), 60000, replace=False)]
        _, lab, cen = cv2.kmeans(px, k, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5), 3, cv2.KMEANS_PP_CENTERS)
        share = np.bincount(lab.ravel(), minlength=k) / len(lab); o = np.argsort(-share)
        return [('#%02X%02X%02X' % tuple(int(c) for c in cen[j]), float(share[j])) for j in o]
    shot_rows = []
    for k, (st, kind, span) in enumerate(shots):
        a, b = st, starts[k + 1] - 1; g = pf.iloc[a:b + 1]
        seq, locs = [], []
        for s in g.shot_size:
            if not seq or seq[-1] != s: seq.append(s)
        for l in g.location:
            if not locs or locs[-1] != l: locs.append(int(l))
        shot_rows.append(dict(
            shot=k + 1, start=a, end=b, frames=b - a + 1, tc_in=tc(a), tc_out=tc(b + 1), secs=(b - a + 1) / FPS,
            transition_in=kind, transition_frames=(span[1] - span[0] + 1) if span else (None if kind == 'Start' else 0),
            transition_span=f"{span[0]}–{span[1]}" if span else '',
            sizes=' → '.join(seq), size_changes_inside=int(g.size_change.iloc[1:].sum()), size_change_at_cut=bool(chg[a]) if a > 0 else False,
            locations=' → '.join(str(x) for x in locs), location_names=' → '.join(LOC[x] for x in locs),
            luma_mean=g.luma_mean.mean() / 2.55, luma_min=g.luma_mean.min() / 2.55, luma_max=g.luma_mean.max() / 2.55,
            contrast_sd=g.luma_std.mean() / 2.55, p5=g.luma_p5.mean() / 2.55, p95=g.luma_p95.mean() / 2.55,
            pct_black=g.pct_black.mean(), pct_white=g.pct_white.mean(), sat=g.sat_mean.mean(), colourfulness=g.colourfulness.mean(),
            hue=circ_mean(g.hue_deg.values, g.hue_strength.values), L=g.L.mean(), a=g.a.mean(), b=g.b.mean(),
            avg_rgb='#%02X%02X%02X' % (int(g.R.mean()), int(g.G.mean()), int(g.B.mean())), palette=palette(np.arange(a, b + 1)),
            captions=int(((cs.start >= a) & (cs.start <= b)).sum())))
    for r in shot_rows: r['hue_name'] = hue_name(r['hue'])
    seg_len, run = [], 1
    for i in range(1, N):
        if size[i] == size[i - 1]: run += 1
        else: seg_len.append(run); run = 1
    seg_len.append(run)
    total = int(chg.sum()); at_cut = int(sum(chg[s] for s in starts[1:-1]))
    has_cap = np.zeros(N, bool)
    for _, r in cs.iterrows(): has_cap[int(r.start):int(r.end) + 1] = True
    good = cs[(abs(cs.cx - W / 2) <= 8)]
    capH_top = good.y0.median()
    cg = dict(cards=int(len(cs)), words=int(cs.words.sum()),
              one_word_cards=int((cs.words == 1).sum()), two_word_cards=int((cs.words == 2).sum()), three_word_cards=int((cs.words >= 3).sum()),
              mean_card_frames=float(cs.frames.mean()), median_card_frames=float(cs.frames.median()),
              min_card_frames=int(cs.frames.min()), max_card_frames=int(cs.frames.max()),
              cap_top_px=float(good.y0.quantile(0.25)), baseline_px=float(good.y1.quantile(0.25)), descender_px=float(good.y1.quantile(0.9)),
              xheight_top_px=float(good.y0.quantile(0.95)),
              centre_x_px=float(good.cx.median()), cards_within_3px_of_centre=int((abs(cs.cx - W / 2) <= 3).sum()),
              min_w_px=float((good.x1 - good.x0).min()), max_w_px=float((good.x1 - good.x0).max()), med_w_px=float((good.x1 - good.x0).median()),
              frames_with_caption=int(has_cap.sum()), style=an.get('caption_style', ''))
    cg['cap_height_px'] = cg['baseline_px'] - cg['cap_top_px']; cg['xheight_px'] = cg['baseline_px'] - cg['xheight_top_px']
    cg['line_centre_y_px'] = (cg['cap_top_px'] + cg['baseline_px']) / 2
    S = dict(title=an['title'], key=an.get('key', os.path.basename(d)), frames=N, duration=N / FPS, width=W, height=H, fps=FPS,
             shots=len(shots), transitions=len(shots) - 1,
             dissolves=sum(1 for s in shots if s[1].startswith('Dissolve')), hard_cuts=sum(1 for s in shots if s[1] == 'Hard cut'),
             hidden_cuts=sum(1 for s in shots if s[1].startswith('Hidden cut')),
             other_transitions=[s[1] for s in shots[1:] if not (s[1].startswith('Dissolve') or s[1] == 'Hard cut' or s[1].startswith('Hidden cut'))],
             dissolve_frames=[s[2][1] - s[2][0] + 1 for s in shots if s[1].startswith('Dissolve') and s[2]],
             asl=N / FPS / len(shots), shot_len_median=float(np.median([r['secs'] for r in shot_rows])),
             shot_len_min=min(r['secs'] for r in shot_rows), shot_len_max=max(r['secs'] for r in shot_rows),
             size_changes=total, size_changes_at_cuts=at_cut, size_changes_inside=total - at_cut,
             size_segments=len(seg_len), size_hold_mean=float(N / FPS / (total + 1)), size_hold_median=float(np.median(seg_len) / FPS),
             size_changes_per_sec=total / (N / FPS),
             size_secs={k: float(v / FPS) for k, v in pd.Series(size).value_counts().items()},
             locations=len(set(loc)), location_changes=int((loc[1:] != loc[:-1]).sum()), location_names=LOC,
             location_secs={int(k): float(v / FPS) for k, v in pd.Series(loc).value_counts().items()},
             luma_mean=pf.luma_mean.mean() / 2.55, luma_sd_across_frames=pf.luma_mean.std() / 2.55,
             luma_min_frame=int(pf.luma_mean.idxmin()), luma_min=pf.luma_mean.min() / 2.55,
             luma_max_frame=int(pf.luma_mean.idxmax()), luma_max=pf.luma_mean.max() / 2.55,
             contrast_sd=pf.luma_std.mean() / 2.55, p5=pf.luma_p5.mean() / 2.55, p95=pf.luma_p95.mean() / 2.55,
             pct_black=pf.pct_black.mean(), pct_white=pf.pct_white.mean(),
             luma_top=pf.luma_top.mean() / 2.55, luma_mid=pf.luma_mid.mean() / 2.55, luma_bot=pf.luma_bot.mean() / 2.55,
             sat=pf.sat_mean.mean(), sat_min=pf.sat_mean.min(), sat_max=pf.sat_mean.max(), colourfulness=pf.colourfulness.mean(),
             hue=circ_mean(pf.hue_deg.values, pf.hue_strength.values), L=pf.L.mean(), a=pf.a.mean(), b=pf.b.mean(),
             warm_frames_pct=float((pf.b > 0).mean() * 100),
             avg_rgb='#%02X%02X%02X' % (int(pf.R.mean()), int(pf.G.mean()), int(pf.B.mean())), palette=palette(np.arange(N), 6),
             captions=cg, notes=an.get('notes', ''))
    S['hue_name'] = hue_name(S['hue'])
    pf.to_csv(f'{d}/per_frame_full.csv', index=False)
    json.dump(dict(summary=S, shots=shot_rows, size_spans=an['size_spans'], loc_spans=an['loc_spans'], LOC=LOC),
              open(f'{d}/analysis.json', 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
    pd.set_option('display.width', 250)
    print(json.dumps({k: v for k, v in S.items() if k not in ('location_names', 'palette')}, indent=1, default=str))
    print(pd.DataFrame(shot_rows).drop(columns=['palette', 'location_names']).round(2).to_string())


if __name__ == '__main__':
    step, d = sys.argv[1], sys.argv[2].rstrip('/')
    rest = sys.argv[3:]
    if step == 'prep': prep(d, rest[0] if rest else None)
    elif step == 'measure': measure(d)
    elif step == 'small': small(d)
    elif step == 'sheets': sheets(d)
    elif step == 'capband': capband(d)
    elif step == 'captions': captions(d)
    elif step == 'capbox': capbox(d)
    elif step == 'capstyle': capstyle(d, [int(x) for x in rest])
    elif step == 'assemble': assemble(d)
    elif step == 'strip': strip(d, int(rest[0]), int(rest[1]), rest[2] if len(rest) > 2 else None)
    elif step == 'grid': grid(d, rest[0], rest[1:])
    elif step == 'blendfit': blendfit(d, int(rest[0]), int(rest[1]))
    elif step == 'contact':
        sys.argv = [sys.argv[0], d]; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'contact_sheet.py')).read())
    else: raise SystemExit('unknown step')
