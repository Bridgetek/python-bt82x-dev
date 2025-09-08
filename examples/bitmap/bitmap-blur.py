# Typical command line:
# python bitmap-blur.py --connector ft4222module
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

    source_image = "assets/paris-1280.png"
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

    eve.LIB_BeginCoProList()
    eve.CMD_DLSTART()
    eve.CLEAR()
    eve.VERTEX_FORMAT(0) # integer coordinates
    eve.BEGIN(eve.BEGIN_BITMAPS)
    eve.BITMAP_HANDLE(0)
    # Draw original image (unblurred at this stage)
    eve.VERTEX2F(220, 210)
    
    # Draw a blurred representation of the screen at the current point in the display commands
    eve.CMD_GRAPHICSFINISH()
    eve.CMD_BLURSCREEN()
    eve.CMD_BLURDRAW()
    # Continue drawing over the blurred screen
    eve.VERTEX_FORMAT(0) # important: integer coordinates

    # Draw a smaller version of the image over the blurred image
    eve.CMD_LOADIDENTITY()
    # Half the size of the original image
    eve.CMD_SCALE(32768, 32768)
    eve.CMD_SETMATRIX()
    # Draw resized image in center of original image
    eve.VERTEX2F(220 + (1920//6), 210 + (720//4))

    eve.DISPLAY()
    if TAKE_SCREENSHOT:
        status = eve.LIB_FSSnapShot(0x400000, "paris.bmp", 0)
        assert status == 0, "SD card couldn't be written"
    
    eve.CMD_SWAP()
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()

apprunner.run(blur, patch)
