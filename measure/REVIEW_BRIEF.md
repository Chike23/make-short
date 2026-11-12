# Review brief: frame-by-frame breakdown of one reference Short (one agent per video)

You are measuring one Short or Reel (converted by `prep` to 720×1280 at 30 fps), frame by frame, so its editing style can be copied.
The user's instruction for this work: "Don't tell me what you think of them. Measure them, frame by frame: colour,
brightness, every cut, how often the shot size changes, how many locations, where the captions sit. One contact
sheet per video, one table." Report measurements, not opinions.

The worked example is `measure/example-annotations/r1.json` (Why Perfect Railroads Don't Work). Read it first.
That video is long continuous 3D camera moves joined mostly by ~8-frame dissolves, one hard cut hidden behind
smoke covering the lens, and two plain hard cuts. Do not assume your video is the same: verify everything.

## Your folder
`<DIR>/` (one folder per reference) contains `video.mp4` (720×1280, 30 fps), `source_meta.json` (the download's real frame rate: read its `note` first, because a 25 fps source has a repeated frame about every 6th frame and a 60 fps source loses every other frame), `frames/f_00001.jpg` … (**f_00001.jpg = frame 0**; frame i is
`f_{i+1:05d}.jpg`), and outputs of automated steps:
- `sheets/sheet_XXXX.png` — EVERY frame as a 90×160 thumbnail with its frame number, 240 per sheet. You must look at every sheet.
- `diffplot.png`, `diffs.csv`, `log_small.txt` — frame-difference signals and a list of cut candidates (a candidate frame = first frame after a change). Candidates are hints only: continuous camera moves create false spikes, and dissolves/hidden cuts often do not spike.
- `caption_band.json` — detected caption line (y centre in px, estimated cap height).
- `caption_cards_auto.csv`, `log_captions.txt` — automatic caption segmentation + OCR (text is often wrong; segment boundaries are usually right).
- `per_frame.csv` — colour/brightness for every frame (computed; you don't need to touch it).
Wait until `STEP1_DONE` and `MEASURE_DONE` exist in your folder before using captions/per_frame outputs (check with `ls`; sleep and recheck if needed).

## Tools (run exactly like this; do NOT edit anything in `measure/`: if a script fails, copy it into your folder, patch the copy, and say so in your report)
```
P="python3 -I <SKILL>/measure/pipeline.py"
$P strip  <DIR> <a> <b> [name]      # full-res strip of frames a..b (≤ 14 frames reads well) -> <DIR>/strips/
$P grid   <DIR> <name> a:b:step ...  # medium grid, e.g. 0:200:3 -> <DIR>/strips/<name>.jpg
$P blendfit <DIR> <a> <b>            # alpha per frame, F_i ≈ α·F_a + (1−α)·F_b  (pick a,b = clean frames either side of a dissolve)
$P capstyle <DIR> <f1> <f2> <f3>     # caption fill colour + outline ring profile on chosen frames
$P capbox   <DIR>                    # after you write caption_cards.csv
$P assemble <DIR>                    # after you write annotations.json
$P contact  <DIR>                    # renders <DIR>/contact_sheet_<key>_<title>.png
```
View images with the Read tool.

## What to produce
### 1. Every transition, frame-accurate
Look at every sheet. For each change of shot, verify with `strip` at full resolution. Classify:
- `Hard cut` — instant change between two frames.
- `Dissolve` — crossfade. Run `blendfit` with a and b a few frames outside the blend. Shot starts at the first frame with α < 0.5. The span is the frames with 0.1 < α < 0.9; if camera motion makes α drift (long tails), use the frames where both images are visibly superimposed and say so in `notes`.
- `Hidden cut (<what covers it>)` — a cut masked by smoke, a foreground object, a whip-pan blur, a flash etc. The span = the masking frames.
- Anything else (whip pan with no cut, fade to/from black/white, wipe, zoom transition): use a short descriptive name, e.g. `Fade to white`, and give its span.
A continuous camera move (even a very fast one with motion blur, or one that flies from one place to another) is NOT a transition unless the picture actually jumps — check frame pairs closely. Camera-move-driven changes of place still count as location changes (below), not cuts.

### 2. Shot size for every frame (coded by eye, ±3 frames at boundaries)
Scale, judged on the main character in frame (ref 1 used exactly this):
`EWS` no figure, or figure tiny in a big environment · `WS` whole figure visible but small in frame · `FS` whole figure, large (roughly ≥ 1/3 of frame height) · `MS` framed around knees/waist up · `MCU` chest up · `CU` head fills a large part of the frame, or a very close framing of part of a body · `INS` close detail of an object with no character.
Sizes change inside continuous camera moves — code those changes too. Use `grid` (every 2–4 frames, bigger tiles) on the character scenes to place boundaries.

### 3. Locations
A location = a distinct set (same background geometry/place). Number them 1, 2, 3 … in order of first appearance; a revisit reuses its number. Give each a short descriptive name (≤ 8 words). A camera move that travels from one place to another changes location without a cut — mark the frame where the new place takes over.

### 4. Captions
Check visually that captions sit on the detected line (`caption_band.json`) in every part of the video and that there are no captions elsewhere (titles, labels, second lines). Then write `<DIR>/caption_cards.csv` with columns `start,end,text` — one row per caption card, consecutive and covering every frame that has a caption (frames with no caption = gap). Fix OCR text by reading the frames (the words make a sentence; read the whole transcript back to check it). Merge spurious splits caused by objects/characters passing through the caption band; keep genuine 1–3-frame cards (ref 1 had real 1-frame cards). Then run `capbox`.
Run `capstyle` on three frames whose caption sits on a plain background, and write a style string in the same form as ref 1's `caption_style` (fill colour, outline thickness in px at 720 wide, shadow, typeface look, lines, animation — check for any pop/scale/colour animation across a card's first frames with `strip`; note any highlighted/coloured words).

### 5. Write `<DIR>/annotations.json`
Same schema as `measure/example-annotations/r1.json`:
`key`, `title`, `shots` = [[start_frame, "Start"|"Hard cut"|"Dissolve"|"Hidden cut (…)"|other, [span_first, span_last] or null], …] (first entry `[0, "Start", null]`; for hard cuts the span is null),
`size_spans` = [[a, b, SIZE], …] covering every frame 0..N-1 with no gaps or overlaps,
`loc_spans` = [[a, b, id], …] covering every frame, `LOC` = {"1": "name", …}, `moods` = {"<shot number>": "day"|"night"|"interior"|"dusk"} (for `bands.py`), `caption_style`, `notes` (one or two plain sentences on anything unusual and any uncertainty).
Then run `capbox`, `assemble`, `contact`. Open the contact sheet with Read and check it: thumbnails match the size labels, the shot ribbon matches your edit list, nothing overlaps. Fix and re-run until correct.

### 6. Report back (short)
Your final message is read by the coordinator, not the user. Give: the transition list (frame, type, span), shot count, number of shot-size changes, number of locations, caption line y (px) and count of cards, the output file paths, and any uncertainty or anything that does not fit the scheme above (for example a different caption style, on-screen text other than captions, colour grading changes, black frames, a speed ramp). No opinions about quality.
