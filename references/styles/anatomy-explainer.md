# Style: anatomy explainer (health science in a warm 3D room, with X-ray reveals)

**Status: in setup.** Captions and callouts are built and tested (`v3/voice/captions-explainer.mjs`). Everything below marked **~** is an estimate from the reference account's profile thumbnails, and gets replaced by the 30 fps measurement (section 8). The character kit, sets and X-ray look are not built yet (section 6).

**Reference:** the 6 most recent Reels on the Instagram account `muscle40plus_` as of 12 Nov 2026 (reel IDs DfpH4-IhLLO, DfnTGaAhtkZ, DfnGtYQx1L1, Dfm-go6hx-N, DfmjmCfB9Vh, DfkuUO-RC9p). Use only these 6 unless the user says otherwise. Older posts on that page (food plates, petri dishes) are a different look.
**Copy the style, never the content:** original characters and rooms, our own scripts, no names, logos or watermarks from the reference.

## 1. What the 6 reels look like
| # | Shot | What is in it |
|---|---|---|
| 1 | Deadlift in a dim gym | Bald, grey-bearded man in an orange tee lifting a barbell; a ghosted double exposure of his body (a motion echo); orange floor tape; one-word caption "follows" |
| 2 | Side profile, living room | Same man; brain and spinal cord glowing orange-gold through the head and neck; floor lamp; dust specks in the light |
| 3 | Full X-ray | A glowing white skeleton at a barbell; an "age / 30" counter with a thin rule; a magnifier circle showing bone micro-structure with leader lines; caption "resistance training" with "resistance" in a blue selection box |
| 4 | Macro insert | A hand scooping white powder from a big white tub; warm wood background |
| 5 | Push-up, living room at sunset | A second man (dark hair, beard, grey tee) on a round rug; green sofa, framed pictures, window with a skyline |
| 6 | Kitchen X-ray | A figure as an X-ray: red skeleton, body water in magenta, pink brain; "1%" stat with "of body weight, lost as water"; wall clock, kettle |

**The look:**
- **World:** stylised 3D. Simplified, smooth forms; matte materials; soft bounce light. Rooms are lived-in and fully dressed (gym, living room, kitchen).
- **Light:** warm, low-key interiors: an amber lamp or a sunset window as the key, deep brown shadows, a dark vignette. The top of the frame stays dark, and the captions sit there.
- **People:** adults 40-60 with realistic proportions (not beans or chibi), a simple face, plain clothes in one strong colour (orange, grey). The same lead returns across videos.
- **X-ray reveal (the signature):** the body turns see-through and the relevant system glows: bones white-gold, nerves and brain orange-gold, fluids in magenta. The room stays as it was.
- **Infographics:** thin, clean UI. A big number with a small label, an "age" counter with a rule, magnifier circles with leader lines, CAPS tags ("FOREARM FLEXORS"), and a small grey footnote saying what a colour means ("Body water shown in magenta").
- **Motion:** body movement (lifts, push-ups), slow camera drift, motion echoes on fast moves, dust specks in the light.

## 2. How it was probably made (best guess, not confirmed)
Confidence is medium: this is from stills only, because Instagram needs a sign-in to play the reels.
1. **Script:** an AI-written science script with a follow line at the end; AI voice (ElevenLabs-type).
2. **Pictures:** an AI image model with a fixed style prompt and a character reference sheet, one still per beat. Each X-ray shot is an edit of the same still ("same frame, X-ray view").
3. **Motion:** an image-to-video model (Kling, Veo, Seedance or Hailuo class) animating each still into a 5-10 s clip; start/end frames for the normal-to-X-ray reveals.
4. **Finish:** an editor (CapCut, After Effects or Premiere) for cuts, word-highlight captions, the selection box, the number callouts and the magnifier circles, plus music and sound effects.

**Why:** every reel has new, fully dressed rooms and props; the X-ray versions keep the room and pose pixel-for-pixel; the deadlift has the ghosting that fast motion produces in AI video; the overlays are crisp vector graphics added afterwards. **Second possibility:** real 3D (Blender or Cinema 4D) with a rigged anatomy model, with the overlays done in After Effects.

**Confirming it (do this first when the files arrive):** look at fast movement frame by frame at 30 fps (`pipeline.py strip`). Hands, fingers, plates or furniture that subtly change shape, or textures that slide over a surface, mean AI video. Rigid geometry, a perfectly repeated character model and clean perspective mean 3D. Write the answer into section 2 and pick the route (section 5) from it.

