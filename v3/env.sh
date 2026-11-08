# sourced by every script: sets HERE (project folder), BL (Blender 5.x), PY (python 3) and abspath().
# Windows (Git Bash), macOS and Linux. Override Blender with BLENDER=/path/to/blender
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -n "$BLENDER" ]; then BL="$BLENDER"
else
  case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*) BL="$(ls -d "/c/Program Files/Blender Foundation/Blender 5."*/blender.exe 2>/dev/null | sort -V | tail -1)";;
    Darwin) BL="$(ls -d /Applications/Blender*.app/Contents/MacOS/Blender "$HOME"/Applications/Blender*.app/Contents/MacOS/Blender 2>/dev/null | sort -V | tail -1)";;
    *) BL="$(command -v blender)";;
  esac
fi
[ -x "$BL" ] || { echo "Blender 5.x not found. Install it or set BLENDER=/path/to/blender"; exit 1; }
# python: $PYTHON, else the first of python / python3 / py that really runs (skips the Windows Store stub)
PY="$PYTHON"
if [ -z "$PY" ]; then for c in python python3 py; do "$c" -c 'import sys' >/dev/null 2>&1 && { PY="$(command -v "$c")"; break; }; done; fi
[ -n "$PY" ] || { echo "Python 3 not found. Install it or set PYTHON=/path/to/python"; exit 1; }
# Blender needs a native absolute path: C:/... on Windows (pwd -W), a normal path elsewhere
abspath() { if pwd -W >/dev/null 2>&1; then (cd "$1" && pwd -W); else (cd "$1" && pwd); fi; }
