"""mouth-cues.py: talking-mouth keys for the Blender lead, from the voice (no extra tools).
  python3 -I voice/mouth-cues.py  [voice.mp3] [voice-timing.json] [out.json]   (in P)
How open the mouth is follows the voice's loudness frame by frame (30 fps); how wide or round it is follows the vowels of
the word being spoken (ee/i = wide, o/oo/u/w = round); m/b/p at a word start close it briefly.
Also writes natural blink frames (every 2.5-4.5 s, never mid-word for long). Output: {"fps", "cues": [[frame, open, wide]], "blinks": [...]}"""
import json, os, re, subprocess, sys, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
mp3 = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'voice.mp3')
tim = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'voice-timing.json')
out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, 'mouth_cues.json')
FPS, SR = 30, 16000
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', mp3, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
a = np.frombuffer(raw, np.float32)
hop = SR // FPS; n = len(a) // hop
rms = np.array([np.sqrt(np.mean(a[i * hop:(i + 1) * hop] ** 2)) for i in range(n)])
ref = np.percentile(rms[rms > 1e-4], 95) if (rms > 1e-4).any() else 1.0
env = np.clip(rms / ref, 0, 1) ** 0.7
env = np.convolve(env, [0.25, 0.5, 0.25], 'same')                      # soften frame-to-frame chatter
T = json.load(open(tim, encoding='utf-8-sig'))
words = [w for l in T['lines'] for w in l['words']]
def shape(word):
    w = re.sub(r'[^a-z]', '', word.lower())
    wide = 0.7 if re.search(r'ee|ea|i|y$', w) else 0.4
    if re.search(r'oo|o|u|w', w) and not re.search(r'ee|ea', w): wide = 0.15
    return wide
cues = []
for f in range(0, n, 2):
    t = f / FPS
    cur = next((w for w in words if w['start'] - 0.03 <= t <= w['end'] + 0.03), None)
    op = float(env[f]) if cur else 0.0
    wd = shape(cur['w']) if cur else 0.4
    if cur and re.match(r'[mbp]', cur['w'].lower()) and t - cur['start'] < 0.06: op = 0.0
    cues.append([f + 1, round(op, 3), round(wd, 3)])                  # Blender frames start at 1
random.seed(7); blinks = []; t = 0.8
while t < n / FPS - 0.5:
    blinks.append(int(t * FPS) + 1); t += random.uniform(2.5, 4.5)
json.dump(dict(fps=FPS, cues=cues, blinks=blinks), open(out, 'w'))
print(f'wrote {out}: {len(cues)} mouth keys, {len(blinks)} blinks, {n / FPS:.2f} s')
