# Typical command line:
# python bitmap-split.py --connector ft4222module
import sys
from PIL import Image
import numpy as np
import zlib

# Add the library directories to the module search path.
sys.path.append('../..')
sys.path.append('../../bteve2')

import bteve2

# This module provides the connector to the EVE hardware.
import apprunner

def pad4(s):
    while len(s) % 4:
        s += b'\x00'
    return s

def iload(self, a, plain):
    self.CMD_INFLATE(a, 0)
    self.cc(pad4(zlib.compress(plain)))

def dith(w, h):
    return np.tile(np.concatenate((
        np.tile(np.array([0, 2]), (w+1) // 2)[:w],
        np.tile(np.array([3, 1]), (w+1) // 2)[:w]
    )), (h+1) // 2)[:w*h]

def convert(eve, im, fmt, dither = False):
    colorfmts = {
        eve.FORMAT_RGB565 :   (0, 5, 6, 5)
    }

    dd = dith(*im.size)
    sizes = colorfmts[fmt][::-1]
    bpp = sum(sizes)
    cs = [np.frombuffer(c.tobytes(), np.uint8).astype(np.uint32) for c in im.split()]

    xswiz = {
        1: 7,
        2: 3,
        4: 1,
    }.get(bpp, 0)

    # Arrange as B, G, R, A
    (b, g, r, a) = (0, 0, 0, 0)
    if im.mode in ("L", "P"):
        (b,) = cs
    elif im.mode == "LA":
        (b, a) = cs
    elif im.mode == "RGB":
        (r, g, b) = cs
    elif im.mode == "RGBA":
        (r, g, b, a) = cs
    cs = [b, g, r, a]
    p = 0
    w = np.zeros_like(cs[0], dtype=np.uint32)  # Ensure w is uint32
    for c, s in zip(cs, sizes):
        df = dither * {1: 32, 2: 16, 3: 8, 4: 4, 5: 2, 6: 1}.get(s, 0)
        dc = np.minimum(255, c + df * dd).astype(np.uint32)
        w |= (dc >> (8 - s)) << p
        p += s

    nb = bpp * len(w)
    indices = np.arange(nb, dtype=np.uint32)

    # Ensure indices are valid and of the correct type
    wi = ((indices // bpp) ^ xswiz).astype(np.uint32)
    wb = (indices % bpp).astype(np.uint32)

    # Use numpy's advanced indexing instead of take
    res = ((w[wi] >> wb) & 1).astype(np.uint32)

    bits = indices.astype(np.uint8) & 7
    bb = (res << bits).reshape((len(indices) // 8, 8)).sum(1).astype(np.uint8).tobytes()

    return bb

def oe_split(eve, dst0, dst1, src):
    eve.CMD_RENDERTARGET(*dst0)
    eve.CMD_SETBITMAP(*src)
    eve.BLEND_FUNC(eve.BLEND_SRC_ALPHA, eve.BLEND_ZERO)
    eve.BEGIN(eve.BEGIN_BITMAPS)
    eve.BITMAP_TRANSFORM_A(0, 0x200)       # Shrink 2x
    eve.VERTEX2F(0, 0)
    eve.DISPLAY()
    eve.CMD_SWAP()

    eve.CMD_DLSTART()
    eve.CMD_RENDERTARGET(*dst1)
    eve.BLEND_FUNC(eve.BLEND_SRC_ALPHA, eve.BLEND_ZERO)
    eve.BEGIN(eve.BEGIN_BITMAPS)
    eve.BITMAP_TRANSFORM_A(0, 0x200)       # Shrink 2x
    eve.BITMAP_TRANSFORM_C(0x100)          # Offset 1 pixel
    eve.VERTEX2F(0, 0)
    eve.DISPLAY()
    eve.CMD_SWAP()

def bitmap_split(eve):
    (w, h) = (1024, 800)
    im0 = Image.open("assets/oe_AB.png").resize((2 * w, h))

    fmt = eve.FORMAT_RGB565
    block_addr = 0x400000       # allocate 4MB per block
    src = bteve2.Surface(block_addr * 5, fmt, 2 * w, h)
    dst0 = bteve2.Surface(block_addr * 6, src.fmt, w, h)
    dst1 = bteve2.Surface(block_addr * 7, src.fmt, w, h)

    eve.LIB_BeginCoProList()
    iload(eve, src.addr, convert(eve, im0, src.fmt))

    oe_split(eve, dst0, dst1, src)
    eve.CMD_GRAPHICSFINISH()
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()

    eve.LIB_BeginCoProList()
    eve.CMD_DLSTART()
    eve.CLEAR(1, 1, 1)
    framebuffer = bteve2.Surface(eve.SWAPCHAIN_0, eve.FORMAT_RGB6, 1920, 1200)
    eve.CMD_RENDERTARGET(*framebuffer)
    eve.VERTEX_FORMAT(0) # integer coordinates
    eve.BEGIN(eve.BEGIN_BITMAPS)
    eve.CMD_SETBITMAP(*dst0)
    eve.VERTEX2F(0, 0)

    eve.CMD_SETBITMAP(*dst1)
    eve.VERTEX2F(1024, 0)
    eve.DISPLAY()
    eve.CMD_SWAP()
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()

apprunner.run(bitmap_split)
