"""grade_fix.py: per-shot post-grade of the rendered clips (render/ -> render_graded/), from grade_fix.json.
Shots not listed are copied as they are. Prints signalstats YAVG / SATAVG before -> after (1080x1920, every 6th frame)."""
import json, os, re, shutil, subprocess, sys
src, dst = 'render', 'render_graded'; os.makedirs(dst, exist_ok=True)
G = {k: v for k, v in json.load(open('grade_fix.json')).items() if not k.startswith('_')}
def stats(fn):
    o = subprocess.run(['ffmpeg', '-v', 'error', '-i', fn, '-vf', "select='not(mod(n\\,6))',scale=1080:1920,format=rgb24,format=yuv444p,signalstats,metadata=print:file=-",
                        '-vsync', '0', '-f', 'null', '-'], capture_output=True, text=True).stdout
    y = [float(v) for v in re.findall(r'YAVG=([\d.]+)', o)]; s = [float(v) for v in re.findall(r'SATAVG=([\d.]+)', o)]
    return sum(y) / len(y), sum(s) / len(s)
for f in sorted(os.listdir(src)):
    if not f.endswith('.mp4'): continue
    sid, a, b = f[:3], os.path.join(src, f), os.path.join(dst, f)
    if sid in G:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', a, '-vf', G[sid], '-c:v', 'libx264', '-crf', '14', '-preset', 'medium', '-pix_fmt', 'yuv420p', b], check=True)
        (y0, s0), (y1, s1) = stats(a), stats(b)
        print(f'{sid}: YAVG {y0:.0f} -> {y1:.0f}   SATAVG {s0:.1f} -> {s1:.1f}   [{G[sid]}]')
    else:
        shutil.copy(a, b)
for f in os.listdir(src):
    if f.endswith('.json'): shutil.copy(os.path.join(src, f), os.path.join(dst, f))
