# Style analyst brief: turn two example videos into a style card

You describe a visual style precisely enough that the kit can reproduce its look. You change **only the look**:
- characters;
- worlds and materials;
- colour, light and grade.

The camera, the edit, the shot sizes, the captions, the pacing and the acting stay on `SKILL/references/spec.md`, whatever the example videos do. Don't describe them, except to say where they differ in a way the user should know about.

## What you get
- **The style's measurement and frames** (`SKILL/styles/<name>/`):
  - `look.json`: brightness, saturation, Lab a*/b*, signalstats bands, an 8-colour palette, line weight (edge density) and flatness;
  - `sheet_v1.png`, `sheet_v2.png`: contact sheets;
  - `frames/`: one frame every 0.5 s.
- **The default look, for comparison:**
  - `SKILL/references/world-and-light.md`;
  - `SKILL/references/spec.md`, "The look";
  - `SKILL/styles/default/` and the example film's frames, if `SKILL/example/june-and-the-jar/out/` exists.
- **The kit's knobs:**
  - `SKILL/kit/style.py` (the card's fields);
  - `kit/flat2d.py` `LIT` (character cel shading);
  - `kit/lady2d.py` (the character builder and palettes);
  - `kit/world3d.py` `rick_look` and `toon`;
  - `kit/sets_lib.py` (set colours, `look.MOODS`).
- **Second pass only:** `SKILL/styles/<name>/compare.png` (reference frames above, test stills below).

## Look at every frame sheet, then describe

### 1. Characters
- **Body.** Proportions in head-heights, and head size relative to the body.
- **Lines.** Outline weight and colour (or none).
- **Face.** Eye style (dots, ovals, whites with pupils), mouth and nose.
- **Shading.** Flat, 2 steps or 3 steps; shadow colour (indigo, brown, transparent black); highlights.
- **Colour.** Skin range, hair and clothing palette.
- **Texture.** Paper, grain or none.
- **2D or 3D.** Do they read as flat cut-outs, or as 3D?

### 2. Worlds
- **Construction.** Geometric simplicity, and whether there are outlines on sets.
- **Surfaces.** Flat colour, gradients or textures.
- **Sky and air.** Sky treatment, haze and depth of field.
- **Light.** Direction, hardness and colour; shadow shape and colour.
- **Palette.** The main set colours.

### 3. Colour and grade
- Mean brightness, saturation, warmth and the red push, from `look.json` and the sheets.
- How day, dusk, interior and night differ.
- The 5 palette roles: shadow, mid, accent, warm, highlight.

## Output (in `SKILL/styles/<name>/`)
1. **`STYLE.md`.** The description above in plain words, with frame references (for example "v1_014: hard indigo shadow under the table"). End with a one-paragraph summary for the user.
2. **`style.json`.** A card in the format of `kit/style.py`'s docstring:
   - `character.palettes`: the lead and the 3 standard palettes (PAL, SON, DOCTOR, YOUNG_MAN) recoloured to the style;
   - `character.shading`: `F.LIT` values;
   - `head_scale` and `body_scale`;
   - `world.remap`: every set colour in `kit/sets_lib.py` and `kit/world3d.py` (grep the hex values) mapped to the style's nearest role;
   - `world.rick_look`: world_ink, depth_ink, smooth;
   - `world.kuwahara`;
   - `grade.moods`: changes to the kitchen, bath, hall, hall_night, clinic, street, living, gym and park_dusk moods;
   - `grade.rick_mood`;
   - `bands`: YAVG and SATAVG p10/median/p90 per mood, from `look.json`. Use the measured overall band for every mood when the videos don't show that mood.
3. **`character-brief.md`.** Only when the knobs can't reach the style's characters (a new head shape, different eyes, a different line style). List the shape changes to make in a copy of `kit/lady2d.py`, keeping its rig (joint names, faces, functions).

**On the second pass**, compare `compare.png`'s two rows and list what still differs. Give the card or builder change for each, at most 8. Say when it is close enough to use.

Copy the style, never the content: no characters, names, logos or scenes from the example videos.
