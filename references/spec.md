# The spec: what every Short must hit

This is the target for every film the skill makes. It comes from four reference Shorts that were measured frame by frame (`reference-style.md` has every number and how it was measured), plus the user's house rules.

The spec has two parts:
- **The format.** This is the edit, the camera, the shot sizes, the captions and the pacing. It **never changes**, whatever the style.
- **The look.** This is colour, light, characters and worlds. A new style (`style-change.md`) may change it.

The tools check the spec in two places:
- `tools/plan_check.py` runs before any rendering.
- `tools/audit.py` runs on the finished video.

## House rules (from the user; they override the reference where they differ)

1. **The camera moves like the reference most of the time.** A short stop (under about 0.7 s) is fine, as long as the film as a whole has the reference's motion numbers.
2. **Fast moves, then slow drifts.** The camera makes a quick move to each new framing. Then it keeps going very slowly in the same direction (a slow push-in or a slow pan) until the next move. It never wanders and never whips.
3. **Wide shots follow the reference mix.**
   - EWS + WS together take at least 25% of screen time (36% in the reference).
   - MS takes at most 20%.
   - Open every new place wide.
4. **Black outlines on every piece of text.** That covers captions, callouts and in-world labels (dumbbell weights, notes, signs). The kit draws in-world text with an outline automatically (`sets_lib.text`), and `checks.py` fails any text without one.
5. **Characters are always head-on to the camera.** They turn to face it as it moves (`face_camera`).
6. **Characters travel.** They walk, climb, jog or step in every shot. Nobody stands on one spot for a whole shot.
7. **No lip-sync and no breathing.** Characters react and act out the story. They blink, change faces and make big moves.
8. **Library first.**
   - Furniture and props come from Poly Haven.
   - The camera shake comes from Camera Shakify.
   - Build something from scratch only when no library has it.
9. **Original characters and content.** A reference style may be copied, but not its characters, names, logos or scripts.

## The format (fixed in every style)

### Edit
| | Target | Allowed |
|---|---|---|
| Length | 62 s | 56–65 s |
| Shots | 15 | 11–19 (one shot = one story beat) |
| Average shot | 4.3 s | 3.1–5.1 s |
| Longest shot | 8.3 s | never over 8.6 s |
| Transitions | 8-frame crossfades | no whips, no dips to black, at most 1–2 hard cuts |
| Places | 9 | 7–13; revisiting 3–4 of them is good |

- **Dissolves.** Every shot renders 8 extra frames (the handle), and the next shot dissolves over them. The cut sits 4 frames before the first word of the new beat, so the dissolve is half done on the word.
- **Opening frame.** Frame 1 is a character in FS or MS, already moving. It is never black, a title or a logo.

### Camera: the grammar (house rule 2)

The camera is a list of framings, one per story moment. Each framing is a key with a frame `f`: the camera **lands** on it at `f`.
- **The move.** The camera moves into each key with an eased move (soft start, soft landing). `shotkit.camera` makes the move long enough that its fastest frame stays under about 34 px/frame at 720 wide: 10 frames for a small change, about 30 for FS→MS with a turn, and 48 at most.
- **The drift.** After landing, the camera keeps drifting until the next move starts, at about 1.5–2 px/frame. By default it keeps going the way the last move went (`follow`). The first key of a shot drifts as a slow push-in. A key can choose another drift: `push`, `pull`, `left`, `right`, `up`, `down`, `orbit_l`, `orbit_r`, or `hold` (a stop: use it rarely).
- **Shake.** Camera Shakify adds a light handheld shake on top. It is never locked off.

Key frames come from words (`wf(line, 'word')`): the camera lands on the framing a word is about.

| Camera motion (picture speed at 720 wide) | Target | Allowed |
|---|---|---|
| Median | 3.2 px/frame | 2.9–4.7 (camera-only estimate before render: 2.0–4.7) |
| Still frames (< 0.5 px) | 8% | up to 21%; short stops are fine |
| Fast frames (> 10 px) | 20% | 12–32% |
| Whips (> 45 px) | none | none |
| Shot-size changes | 0.73 a second | 0.51–0.78; 77% happen inside a move |

- **Most common moves.** FS→MS, WS→FS, FS→WS, MS→FS and MS→MCU. The camera pushes in and pulls back around a full shot, and most changes are one step on the size scale.
- **Holds per size (median frames).** MS 12 (passed through), MCU 22, CU 24, WS 35, FS 36, INS 36, EWS 51 (held longest, with the camera travelling through the place).
- **Flying between places.** About one place change in five happens with no cut: the camera flies from one place to the next. Build the two places as areas of one set.

