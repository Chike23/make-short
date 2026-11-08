# Improvements from a frame-accurate measurement of the reference

This copy of make-short has been retuned to a measurement of four reference Shorts from the same channel. All 7,359 frames were decoded at 30 fps, and every transition was checked by eye at full resolution. One of the four, `7xS87iActkU`, is the video the original contract measured from 1 fps sheets.

The skill's process held up well: measure, gate, an independent critic, lessons. Its numbers were the problem. Most of its edit and camera rules came from 1 fps samples and pointed the film away from the reference. The shipped 60 s example is furthest off: 1.55 s shots, 31 hard cuts and no wide shots, against 4.3 s, crossfades and 36% wides.

All measured values are in `references/reference-style.md`.

## How the two analyses compare

| What | make-short assumed (where) | Measured on every frame (4 videos) |
|---|---|---|
| Method | 1 fps contact sheet + `signalstats` on JPG stills (SKILL step 1) | every frame; a review agent per video confirms each transition at full resolution |
| Saturation, same video `7xS87iActkU` | SATAVG 41.9; contract demands ≥ 38 | **31.4**. Day median 32. The gate pushed saturation up (see lesson 24b, the red ground) |
| Mean luma (YAVG) | 105, band 95–115 | 116 on that video; 105–116 across the four. Close |
| Shot length | "cuts every 2.8 s" in the reference (lesson 47); the example cuts every 1.55 s | **a picture shot every 4.34 s** on that video; 4.3 s median of four (3.1–5.1); never over 8.6 s |
| Transitions | 6–8-frame whips, dissolves that dip to ink, hard cuts at beat edges (lessons 7, 42; contract) | **52 of 56 are 8-frame crossfades** (6–10) with the camera moving through; 3 hard cuts, **0 whips**, no dip, no black frames |
| Shot-size changes | "every 2–3 s"; one size per shot (scene.py keys only the first and last camera key) | **every 1.35 s**, and **77% happen inside one continuous camera move** |
| Camera | "mostly calm and eased" (lesson 17) | moving on 79–96% of frames; median 3.2 px/frame at 720 wide; fast (> 10 px) on 20% of frames |
| Wide shots | "dead air, 1 s at most" (lesson 8); the example has 0% wides | EWS + WS fill **36%** of screen time; EWS held longest (median 1.7 s), with the camera travelling |
| Face size | heads 30–40% of frame in character shots; rubric wants ≥ 30% in ≥ 70% of frames | only CU and MCU frame heads that big: 13.5% of screen time. **FS dominates at 27%** |
| Locations | rubric ≥ 5; the example uses 4 sets | **7–13 (median 9)**, 3–4 revisited; 18% of place changes are the camera flying across, with no cut |
| Night grade | YAVG 50–65, SATAVG 40–46 | **YAVG 69–118 (median 85)**: bright, and the most saturated mood (SATAVG median 49, blue) |
| Interior grade | YAVG 95–105, SATAVG 33–42 | YAVG 67–139, SATAVG 19–35: dimmer and less saturated |
| Caption position | about 68% (rubric); `MarginV 560` puts the line centre near 68.2% | **70.2%**: cap top 1,321 px, baseline 1,376 px at 1080×1920. Identical to the pixel in all four |
| Caption size | cap height about 52 px (lesson 33); Arial Black 108 ≈ 55 px | **54 px**. The repo was right |
| Caption animation | each card scales 80% → 100% over 90 ms | **none**; a card replaces the last on one frame |
| Caption grouping | 61% one-word cards in the example; punctuation stripped; held 0.9 s at most | **75% one-word**; punctuation kept; held until the next card (a caption on every frame) |
| Caption stroke | outline 10 + hard 6 px drop shadow | thinner outline + a soft, even shadow (fitted: outline 5 + a blurred shadow layer) |
| Narration speed | at most 3 words/s (the example: 2.98) | **3.75 words/s** (3.35–3.91); 60 s ≈ 220–245 words |
| Story | paradox hook, escalation, "You see…", payoff | confirmed. The hook lands in the first 4 s; "You see," comes right after the hook or at about 65%; every video ends on the twist |

## What changed in this copy

