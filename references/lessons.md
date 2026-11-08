# Lessons: v3 bean-world Short (append after every round)

Each lesson records what we learned and how it changes the next build. Every agent reads this first.

## Look and grade
1. **Passing the numbers doesn't mean it looks right.** The gate passed 37/37 while the night insert was a magenta wash with a blue can. Always LOOK at the stills next to the reference; the numbers only catch drift.
2. **Don't grade a mood onto a macro insert.** Grading the tabletop to "night" turned the props purple or blue. The fix was changing the mood itself: inserts use the warm lantern look, and the night feel is carried by the wide shots and the sky. Faces, labels and props keep their real colours.
3. **Firelight on the ground spreads red.** Keep the fire glow orange with a small falloff.
4. **Pushing saturation at night turns it garish.** Get the night colour from blue/orange contrast, not from more saturation.
5. **Grain hurts the look.** The reference is clean.

## Camera and edit
6. **Automatic framing from the real positions** beats hand-set camera numbers, which missed characters and went through objects.
7. **Long whips turn a lot of the film into smear (about 15%).** Whips should be about 6 frames.
8. **Wide shots with tiny characters are dead air in 9:16.** Faces should be 30–40% of the frame height in close-ups, and a wide shot lasts 1 s at most.
9. **Show every story beat on screen in the frame where its word lands.** On "pops" the camera was on the chef, not the can. Check each cue word's frame.

## Characters
10. **Holding poses and swapping faces reads stiff (6.5/10).** The reference beans squash and stretch, lean, anticipate and hold their reactions, and their mouths flap on dialogue.

## Round 1 critic (independent, 4.2/10; my self-rating was 6.5, so self-rating inflates)
15. **Always get an independent critic with side-by-side reference sheets.** My own eye graded 2 points too high.
16. **Reference beans are full-body,** with stick legs and feet on the ground, in calm medium two-shots. Half-beans buried at the waist read as cut off.
17. **"Shot size every 2–3 s" got over-applied into constant whips and dutch close-ups.** The reference camera is mostly calm and eased; the variety comes from the cut points, not from motion everywhere.
18. **A painterly ground is smooth** (soft patches and few marks). Dense brush-stroke noise reads as neon mush.
19. **Only about 9 of 22 beats were visible at their word.** Build the shot list FROM the beat list: one beat, one readable frame.
20. **Puffs and whips were hiding the gags.** Gag frames stay clean, followed by a 12–24 frame reaction hold.

## Round 3 build
21. **Agent time boxes slipped about 50 min** (12:15 became about 13:05). Building plus test renders in Blender take longer than planned, so quote ETAs at 1.5× the agent's box.
22. **The world pass made the ground calmer, but wide shots still show about 50% bare grass.** Clearing a "character corridor" empties the frame. Put foreground props at the frame edges instead.
23. **Stick legs instantly read as the reference style.** The full-body change was the right priority.

24. **The world pass caused regressions:** a red dirt disc, posterized banding and lavender night faces. Each agent must re-render the APPROVED baseline shots and diff them against the earlier stills before reporting; checking only "my 5 shots, my numbers" misses side effects.
24b. **The red ground was NOT the world pass:** it came from the integrator's `day_hot` grade (saturation ×1.9) in scene.py. Cap any per-shot saturation boost at about 1.2. Find the root cause before blaming the latest change.
24c. **Shot ids changed when shots.json was rewritten,** so "s16" meant a different shot to each agent. Refer to shots by frame range, or freeze the ids once they're published.
25. **A shared palette token (`red`) is risky.** Changing it hits every material that uses it. Give each material its own colour.
26. **Full-body medium shots at eye level** (s02, s05, s11, s40 in r3) instantly read like the reference. A top-down or high camera on a bean shows only a hat.

27. **Drive the SFX from data:** whooshes come from the whip cuts in shots.json, and the cues from the words, so a re-cut never breaks the sound. The critic can't hear audio from frames, so verify the sound separately.

## Round 2 critic (5.7/10, +1.5)
28. **Verify the critic too.** It said the captions were "about 20 px", but a full-res crop showed the same size as the reference. The real differences were case, word grouping and the shadow. Check every claim at full resolution before acting on it.
29. **Time SFX to the visible impact, not the word start.** The tree was 9 frames early and the pop 3. Ask the animator for the impact frames.
30. **A prop that doesn't read as itself** (the opener looked like an arrow) kills its beat. Make hero props recognisable at phone size.

