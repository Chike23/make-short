#!/bin/bash
# sheet.sh clip.mp4 every out.png [w]
w=${4:-200}; h=$((w*16/9)); d=$(mktemp -d)
ffmpeg -v error -i "$1" -vf "select=not(mod(n\,$2)),scale=$w:$h" -vsync 0 $d/f_%03d.png
python3 -c "
from PIL import Image; import glob,sys
fs=sorted(glob.glob('$d/f_*.png')); cols=9; rows=(len(fs)+cols-1)//cols
s=Image.new('RGB',(cols*$w,rows*$h))
for i,f in enumerate(fs): s.paste(Image.open(f),((i%cols)*$w,(i//cols)*$h))
s.save('$3'); print(len(fs))"
