"""grade_fix.py: a per-shot post-grade of the rendered clips, without re-rendering (render/ -> render_graded/).

    python3 tools/grade_fix.py [render] [render_graded]
grade_fix.json maps a shot to an ffmpeg filter, for example
    {"S08": "curves=all='0/0 0.5/0.41 1/0.88'", "S10": "hue=s=0.78", "S06": "colorchannelmixer=rr=0.9:gg=0.9:bb=0.9,hue=s=1.4"}
tools/color_check.py writes suggestions to grade_fix.suggested.json. Shots not listed are copied as they are.
Prints signalstats YAVG / SATAVG before -> after. Afterwards: make_shots.py and assemble.py on render_graded.
Then carry each change into the set's mood (kit/sets_lib.py) so the next film needs no post-grade."""
import json, os, re, shutil, subprocess, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(P, sys.argv[1] if len(sys.argv) > 1 else 'render')
dst = os.path.join(P, sys.argv[2] if len(sys.argv) > 2 else 'render_graded'); os.makedirs(dst, exist_ok=True)
G = {k: v for k, v in json.load(open(os.path.join(P, 'grade_fix.json'))).items() if not k.startswith('_')}


def stats(fn):
    o = subprocess.run(['ffmpeg', '-v', 'error', '-i', fn, '-vf', "select='not(mod(n\\,6))',scale=1080:1920,format=rgb24,format=yuv444p,signalstats,metadata=print:file=-",
                        '-vsync', '0', '-f', 'null', '-'], capture_output=True, text=True).stdout
    y = [float(v) for v in re.findall(r'YAVG=([\d.]+)', o)]; s = [float(v) for v in re.findall(r'SATAVG=([\d.]+)', o)]
    return sum(y) / len(y), sum(s) / len(s)


for f in sorted(os.listdir(src)):
    a, b = os.path.join(src, f), os.path.join(dst, f)
    if f.endswith('.json'): shutil.copy(a, b); continue
    if not re.match(r'S\d\d_\d{4}-\d{4}\.mp4$', f): continue
    sid = f[:3]
    if sid in G:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', a, '-vf', G[sid], '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', '-pix_fmt', 'yuv420p', b], check=True)
        (y0, s0), (y1, s1) = stats(a), stats(b)
        print(f'{sid}: YAVG {y0:.0f} -> {y1:.0f}   SATAVG {s0:.1f} -> {s1:.1f}   [{G[sid]}]')
    else:
        shutil.copy(a, b)
os.makedirs(os.path.join(dst, 'pre_dissolve'), exist_ok=True)
