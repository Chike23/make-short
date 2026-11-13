# Verifier brief: measure the finished Short against the spec

You are an independent checker. You did not make this video. Measure it; take nobody's word for how it looks.

## What you check (in the project folder P)
- `out/short-final.mp4`: the finished video (1080×1920, 30 fps), with captions and sound.
- `out/short-silent.mp4`: the picture only.
- `shots.json`: the edit (`tools/make_shots.py`).
- `plan/film.json`: each shot's frames, place and mood.
- `voice/voice-timing.json`: the narration (global frame = round(t × 30) + 1).
- The rules:
  - `SKILL/references/spec.md`: the format, the look, the house rules and the numbers.
  - `SKILL/references/reference-style.md`: how every number was measured.
  - `critic/targets.json`, if present: a new style's own colour bands, which replace the default look's.

## Tools
- `python3 tools/audit.py`: the skill's own audit. It writes `critic/audit.md`. Read every FAIL and INFO line.
- `python3 tools/color_check.py render_graded` (or `render`): per-shot brightness and saturation against the mood bands.
- `checks/plan_check.md`: the pre-render check, for comparison.
- ffmpeg (signalstats), python3 with numpy, opencv-python and PIL.

## Checks
1. **Edit.** Shot count, average shot length (3.1–5.1 s), longest shot (≤ 8.6 s), transitions per minute, places (7–13).
2. **Camera motion.**
   - Method: optical flow on the silent video. Use the reference's own method: 90×160 frames, scaled ×8 to 720 wide. Plain Farneback at 720 reads 0 on flat colour.
   - Report the median px/frame, % still (< 0.5), % fast (> 10), whips (> 45), and every run of still camera longer than 20 frames.
   - House rule: short stops are fine if the film as a whole hits the targets.
3. **Camera grammar.** On 3 shots, plot or list the per-frame motion. It should show quick moves into framings, then slow drifts. Report wandering, reversals and whips.
4. **Shot sizes.** The share of each size by screen time, and size changes a second. House rule: EWS + WS at least 25%, MS at most 20%.
5. **Brightness and colour.**
   - At least 2 stills per shot: YAVG and SATAVG against that shot's mood band.
   - Mean luma (about 42%), HSV saturation (about 51%), Lab a* (about +18).
   - Shadows: indigo, not black.
   - Cool and warm blocks, and the darkest stretch (24–30% luma).
6. **Captions.** On 8+ frames: one line, centred, cap height about 54 px, baseline near y 1376, near-white with a black outline. Callouts outlined and off faces. A caption on every frame.
7. **Narration.** Words per second (3.75; 3.35–3.91), and the word count.
8. **Transitions.** Every one an 8-frame crossfade, with no dip and no hard cut. The camera moves through each one.
9. **Black outlines on all text** (house rule 4). Captions, callouts and in-world labels (weights, notes, signs).
10. **Character rules.**
    - Head-on to the camera in every shot.
    - Travel in every shot.
    - No floating, sinking or clipping through objects, except deliberate ones listed in film.py's `FILM['allow']`.
11. **Overall look.**
    - Make a contact sheet, 1 frame every 0.5 s, 8 columns: `critic/contact.png`. Look at all of it.
    - Judge it against `spec.md`'s look:
      - smooth 3D sets with no set outlines;
      - one strong key with cast shadows;
      - haze outdoors;
      - shallow depth of field on MS and closer;
      - warm/cool contrast.
    - Note anything broken: z-fighting, missing textures, sparkling noise, ugly edge cuts.

## Output
Write `critic/verify.md` with:
1. A table, one row per check: the measured value, the target and range, and PASS, FAIL or NOTE.
2. The 5 most important fixes, ranked. For each, name the shot, the parameter and the change, and mark whether it needs a re-render. For example: "S15 YAVG 104 under the dusk band 114–153: grade_fix S15 `curves=all='0/0 0.5/0.55 1/1'` (no re-render)".
3. A one-paragraph verdict: does it meet the spec and the house rules?

Don't edit any file outside `critic/`, and don't re-render. Return a short summary: the verdict and the top 5 fixes.
