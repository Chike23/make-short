"""paths.py: where the kit keeps shared assets (textures, Poly Haven downloads). One folder for every project.

    MAKESHORT_ASSETS   (environment variable) overrides the default ~/shorts/_assets
"""
import os

ASSETS = os.environ.get('MAKESHORT_ASSETS') or os.path.expanduser('~/shorts/_assets')
TEX = os.path.join(ASSETS, 'tex')                 # painted textures, generated once by sets.py (needs pillow + numpy)
POLYHAVEN = os.path.join(ASSETS, 'polyhaven')     # Poly Haven CC0 models, downloaded on first use by props_lib.py


def font(*names, size=100):
    """A TrueType font for texture text on any OS (the old code had Windows paths only)."""
    from PIL import ImageFont
    dirs = ['/System/Library/Fonts/Supplemental', '/System/Library/Fonts', '/Library/Fonts',
            os.path.expanduser('~/Library/Fonts'), 'C:/Windows/Fonts', '/usr/share/fonts/truetype/dejavu']
    for n in names + ('Arial Black.ttf', 'Arial Bold.ttf', 'arialbd.ttf', 'DejaVuSans-Bold.ttf'):
        for d in dirs:
            p = os.path.join(d, n)
            if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()
