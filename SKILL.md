---
name: make-short
description: Make an animated YouTube Short end to end (9:16, bean characters in a painted Blender world) from one idea, matched to a frame-accurate measurement of the reference channel (references/reference-style.md). Claude measures a reference clip, writes a paradox story, records or generates the voice, builds the shot list and acting, checks stills by numbers AND by eye, renders natively, mixes sound, then an independent critic scores it and one director fixes each flagged beat. Supports a target length (for example a 15 s quick run). Never uploads without the user's explicit go. Use for "/make-short <idea>", "make an animated short about ...", "turn this into a Short".
---

# make-short (v3: Blender engine)

**SKILL** = this skill's folder ("Base directory for this skill"). **P** = the user's project folder, a copy of `SKILL\v3` (step 0). Paths below are relative to P unless they start with SKILL. Install problems: `SKILL\INSTALL.md`. What to test after install: `SKILL\CHECKLIST.md`. The older 2D Chrome route (no Blender) is `references/legacy-2d-route.md`.

## Rules, always
- Nothing is uploaded or posted unless the user types "go" (step 9). Never print or ask for API keys; they live in the user's environment only.
- No false claims: never write "1 prompt", "one prompt", "one click", "fully automatic". True: the user approved the story, and Claude wrote the shots, acting and code.
- Generic IP only: original characters and world.
- **LOOK at every still and strip yourself** (read the PNG). Passing numbers is not passing (lesson 1).
- **Never self-score.** Builders rate about 2 points too high; only the independent critic scores (step 6).
- Read `references/reference-style.md` (the measured reference: edit, camera, shot sizes, colour per mood, captions, narration speed) before steps 2 and 4. Where an older lesson or rubric line disagrees with it, the measurement wins (lessons 51-62).
- Read `references/lessons.md` (binding) before step 4 and before every fix round. Append new lessons after every round.
- Quote ETAs from the clock (`Get-Date` on Windows, `date` on macOS/Linux), at 1.5x your first guess.
- At most 5 short lines to the user between steps.
- go.sh loads the GPU. If the user is screen-recording or editing, ask before rendering.

## 0. Set up the project (once per Short)
1. Windows: `Copy-Item -Recurse "SKILL\v3" "<work folder>\<slug>"` (outside OneDrive, for example `C:\shorts`). macOS/Linux: `cp -R "SKILL/v3" ~/shorts/<slug>` (outside iCloud Drive). That is P. Work inside P.
2. **Target length:** ask once; default 60 s (the reference runs 56-65 s). **Quick run: 15 s = 450 frames at 30 fps, about 4 picture shots, about 55 words.** Everything scales: `go.sh` reads the length from the last `f_out` in `shots.json`.
3. Fresh install: run `CHECKLIST.md` section A first.

## 1. Reference measure
The reference channel is already measured frame by frame (4 videos, 7,359 frames): `references/reference-style.md`. Its numbers are the defaults for every step below, and `gate.py` BAND and `audit.py` already use them. Copy the parts this Short needs (length, shots, sizes, moods, captions) into `critic/targets.md`.
**New reference clip only:** measure it with `SKILL/measure/` (see its README). Do not use a 1 fps sheet: it misses 8-frame dissolves and 4-frame inserts, counts camera-move size changes as cuts, and on the same video gave saturation 41.9 against 31.4 measured on every frame (lesson 51). Steps: the automatic passes, then **one review agent per video** (`measure/REVIEW_BRIEF.md`; Opus at high effort, a fresh context each) that views every frame sheet and confirms every transition at full resolution. Then `bands.py` for the gate bands, and update `reference-style.md`.

