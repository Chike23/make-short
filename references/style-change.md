# Changing the animation style (from two example videos)

A new style changes **how things look**: the characters, the worlds, the colours, the light and the grade. It never changes **how the film moves**: the camera grammar and numbers, the shot sizes, the edit, the transitions, the captions, the narration pace and the acting rules all stay on `spec.md`. Measured camera and pacing numbers from the new videos are ignored on purpose.

## What you need from the user
- **Two example videos** in the style they want, saved as files. Ask them to attach the files or put them in a folder. The skill cannot download from YouTube or Instagram.
- **Use them as reference only.** The style may be copied; their characters, names, logos and stories may not.
- **20–90 s each.** Pick videos that show people, an interior and an exterior if possible.
- **A short name** for the style, for example `soft-clay` or `bold-ink`.

## Steps
1. **Measure the look.**
   - Run `python3 SKILL/tools/look_measure.py <name> <video1> <video2>`.
   - It writes `SKILL/styles/<name>/`:
     - a frame every 0.5 s;
     - two contact sheets;
     - `look.json`: brightness, saturation, the Lab red push and warmth, the signalstats bands, an 8-colour palette, line weight (edge density) and flatness.
   - Look at both sheets yourself.
2. **Analyse.**
   - Start a fresh agent with `agents/style-analyst.md`. It compares the reference frames with the default look and writes:
     - `STYLE.md`: the style in words;
     - `style.json`: the style card;
     - `character-brief.md`, only if the characters need a new builder.
   - Show the user its one-paragraph summary.
3. **Build the style.**
   - **The style card** (`kit/style.py` reads it). It sets:
     - the character palettes (skin, hair, clothes) and cel shading (`shading`);
     - head and body proportions (`head_scale`, `body_scale`);
     - a colour remap for every set colour (`world.remap`, hex for hex);
     - set outlines and smoothing (`world.rick_look`) and the painterly filter (`world.kuwahara`);
     - the mood grades (`grade.moods`, `grade.rick_mood`);
     - the colour bands (`bands`).
   - **A new character builder**, only when the drawings must change shape: a different head shape, eyes, line style or body type. Copy `kit/lady2d.py` to `styles/<name>/character.py` and change the shapes. Keep the rig, so `big()`, the walks and the checks keep working:
     - the joint names (root, hips, torso, head, thigh/shin/arm/fore/hand per side);
     - `R['eyes']`, `R['eyes_all']`, `R['mouth_all']`, `R['xray']`;
     - the functions `face`, `pose`, `look`, `blink`, `hold`, `blob_shadow`, `face_camera`.
     Set `"builder": "character.py"` in the card.
   - **New sets**, only when the style's world needs places the kit lacks. Add them to `kit/sets_lib.py` as usual.
4. **Test.**
   1. Make a test project: `python3 SKILL/tools/new_project.py style-test-<name> --style <name>`.
   2. Run, in that folder: `MAKESHORT_PROJECT=$PWD blender -b --python kit/style_test.py -- style_test preview`.
   3. Make the comparison: `python3 tools/style_compare.py <name> style_test`. It writes `styles/<name>/compare.png`, with reference frames above and the test stills below:
      - the whole cast;
      - a day wide shot;
      - a night interior;
      - a close-up.
5. **Judge and fix.** Give `compare.png` and `STYLE.md` to the style analyst for a second pass: what still differs, and the card or builder change for each. Allow 2–3 rounds. Then show the user `compare.png` and ask:
   - **Use this style**;
   - **Change something**;
   - **Stop**.
6. **Save it.** Copy the style folder back to `SKILL/styles/<name>/`, leaving out `frames/`. Write the colour bands into the project's `critic/targets.json` (`{"bands": {...}}`), so `color_check.py` and `audit.py` hold the film to the new style's colours. Every later film can start with `new_project.py <slug> --style <name>`.

## What a style may change, and what it may not
| May change (the look) | Never changes (the format) |
|---|---|
| character designs, palettes, proportions, line weight, cel shading | the camera grammar (fast move, slow drift), its speeds and the shake |
| set colours and materials, outlines on sets, painterly filter | the shot-size mix (wides at least 25%, MS at most 20%) |
| light colours and strengths, haze, depth of field strength | the edit: about 4.3 s shots, 8-frame crossfades, no whips, no dips to black |
| mood grades and their colour bands | the captions: geometry, one word per card, black outline |
| sound effects and music | the narration pace (3.75 words a second) and the story shape |
| | the acting rules: on twos, anticipation, overshoot, settle, travel in every shot, head-on to camera, no lip-sync |
| | black outlines on all text |
