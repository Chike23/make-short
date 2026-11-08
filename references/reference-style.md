# Reference style: measured frame by frame

These numbers come from four Shorts by the reference channel, decoded at their full frame rate. That is 7,359 frames at 720×1280 and 30 fps, 245 s in total. The first of the four is `7xS87iActkU`, the same video the original contract measured at 1 fps.

| Ref | Video | Length | Frames |
|---|---|---|---|
| R1 | Why Perfect Railroads Don't Work (`7xS87iActkU`) | 65.17 s | 1,955 |
| R2 | What the Grave Bell Really Meant | 59.50 s | 1,785 |
| R3 | Why the Second Draw Always Wins | 56.07 s | 1,682 |
| R4 | Why Sailors Carried Storm Oil | 64.57 s | 1,937 |

**How the numbers were measured**

- Computed on every frame: brightness, colour, frame differences, optical flow and caption geometry.
- Checked by eye on every frame: transitions (each confirmed at full resolution, and dissolves with a blend-weight fit), shot size, location and caption text.
- Target = median of the four. Range = lowest to highest of the four, unless a pooled percentile is named.
- These numbers **override** older rules in `lessons.md`, `RUBRIC-blank.md` and `contract-example.md` wherever they disagree (see lessons 51–62).
- Tools: `../measure/`.

## 1. Edit

| Parameter | Target | Range |
|---|---|---|
| Length | 62 s | 56–65 s |
| Shots | 15 | 11–19 |
| Average shot (ASL) | 4.3 s | 3.1–5.1 s; pooled average of all 60 shots: 4.1 s |
| Shot length, pooled | median 3.8 s | middle half 2.2–6.0 s; 10% under 1.1 s; 10% over 7.7 s |
| Longest shot | 8.3 s | 7.9–8.6 s; no shot in any video is longer than 8.6 s |
| Transitions per minute | 13 | 10.7–18.2 |
| Transitions that are dissolves | 95% | 79–100%; 52 of 56 overall |
| Hard cuts | 0–1 | 0–2 (3 of 56) |
| Whip pans | **0** | none in any of the four videos |
| Fade to or through black | **0** | none; there are no black frames |

**What a dissolve looks like**

- It is a true crossfade: frame ≈ α × outgoing + (1 − α) × incoming. Brightness never dips; it moves straight from one shot's level to the next.
- The median dissolve is 8 frames (0.27 s). The middle half run 6–10 frames, and the full range is 3–12.
- The shot starts at the first frame where α < 0.5.
- The camera keeps moving on both sides of every dissolve. No dissolve sits on a still frame.

**What a transition does**

- 70% of transitions also change location. The rest move to a new angle in the same place.
- The three hard cuts are R3's 4-frame insert of a gun firing at 0.67 s, and R1's two cuts: one to a low angle at 44.0 s and one into the closing explosion at 64.2 s.
- R1 hides one cut behind locomotive smoke that covers the lens for 3 frames.
- R3 dissolves through a character's pupil into a round window, a graphic match.

## 2. Camera

The camera is almost never still, and it changes the framing far more often than the edit does.

| Parameter | Target | Range |
|---|---|---|
| Frames with a still camera (median optical flow < 0.5 px/frame at 720 wide) | 8% | 4–21% |
| Median camera motion | 3.2 px/frame at 720 wide (≈ 4.8 at 1080) | 2.9–4.7 (4.4–7.1 at 1080) |
| Frames with fast motion (> 10 px/frame at 720) | 20% | 19–32% |
| Shot-size changes per second | 0.73 | 0.51–0.78 (33–51 per video) |
| Average hold before the size changes | 1.35 s | 1.25–1.9 s |
| Size changes made **inside** a continuous camera move | 77% pooled | 67–86% |
| Size changes of one step on the scale | 65% | two steps 22%, three or more 13% |
| Location changes made by the camera alone (flying from one place to the next, no cut) | 18% pooled | R4 6, R1 2, R3 1, R2 0 |

- **Most common size moves:** FS→MS (20), WS→FS (16), FS→WS (10), MS→FS (9), MS→MCU (9). The camera pushes in and pulls back around a full shot.
- **Median hold per size (frames):** MS 12, MCU 22, CU 24, WS 35, FS 36, INS 36, EWS 51. Medium shots are passed through; extreme wides are held longest.
- **Opening frame:** all four open on a character in FS or MS. Frame 1 is never black, a logo or a fade.

