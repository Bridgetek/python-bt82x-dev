# Typical command line:
# python simple2.py --connector ft4222module
import sys
import argparse

# Add the library directories to the module search path.
sys.path.append('../..')
sys.path.append('../../bteve2')

# This module provides the connector to the EVE hardware.
import apprunner

import simplefont
import simpleimage

font_custom = 8
logo_handle =  7

def eve_display(eve):
    counter = 0
    key = 0
    keyprev = 0
    units = 1
        
    while True:
        # Start drawing test screen.
        eve.LIB_BeginCoProList()
        eve.CMD_DLSTART()
        eve.CLEAR_COLOR_RGB(0, 0, 0)
        eve.CLEAR(1,1,1)
        eve.COLOR_RGB(255, 255, 255)
        
        eve.BEGIN(eve.BEGIN_BITMAPS)
        eve.BITMAP_HANDLE(logo_handle)
        # Set origin on canvas using eve.VERTEX_TRANSLATE.
        eve.VERTEX_TRANSLATE_X(((eve.EVE_DISP_WIDTH // 2)-(simpleimage.eve_img_bridgetek_logo_width // 2)) * 16)
        eve.VERTEX_TRANSLATE_Y(((eve.EVE_DISP_HEIGHT // 4)-(simpleimage.eve_img_bridgetek_logo_height // 2)) * 16)
        eve.VERTEX2II(0, 0, logo_handle, 0)
        eve.VERTEX_TRANSLATE_X(0)
        eve.VERTEX_TRANSLATE_Y(0)
        eve.CMD_TEXT(eve.EVE_DISP_WIDTH/2, simpleimage.eve_img_bridgetek_logo_height * 8,
                    32, eve.OPT_CENTERX, "Touch the counter")

        eve.TAG(100)

        eve.COLOR_RGB(255, 0, 0)

        eve.BEGIN(eve.BEGIN_BITMAPS)

        eve.VERTEX_TRANSLATE_Y((eve.EVE_DISP_HEIGHT / 2) * 16)

        units = 1
        for i in range(0, 5):
            eve.VERTEX_TRANSLATE_X((((eve.EVE_DISP_WIDTH - (simplefont.font_width_in_pixels * 5)) / 2) - (simplefont.font_width_in_pixels) + (simplefont.font_width_in_pixels * (5 - i))) * 16)
            eve.VERTEX2II(0, 0, font_custom, ((counter / units) % 10)+1) # +1 as in the converted font the number '0' is in position 1 in the font table
            units *= 10
        eve.VERTEX_TRANSLATE_X(0)

        # copy/backup the list from current working display buffer to RAM_G addr 0x100
        eve.CMD_COPYLIST(0x100)
        eve.DISPLAY()
        eve.CMD_SWAP()      # swap to the other display buffer

        # copy the list from RAM_G addr 0x100 to the new working display buffer
        eve.CMD_DLSTART()
        eve.CMD_CALLLIST(0x100)
        eve.DISPLAY()
        eve.CMD_SWAP()

        eve.LIB_EndCoProList()
        eve.LIB_AwaitCoProEmpty()

        while True:
            eve.LIB_BeginCoProList()
            eve.CMD_SWAP()
            eve.LIB_EndCoProList()
            eve.LIB_AwaitCoProEmpty()
            # Read the tag register on the device
            key = eve.rd32(eve.REG_TOUCH_TAG)

            # Debounce keys.
            if (key != keyprev):
                keyprev = key

                if (key == 100):
                    counter += 1
                    break

def simple(eve):
    font_end = None

    # Calibrate the display
    print("Calibrating display...\n")
    # Calibrate screen if necessary. 
    eve.LIB_AutoCalibrate()

    # Load fonts and images
    print("Loading font...")
    font_end = simplefont.eve_init_fonts(eve, font_custom)
    print("Loading images...")
    simpleimage.eve_load_images(eve, font_end, logo_handle)

    # Start example code
    print("Starting demo:")
    eve_display(eve)

apprunner.run(simple)
