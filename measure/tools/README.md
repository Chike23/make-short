# Quick passes (used for the anatomy-explainer measurement)
Lighter than the full per-frame review in `../README.md`. Run them from the folder that holds `r1/ … rN/` (each after `pipeline.py prep` and `small`). The reel lists and frame counts at the top of `editstats.py`, `zoomcheck.py`, `wordonsets.py` and `capstats.py` are the anatomy-explainer ones: edit them for a new reference.
- `transitions.py <dir>`: classifies cut candidates (crossfade, dip through dark, cut, slide/push, in-shot change, slow change) → `transitions.json`.
- `tmosaic.py <dir> <kinds> <out.jpg>`: frame strips of chosen transition kinds, to check by eye.
- `editstats.py`: shot lengths and transition mix across reels (set the verified slow changes in `REAL_SLOW`).
- `zoomcheck.py`: camera inside shots every 0.5 s (still / push-in / pull-out / pan, zoom rate).
- `wordonsets.py`: words a second, from new white words in word-by-word captions.
- `capstats.py`: caption coverage and how often a blue key-word box is on screen.
