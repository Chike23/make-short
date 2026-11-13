# Judge brief: one pass on the whole-film preview

You are an independent judge. You did not make this film, and you score it fresh: you never see your own earlier scores. Your job is to say what will make it **fluid, lively and charismatic**, and to find every visible fault, while the fixes are still cheap (before the final render).

## What you get (all in the project folder P)
- `out/preview.mp4`: the whole film at preview quality (360×640 upscaled), with voice, captions and sound.
- `preview/S??_*.mp4`: one clip per shot. Make contact sheets: `bash tools/sheet.sh <clip> 6 critic/<sid>.png 160`, or extract single frames with ffmpeg at the frames you need.
- `checks/S??.json` and `checks/plan_check.md`: the automatic checks.
  - **camera**: blocked, lens against an object, framing.
  - **clipping**: a character through an object, with the suggested move.
  - **outlines_missing**.
  - **motion**: camera px/frame, frame by frame.
  - **camera_keys_too_close**.
- `film.py`: the shot code (one function per shot; times come from words: `wf(line, 'word')`). `story.md`: the beats and narration. `voice/voice-timing.json`: the word times (global frame = round(t × 30) + 1).
- The spec: `SKILL/references/spec.md` (the house rules and numbers), `acting.md` and `world-and-light.md`.

## Look at every shot, then the whole film once with sound

### 1. Fluid movement
- Are moves eased, with anticipation, overshoot and settle?
- Do pose changes pop?
- Does travel slide or float? Do feet stay on the ground?
- On twos: the characters should step 2 frames at a time, while the camera stays smooth.

### 2. Energy and charisma
- Is there one big readable action per beat?
- Does every reaction land on its word, on screen, on a face we can read?
- Does anyone stand still for a whole shot? Do holds freeze? Would a viewer keep watching?
- Name the dullest 3 seconds of the film.

### 3. Staging and clipping
- Confirm or reject each `clipping` event in `checks/*.json` by looking at its frames.
- Look for clipping the check can't see: an arm through a prop, a held prop through the body, a character half inside a wall at the frame edge, feet below the floor, two characters overlapping badly.
- For each real one, give the fix in film.py terms. Use the check's suggested move when it is right ("S16: start June at x 0.0 instead of 0.3 (the check suggests 0.3 m left)"), otherwise your own.

### 4. Camera grammar (house rule 2)
- The camera should make a quick, eased move to each framing, then drift very slowly in the same direction until the next move.
- Flag moves that feel like whips (the `motion` array over 45 px/frame), moves that wander or wobble, and drifts that are too fast or that reverse.
- Flag stops long enough to notice (over about 0.7 s).
- Fixes are key changes: move a key's `f`, drop a key, change `drift` (`push`, `follow`, `hold`, ...), change `move`.

### 5. Framing and shot sizes (house rule 3)
- Do the wides open each place?
- Is MS only passed through?
- Are close-ups saved for the big moments?
- Is any head cut, face in the caption band, subject off-centre, lens pressed against something, or reaction off screen?
- `plan_check.md` gives the size shares.

### 6. Light and colour
- One strong key with shadows that read.
- Indigo shadows, never black.
- Warm/cool blocks, and a darkest stretch.
- Night saturated blue, not crushed.
- No garish clipping (pure electric blue, orange skin).
- No sparkling noisy textures.

### 7. Readability at phone size
- Hero props recognisable (the jar, the note, the weight's label).
- In-world text readable and outlined.
- Callouts (stat, counter) off faces.
- Captions clear of busy areas.

## Output
Write `critic/judge.md` with:
1. **Scores 1–10**, one line each: fluid movement, energy and charisma, staging and clipping, camera grammar, framing, light and colour, readability, overall.
2. **Top 10 fixes, ranked by how much they improve the film.** Each one names:
   - the shot and frames;
   - what is wrong, in plain words;
   - the exact change in film.py terms (the key, the value, the new value) or the set or mood to change;
   - whether it needs only a check re-run (the camera, positions) or a new look at stills.
3. **Clipping table.** Every clipping event: real or not, and the fix.
4. **What works.** The 3 moments to keep exactly as they are.

Be concrete and short. Check every claim at full resolution before you make it: an earlier critic called captions "20 px" when they measured right. Don't edit any file outside `critic/`, and don't render.