## Round 3 critic (6.0/10, +0.3: a plateau)
31. **One integrator holding the whole film stalled.** The same 5 gags failed 2 rounds running while its context grew past 450k tokens. The fix was splitting the work: one beat director per gag, each owning a `beats/<name>.json` override on a locked timeline (same shot ids and f_in/f_out), each with fresh context. scene.py merges them.
32. **Lock the timeline (voice, shot boundaries) before the parallel beat work,** so agents can't collide.
33. **Captions:** the reference sits at about 70% of the height, and a full-res measurement matters (cap height about 52 px).

34. **Characters and props linger in other sets** (Marcel stood in the insert set and filled a close-up). Every shot should place off-screen anyone it doesn't use, and hide props per shot (`hide_props`).
35. **Big close-ups make props read wrong** (the opener read as a cannon tube). A 3/4 high angle that shows the whole silhouette reads as the object.

36. **A defect that shows up in many beats is a RIG bug, not a shot bug.** "The hat covers the face on forward leans" turned up in the hook, the pan, the clang and the betrayed shot. Fix it once in chars.py (counter-rotate the head, net pitch at most 8°) instead of 4 directors working around it.
37. **The gag prop goes in the character's hands,** next to the face. A prop on the ground beside a character reads as unrelated.
38. **Relative OUTDIR paths in scene.py resolve to C:\.** Always pass absolute paths.

39. **Archive every round's render** (`out\rounds\rN-criticX.mp4`). Round 1 (4.2) was overwritten, and the tutorial needs every "before". Only the critic's 4 fps frames survived.

40. **Grep for every place that destroys shared state** (`constraints.clear()` and `remove` on a shared prop) before blaming the shot. The can-hold bug lived in 2 places and blocked 3 beats.
41. **Check my own clock with Get-Date before every ETA.** I ran about 1 h ahead of the real time for part of the afternoon.

42. **A transition belongs to the NEXT shot** (`transition_in`), so its blur eats the end of the previous director's shot. Beat boundaries need an owner for the cut between them; default to hard cuts at beat edges.

43. **Anchors must be immutable.** `HOME[('can','camp')]` gets overwritten mid-build by the tree gag's fly_to, so camrel in camp was relative to the wrong point. The knife director baked a compensation in. For the next build, snapshot anchors before the shot loop and never mutate them.

