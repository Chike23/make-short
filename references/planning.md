# Planning: from an idea to film.py

Every number below is in `spec.md`. The worked example is `example/june-and-the-jar/` (`story.md`, `film.py`, `voice/`).

## 1. Story (`story.md`)
- **Sources first.** Every fact has a source you checked, listed under `## Sources`. Health facts above all. Explain, never prescribe.
- **Logline.** One sentence: who wants what, what goes wrong, how it turns.
- **The shape.**
  1. A hook in the first 4 s: a surprising action stated as fact ("At sixty-two, June couldn't open a jar of pickles.").
  2. "You see," explains right after it.
  3. The middle escalates through attempts and setbacks.
  4. The turn.
  5. The payoff lands in the last 10–15% and ends on it. It may call back to the hook (the jar).
- **Beats.** 14–16 beats for 60 s, one per shot, about 4 s each. Each beat has a place, an action you can SEE, and a reaction.
- **Places.** 7–13 for 60 s. Re-use 3–4 of them: the street, the stairs and the kitchen came back in the example and showed the change.
- **Characters.** Original ones only. One lead with a clear want, plus 1–3 others. A reference style may be copied; its characters may not.

## 2. Narration (`## Narration` in story.md)
- **Length.** 3.75 words a second: 60 s ≈ 225 words (220–245).
- **Lines.** One numbered line per beat or less. Short lines between long ones ("Two kilos.", "First try.").
- **"You".** It talks to the viewer at least once.
- **Show the user** the logline, the beats and the narration, then ask for approval. Write the approval time into story.md.

## 3. Voice
- **ElevenLabs.**
  - Make a take: `ELEVENLABS_ENV_FILE=~/.make-short-keys node voice/take.mjs <voiceId> voice`. The key stays in the user's key file; never open or print it.
  - Fit the pace: `python3 voice/fit_pace.py` cuts long pauses and gently speeds up to 3.75 words a second. It keeps the original in `voice/raw/`.
- **Own recording.**
  1. Convert it to `voice/voice.mp3` with ffmpeg.
  2. Time every word with Whisper (`whisper voice/voice.mp3 --model small --word_timestamps True --output_format json`), then run `node voice/whisper-to-timing.mjs`.
  3. Read `voice/voice-timing.json` against the script, and fix mis-heard lines.
- **Lock it.** After this, the timing is locked: every key frame in the film comes from it.

## 4. The shot plan (show it to the user before building)
One row per shot. Fill it in this order:

| Shot | Words (cut on) | Place, mood | What we see (action + travel) | Sizes the camera lands on |
|---|---|---|---|---|
| S01 | 1–2 "At sixty-two…" | kitchen, interior | June walks to the counter, fights the jar, glares at the lid | FS → MS → MCU → INS (lid) → MS |
| S03 | 5 "Nobody…" | street, day | she walks home, the bags drag her arms down | EWS → WS → FS |

- **Cut words.** Each shot starts on the first word of its beat: `FILM['cuts'] = [(line, 'Word'), ...]`, one entry per shot after the first. The cut sits 4 frames before the word.
- **Place and mood.** One per shot: `FILM['loc']`, `FILM['mood']`. The mood is day, dusk, interior or night.
- **The size budget** (house rule 3). Add up the sizes the plan lands on, by time, before writing any camera key:
  - **EWS + WS: about a third of the film.** Open every new place wide and hold it while the camera travels through it. EWS is held longest (about 1.7 s).
  - **FS: about a quarter.** It is home base: full figure, a third of the frame or more.
  - **MS: at most a fifth (13% target).** It is passed through on the way in or out, not parked on.
  - **MCU and CU: about 13% together.** Only for the big reactions, and only a few frames each.
  - **INS: about a tenth.** The hero prop: the jar lid, the weight's label, the prescription.
  - A good shot often goes **WS → FS → MS → FS**, or **EWS → FS → MCU → FS**.
- **Travel in every shot** (house rule 6): walk in, cross, climb, jog, step back. Write the path in the plan.
- **One big action per beat** that you can read with the sound off.
- **Light and colour.** One cool block and one warm block across the film, and one darkest stretch (24–30% luma) about halfway: the night fall in the example.

## 5. Write film.py (from `template/film.py`)
For each shot function:
1. `setup(f0, f1)` and the set: `S6.kitchen()`, `S6.street()`, `S6.stairs(night)`, `S6.bathroom()`, `S6.doctor()`, `W.living_room()`, `W.gym()`, `W.park(mood)`. A new place gets a new set function in `kit/sets_lib.py`: simple shapes plus Poly Haven props, a `LIGHT` entry, a mood and a ground function.
2. Cast: `cast('june', (x, y), pal=L.PAL, face=...)`. Palettes: `L.PAL`, `L.SON`, `L.YOUNG_MAN`, `L.DOCTOR`, or your own dict.
3. `light('<set>', f0, f1)`.
4. Times from words: `a = wf(line, 'word')`.
5. Acting (`acting.md`): `L.walk/jog/travel` paths, `big()` per beat, `L.face`, `L.look`, `hop`, `tremble`, props with `hold_prop`.
6. Camera keys (`spec.md` grammar):
   - one key per framing, landing on its word;
   - about 33 frames between keys per frame-height of change; FS→MS needs about 25–30;
   - `drift` only when the default (follow) is wrong.
7. `finish('Sxx', f0, f1, cam, grounds=..., allow=...)`.

Then run step 1 of `workflow.md`.

## 6. Sound effects and callouts (`voice/cues.json`)
The example's `voice/cues.json` shows every field.
- **`cues`.** A sound effect on a word: `["pop", 4, "eight", 0.0]` is a pop on "eight" in line 4, 0.0 s later. The sounds in `voice/sfx/` are pop, ding, clang, sit, boot, whoosh, crate, tree, rock, pan, bend and night.
- **`hits`.** A sound effect on a frame: `["boot", 562, 0.75]` is an impact. Put it on the impact frame, not on the word.
- **`overlays`.** 1–3 callouts per film, on the facts that matter:
  - `stat`: a big number with a label ("8%", "muscle lost per decade").
  - `counter`: a small label over a number ("a week" over "2×").
  - Give each `at` and `until` (a "line:word" or seconds) and `x`/`y` in 1080×1920 pixels.
  - Callouts are drawn with a black outline. Keep them off faces: check them in the preview frames, because the camera moves.
- **Music.** `voice/sfx/music.mp3` (the starter track, ducked under the voice), or the user's own track.

## Mistakes the checks now catch, and how they were found
- **Lens against an object.** The camera pressed against the back of the doctor's laptop for 20 frames. Fix: move the prop off the sightline, or raise the camera.
- **Big moves crammed into a few frames.** Keys 4–10 frames apart for big changes made whips at 90–110 px/frame. Fix: space the keys, or drop the middle one.
- **A reaction off screen.** June's "not a pill?!" take happened outside the frame. Fix: a two-shot key on the reaction word; the judge checks every reaction word is on screen.
- **A prop covering a face.** The doctor's note covered her face. Fix: hold props beside the face, not in front of it.
- **A reversed pose, a head cut.** The framing checks print them before any render.
