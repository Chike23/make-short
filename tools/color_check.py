"""color_check.py: each shot's brightness and colour against its mood band, with a ready post-grade fix.

    python3 tools/color_check.py [preview|render]        -> a table, and grade_fix.suggested.json
Measures ffmpeg signalstats (YAVG = brightness, SATAVG = saturation) on every 6th frame of each clip at 1080x1920,
exactly as the reference was measured (references/reference-style.md section 5). For a shot outside its band it
suggests the smallest correction that lands it inside: an exposure curve and/or a saturation change. Copy the lines
you agree with into grade_fix.json and run tools/grade_fix.py (no re-render). Then move the same change into the
set's mood in kit/sets_lib.py (look.MOODS) so the next film starts right.
Bands come from critic/targets.json "bands" when a new style set them, otherwise from the reference.
"""
import glob, json, os, re, subprocess, sys

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BAND = {'day': (99, 116, 146, 22, 32, 44), 'dusk': (114, 125, 153, 18, 30, 35),
        'interior': (67, 88, 139, 19, 25, 35), 'night': (69, 85, 118, 29, 49, 61)}     # p10, median, p90 (Y, then SAT)
tp = os.path.join(P, 'critic', 'targets.json')
if os.path.exists(tp): BAND.update({k: tuple(v) for k, v in json.load(open(tp)).get('bands', {}).items()})
d = sys.argv[1] if len(sys.argv) > 1 else 'preview'
d = d if os.path.isabs(d) else os.path.join(P, d)
film = {s['id']: s for s in json.load(open(os.path.join(P, 'plan', 'film.json')))['shots']}


def stats(fn):
    o = subprocess.run(['ffmpeg', '-v', 'error', '-i', fn, '-vf', "select='not(mod(n\\,6))',scale=1080:1920,format=rgb24,"
                        "format=yuv444p,signalstats,metadata=print:file=-", '-vsync', '0', '-f', 'null', '-'],
                       capture_output=True, text=True).stdout
    y = [float(v) for v in re.findall(r'YAVG=([\d.]+)', o)]; s = [float(v) for v in re.findall(r'SATAVG=([\d.]+)', o)]
    return (sum(y) / len(y), sum(s) / len(s)) if y else (None, None)


fix = {'_why': 'suggested by color_check.py: shots outside their mood band. Review, then copy into grade_fix.json.'}
print(f"{'shot':5} {'mood':9} {'YAVG':>6} {'band':>11} {'SATAVG':>7} {'band':>9}  result")
for clip in sorted(glob.glob(os.path.join(d, 'S[0-9][0-9]_*.mp4'))):
    sid = os.path.basename(clip)[:3]; mood = film.get(sid, {}).get('mood', 'interior')
    ylo, ymed, yhi, slo, smed, shi = BAND.get(mood, BAND['interior'])
    y, s = stats(clip)
    if y is None: continue
    why, f = [], []
    if not ylo <= y <= yhi:
        tgt = yhi - 8 if y > yhi else ylo + 8
        mid = max(0.25, min(0.75, 0.5 * tgt / y))                 # curve the mid-tones: keeps blacks and whites
        f.append(f"curves=all='0/0 0.5/{mid:.2f} 1/{min(1.0, 0.5 + mid):.2f}'"); why.append('Y')
    if not slo <= s <= shi:
        tgt = shi - 2 if s > shi else slo + 3
        f.append(f'hue=s={tgt / s:.2f}'); why.append('SAT')
    if f: fix[sid] = ','.join(f)
    print(f"{sid:5} {mood:9} {y:6.0f} {ylo:4.0f}-{yhi:<5.0f} {s:7.1f} {slo:3.0f}-{shi:<4.0f}  {'PASS' if not why else 'FIX ' + ' '.join(why)}")
json.dump(fix, open(os.path.join(P, 'grade_fix.suggested.json'), 'w'), indent=1)
print(f'\n{len(fix) - 1} shots to fix -> grade_fix.suggested.json')
