# Troubleshooting: what broke before, and the fix

| Symptom | Cause | Fix |
|---|---|---|
| A Blender MCP call stops after about 80 s | the MCP has a time limit | run long work in the background: `tools/chain.py`, or `blender -b --python film.py -- ...` |
| A render chain crashed or rendered old code after an edit | a file it was reading changed under it | `chain.py` freezes the code in `OUT/_code/`; never run two chains from one live folder |
| `CHECK ... lens against <object>`, or a blank, blurry stretch in a clip | the camera is pressed against a prop (the doctor's laptop) | move the prop off the sightline or move the camera key; never render with this CHECK |
| `CHECK ... camera keys too close` or a whip (> 45 px/frame) | two framings too close in time for a smooth move | space the keys (about 33 frames per frame-height of change), or drop the middle key |
| `CHECK ... clipping: june through <object>` | the cut-out passes through a set object | apply the suggested move to her position or path; if it is on purpose (sitting in the sofa), add it to `FILM['allow']` |
| A reaction happens off screen | the camera key isn't on the reaction | add a two-shot or MCU key landing on the reaction word |
| The night is pure electric blue | the mood's saturation is too high, and blue clips | mood `sat` at most about 1.0; then `color_check.py` and a post-grade |
| A shot is too bright or too saturated for its mood | the mood's gain or saturation | `tools/color_check.py`, then `grade_fix.py` (no re-render); then fix `look.MOODS` in `kit/sets_lib.py` |
| Faces look orange at dusk | dusk saturation × the grade's saturation push | lower `park_dusk` `sat`, or `grade_fix` `hue=s=0.85` |
| Pops or stutters on big moves | BACK easing drawn on twos | use `big()` (Bezier with overshoot keys), not BACK |
| Her size pulses while she walks | the travel was stepped on twos | `on_twos` skips the root's x/y; keep travel on `L.walk/travel` |
| The jar lies sideways in her hand | the prop follows the hand's rotation | `hold_prop` (COPY_ROTATION to the root) |
| Blinks reset a shocked face | the blink came back to "open" | `blinks()` returns to whatever eyes she had and avoids face changes |
| Captions are in the wrong place, or there is no outline | the font is missing; libass can't read woff2 | `finish.mjs` uses Arial Black or the bundled Inter (otf); check `audit.py` caption lines |
| "2×" or "8%" sits on a face | the callout's x/y in `voice/cues.json` | move it (it is drawn on top), then re-run `finish.mjs` only |
| The last caption disappears early | the last card ended at the voice end | `finish.mjs` holds the last card to the end of the picture |
| ElevenLabs runs at 2.98 words/s | `speed` is ignored by eleven_v4 | `voice/fit_pace.py` (cuts long pauses, gentle atempo) |
| The voice is out of sync after a re-cut | the timing was edited by hand | the timing is locked after step 6; re-run `fit_pace.py` from `voice/raw/` |
| Textures are missing (pink objects) | `~/shorts/_assets/tex` was never generated | `python3 SKILL/kit/sets.py` (needs pillow and numpy) |
| `KeyError` for a mood | a mood is used before it is defined | moods live in `kit/sets_lib.py` (and `world3d.py`); define new ones there |
| A render takes much longer than the estimate | three or more Blender processes are sharing the GPU | at most 2 chains; don't run test renders during a final render |
| Wide shots show the edge of the set | the set wasn't built that far | widen the set (walls, floor, sky) or pick a lower angle with a foreground object |
