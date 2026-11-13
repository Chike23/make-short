"""style_compare.py: reference frames above, the style test stills below, in one picture for the judge and the user.
    python3 tools/style_compare.py <style-name> <test_dir> [frame numbers...]  -> styles/<style-name>/compare.png"""
import glob, os, sys
from PIL import Image, ImageDraw
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
name, test = sys.argv[1], sys.argv[2]
sd = os.path.join(P, 'styles', name)
refs = sorted(glob.glob(os.path.join(sd, 'frames', '*.png')))
pick = [int(x) for x in sys.argv[3:]] or [int(i * (len(refs) - 1) / 3) for i in range(4)]
tops = [refs[i] for i in pick if i < len(refs)][:4]
bots = sorted(glob.glob(os.path.join(test, 't[0-9]_*.png')))[:4]
w, h = 270, 480
c = Image.new('RGB', (w * 4, h * 2 + 40), (20, 20, 20)); d = ImageDraw.Draw(c)
for i, f in enumerate(tops): c.paste(Image.open(f).convert('RGB').resize((w, h)), (i * w, 20))
for i, f in enumerate(bots): c.paste(Image.open(f).convert('RGB').resize((w, h)), (i * w, h + 40))
d.text((6, 4), 'reference', fill=(255, 255, 255)); d.text((6, h + 24), 'style test', fill=(255, 255, 255))
dst = os.path.join(sd, 'compare.png'); c.save(dst); print(dst)