## Round 6 critic (7.6/10, +0.3 a round: a plateau again)
44. **When gains drop to about 0.3 a round, look for a systemic lever, not more shot fixes.** We rendered at 720×1280 and upscaled, so "detail" was capped (934 vs the reference's 1591). Native 1080×1920 gave +43% edge energy on the same frame. Render at the delivery resolution from day 1.
45. **"Characters go still between beats" is a rig-layer fix** (an automatic idle sway plus word-driven head bobs), not 6 directors keying it by hand.

46. **Parallel render processes must never write the same temp file.** acting_merged.json was raced by 3 Blender processes, and one read a half-written file and crashed. Name temp files per process (pid), or write them once before launching the shards.

47. **A holistic critic misses proportions.** Measurement found bodies at 2.6 HH vs the reference's 3.2, ink at 2.6% vs 6.6% of head width, and cuts every 1.4 s vs 2.8 s, after 7 critic rounds never flagged them. Run a numeric character and edit audit (head heights, ink %, cut rate) at the START, not just a rubric score.

48. **Changing character proportions late breaks every hand-set camera** (camrel). Lock the proportions BEFORE directing beats. When forced to change them, fan the crop fixes out to the beat owners in parallel, after one native stills check.

## Pipeline
11. **libass can't load woff2 fonts.** Use a system TTF (Arial Black) for heavy captions.
12. **ElevenLabs eleven_v4 ignores `speed`.** Fit the timing by tightening the script plus a delivery tag, and use only light atempo.
13. **Split render plus splice works:** re-render only the bad frame ranges (3 processes, about 1 s per frame at 720p and 12 samples).
14. **Parallel agents need separate files and a contract.** Each agent writes only its own files.

## Round 8 critic (7.8/10 on r10, +0.0)
49. **A big rig change (proportions, ink) moves the score only if every shot is re-checked for its side effects.** The gags gained and the new crops (chef face turned away, can at 7% on the pop) cost the same. Thicker ink raised detail just 12%; the flat planes (grass, tent walls, floor) are the real detail gap. Next lever: surface detail in the world, not lines.
50. **The critic's "known suspects" list works:** 3 of 4 were confirmed and 1 cleared (the 44 s "blur" was wood grain). Always hand the critic my own suspicions to verify.

## Frame-accurate re-measurement (4 reference videos, every frame; numbers in reference-style.md)
51. **A 1 fps reference sheet gives wrong targets.** On the same video (`7xS87iActkU`) every-frame measurement found SATAVG 31.4, not 41.9, and a picture shot every 4.34 s, not "cuts every 2.8 s". At 1 fps, 8-frame dissolves and 4-frame inserts are invisible, and size changes inside camera moves look like cuts. Measure references with `measure/` at full frame rate. This supersedes the contract's "saturation ≥ 38" and the cut rate in lesson 47.
52. **The reference never whips and never dips to black.** 52 of 56 transitions across four videos are crossfades of 6–10 frames (median 8), with the camera moving on both sides. There are 3 hard cuts and 0 whips, and luma never dips. This supersedes lesson 7 (6-frame whips), lesson 42 ("default to hard cuts at beat edges") and the contract's "travel, whip or dissolve". Render dissolves with `DISSOLVE=cross`.
53. **Wides are not dead air in the reference: they fill 36% of its screen time.** Extreme wides hold longest (median 51 frames), because the camera travels through the place. Lesson 8's dead air came from static wides. The fix is a moving camera, not fewer wides.
54. **Big faces belong to close shots only.** Heads at 30–40% of the frame happen in CU and MCU, which are 13.5% of screen time. Full shots dominate at 27%. This supersedes rubric criterion 2 ("head ≥ 30% in ≥ 70% of frames").
55. **Shot-size variety comes from camera moves.** 77% of the reference's size changes happen inside one continuous move, about every 1.35 s and mostly one step at a time. The camera is still on only 4–21% of frames. Lesson 17's "the camera is mostly calm" was a 1 fps impression: the moves are smooth, not absent. Write them as camera keys with `size`.
56. **The 60 s example is furthest from the reference on edit numbers.** It has 39 shots in 60 s (1.55 s each, against 4.3 s), 31 hard cuts, 4 whips, no wides and 4 sets (against about 9 locations). Use it as a schema example only.
57. **Night is bright and saturated in the reference.** Night frames have YAVG 69–118 (median 85) and are the most saturated mood (SATAVG median 49, blue). The old night band of 50–65 forced the image too dark, which then had to be lifted by saturation (lessons 1–4). Interiors sit at YAVG 67–139 and SATAVG 19–35. `gate.py` BAND now uses the measured p10–p90. The example project's night look (`look.MOODS['night']`, exp 0.12) was tuned to the old band, so its night shots now fail the gate until the night exposure/gain is lifted (`tune.sh` / `LOOK_TUNE`) and re-checked against the reference stills.
58. **Captions:** line centre at 70.2%, not 68%; cap top 1,321 px and baseline 1,376 px at 1080×1920. There is no pop-in: the 80→100% scale was ours, not the reference's. Punctuation is kept, 75% of cards are one word, and each card holds until the next, so a caption is on every frame. `finish.mjs` now does all of this.
59. **The narration is faster than the old cap.** It runs at 3.75 words per second (3.35–3.91), against our cap of 3; 60 s is 220–245 words.
60. **Audit the render against the measurement in one run:** `python3 audit.py` (`python audit.py` on Windows). It checks the edit, size mix, camera motion, colour per mood, caption position and caption timing. All four reference videos pass it.
61. **Lesson 33 confirmed:** the cap height is 54 px at 1080, and the caption geometry is identical to the pixel across all four videos.
62. **About one location change in five has no cut.** The camera flies from one place to the next (R4 does it 6 times). In this engine a shot cannot cross sets (they sit 300 m apart), so build the two places as areas of ONE set with the camera path between them. Mark the key where the new place takes over with `loc`, so `audit.py` counts it.
