#!/bin/bash
# keystills.sh -> gate/fNNNN.png for EVERY camera key of every shot (gate.sh only renders each shot's middle frame).
# Use it to check the framing of each size key (FS -> MS -> MCU inside one shot).
. "$(dirname "$0")/env.sh"; cd "$HERE"; mkdir -p gate
"$PY" -c "import json;S=json.load(open('shots.json'));print(' '.join(str(f) for s in S for f in [s['f_in']]+[k['f'] for k in s['camera'][1:-1]]+[s['f_out']-1]))" > gate/keys.txt
"$BL" -b -P scene.py -- list "$(abspath gate)" "$(abspath gate)/keys.txt" 2>&1 | grep -E "Traceback|Error"
echo "key stills: $(wc -w < gate/keys.txt) frames in gate/"
