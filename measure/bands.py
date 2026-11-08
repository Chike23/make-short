"""Brightness/saturation bands per mood in ffmpeg signalstats units (the units v3/gate.py uses).
Samples every 10th frame as a 1080x1920 RGB PNG (as a Blender render would be), runs signalstats on it,
and groups the samples by the mood written per shot in annotations.json: "moods": {"1": "day", "2": "night", ...}.
usage: python3 bands.py refdir1 [refdir2 ...]   -> prints p10/median/p90 of YAVG and SATAVG per mood, writes bands.json"""
import sys, os, re, json, subprocess, numpy as np, pandas as pd
rows = []
for d in [x.rstrip('/') for x in sys.argv[1:]]:
    an = json.load(open(f'{d}/annotations.json')); moods = an.get('moods', {})
    starts = [s[0] for s in an['shots']]
    os.makedirs(f'{d}/png10', exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{d}/video.mp4', '-vf',
                    "select=not(mod(n\\,10)),scale=1080:1920:in_color_matrix=bt709:in_range=tv:out_range=pc:flags=bicubic,format=rgb24",
                    '-vsync', '0', '-start_number', '0', f'{d}/png10/p_%04d.png'], check=True)
    txt = subprocess.run(['ffmpeg', '-v', 'error', '-i', f'{d}/png10/p_%04d.png', '-vf', 'signalstats,metadata=print:file=-', '-f', 'null', '-'],
                         capture_output=True, text=True).stdout
    cur = {}; i = 0
    for line in txt.splitlines() + ['frame:end']:
        if line.startswith('frame:'):
            if cur:
                f = i * 10; shot = sum(1 for s in starts if s <= f)
                rows.append(dict(ref=d, frame=f, shot=shot, mood=moods.get(str(shot), 'unlabelled'), **cur)); i += 1
            cur = {}
        m = re.match(r'lavfi\.signalstats\.(\w+)=([\d.]+)', line)
        if m and m.group(1) in ('YAVG', 'YLOW', 'YHIGH', 'SATAVG'): cur[m.group(1)] = float(m.group(2))
D = pd.DataFrame(rows); out = {}
for mood, g in D.groupby('mood'):
    out[mood] = dict(n=len(g), YAVG=[round(float(g.YAVG.quantile(q)), 1) for q in (.1, .5, .9)],
                     SATAVG=[round(float(g.SATAVG.quantile(q)), 1) for q in (.1, .5, .9)],
                     spread=round(float((g.YHIGH - g.YLOW).median()), 1), blown_pct=round(float((g.YHIGH > 232).mean() * 100), 1))
    print(mood, out[mood])
json.dump(out, open('bands.json', 'w'), indent=1)
