"""look_measure.py: measure the LOOK of two example videos, for a style change (references/style-change.md).

    python3 tools/look_measure.py <style-name> <video1> <video2>      -> SKILL-or-P/styles/<style-name>/
Writes:
  frames/v1_000.png ...   one frame every 0.5 s from each video (720 wide), for the style analyst to look at
  sheet_v1.png, sheet_v2.png   contact sheets (8 columns)
  look.json   brightness and colour (mean luma, HSV saturation, Lab a*/b*, signalstats YAVG/SATAVG p10/median/p90),
              an 8-colour palette with shares, line weight (edge density), flatness (share of flat-colour pixels)
Only the look is measured. The camera, the edit, the shot sizes, the captions and the pacing stay on the house spec
(references/spec.md) whatever the style.
Needs: ffmpeg, python packages numpy + opencv-python + pillow.
"""
import glob, json, os, subprocess, sys
import numpy as np
import cv2

if len(sys.argv) < 4: sys.exit(__doc__)
name, vids = sys.argv[1], sys.argv[2:4]
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(P, 'styles', name); fr = os.path.join(out, 'frames'); os.makedirs(fr, exist_ok=True)


def frames(v, tag):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', v, '-vf', 'fps=2,scale=720:-2', os.path.join(fr, f'{tag}_%03d.png')], check=True)
    return sorted(glob.glob(os.path.join(fr, f'{tag}_*.png')))


def signalstats(v):
    o = subprocess.run(['ffmpeg', '-v', 'error', '-i', v, '-vf', 'fps=2,scale=1080:1920,format=rgb24,format=yuv444p,signalstats,metadata=print:file=-',
                        '-f', 'null', '-'], capture_output=True, text=True).stdout
    import re
    y = np.array([float(x) for x in re.findall(r'YAVG=([\d.]+)', o)]); s = np.array([float(x) for x in re.findall(r'SATAVG=([\d.]+)', o)])
    q = lambda a: [round(float(np.percentile(a, p)), 1) for p in (10, 50, 90)] if len(a) else []
    return {'YAVG_p10_med_p90': q(y), 'SATAVG_p10_med_p90': q(s)}


def sheet(fs, path, cols=8, w=180):
    from PIL import Image
    ims = [Image.open(f).convert('RGB') for f in fs]
    h = int(w * ims[0].height / ims[0].width); rows = (len(ims) + cols - 1) // cols
    s = Image.new('RGB', (cols * w, rows * h))
    for i, im in enumerate(ims): s.paste(im.resize((w, h)), ((i % cols) * w, (i // cols) * h))
    s.save(path)


res = {'videos': {}, 'note': 'look only; camera, edit, sizes, captions and pacing stay on references/spec.md'}
allpix = []
for i, v in enumerate(vids, 1):
    fs = frames(v, f'v{i}'); sheet(fs, os.path.join(out, f'sheet_v{i}.png'))
    luma, sat, A, B, edge, flat = [], [], [], [], [], []
    for f in fs:
        im = cv2.imread(f); rgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB).astype(np.float32) / 255
        luma.append(float((0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]).mean()))
        hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV); sat.append(float(hsv[..., 1].mean() / 255))
        lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(np.float32); A.append(float(lab[..., 1].mean() - 128)); B.append(float(lab[..., 2].mean() - 128))
        g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY); edge.append(float((cv2.Canny(g, 60, 160) > 0).mean()))
        var = cv2.blur((g.astype(np.float32) - cv2.blur(g.astype(np.float32), (7, 7))) ** 2, (7, 7)); flat.append(float((var < 4).mean()))
        allpix.append(cv2.resize(rgb, (90, 160)).reshape(-1, 3))
    res['videos'][os.path.basename(v)] = {
        'frames': len(fs), 'mean_luma_pct': round(100 * np.mean(luma), 1), 'hsv_sat_pct': round(100 * np.mean(sat), 1),
        'lab_a': round(np.mean(A), 1), 'lab_b': round(np.mean(B), 1), 'edge_pct': round(100 * np.mean(edge), 2),
        'flat_pct': round(100 * np.mean(flat), 1), **signalstats(v)}
px = np.concatenate(allpix).astype(np.float32)
crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5)
_, lab_, cen = cv2.kmeans(px, 8, None, crit, 3, cv2.KMEANS_PP_CENTERS)
cnt = np.bincount(lab_.ravel(), minlength=8) / len(lab_)
res['palette'] = [{'hex': '#%02x%02x%02x' % tuple(int(round(c * 255)) for c in cen[i]), 'share_pct': round(100 * float(cnt[i]), 1)}
                  for i in np.argsort(-cnt)]
json.dump(res, open(os.path.join(out, 'look.json'), 'w'), indent=1)
print(json.dumps(res, indent=1))
print(f'-> {out}/look.json, sheet_v1.png, sheet_v2.png, frames/')
