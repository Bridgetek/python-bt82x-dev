# Typical command line:
# python bitmap-merge.py --connector ft4222module
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

def oe_merge(eve, dst, src0, src1):
    eve.CMD_RENDERTARGET(*dst)

    scratch = eve.ramgtop # maximum allowable address in RAM_G
    mask = bteve2.Surface(scratch, eve.FORMAT_L8, 2, 1)

    eve.CMD_SETBITMAP(*mask)
    eve.BITMAP_SIZE(eve.FILTER_NEAREST, eve.WRAP_REPEAT, eve.WRAP_REPEAT, 0, 0)
    eve.BITMAP_SIZE_H(0, 0)

    eve.CLEAR()
    eve.BEGIN(eve.BEGIN_BITMAPS)

    eve.STENCIL_FUNC(eve.TEST_ALWAYS, 0xff, 0xff)
    eve.STENCIL_OP(eve.STENCIL_REPLACE, eve.STENCIL_REPLACE)
    eve.ALPHA_FUNC(eve.TEST_NOTEQUAL, 0)
    eve.VERTEX2F(0, 0)
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()

    eve.LIB_BeginCoProList()
    eve.STENCIL_MASK(0)
    eve.BLEND_FUNC(eve.BLEND_SRC_ALPHA, eve.BLEND_ZERO)
    eve.BITMAP_TRANSFORM_A(0, 0x080)       # zoom 2x

    for (i, src) in enumerate((src0, src1)):
        eve.CMD_SETBITMAP(*src)
        eve.BITMAP_SIZE(eve.FILTER_NEAREST, eve.WRAP_BORDER, eve.WRAP_BORDER, 0, 0)
        eve.BITMAP_SIZE_H(0, 0)
        eve.STENCIL_FUNC(eve.TEST_EQUAL, i, 1)
        eve.VERTEX2F(0, 0)

    eve.DISPLAY()
    eve.CMD_SWAP()

def bitmap_merge(eve):
    (w, h) = (1024, 800)
    im0 = Image.open("assets/oe_A.png").resize((w, h))
    im1 = Image.open("assets/oe_B.png").resize((w, h))

    fmt = eve.FORMAT_RGB565
    block_addr = 0x400000       # allocate 4MB per block
    src0 = bteve2.Surface(block_addr * 1, fmt, w, h)
    src1 = bteve2.Surface(block_addr * 2, fmt, w, h)
    dst = bteve2.Surface(block_addr * 3, fmt, 2 * w, h)

    eve.LIB_BeginCoProList()
    iload(eve, src0.addr, convert(eve, im0, fmt))
    iload(eve, src1.addr, convert(eve, im1, fmt))

    oe_merge(eve, dst, src0, src1)
    eve.CMD_GRAPHICSFINISH()
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()

    eve.LIB_BeginCoProList()
    eve.CMD_DLSTART()
    eve.CLEAR()
    framebuffer = bteve2.Surface(eve.SWAPCHAIN_0, eve.FORMAT_RGB6, 1920, 1200)
    eve.CMD_RENDERTARGET(*framebuffer)
    eve.BEGIN(eve.BEGIN_BITMAPS)
    eve.CMD_SETBITMAP(*dst)
    eve.VERTEX2F(0, 0)
    eve.CMD_SWAP()
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()

apprunner.run(bitmap_merge)