| File | Change | Tested here? |
|---|---|---|
| `references/reference-style.md` (new) | Every measured parameter, in % and in `signalstats` units, plus bands per mood, palette roles, caption spec and story timing | From the measured data |
| `measure/` (new) | Full-frame-rate breakdown toolkit: automatic passes, a review brief for one agent per video, contact sheet, workbook, gate bands, motion. The four videos' edit lists are in `example-annotations/` | Yes, it produced the four breakdowns |
| `v3/audit.py` (new) | A PASS/FAIL line per reference parameter on a finished render (edit, size mix, camera motion, colour per mood, caption position and timing) → `critic/audit.md` | Yes. The four references, rebuilt as projects, pass every check (0 FAIL). The 60 s example's shot list fails 10 of its 12 edit and size checks. Streams frames (no 2 GB buffer); audits the silent render if there is no final mix yet |
| `v3/gate.py` | `BAND` = measured p10–p90 per mood, plus `dusk`; mood aliases (`night_in`, `day_hot`, …) no longer crash | Values computed from 738 reference stills; script parsed only |
| `v3/voice/finish.mjs` | Captions placed at baseline 1,376 (`captionY` to adjust); no pop-in; outline 5 + soft shadow layer; punctuation kept; pairs chosen to give 75% one-word cards; no gaps | Grouping run on the example timing (74.8% one-word, full coverage). Caption rendered through libass with a stand-in black-weight font: the cap-height and baseline model matched to the pixel. **Not run end to end with Arial Black** |
| `v3/shots/validate.js` | Accepts `cut` (the example uses 31; the old validator rejected them and demanded exactly 1,815 frames); length checked against the narration; pacing warnings; per-key `size` | Syntax only |
| `v3/scene.py` | Every camera key is used, with optional `size`/`subj`, so a shot can push FS → MS → MCU; keys interpolate by frame; `KEYMUL` keeps MS/MCU keys tighter than the old 2.5 m minimum allowed; no handle overshoot at shot ends. `DISSOLVE=cross` adds a `handles` mode for real crossfades, drops the dip and keeps the camera moving through the dissolve | Syntax only. **Needs one Blender test** (CHECKLIST.md section D) |
| `v3/keystills.sh`, `v3/save.sh` (new) | A gate still at every camera key; `scene.blend` for opening in Blender over MCP | Parsed with `bash -n` only |
| `v3/dissolve.py` (new) | Blends the render and the handles into 8-frame crossfades | Yes, on synthetic frames (linear ramp, safe to re-run) |
| `v3/env.sh`, `gate.sh`, `render.sh`, `tune.sh`, `go.sh`, `lib/sets.py` | macOS and Linux: Blender path detection, a Python that actually runs (`$PYTHON` first; skips the Windows Store `python3` stub), `pwd -W` only where it exists; `go.sh` runs the crossfade step | Parsed with `bash -n` only |
| `SKILL.md` | Step 1 → the shipped measurement (or `measure/` for a new reference); measured edit, camera and caption rules in steps 2, 4 and 6; `audit.py` before the critic; a Blender MCP section; Mac commands | — |
| `references/lessons.md` | Lessons 51–62: what the measurement corrects, naming the older lessons it supersedes | — |
| `v3/critic/RUBRIC-blank.md`, `references/contract-example.md`, `v3/shots/NOTES.md`, `INSTALL.md`, `README.md`, `CHECKLIST.md` | Targets and instructions brought in line with the measurement | — |

The narration transcripts of the reference videos are **not** included; only edit lists, measurements and caption geometry are. Keep it that way if you publish a fork.

## Not done yet

- **Run CHECKLIST.md section D in Blender.** The `scene.py` changes (multi-key camera, crossfade handles) are untested, and both are opt-in or backward-compatible: a 2-key shot behaves as before, and without `DISSOLVE=cross` nothing changes.
- **The framing scale for `MS` and `MCU` keys** (`KEYMUL` in scene.py: MS 0.65 × the MED frame, MCU 1.2 × the CU frame) is a starting value. Check it on key stills (`keystills.sh`).
- **The example project's night shots will fail the new night band.** Its night look (`look.MOODS['night']`) was tuned to the old, darker band. Lift exposure/gain with `tune.sh` and compare the stills with the reference before trusting the gate.
- **Crossing sets inside one shot is not possible:** sets sit 300 m apart. Build places the camera flies between as areas of one set.
- **Not measured:** sound (music, effects, voice tone), acting rates (pose changes per second) and character proportions. Lesson 47's 3.2 head heights and ink at 6.6% of head width still stand.

## To recreate these videos with Blender MCP and Claude

- **Your Mac:** Blender 5.x plus the Blender MCP server (already connected to Claude on your computer), and `brew install ffmpeg node python`. Arial Black ships with macOS.
- **Workflow:** scripts and JSON stay the source of truth. Claude writes `story.md`, `shots.json` and `beats/*.json` and builds the scene on the command line. It then opens `scene.blend` through MCP to look at each camera key and measure framing. Final renders run on the command line (`go.sh`), never inside an MCP call.
- **A character kit in the reference style:**
    - white round heads, a black ink outline and stick limbs;
    - costume read by the hat;
    - full figures at eye level;
    - a library of named poses and faces.
  The engine ships three bean characters. A new story usually needs new props and one new set; budget time for them.
- **Sets:** about 9 locations per minute, 3–4 revisited. Build 2–4 sets with several areas each, so the camera can travel between places without a cut.
- **Voice:** your own recording or ElevenLabs, written to about 3.75 words/s. Whisper gives the word timing.
- **The loop that gets quality:**
    1. `bash keystills.sh`: a still at every camera key.
    2. `DISSOLVE=cross bash go.sh r1`.
    3. `node voice/finish.mjs`, then `python3 audit.py` (`python audit.py` on Windows).
    4. A fresh critic with `critic/audit.md`.
    5. Fix only the confirmed problems.
    6. Re-measure with `measure/` whenever you adopt a new reference.