## 3. Shot size: share of screen time

The scale is judged on the main character:

- **EWS:** no figure, or a tiny one.
- **WS:** whole figure, small.
- **FS:** whole figure, large (about a third of the frame height or more).
- **MS:** knees or waist up.
- **MCU:** chest up.
- **CU:** head or close body.
- **INS:** close detail of an object.

| Size | Pooled share | Range by video | Engine size (`shots.json`) |
|---|---|---|---|
| EWS | 19.0% | 6.0–36.9% | XW |
| WS | 16.9% | 12.7–24.7% | WIDE |
| FS | **26.7%** | 22.7–31.1% | MED (wide end) |
| MS | 13.0% | 10.6–16.9% | MED |
| MCU | 8.3% | 2.7–20.2% | CU (loose) |
| CU | 5.2% | 3.0–9.7% | CU |
| INS | 11.0% | 2.1–19.6% | MACRO |

**Engine targets:** XW 19%, WIDE 17%, MED 40%, CU 13.5%, MACRO 11%.

- Wide and extreme-wide frames fill 36% of screen time, almost always with the camera moving through the place.
- Heads at 30% or more of the frame height happen only in CU and MCU, which together are 13.5% of screen time.

## 4. Locations and structure

| Parameter | Target | Range |
|---|---|---|
| Locations (distinct sets) | 9 | 7–13 |
| Location changes | 14 | 6–15 |
| Average visit | 4.4 s | 3.7–8.0 s |
| Videos that revisit a location | 3 of 4 | each revisits 3–4 places |
| Location changes made at a transition | 82% pooled | the rest are the camera flying between places |

## 5. Brightness and colour

Two unit systems are given:

- **%:** BT.709 luma from a full-range RGB decode, as a percent of full scale.
- **signalstats:** ffmpeg `signalstats` run on 1080×1920 RGB PNG stills, exactly as `v3/gate.py` measures (YAVG, SATAVG, YLOW = 10th percentile, YHIGH = 90th percentile).

| Parameter | Target | Range |
|---|---|---|
| Mean luma | 42% | 40.0–44.6% |
| Darkest 5% of pixels (average) | 13% | 10.7–15.2% |
| Brightest 5% of pixels (average) | 79% | 76.2–80.9% |
| Contrast (luma SD within a frame) | 20.6% | 20.2–22.5% |
| Pixels below 4% luma | 0.6% | 0.5–3.4%; shadows are lifted, nothing crushes to black |
| Pixels above 96% luma | 1.3% | 0.7–5.0% |
| Darkest frame (mean luma) | 16.5% | 15.9–17.9%; no frame is darker |
| Brightest frame | 80% | 70–90% (explosion, glowing bowl, dawn, close-up of an eye) |
| Shot mean luma, pooled | median 43% | 80% of shots between 26% and 58% |
| Mean HSV saturation | 51% | 48–65% |
| Colourfulness (Hasler–Süsstrunk M) | 81 | 73–91 |
| CIELAB a* (red push) | +18 | +13 to +21 in every video |
| CIELAB b* (warm +, cool −) | −5 | −15 to +3 overall; shots swing from −65 to +57 |
| signalstats YAVG / SATAVG, all frames | 111 / 31.5 | per video YAVG 105–116, SATAVG 29–44 |
| signalstats spread (YHIGH − YLOW) | 117 | per video 111–127 |

**Bands per mood (signalstats, p10–p90 of reference frames).** Use these as the `BAND` table in `gate.py`.

| Mood | Frames sampled | YAVG p10 / median / p90 | SATAVG p10 / median / p90 |
|---|---|---|---|
| day | 417 | 99 / 116 / 146 | 22 / 32 / 44 |
| dusk (sunset) | 33 | 114 / 125 / 153 | 18 / 30 / 35 |
| interior | 145 | 67 / 88 / 139 | 19 / 25 / 35 |
| night | 143 | 69 / 85 / 118 | 29 / 49 / 61 |

**How the moods behave**

- Night is **saturated blue**: the night median SATAVG of 49 is higher than day's 32.
- Night is not dark: the YAVG median is 85, where the old night band was 50–65.
- Interiors are dimmer and less saturated than exteriors.
- Each video plays in long colour blocks. Every video has a cool block, its coolest shot at b* −25 to −65, and a warm block, its warmest shot at +14 to +57. There are 3–8 warm/cool flips between shots per video.
- Every video has one darkest stretch at 24–30% mean luma for a tenth of the runtime. In three of the four it falls between 40% and 60% of the runtime.

