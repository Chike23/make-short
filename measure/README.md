# measure/: frame-accurate reference breakdown

This replaces the old 1 fps step (`v3/measure.sh` plus a 1 fps contact sheet). At 1 fps an 8-frame dissolve is invisible, so is a 4-frame insert. Size changes made inside camera moves get counted as cuts. On `7xS87iActkU` the old method gave saturation 41.9 and "cuts every 2.8 s". Every frame gives 31.4 and a shot every 4.3 s (lesson 51).

The results for the four reference videos are already in `../references/reference-style.md`. Run this only to measure a **new** reference.

**Needs:**

- Python 3.10+ with `numpy`, `opencv-python`, `pandas` and `pillow`.
- `openpyxl`, for the workbook only.
- `pytesseract` with the `tesseract` binary. This is optional; without it the caption text is typed in during review.
- `ffmpeg`.
- macOS: `brew install ffmpeg tesseract`, then `pip3 install numpy opencv-python pandas pillow openpyxl pytesseract`.

## Everything is measured at 30 fps

References come from YouTube, Instagram and TikTok at 24, 25, 30, 50 or 60 fps and 720 to 1080 wide. `prep` converts each one to **720×1280 at exactly 30 fps** (constant frame rate) before anything is measured, so every number (shot length, dissolve length, caption timing) is in the same 30 fps frames as our renders. The original download stays in the folder and `source_meta.json` records its real size and frame rate, plus a note when the conversion repeated or dropped frames. `measure` and `small` refuse to run on a video that is not 720×1280 at 30 fps.

## Steps (one folder per reference video: put the download in `<DIR>/`, any name, any frame rate)

```bash
M=<SKILL>/measure
python3 -I $M/pipeline.py prep     <DIR>    # any download -> video.mp4 at 720x1280, 30 fps + every frame as frames/f_00001.jpg (= frame 0)
python3 $M/pipeline.py capband  <DIR>    # finds the caption line
python3 $M/pipeline.py small    <DIR>    # 90x160 frames, frame-difference signals, cut candidates, diffplot.png
python3 $M/pipeline.py sheets   <DIR>    # EVERY frame as numbered thumbnails, 240 per sheet
python3 $M/pipeline.py measure  <DIR>    # brightness/colour per frame (BT.709 decode) -> per_frame.csv
python3 $M/pipeline.py captions <DIR>    # caption cards + OCR -> caption_cards_auto.csv
```

**Review by eye (the part that cannot be automated).** One agent per video reads `REVIEW_BRIEF.md` and works through every sheet. It confirms each transition at full resolution (`strip`, `blendfit`), codes shot size and location for every frame, and fixes the caption text. It writes `<DIR>/annotations.json` and `<DIR>/caption_cards.csv`; the four reference edit lists are in `example-annotations/`. Use a separate agent per video, at high effort: the review is long and a fresh context keeps it accurate.

```bash
python3 $M/pipeline.py capbox   <DIR>    # caption geometry per card
python3 $M/pipeline.py assemble <DIR>    # analysis.json + per_frame_full.csv
python3 $M/pipeline.py contact  <DIR>    # the contact sheet
python3 $M/motion.py  <DIR> ...          # camera motion (optical flow)
python3 $M/bands.py   <DIR> ...          # gate.py BAND values per mood (needs "moods" in annotations.json)
python3 $M/params.py  <DIR> ...          # pooled parameters -> params.json
python3 $M/build_workbook.py out.xlsx <DIR> ...   # one workbook: comparison, shots, every frame
```

Then update `../references/reference-style.md` with the new numbers.

**Helpers**

| Command | What it does |
|---|---|
| `pipeline.py strip <DIR> a b` | full-resolution strip of frames a..b |
| `pipeline.py grid <DIR> name a:b:step …` | medium-size grid of chosen frames |
| `pipeline.py blendfit <DIR> a b` | blend weight per frame across a dissolve |
| `pipeline.py capstyle <DIR> f1 f2 f3` | caption fill colour and outline thickness |
