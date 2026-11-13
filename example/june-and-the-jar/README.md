# Example: "June and the jar" (62 s, 16 shots, 8 places)

At sixty-two, June can't open a jar of pickles. Muscle fades after forty; the stairs, the shopping and the sofa get harder; a fall; her doctor prescribes lifting; the gym; she rebuilds; at the end she opens the jar her son couldn't. Narrated by ElevenLabs "Brian", fitted to 3.75 words a second.

**Use it to learn the kit.** Every pattern a film needs is in `film.py`:
- word-timed acting with `big()`;
- walks, climbs and jogs on ground functions;
- held props that stay upright;
- an X-ray reveal with muscles that shrink and grow;
- a fall with a hit-stop;
- a time-lapse;
- two-shots for reactions;
- camera keys under the move-and-drift grammar.

**Try it.**
1. `python3 SKILL/tools/new_project.py june-example --example`, then `cd ~/shorts/june-example`.
2. `python3 tools/chain.py check`, then `python3 tools/plan_check.py`.
3. `python3 tools/chain.py preview`, then `python3 tools/assemble.py preview`, then `node voice/finish.mjs out/preview-silent.mp4`.

**History.** The film was first rendered with a spline camera, and its framing was MS-heavy: 46–50% MS, 13% wides. Its camera keys were then re-planned to the house size mix: every place opens wide, FS is home, and MS is passed through. Its colour fixes are in `grade_fix.json`. The notes from that first render are in `SKILL/references/lessons.md` (63–74).