## 2. Story: the paradox formula (GATE 1, the user approves)
Write `story.md` (layout: `example-60s/story.md`; do NOT reuse its story):
- **Sources** first: only facts you checked; list the caveats you dropped.
- **Hook = a paradox in line 1:** two true things that should not both be true ("canned food existed 48 years before the can opener"). The hero and the want are in frame 1.
- **Middle = escalating failed attempts**, each one visible gag per line (one noun or verb), with a hold on the reaction.
- **Payoff resolves the paradox** with the real fact; the last frame loops to the first.
- `## Narration`: numbered lines, about 3.75 words per second (reference 3.35-3.9; 60 s is about 220-245 words, 15 s about 55).
- **Timing from the reference:** the hook sentence lands in the first 4 s; "You see," either explains right after the hook (about 5% in) or brings the reveal at about 65%; the twist or payoff sits in the last 10-15%, and the film ends on it (no outro). Speak to the viewer ("you") at least once.
- Show the logline, the paradox, the numbered lines and the sources. Ask "Approve or change?". Continue only on approve.

## 3. Voice (before the shots: the shots lock to it)
Choose with the user:
- **Free route (default): record yourself** reading the narration, one calm take, save as `voice/voice.mp3`. Transcribe locally: `whisper voice/voice.mp3 --model small --language en --word_timestamps True --output_format json --output_dir voice`, then `node voice/whisper-to-timing.mjs voice/voice.json`. Read `voice/voice-timing.json` against the script. (Whisper is a separate install: `pip install openai-whisper`.)
- **ElevenLabs (optional, paid per character):** the user sets `$env:ELEVENLABS_API_KEY` in their own terminal. Tell them the character count first. `node voice/take.mjs <voiceId> voice` writes `voice/voice.mp3` and `voice/voice-timing.json`.
- Sound effects: `voice/sfx/*.mp3` is a starter set (crate, bend, boot, rock, pan, clang, pop, ding, night, music). New ones: `node voice/sfx.mjs` (same key rule), or skip.
- Frame of a word = `round(seconds*30)`.

## 4. Contract + build
1. Write `CONTRACT.md` (model: `references/contract-example.md`): length in frames, sets (`camp`, `insert`, `night`, `tent` ship in `lib/sets.py`), characters (`marcel`, `gaston`, `soldier`), props, the numbers to hit. A story needing a NEW set, prop or character means editing `lib/sets.py` or `lib/chars.py`: tell the user and budget the time.
2. **Beat list first:** one narration line = one beat = one readable frame (line, noun/verb, impact word, frame).
3. Write `shots.json` and `acting.json` from the beat list (schema: `example-60s/`, `shots/NOTES.md`; `shots/gen.js` is the generator the 60 s film used). Then `node shots/validate.js` (it now also warns on pacing). Edit and camera, from `reference-style.md`:
   - **Picture shots:** about one every 4.3 s (3.1-5.1), none longer than 8.6 s, so a 60 s Short has about 15. Several narration beats live inside ONE shot. Join them with the camera, as `travel` shots or camera keys, not with cuts.
   - **Transitions:** `dissolve` for nearly all of them (reference 95%), rendered as 8-frame crossfades with `DISSOLVE=cross`; 0-2 `cut` (an insert or the final impact); **no `whip`**, no dip to black. The camera keeps moving through every dissolve.
   - **The camera moves on 79-96% of frames** and changes framing about every 1.35 s, mostly one step at a time (FS->MS, WS->FS, MS->MCU). Write those changes as **camera keys with `size`** (and `subj`) inside the shot: scene.py frames every key and glides through the middle ones.
   - **Size mix (screen time):** XW 19%, WIDE 17%, MED 40% (FS 27 + MS 13), CU 13.5% (MCU 8 + CU 5), MACRO 11%. Wides are not dead air when the camera travels through the place. Faces at 30-40% of the frame belong to CU/MCU only.
   - **Places:** about 9 locations a minute, revisiting 3-4 of them. About one location change in five is the camera flying from one place to the next with no cut.
   - **Acting:** react, squash and lean on every line; a 12-24 frame reaction hold after each gag; no puff or blur on a gag frame.
4. **Team (30 s and up):** one subagent per frame range. Each reads `references/beats-brief.md`, writes only `beats/<name>.json`, and reports the exact impact frame. For a 15 s run, build it yourself.

