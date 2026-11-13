# explainer/: the anatomy-explainer shot builder

`compose.py` turns still renders into the moving, silent video: `out/short-v3-silent.mp4`, 1080x1920 at 30 fps. Then `voice/finish.mjs` adds the voice, music, sound effects, captions (`"captionStyle": "explainer"`) and callouts. The look and the numbers it follows are in `references/styles/anatomy-explainer.md`. The build steps are in `references/route-explainer.md`.

## shots.json
```json
{"vignette": 0.35,
 "shots": [
  {"id": "s01", "at": 0, "base": "renders/s01.png",
   "camera": {"from": [1.0, 0.5, 0.5], "to": [1.08, 0.5, 0.42], "ease": "inout"},
   "layers": [{"img": "renders/s01_xray.png", "in": "2:bones", "fade": 0.3, "mode": "screen"},
              {"dim": 0.45, "in": "4:percent", "fade": 0.2}],
   "transition_in": "crossfade"}
 ]}
```
- **at**: when the shot starts. Seconds, or `"line:wordStem"` (that word's start in `voice/voice-timing.json`). The first shot starts at 0; each shot runs until the next one starts.
- **base**: the shot's still, rendered a little larger than 1080x1920 (for example 1350x2400) so the zoom has room. Any 9:16 size works.
- **camera**: `[zoom, centre x, centre y]` from the start to the end of the shot; the centre is 0-1 across the image. Leave it out for a locked-off shot. The reference pushes in or pulls out 2-6% a second (about 24% and 15% of the time), and holds still the rest.
- **layers**: images from the same camera at the same size (an X-ray pass, labels, sweat), or `dim` (darkens the shot under a stat callout).
  - `in` / `out`: when the layer appears and disappears (seconds or `"line:wordStem"`).
  - `fade`: how long the fade takes, in seconds.
  - `mode`: `normal`, `screen` (glows) or `add`.
- **transition_in**: how this shot arrives.
  - `crossfade` (3 frames, most of the reference) and `fade` (8 frames, the slow ones);
  - `push_up` / `push_down` (4 frames with motion blur, about 16%);
  - `cut` (about 16%) and `dip` (6 frames through near-black, about 4%).
  - Or give an object: `{"type": "crossfade", "frames": 4}`.

## Commands (in P)
- `python3 explainer/compose.py --stills`: one still from the middle of each shot plus one at each transition, in `gate/explainer/`. Look at them before rendering.
- `python3 explainer/compose.py`: the whole video, about 0.1 s a frame (about 2-3 min for 45 s).
- `python3 explainer/compose.py --from 4 --to 7`: shots 4 to 7 only, in `out/part.mp4`.
