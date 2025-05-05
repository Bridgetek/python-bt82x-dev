# Typical command line:
# python bitmap-crop.py --connector ft4222module
import sys
from PIL import Image

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

def crop(gd, dst, src, x, y):
    gd.cmd_dlstart()
    gd.cmd_rendertarget(*dst)

    gd.cmd_setbitmap(*src)
    gd.BlendFunc(eve.ONE, eve.ZERO)
    gd.Begin(eve.BITMAPS)
    gd.VertexFormat(0)
    gd.Vertex2f(-x, -y)
    gd.swap()
    gd.cmd_graphicsfinish()
    gd.finish()

def imagetest(gd):
    source_image = "assets/paris-1280.png"
    src = eve.Surface(0, eve.RGB565, 1280, 720)
    gd.cmd_loadimage(src.addr, 0)
    gd.cc(pad4(open(source_image, "rb").read()))
    gd.finish()

    buf_addr = 4 << 20
    dst = eve.Surface(buf_addr, eve.RGB565, 320, 180)

    for x in range(0, 1280, 320):
        for y in range(0, 720, 180):
            crop(gd, dst, src, x, y)
            # adjust to next address
            dst = eve.Surface(dst.addr + (320 * 180 * 2), dst.fmt, dst.w, dst.h)

    # restore address
    dst = eve.Surface(buf_addr, dst.fmt, dst.w, dst.h)

    gd.cmd_dlstart()
    gd.Clear(1, 1, 1)
    framebuffer = eve.Surface(eve.SWAPCHAIN_0, eve.RGB6, 1920, 1200)
    gd.cmd_rendertarget(*framebuffer)
    gd.VertexFormat(0) # integer coordinates
    gd.Begin(eve.BITMAPS)
    gd.cmd_setbitmap(*src)
    gd.Vertex2f(220, 210)

    # top 4
    gd.cmd_setbitmap(dst.addr, eve.RGB565, 320, 180)
    gd.Vertex2f(100, 0)

    gd.cmd_setbitmap(dst.addr + (4 * 320 * 180 * 2), eve.RGB565, 320, 180)
    gd.Vertex2f(500, 0)

    gd.cmd_setbitmap(dst.addr + (8 * 320 * 180 * 2), eve.RGB565, 320, 180)
    gd.Vertex2f(900, 0)

    gd.cmd_setbitmap(dst.addr + (12 * 320 * 180 * 2), eve.RGB565, 320, 180)
    gd.Vertex2f(1300, 0)

    # bottom 4
    gd.cmd_setbitmap(dst.addr + (3 * 320 * 180 * 2), eve.RGB565, 320, 180)
    gd.Vertex2f(100, 960)

    gd.cmd_setbitmap(dst.addr + (7 * 320 * 180 * 2), eve.RGB565, 320, 180)
    gd.Vertex2f(500, 960)

    gd.cmd_setbitmap(dst.addr + (11 * 320 * 180 * 2), eve.RGB565, 320, 180)
    gd.Vertex2f(900, 960)

    gd.cmd_setbitmap(dst.addr + (15 * 320 * 180 * 2), eve.RGB565, 320, 180)
    gd.Vertex2f(1300, 960)

    # side 2
    gd.cmd_setbitmap(dst.addr + (13 * 320 * 180 * 2), eve.RGB565, 320, 180)
    gd.Vertex2f(1530, 370)

    gd.cmd_setbitmap(dst.addr + (14 * 320 * 180 * 2), eve.RGB565, 320, 180)
    gd.Vertex2f(1530, 590)

    gd.Display()
    gd.swap()

apprunner.run(imagetest)
