# Typical command line:
# python bitmap-blurimage.py --connector ft4222module
import sys

# Add the library directories to the module search path.
sys.path.append('../..')
sys.path.append('../../bteve2')

# Use the SD card and the fssnapshot extension to take a screenshot
TAKE_SCREENSHOT = 0

import bteve2

# This module provides the connector to the EVE hardware.
import apprunner
# Import the patch file required by this code.
import patch_blur as patch

def pad4(s):
    while len(s) % 4:
        s += b'\x00'
    return s

def blur(eve):
    if TAKE_SCREENSHOT:
        status = eve.LIB_SDAttach(eve.OPT_IS_SD)
        assert status == 0, "SD card not attached"

    source_image = "assets/felix.png"
    src = bteve2.Surface(0, eve.FORMAT_RGB565, 320, 200)
    dst = bteve2.Surface(0x400000, eve.FORMAT_RGB565, 320, 200)
    eve.LIB_BeginCoProList()
    eve.BEGIN(eve.BEGIN_BITMAPS)
    # Tell coprocessor to load image from the SPI interface
    eve.CMD_LOADIMAGE(src.addr, 0)
    # Load the original image from the host hard disk
    eve.cc(pad4(open(source_image, "rb").read()))

    eve.CMD_GRAPHICSFINISH()

    eve.BITMAP_HANDLE(0)
    eve.CMD_SETBITMAP(*src)

    # Draw a blurred representation of the screen at the current point in the display commands
    eve.CMD_BLURIMAGE(src.addr, dst.addr, eve.FORMAT_RGB565, 320, 200) 

    eve.BEGIN(eve.BEGIN_BITMAPS)
    eve.BITMAP_HANDLE(2)
    eve.CMD_SETBITMAP(*dst)

    eve.DISPLAY()
    eve.CMD_SWAP()
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()

    eve.LIB_BeginCoProList()
    eve.CMD_DLSTART()
    eve.CLEAR()
    eve.VERTEX_FORMAT(0) # integer coordinates
    eve.BEGIN(eve.BEGIN_BITMAPS)

    # Draw original image (unblurred at this stage)
    eve.BITMAP_HANDLE(0)
    eve.VERTEX2F(220, 210)

    # Draw blurred image in center of original image
    eve.BITMAP_HANDLE(2)
    eve.VERTEX2F(220, 210 + 200)

    eve.DISPLAY()
    if TAKE_SCREENSHOT:
        status = eve.LIB_FSSnapShot(0x800000, "felix.bmp", 0)
        assert status == 0, "SD card couldn't be written"

    eve.CMD_SWAP()
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()

apprunner.run(blur, patch)