## 5. Gate: numbers AND look
1. `bash gate.sh` renders one still per shot; `gate.py` prints PASS/FAIL per shot (saturation/luma bands, blown whites, crops). Fix FAILs; `tune.sh` tries grade overrides.
2. `bash contact.sh 1 24` makes `gate/contact_1.png`. **Open it and look.** Per shot: gag object visible and big, faces readable, nothing cropped, no giant foreground clutter, characters not overlapping, the mood colour right.
3. At most 3 gate rounds. Show the user the sheet; render only after they say "render".

## 6. Render, mix, independent critic
1. `DISSOLVE=cross bash go.sh r1` (native 1080x1920, 3 processes, plus the crossfade handles; about 21 min for 60 s on the author's GPU, so roughly 5-6 min for 15 s; give a clock-time ETA). Output `out/rounds/r1-silent.mp4`.
2. Mix: write `voice/cues.json` from the impact frames (format in its `_note`), then `node voice/finish.mjs` (captions now follow the measured spec: line centre at 70.2%, no pop-in, 75% one-word cards, held until the next card). Output `out/short-v3-final.mp4`; copy it to `out/rounds/r1-final.mp4`.
   Then `python3 audit.py` (`python audit.py` on Windows) (in P): one PASS/FAIL line per measured reference parameter (edit, sizes, camera motion, colour per mood, caption position and timing) written to `critic/audit.md`. The four reference videos pass it. Fix every FAIL that is not a deliberate choice before the critic round; if the caption baseline is off, move `captionY` in `voice/cues.json` by the difference.
3. **Critic = a fresh subagent** that did not build the film. Give it the final mp4, the reference clip, `critic/RUBRIC-blank.md`, `critic/audit.md` and your suspicions to verify. It makes frames and cmp sheets, fills the rubric, writes `critic/critique-r1.md` with 3 fixes by FRAME RANGE. Verify each claim at full resolution before acting (lesson 28).
4. Pass = criteria 1-4 each >= 7 and mean >= 8. The first Short took 12 renders; a 15 s one should need far fewer, but time the real run and report the real number.

## 6b. Blender MCP route (optional: when a Blender MCP server is connected)
The scripts stay the source of truth. Use MCP to **look and measure**, not to hand-build.
- **Build the scene:** `bash save.sh` (in P) writes `scene.blend`. Open it in the live Blender with `execute_blender_code` (`bpy.ops.wm.open_mainfile(filepath=...)`). Never run scene.py inside the live session: it resets the file.
- **Look:** jump to each camera-key frame and check it with `render_thumbnail_to_path`, or `get_screenshot_of_window_as_image` for blocking. This is faster than a gate render for camera and framing iteration.
- **Measure:** query positions and project heads or props to the camera (`world_to_camera_view`) at each key. Use this to tune `KEYMUL` (or a key's own `hvmul`) until each key's framing matches its size.
- **Write back:** put every change into `shots.json`, `beats/*.json` or `lib/*.py`, then rebuild. Edits made only in the .blend are lost on the next build.
- **Renders stay on the CLI** (`go.sh`): a long render through an MCP call times out. `execute_blender_code_for_cli` suits short background jobs on `scene.blend`.

## 7. One director per flagged beat
Per flagged frame range, one subagent: reads `references/beats-brief.md`, `references/lessons.md`, the critique and the stills; writes only `beats/<range>.json`; re-renders only its range (`bash render.sh A B`, output in `render/`); makes a strip; LOOKS at it twice; reports the impact frame. Then redo steps 5-6 for that range. Stop at the pass bar or when the user says stop. Never "ship the best we have, call it a first try".

## 8. Lessons
Append to `references/lessons.md` (numbered, one line: what the critic found, what fixed it). Copy new lessons back into SKILL's `references/lessons.md`.

## 9. Upload (manual by default)
Hand over `out/short-v3-final.mp4`. Titles start with a verb; the description has the fact, its source and `#Shorts`. The user uploads by hand. Auto-post only if the user asks: copy the final to `out/<slug>-9x16.mp4`, then `node "SKILL\scripts\post.mjs" "P" --platforms youtube` is a dry run; `--go` only after the user types "go" in this conversation. It needs their own `$env:BLOTATO_API_KEY` (generating it starts a paid plan). Private by default; `--public` only if told. Never handle the key.
