# Typical command line:
# python simple.py --connector ft4232h standard
import sys
import argparse

# This module provides the connector (eve) to the EVE hardware.
import bteve2 as eve
import apprunner as app

# Target EVE device.
family = "BT82x"

# EVE family support check.
device_families = ["FT80x", "FT81x", "BT81x", "BT82x"]
assert(family in device_families)

def simple(eve):
    # Handle for fonts to use in the test.
    font = 24

    parser = argparse.ArgumentParser(description="EVE simple demo")
    parser.add_argument("text", help="text to write")
    parser.add_argument("--font", help="font number", default="24")
    args = parser.parse_args(sys.argv[1:])

    if args.font:
        font = int(args.font, 0)
        
    # Calibrate screen if necessary. 
    # Don't do this for now.
    #eve.calibrate()

    # Start drawing test screen.
    eve.CMD_DLSTART()
    eve.CLEAR_COLOR_RGB(64,72,64)
    eve.CLEAR(1,1,1)

    eve.CMD_TEXT(100, 100, font, eve.OPT_CENTER, args.text)

    eve.DISPLAY()
    eve.CMD_SWAP()
    eve.LIB_AwaitCoProEmpty()
    
app.run(simple, connector="ft4222module")
