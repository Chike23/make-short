"""assemble.py: the shot clips -> one silent 1080x1920 30 fps video, joined with 8-frame crossfades.

Each clip covers Blender frames f0..f1+8 (shotkit renders 8 handle frames past the shot's end), so the dissolve into
the next shot is the next shot's first 8 frames over this one's last 8. Global frame n sits at t = (n - 1) / 30, so
the voice lines up with no offset.
    python3 tools/assemble.py [render|preview|render_graded] [out/short-silent.mp4]
"""
import glob, os, re, subprocess, sys

P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS, XF = 30, 8
d = sys.argv[1] if len(sys.argv) > 1 else 'render'
d = d if os.path.isabs(d) else os.path.join(P, d)
dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(P, 'out', 'preview-silent.mp4' if 'preview' in d else 'short-silent.mp4')
clips = sorted(glob.glob(os.path.join(d, 'S[0-9][0-9]_[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9].mp4')),
               key=lambda p: int(re.search(r'_(\d{4})-\d{4}', p).group(1)))
starts = [int(re.search(r'_(\d{4})-(\d{4})', p).group(1)) for p in clips]
ends = [int(re.search(r'_(\d{4})-(\d{4})', p).group(2)) for p in clips]
assert clips and starts[0] == 1, 'the first clip must start at frame 1'
args, fc = [], []
for i, p in enumerate(clips):
    args += ['-i', p]
    fc.append(f'[{i}:v]fps={FPS},settb=AVTB,setpts=PTS-STARTPTS,format=yuv420p[c{i}]')
prev = 'c0'
for i in range(1, len(clips)):
    off = (starts[i] - 1) / FPS
    assert ends[i - 1] >= starts[i] + XF - 1, f'{os.path.basename(clips[i - 1])} has no {XF}-frame handle'
    fc.append(f'[{prev}][c{i}]xfade=transition=fade:duration={XF / FPS:.4f}:offset={off:.4f}[x{i}]'); prev = f'x{i}'
fc.append(f'[{prev}]scale=1080:1920:flags=lanczos,setsar=1[v]')
os.makedirs(os.path.dirname(dst), exist_ok=True)
subprocess.run(['ffmpeg', '-y', '-v', 'error', *args, '-filter_complex', ';'.join(fc), '-map', '[v]', '-c:v', 'libx264',
                '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', str(FPS), dst], check=True)
n = int(subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries',
                        'stream=nb_read_frames', '-of', 'csv=p=0', dst], capture_output=True, text=True).stdout.strip())
print(f'wrote {dst}: {n} frames ({n / FPS:.2f} s), {len(clips)} shots, dissolves at frames {starts[1:]}')