### Shot sizes (house rule 3)
Shot size is judged on the main character.

| Size | Share of screen time | Allowed | What it is |
|---|---|---|---|
| EWS | 19% | 6–37% | the place, a tiny figure or none |
| WS | 17% | 13–25% | the whole figure, small |
| FS | **27%** | 23–31% | the whole figure, a third of the frame height or more: home base |
| MS | 13% | 11–17%; **never over 20%** | knees or waist up: passed through on the way in or out |
| MCU | 8% | 3–20% | chest up: a big reaction |
| CU | 5% | 3–10% | the face: the biggest reactions only |
| INS | 11% | 2–20% | a close detail of an object (the jar lid, the weight's label) |

Plan the sizes before writing any camera key (`planning.md`). `plan_check.py` adds up the screen time from the keys and fails the plan if MS is over 20% or the wides are under 25%.

### Captions (fixed)
- **Words.** One word per card (75%); the rest are two-word pairs (a short word plus the next word). Cards keep the punctuation and never cross it. Each card holds until the next one, so a caption is on every frame. Cards appear with no animation.
- **Look.** Near-white heavy black-weight sans, sentence case, a black outline (5 px) plus a soft shadow (outline 10, blur 5). There are no coloured or highlighted words.
- **Place.** One line, centred: cap height 54 px, baseline at y 1376 of 1920 (70% down).
- **Callouts** (a big number such as "8%", or "2×"): black outline, and never over a face. Check them in the preview.
- **Done by** `voice/finish.mjs`, which reads `voice/voice-timing.json` and `voice/cues.json`.

### Narration and story timing (fixed)
- **Pace.** 3.75 words a second, so 60 s is about 220–245 words. `voice/fit_pace.py` tightens pauses to hit it.
- **Hook.** A surprising action stated as fact, in the first 4 s.
- **"You see,".** It explains right after the hook, or brings the reveal at about two-thirds of the way.
- **Middle.** Escalating attempts and reactions, with short lines between long ones.
- **Payoff or twist.** It lands in the last 10–15% and ends on the twist (no outro).
- **Second person.** "You" talks to the viewer at least once.

### Acting (fixed; details in `acting.md`)
- **On twos.** Characters get a new pose every 2 frames. The camera, the world and the characters' travel stay on ones.
- **Big moves.**
  - The eyes lead by 3 frames.
  - 4–8 frames of anticipation.
  - 10–20% overshoot.
  - An 8–14 frame settle.
  - A 3-frame hit-stop on impacts.
- **One readable emotion per beat.** Holds never freeze.

## The look (the default style; a new style replaces this part)

### Light and world (from frame studies of the reference)
- **Sets.**
  - Smoothly lit 3D sets with no outlines on the set: only the 2D characters have lines.
  - Plain colours with fine detail such as grout lines, not noisy textures. Noise sparkles in motion.
- **Light.**
  - One strong key light that casts shadows, a fill at about a third of it, and warm key against cool fill.
  - Interiors keep the ambient low (`wstr` 0.25), so the key's shadows read.
- **Depth and air.**
  - Haze towards a bright horizon outdoors.
  - Shallow depth of field on MS and closer.
  - A low, wide camera with leading lines on wides.

### Colour
| | Target | Allowed |
|---|---|---|
| Mean brightness (luma) | 42% | 40–45% |
| HSV saturation | 51% | 48–65% |
| Red push (Lab a*) | +18 | +13 to +21 |
| Shadows | indigo or violet | never black: under 4% luma on at most about 1% of pixels |
| Blocks | one cool block, one warm block | 3–8 warm/cool flips |
| Darkest stretch | 24–30% luma for about a tenth of the film | usually 40–60% of the way in |

**Bands per mood** (ffmpeg signalstats at 1080×1920: p10 / median / p90):

| Mood | YAVG (brightness) | SATAVG (saturation) |
|---|---|---|
| day | 99 / 116 / 146 | 22 / 32 / 44 |
| dusk | 114 / 125 / 153 | 18 / 30 / 35 |
| interior | 67 / 88 / 139 | 19 / 25 / 35 |
| night | 69 / 85 / 118 | 29 / 49 / 61 (night is saturated blue, not dark) |

`tools/color_check.py` measures every shot against its band and writes a ready post-grade fix.