**Palette roles.** The same five roles appear in every video's 6-colour palette:

| Role | Hex values (R1, R2, R3, R4) |
|---|---|
| Indigo shadows (never black) | #332C4E, #2B1E43, #2E243D, #24318D |
| Rust red-brown | #7A3B38, #7C4D32, #80483C, #8F4B2F |
| Orange or tan | #DD743A, #AC8162, #C59973, #DC9C51 |
| Mid blue | #618AD2, #6B7FDD, #3D98F5, #385AD4 |
| Pale pink or cream highlight | #CEC4C9, #DBB8BB, #E0CEBE, #CED6DD |

## 6. Captions

Captions are identical to the pixel across all four videos.

| Measure | 720×1280 (as uploaded) | 1080×1920 (render) | % of frame |
|---|---|---|---|
| Cap top | 881 px | 1,321 px | 68.8% from top |
| Line centre (cap top to baseline) | 899 px | 1,349 px | **70.2%** from top |
| Baseline | 917 px | 1,376 px | 71.6% from top |
| Bottom of descenders | 926 px | 1,389 px | 72.3% from top |
| Cap height | 36 px | **54 px** | 2.8% of height |
| x-height | 26 px | 39 px | 2.0% of height |
| Horizontal centre | 359.5 px | 540 px | 50% (156–188 of each video's cards within 3 px) |
| Black outline | 4–5 px | 6–7.5 px | |
| Soft dark shadow reaches | ~7 px | ~10 px | even all round, not an offset drop shadow |
| Card width | median 140 px | median 210 px | 19% of width; widest 48–63% |

**Style**

- Near-white fill (RGB 247–251).
- Heavy black-weight sans in sentence case, keeping the narration's punctuation.
- One line. A card never has two lines.
- **No entry or exit animation.** No pop, no scale and no fade. Each card replaces the last on one frame.
- No coloured or highlighted words.
- **libass recipe** (`v3/voice/finish.mjs`): Arial Black 108 placed with `\an2\pos(540,1400)` gives a 54–55 px cap height and a baseline at 1376. Use outline 5 plus a soft shadow layer (outline 10, `\blur5`, black at 69% opacity) underneath. This matched the reference edge profile best after a 720p upload; tested with a stand-in black-weight font. Check the result with `v3/audit.py`.

**Timing**

| Parameter | Target | Range |
|---|---|---|
| Frames with a caption | 100% | 99.9–100%; captions hold until the next card, with no gaps |
| Words per second | 3.75 | 3.35–3.91 |
| Cards per second | 2.9 | 2.73–3.02 |
| One-word cards | 75% | 73–79% (pooled: 1 word 75.4%, 2 words 22.2%, 3 words 2.4%) |
| Card length, median frames | 10 | 9–11 per video |

- **Length tracks the spoken word:** a one-word card of 3 letters or fewer lasts a median 5 frames, 4–5 letters 9 frames, 6–7 letters 12 frames, 8 or more 15 frames. A word followed by punctuation holds about 5 frames longer.
- **Pairs:**
    - Half of the cards that start with a short word (3 letters or fewer) pair it with the next word: "the youngest", "his boss", "a coin".
    - A quarter of two-word cards are a word plus a trailing article or particle: "into a", "close a", "want to".
    - Cards almost never cross punctuation (2 of 711).

## 7. Narration and story timing

- **Length:** 218–246 words for 56–65 s.
- **Hook (0–5% of the runtime):** a surprising action stated as fact, under 4 s ("He sawed gaps into a railroad every 39 feet.", "They buried a man alive with a bell tied to his finger.").
- **"You see,":** appears in all four. Either it explains right after the hook (5% of the runtime, R1 and R2) or it brings the reveal at 65–66% (R3 and R4). R2 uses it again at 90%.
- **Middle:** escalating attempts and reactions, with short lines ("Wait.", "Practiced?", "You go check.") between long ones.
- **Payoff or twist:** in the last 10–15% of the runtime. Three of the four end on the twist itself, with no outro.
- **Second person:** "you" addresses the viewer in every video ("Imagine you're standing…", "Ever blown on a bowl of soup").
