# Style: anatomy explainer (health science in a warm 3D room, with X-ray reveals)

**Status: in setup (measured).** All 6 reference reels were measured at 30 fps on 12 Nov 2026 (section 8). Captions and callouts are built, tuned to the measurement and checked side by side (`v3/voice/captions-explainer.mjs`). Still to build: the shot builder, the lead character and the pictures (section 6).

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

## 2. How it is made (measured; best explanation)
**Illustrated stills animated in an editor**, with a few short image-to-video moves. Confidence: medium-high for the editor part; whether the few body moves are AI video or puppet animation is not certain.
1. **Script:** a sourced science script, about 90 s, read at 3.3 words a second, ending on a phone-UI call to action. Reel r6 was posted as the same video twice with two different hooks (frames 304-2215 repeat as 2520-4431): they A/B test openings.
2. **Pictures:** consistent painterly "illustrated 3D" stills: the same lead character per video, warm dark rooms, props floating on a dark stage. X-ray views are matching stills or layers (organs, bones, muscles) laid over the body.
3. **Motion is mostly the edit, not the scene:** within shots the camera is locked off about 56% of the time; slow push-ins (about 24%) and pull-outs (about 15%) run at 2-6% zoom a second, with pans about 8%. Characters hold a pose while layers fade in (X-ray organs, sweat drops, a towel, labels). Fast motion is on only about 3% of frames.
4. **Real material composited in, with credits:** for example a Wikimedia ultrasound image captioned "carotid ultrasound: Mme Mim, Wikimedia", or "Tomoto et al., JCBFM" next to a study chart.
5. **Editor presets for transitions:** 3-frame crossfades, vertical slides with motion blur, dips through dark. Plus word-by-word captions with a key-word selection box, number callouts, magnifier circles and a phone mock-up for the call to action.

**Evidence:** at 30 fps, faces and printed text (plate weights, "IQ TEST", calendar cards) stay stable with no AI-video warping during camera moves; layers appear and fade independently of the body; real images carry credits; transitions are the same few preset shapes in every reel.