## 3. Captions (built: `captionStyle: "explainer"`)
- A phrase card of 2-4 words (at most 2 lines), centred near the top: **~ line centre 340 px of 1920**, Inter **~64**.
- Words appear as they are spoken. The word being spoken is **white Bold**; the card's earlier words are **grey Regular**. In a pause, the whole card is grey.
- **Key words** (`keyWords` in `voice/cues.json`, word stems) stay white Bold in a **blue text-selection box with two round handles** (top-left, bottom-right). Use about one per sentence, on the term the video teaches ("resistance", "muscle").
- No outline, a soft shadow, no pop-in.
- Not measured yet: exact y, size, grey value, card length, words per card, and whether upcoming words show early.

## 4. Callouts (built: `overlays` in `voice/cues.json`)
```json
{"captionStyle": "explainer",
 "keyWords": ["muscle", "resistance"],
 "overlays": [
  {"type": "counter", "label": "age", "text": "30", "x": 1000, "y": 760, "at": "1:muscle", "until": "2:after"},
  {"type": "stat", "text": "1%", "label": "of body weight, lost as water", "x": 70, "y": 1060, "at": "3:water"},
  {"type": "note", "text": "Body water shown in magenta", "at": "3:water"},
  {"type": "tag", "text": "Forearm flexors", "x": 80, "y": 1380, "to": [330, 1180], "at": 12.4, "until": 15}
 ]}
```
`at` / `until`: seconds, or `"line:wordStem"` (that word's start). `until` defaults to 3 s later. Positions are px at 1080x1920.
**Not built yet:** the magnifier circle (a zoomed crop of the frame inside a ring, with leader lines). Make it in the render (Blender: a second camera, rendered into a circle) or add it as an ffmpeg overlay step.

## 5. Two ways to build the pictures (the user picks, once)
| | **A. AI clips** (closest to the reference) | **B. Blender** (the engine this skill already has) |
|---|---|---|
| How | Claude writes one still prompt per beat (style block plus character sheet), the X-ray edit, and the motion prompt. An image model makes the stills, an image-to-video model animates them, and our `finish.mjs`, audit and critic do the rest | Claude builds the character, rooms, X-ray materials and motion in Blender code, like the bean world |
| Cost | Paid per image and per clip, using the user's own API key, set in their own environment (never in chat). Tell them the clip count before generating | Free |
| One-time setup | An API account and key, plus a character reference sheet (generated once, then reused) | The biggest build: a realistic-proportion character with a rig (MPFB / MakeHuman, CC0 output), anatomy meshes (Z-Anatomy, CC BY-SA 4.0: credit it), an X-ray shader (fresnel emission + see-through body), 2-3 room sets |
| Per video | Fast: new rooms and props cost nothing extra | Slow: every new room or prop is new code |
| Control | Less: clips can morph; regenerate bad ones | Full: frame-exact, repeatable |

## 6. What has to be built
- [x] Captions and callouts (`captions-explainer.mjs`), tested with libass and the shipped Inter fonts
- [x] 30 fps measurement (`measure/pipeline.py prep`)
- [ ] Measure the 6 reels (section 8), then fill in the **~** numbers and `critic/targets.json`
- [ ] Confirm how they were made (section 2), then pick route A or B
- [ ] Lead character: our own design (for example a woman in her 50s, or a man with a different look and colour), with a reference sheet: front, side, three-quarter, X-ray versions
- [ ] Rooms: home gym, living room (lamp + sunset window), kitchen
- [ ] The X-ray look: bones white-gold, nerves orange-gold, fluids magenta
- [ ] Magnifier circle
- [ ] One 15 s test Short, then the critic loop

## 7. Story formula (health explainer)
- **Sources first:** every health claim needs a study or a guideline; list them in `story.md` and drop anything unsupported. Explain, never prescribe: no doses, no diagnoses.
- **Hook in line 1:** a surprising fact about the body after 40, said to "you", with the lead in frame.
- **Inside the body:** the X-ray reveal shows the mechanism; one number callout per claim.
- **What to do:** one simple action (for example "resistance training"), shown being done.
- **Payoff:** what changes, back to the number or the counter.
- **End:** a follow line for the user's own account (their name, never the reference's).
- **Length:** ~ 30-45 s until measured.

## 8. Measuring the 6 reels (at 30 fps)
1. The user downloads the 6 reels (they need to be signed in to Instagram) and attaches them, or saves them to a folder Claude can reach.
2. One folder per reel: `refs/anatomy-explainer/r1/ ... r6/`, with the download inside.
3. `python3 -I <SKILL>/measure/pipeline.py prep <dir>` converts each to 720x1280 at exactly 30 fps and extracts every frame. Read `source_meta.json`: it says if the source was 25 or 60 fps.
4. Then the rest of `measure/README.md`: one review agent per reel, then `bands.py` and `params.py`.
5. Write the numbers in here (replacing every **~**), then write `critic/targets.json` for projects in this style: shot length, transitions, colour bands per mood, caption cards per second. Add `"skip": ["caption_geometry", "caption_cards"]` until audit.py has a top-caption check.
