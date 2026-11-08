#!/bin/bash
# save.sh -> scene.blend in the project folder: the built film, to open in a live Blender (Blender MCP) for looking and measuring.
# The scripts stay the source of truth: change shots.json / beats / lib, then run this again.
. "$(dirname "$0")/env.sh"; cd "$HERE"
"$BL" -b -P scene.py -- save "$(abspath .)" 2>&1 | grep -E "Traceback|Error"
ls -la scene.blend