## 3. Captions (built and tuned: `captionStyle: "explainer"`)
Measured at 720x1280, then converted to 1080x1920:
| | Reference | Ours |
|---|---|---|
| Position | first baseline y 256 of 1280 (20%); second line 55 px lower | baseline y 384 of 1920; line pitch 82 px |
| Size | cap height 35 px at 720 (x-height 25) | Inter 87, letters at 95% width, cap height 52 px |
| Font | geometric sans (Figtree / Plus Jakarta Sans-like) | Inter Regular + Bold (shipped, OFL) |
| Spoken word | white, bold | same |
| Earlier words in the card | warm grey RGB about 112,108,105, regular weight | #74706C regular |
| Key word | white bold in a blue (#3D7BFF-ish) selection box, dark fill, round handles top-left and bottom-right | same |
| Entry | each word blurs in for 1 frame; the line re-centres as words arrive | same |
| Between cards | about 2 empty frames | `cardGap: 2` |
| Words per card | about 3.5 (3.0-3.7), up to 2 lines | `maxWords: 4` |
| Cards per second | about 1.0 (0.9-1.1) | follows the narration |
| Caption on screen | about 92% of frames | same |
| Key-word box on screen | about 27% of frames (19-33%), about 38 boxes a minute: one key word in most phrases | pick 1 key word per phrase |

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
Also seen: small grey **source credits** (author, journal, year) next to the image or chart they belong to, and a **phone in a hand** showing an Instagram DM or share screen as the call to action in the last 5-8 s. **Not built yet:** the magnifier circle (a zoomed crop inside a ring, with leader lines) and source credits as a callout type.

## 4b. Edit, camera, colour, sound (measured)
| | Measured (median, range across the 6) | Bean-world reference, for contrast |
|---|---|---|
| Length | 84-108 s (r6 first version 74 s) | 56-65 s |
| Average shot | **3.9 s** (per reel 3.3-5.3); median 2.9 s; middle 80% between 0.9 and 7.8 s | 4.3 s |
| Transitions per minute | about 16 (10.6-17.3) | 13 |
| Transition types | 3-frame crossfade 54%; vertical slide/push with motion blur 16%; 1-2 frame cut 16%; slow 6-10 frame crossfade or fade 10%; dip through dark 4% | 95% 8-frame crossfades |
| Camera inside a shot | still 56% (40-69%); slow push-in 24%; pull-out 15%; pan 8%; zoom 2-6% a second; fast motion about 3% of frames. **Overridden by the user (12 Nov 2026): the camera moves on every frame, and the lead is livelier than the reference** (house rules in `references/route-explainer.md`) | moving on 79-96% of frames |
| Shot content | character in a room or gym, normal or X-ray (about 45%); props and infographics on a dark stage (about 35%); medical close-ups such as scans, fibres and bone (about 15%); phone-UI call to action (about 5%) | characters in a painted world |
| Brightness | very dark: mean luma 19% of full scale (17-23%); top band (captions) 10%, middle 31%, bottom 14%; signalstats YAVG p10/p50/p90 41 / 57 / 84 | luma 42% |
| Colour | warm orange-brown: hue about 28 degrees, Lab a +3.4, b +7.0; low saturation, signalstats SATAVG p10/p50/p90 4 / 7 / 13 | SATAVG 19-35 interior |
| Narration | **3.3 words a second** (3.2-3.8); about 0.23 s between word onsets | 3.75 words a second |
| Not measured | music and sound effects, voice tone, exact shot sizes per frame | |

## 5. How we build it
**Chosen 12 Nov 2026: B, Blender stills.** Build steps: `references/route-explainer.md`. Option A stays here for reference.

The measurement shows the motion is mostly the edit: still pictures, slow zooms, layers fading in, preset transitions. So every option shares one **shot builder** that Claude writes in code (ffmpeg; section 6). The choice is only where the pictures come from:

| | **A. Image model stills** (closest to the reference) | **B. Blender stills** (free, this skill's engine) |
|---|---|---|
| How | Claude writes one prompt per shot from a fixed style block and the character sheet, plus the X-ray or overlay variant of the same frame. The user generates them in an image tool, or Claude does through an API key in the user's own environment | Claude builds the character, rooms and props in Blender code and renders single frames (plus X-ray passes) instead of full animation |
| Cost | The image tool's plan or per-image API price; tell the user the image count first | Free |
| One-time setup | A character reference sheet, made once and reused | A realistic-proportion character (MPFB / MakeHuman, CC0 output), anatomy meshes (Z-Anatomy, CC BY-SA 4.0: credit it), an X-ray material, 3 rooms and a dark stage |
| Per video | Fast: about 25 shots, each one or two images | Slower: new props are new code, but renders are single frames, so quick |
| Body moves (about 3% of frames) | Optional: an image-to-video tool on the 2-3 shots that need it (paid) | Blender animates those shots for real |

## 6. What has to be built
- [x] Captions and callouts, tuned to the measurement and checked side by side (`captions-explainer.mjs`)
- [x] 30 fps measurement of the 6 reels (`measure/pipeline.py prep`; results in sections 2-4b)
- [x] Confirmed how they are made (section 2), so **route A changes**: stills animated in the edit. Image-to-video only for the few body moves
- [x] Where the stills come from: **Blender** (route B)
- [x] Shot builder: `v3/explainer/compose.py` (stills + layers + slow zooms + crossfade / push / cut / fade / dip), tested end to end with the captions
- [ ] Blender kit: the lead character (our own design) with poses, plus an X-ray version (skeleton, organs, muscles) that lines up with the body
- [ ] Blender kit: rooms (home gym, living room with lamp + window, kitchen), a dark "stage" for props, the warm low-key light and grade (luma about 19%, top band about 10%)
- [ ] Magnifier circle and source-credit callouts; phone-UI call-to-action template
- [ ] `critic/targets.json` for this style: `references/styles/anatomy-explainer.targets.json` (copy it into each project)
- [ ] One 30 s test Short, then the critic loop

## 7. Story formula (health explainer)
- **Sources first:** every health claim needs a study or a guideline; list them in `story.md` and drop anything unsupported. Explain, never prescribe: no doses, no diagnoses.
- **Hook in line 1:** a surprising fact about the body after 40, said to "you", with the lead in frame. The reference tests two hooks for the same body (r6); you can do the same by rendering two openings.
- **Inside the body:** the X-ray reveal shows the mechanism; one number callout per claim.
- **What to do:** one simple action (for example "resistance training"), shown being done.
- **Payoff:** what changes, back to the number or the counter.
- **End:** a follow line for the user's own account (their name, never the reference's).
- **Length:** the reference runs 84-108 s at 3.3 words a second (about 280-350 words). Start with 30-45 s Shorts (100-150 words) and build up.

## 8. Measurement record (12 Nov 2026)
- **Files:** the 6 reels, saved from the user's signed-in browser: 720x1280 at 30 fps, 84-154 s. r6 measured on its first version only (frames 0-2215).
- **Method:** `pipeline.py prep`, `small`, `measure`, `capband`, `sheets`, plus four quick passes:
  - transitions: candidate clusters, an automatic classifier, then every unclear case checked by eye on frame strips;
  - camera: ORB feature matching every 0.5 s inside shots;
  - words: onsets of new white caption words;
  - key-word boxes: blue pixels in the caption band, every 2nd frame.
- **Not done (the full measure/ review):** an agent coding shot size and location for every frame, and clean caption text. The automatic caption OCR did not suit word-by-word captions, so it was stopped. Shot counts are about ±15%: the classifier finds most picture changes, a few in-shot overlay changes count as transitions, and a few slow ones may be missed (r6's longest "shot" of 21 s probably hides one).
- **Re-measuring:** download into `refs/anatomy-explainer/rN/`, then `python3 -I SKILL/measure/pipeline.py prep refs/anatomy-explainer/rN` and the steps in `measure/README.md`. Keep the videos and frames out of the repo.
