# Typical command line:
# python simple.py --connector ft4232h standard
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
    key = False
    units = 1
        
    # Calibrate screen if necessary. 
    # Don't do this for now.
    #eve.LIB_AutoCalibrate()

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
    eve.VERTEX2II(0, 0, logo_handle, 0)
    eve.VERTEX_TRANSLATE_X(0)
    eve.CMD_TEXT(eve.EVE_DISP_WIDTH/2, simpleimage.eve_img_bridgetek_logo_height,
                28, eve.OPT_CENTERX, "Touch the counter")

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

    eve.DISPLAY()
    eve.CMD_SWAP()
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()

def simple(eve):
    font_end = None

    # Calibrate the display
    print("Calibrating display...\n")
    # Calibrate screen if necessary. 
    # Don't do this for now.
    #eve.LIB_AutoCalibrate()

    # Load fonts and images
    print("Loading font...")
    font_end = simplefont.eve_init_fonts(eve, font_custom)
    print("Loading images...")
    simpleimage.eve_load_images(eve, font_end, logo_handle)

    # Start example code
    print("Starting demo:")
    eve_display(eve)

apprunner.run(simple)
