"""
Render the It Happened This Week tally icon at every size we need.

Geometry mirrors favicon.svg exactly, on a 64-unit grid. Drawn at 4x and
downsampled with LANCZOS, because Pillow has no antialiased vector path —
supersampling is what buys us clean diagonals at 16px.
"""
from PIL import Image, ImageDraw

ACCENT = (180, 73, 31, 255)     # #b4491f
CREAM  = (250, 249, 247, 255)   # #faf9f7
SS     = 4                      # supersample factor

# unit geometry (64-grid)
VERTS   = [18, 27, 36, 45]
V_TOP, V_BOT = 18, 46
DIAG    = ((13, 47), (50, 17))
STROKE  = 5
RADIUS  = 14

# Optical size: below ~24px, four uprights plus a diagonal collapse into a
# blur. The small cut drops to three uprights with wider gaps and a heavier
# pen. It still reads unmistakably as a tally, which is the whole job.
VERTS_S  = [21, 32, 43]
DIAG_S   = ((15, 48), (49, 16))
STROKE_S = 6.5
RADIUS_S = 11

def stroke(d, p0, p1, w, fill):
    """A line with round caps — Pillow's line() caps are square, so we cap it ourselves."""
    d.line([p0, p1], fill=fill, width=int(round(w)))
    r = w / 2.0
    for (x, y) in (p0, p1):
        d.ellipse([x - r, y - r, x + r, y + r], fill=fill)

def render(px, scale=1.0, rounded=True, bg=ACCENT, simple=None):
    """scale shrinks the artwork inside the canvas (for maskable safe zones).
    simple=None auto-selects the small-size cut below 24px."""
    if simple is None:
        simple = px < 24
    verts  = VERTS_S  if simple else VERTS
    diag   = DIAG_S   if simple else DIAG
    strokew = STROKE_S if simple else STROKE
    radius = RADIUS_S if simple else RADIUS
    S = px * SS
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    if rounded:
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=radius / 64 * S, fill=bg)
    else:
        d.rectangle([0, 0, S - 1, S - 1], fill=bg)

    # unit -> pixel, with optional inset scaling about the centre
    def u(v):
        return (v - 32) * (S / 64) * scale + S / 2

    w = strokew * (S / 64) * scale
    for x in verts:
        stroke(d, (u(x), u(V_TOP)), (u(x), u(V_BOT)), w, CREAM)
    (x0, y0), (x1, y1) = diag
    stroke(d, (u(x0), u(y0)), (u(x1), u(y1)), w, CREAM)

    return img.resize((px, px), Image.LANCZOS)

# --- web / PWA ---
render(180, rounded=False).save("apple-touch-icon.png")   # iOS applies its own mask
render(192).save("icon-192.png")
render(512).save("icon-512.png")
render(512, scale=0.62, rounded=False).save("icon-512-maskable.png")  # 80% safe zone

# --- favicon.ico, multi-size ---
# Small sizes get a tighter corner radius or the rounding eats the artwork.
ico_sizes = [16, 32, 48, 64]
frames = [render(s) for s in ico_sizes]
frames[0].save("favicon.ico", format="ICO",
               sizes=[(s, s) for s in ico_sizes],
               append_images=frames[1:])

# --- a couple of PNG fallbacks some crawlers still want ---
render(32).save("favicon-32.png")
render(16).save("favicon-16.png")

print("rendered:")
import os
for f in sorted(os.listdir(".")):
    if f.endswith((".png", ".ico")):
        im = Image.open(f)
        print(f"  {f:28} {im.size[0]}x{im.size[1]}  {os.path.getsize(f):>6} bytes")
