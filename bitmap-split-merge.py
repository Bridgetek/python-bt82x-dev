# Typical command line:
# python bitmap-split-merge.py --connector ft4222module split/merge
import sys
import argparse
from PIL import Image
import numpy as np
import zlib


# This module provides the connector (gd) to the EVE hardware.
import apprunner

# Target EVE device.
family = "BT82x"

# EVE family support check.
device_families = ["FT80x", "FT81x", "BT81x", "BT82x"]
assert(family in device_families)

if family == "BT82x":
    # This loads BT82x family definitions only.
    import bteve2 as eve
else:
    # This loads FT80x, FT81x, BT81x family definitions.
    import bteve as eve

def pad4(s):
    while len(s) % 4:
        s += b'\x00'
    return s

def iload(self, a, plain):
    self.cmd_inflate(a, 0)
    self.cc(pad4(zlib.compress(plain)))

def dith(w, h):
    return np.tile(np.concatenate((
        np.tile(np.array([0, 2]), (w+1) // 2)[:w],
        np.tile(np.array([3, 1]), (w+1) // 2)[:w]
    )), (h+1) // 2)[:w*h]

colorfmts = {
    eve.RGB565 :   (0, 5, 6, 5)
    }

def convert(im, fmt, dither = False):
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

def oe_split(gd, dst0, dst1, src):
    gd.cmd_rendertarget(*dst0)
    gd.cmd_setbitmap(*src)
    gd.BlendFunc(eve.SRC_ALPHA, eve.ZERO)
    gd.Begin(eve.BITMAPS)
    gd.BitmapTransformA(0, 0x200)       # Shrink 2x
    gd.Vertex2f(0, 0)
    gd.Display()
    gd.cmd_swap()

    gd.cmd_dlstart()
    gd.cmd_rendertarget(*dst1)
    gd.BlendFunc(eve.SRC_ALPHA, eve.ZERO)
    gd.Begin(eve.BITMAPS)
    gd.BitmapTransformA(0, 0x200)       # Shrink 2x
    gd.BitmapTransformC(0x100)          # Offset 1 pixel
    gd.Vertex2f(0, 0)
    gd.Display()
    gd.cmd_swap()

def oe_merge(gd, dst, src0, src1):
    gd.cmd_rendertarget(*dst)

    scratch = 0x07d8_0000
    mask = eve.Surface(scratch, eve.L8, 2, 1)
    gd.cmd_regwrite(scratch, 0xff00)

    gd.cmd_setbitmap(*mask)
    gd.BitmapSize(eve.NEAREST, eve.REPEAT, eve.REPEAT, 0, 0)
    gd.BitmapSizeH(0, 0)

    gd.Clear(1, 1, 1)
    gd.Begin(eve.BITMAPS)

    gd.StencilFunc(eve.ALWAYS, 0xff, 0xff)
    gd.StencilOp(eve.REPLACE, eve.REPLACE)
    gd.AlphaFunc(eve.NOTEQUAL, 0)
    gd.Vertex2f(0, 0)

    gd.StencilMask(0)
    gd.BlendFunc(eve.SRC_ALPHA, eve.ZERO)
    gd.BitmapTransformA(0, 0x080)       # zoom 2x

    for (i, src) in enumerate((src0, src1)):
        gd.cmd_setbitmap(*src)
        gd.BitmapSize(eve.NEAREST, eve.BORDER, eve.BORDER, 0, 0)
        gd.BitmapSizeH(0, 0)
        gd.StencilFunc(eve.EQUAL, i, 1)
        gd.Vertex2f(0, 0)

    gd.Display()
    gd.cmd_swap()

def bitmap_split(gd):
    (w, h) = (1024, 800)
    im0 = Image.open("assets/oe_AB.png").resize((2 * w, h))

    fmt = eve.RGB565
    block_addr = 0x400000       # allocate 4MB per block
    src = eve.Surface(block_addr * 5, fmt, 2 * w, h)
    dst0 = eve.Surface(block_addr * 6, src.fmt, w, h)
    dst1 = eve.Surface(block_addr * 7, src.fmt, w, h)

    iload(gd, src.addr, convert(im0, src.fmt))

    oe_split(gd, dst0, dst1, src)
    gd.cmd_graphicsfinish()
    gd.finish()

    gd.cmd_dlstart()
    gd.Clear(1, 1, 1)
    framebuffer = eve.Surface(eve.SWAPCHAIN_0, eve.RGB6, 1920, 1200)
    gd.cmd_rendertarget(*framebuffer)
    gd.VertexFormat(0) # integer coordinates
    gd.Begin(eve.BITMAPS)
    gd.cmd_setbitmap(*dst0)
    gd.Vertex2f(0, 0)

    gd.cmd_setbitmap(*dst1)
    gd.Vertex2f(1024, 0)
    gd.swap()
    gd.finish()

def bitmap_merge(gd):
    (w, h) = (1024, 800)
    im0 = Image.open("assets/oe_A.png").resize((w, h))
    im1 = Image.open("assets/oe_B.png").resize((w, h))

    fmt = eve.RGB565
    block_addr = 0x400000       # allocate 4MB per block
    src0 = eve.Surface(block_addr * 5, fmt, w, h)
    src1 = eve.Surface(block_addr * 6, fmt, w, h)
    dst = eve.Surface(block_addr * 7, fmt, 2 * w, h)

    iload(gd, src0.addr, convert(im0, fmt))
    iload(gd, src1.addr, convert(im1, fmt))

    oe_merge(gd, dst, src0, src1)
    gd.cmd_graphicsfinish()
    gd.finish()

    gd.cmd_dlstart()
    gd.Clear(1, 1, 1)
    framebuffer = eve.Surface(eve.SWAPCHAIN_0, eve.RGB6, 1920, 1200)
    gd.cmd_rendertarget(*framebuffer)
    gd.VertexFormat(0) # integer coordinates
    gd.Begin(eve.BITMAPS)
    gd.cmd_setbitmap(*dst)
    gd.Vertex2f(0, 0)
    gd.swap()
    gd.finish()

def bitmap_main(gd):
    parser = argparse.ArgumentParser(description="EVE bitmap split/merge demo")
    parser.add_argument("option", help="option to run")
    args = parser.parse_args(sys.argv[1:])

    # Convert input [option] to uppercase
    option = args.option.upper()

    if option == "SPLIT":
        # Split bitmap
        bitmap_split(gd)
    elif option == "MERGE":
        # Merge bitmap
        bitmap_merge(gd)
    else:
        print("Invalid option. Use 'split' or 'merge'.")

apprunner.run(bitmap_main)
