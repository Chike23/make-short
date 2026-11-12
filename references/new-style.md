# Adding a new style from reference videos

Followed from the guide in `SKILL.md` when the user picks "A new style from my reference videos", or when they pick a style whose file in `references/styles/` says **Status: in setup**. A new style is a one-time build. After it, every Short in that style goes through the normal guide. Claude does not learn from references between sessions. The style lives in this skill's files: the measured numbers, a written style sheet, code, and lessons. That is why everything below ends up in `references/styles/<style>.md` and in the repo.

## 1. Collect the references
- Ask for 2-6 reels or Shorts in the style, as video files (attached here or saved in a folder Claude can reach). If they only have a profile link: Instagram and TikTok need a sign-in to play videos, so the user downloads them while signed in.
- Ask which videos count (for example "the 6 most recent") and write that in the style file. A page often mixes looks.
- One folder per video: `refs/<style>/r1/`, `r2/`, ...

## 2. Measure at 30 fps
- `python3 -I SKILL/measure/pipeline.py prep refs/<style>/rN` for each video. It converts any frame rate or size to 720x1280 at exactly 30 fps and extracts every frame. Read `source_meta.json`'s note.
- Then follow `measure/README.md`: the automatic passes, one review agent per video (`measure/REVIEW_BRIEF.md`), `bands.py`, `params.py`.
- Look at fast motion frame by frame (`pipeline.py strip`) to tell how it was made: morphing shapes or sliding textures mean AI video; rigid geometry means 3D; flat drawn frames mean 2D.

## 3. Write the style file
Copy the layout of `references/styles/anatomy-explainer.md`:
- the reference list and the rule "copy the style, never the content";
- what each video looks like;
- how it was probably made;
- captions, callouts and story formula;
- the build route(s), what has to be built, and the measured numbers.
Write `critic/targets.json` values from the measurement (see audit.py's header for the format).

## 4. Pick the engine
- **Blender (v3):** 3D worlds and characters made in code. Free, exact and repeatable, but every new set, prop or character is new code in `lib/sets.py` / `lib/chars.py`; materials and grade go in `lib/look.py`.
- **2D Chrome engine:** flat, drawn looks. Add a kit `engine/styles/NN-<id>.js` plus `scenes/door/<id>.js` (copy `_stub.js`), then a card in `references/style-catalogue.md`.
- **AI clips:** only if the user chooses it and has their own API key (paid per clip; keys never in chat). Not built into this skill yet: build it as a route file before using it.
- **Captions:** the bean style (`finish.mjs` default), the explainer style (`captionStyle: "explainer"`), or a new preset in `voice/`.

## 5. Look test
- Build one shot. Render one still (Blender: `bash gate.sh s01`; 2D: `node render.mjs --stills f0 --clean`).
- Put it side by side with a reference frame, and have a fresh critic agent list the differences (colour, light, shapes, line, text).
- Fix and repeat, at most 4 rounds, then show the user the pair and ask "Close enough?".

## 6. Test Short, then save
- Make a 15 s Short through the normal guide. Fix what the critic flags.
- Set the style file's status to **ready**. Add the style to the guide's style question in `SKILL.md`. Append lessons. Commit to the user's skill repo (ask first).
