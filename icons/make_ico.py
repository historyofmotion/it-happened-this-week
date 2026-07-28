"""
Build favicon.ico by hand, embedding one PNG per size.

Pillow's ICO writer downscales a single source image, which loses the
per-size tuning. The ICO container happily holds PNG payloads, so we
render each size independently and pack them ourselves.
"""
import struct, io, os
from PIL import Image
import render as _r   # reuse the exact geometry

SIZES = [16, 32, 48, 64, 128, 256]

pngs = []
for s in SIZES:
    im = _r.render(s)
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    pngs.append(buf.getvalue())

out = io.BytesIO()
out.write(struct.pack("<HHH", 0, 1, len(SIZES)))          # ICONDIR
offset = 6 + 16 * len(SIZES)
for s, data in zip(SIZES, pngs):
    dim = 0 if s >= 256 else s                             # 0 means 256
    out.write(struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(data), offset))
    offset += len(data)
for data in pngs:
    out.write(data)

open("favicon.ico", "wb").write(out.getvalue())
print("favicon.ico written:", os.path.getsize("favicon.ico"), "bytes")
