# Typical command line:
# python bitmap-crop.py --connector ft4222module
import sys

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

def crop(eve, dst, src, x, y):
    eve.CMD_DLSTART()
    eve.CMD_RENDERTARGET(*dst)

    eve.CMD_SETBITMAP(*src)
    eve.BLEND_FUNC(eve.BLEND_ONE, eve.BLEND_ZERO)
    eve.BEGIN(eve.BEGIN_BITMAPS)
    eve.VERTEX_FORMAT(0)
    eve.VERTEX2F(-x, -y)
    eve.CMD_SWAP()
    eve.CMD_GRAPHICSFINISH()
    eve.LIB_AwaitCoProEmpty()

def image_crop(eve):
    source_image = "assets/paris-1280.png"
    block_addr = 0x400000       # allocate 4MB for base image
    src = bteve2.Surface(0, eve.FORMAT_RGB565, 1280, 720)
    eve.LIB_BeginCoProList()
    eve.BEGIN(eve.BEGIN_BITMAPS)
    eve.BITMAP_HANDLE(0)
    # Tell coprocessor to load image from the SPI interface
    eve.CMD_LOADIMAGE(src.addr, 0)
    # Load the original image from the host hard disk
    eve.cc(pad4(open(source_image, "rb").read()))
    eve.CMD_SETBITMAP(*src)
    eve.DISPLAY()
    eve.CMD_SWAP()
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()

    # start cropped images after base image allocation
    buf_addr = block_addr
    dst = bteve2.Surface(buf_addr, eve.FORMAT_RGB565, 320, 180)

    for x in range(0, 1280, 320):
        for y in range(0, 720, 180):
            crop(eve, dst, src, x, y)
            # adjust to next address
            dst = bteve2.Surface(dst.addr + (320 * 180 * 2), dst.fmt, dst.w, dst.h)

    # restore address
    dst = bteve2.Surface(buf_addr, dst.fmt, dst.w, dst.h)

    eve.LIB_BeginCoProList()
    eve.CMD_DLSTART()
    eve.CLEAR()
    framebuffer = bteve2.Surface(eve.SWAPCHAIN_0, eve.FORMAT_RGB6, 1920, 1200)
    eve.CMD_RENDERTARGET(*framebuffer)
    eve.VERTEX_FORMAT(0) # integer coordinates
    eve.BEGIN(eve.BEGIN_BITMAPS)
    eve.BITMAP_HANDLE(0)
    eve.CMD_SETBITMAP(*src)
    eve.VERTEX2F(220, 210)

    # assign a bitmap handle and reuse it for each cropped image
    eve.BITMAP_HANDLE(1)
    
    # top 4
    eve.CMD_SETBITMAP(dst.addr, eve.FORMAT_RGB565, 320, 180)
    eve.VERTEX2F(100, 0)

    eve.CMD_SETBITMAP(dst.addr + (4 * 320 * 180 * 2), eve.FORMAT_RGB565, 320, 180)
    eve.VERTEX2F(500, 0)

    eve.CMD_SETBITMAP(dst.addr + (8 * 320 * 180 * 2), eve.FORMAT_RGB565, 320, 180)
    eve.VERTEX2F(900, 0)

    eve.CMD_SETBITMAP(dst.addr + (12 * 320 * 180 * 2), eve.FORMAT_RGB565, 320, 180)
    eve.VERTEX2F(1300, 0)

    # bottom 4
    eve.CMD_SETBITMAP(dst.addr + (3 * 320 * 180 * 2), eve.FORMAT_RGB565, 320, 180)
    eve.VERTEX2F(100, 960)

    eve.CMD_SETBITMAP(dst.addr + (7 * 320 * 180 * 2), eve.FORMAT_RGB565, 320, 180)
    eve.VERTEX2F(500, 960)

    eve.CMD_SETBITMAP(dst.addr + (11 * 320 * 180 * 2), eve.FORMAT_RGB565, 320, 180)
    eve.VERTEX2F(900, 960)

    eve.CMD_SETBITMAP(dst.addr + (15 * 320 * 180 * 2), eve.FORMAT_RGB565, 320, 180)
    eve.VERTEX2F(1300, 960)

    # side 2
    eve.CMD_SETBITMAP(dst.addr + (13 * 320 * 180 * 2), eve.FORMAT_RGB565, 320, 180)
    eve.VERTEX2F(1530, 370)

    eve.CMD_SETBITMAP(dst.addr + (14 * 320 * 180 * 2), eve.FORMAT_RGB565, 320, 180)
    eve.VERTEX2F(1530, 590)

    eve.DISPLAY()
    eve.CMD_SWAP()
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()

apprunner.run(image_crop)
