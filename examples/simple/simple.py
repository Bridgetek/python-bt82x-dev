# Typical command line:
# python simple.py --connector ft4232h standard
import sys
import argparse

# Add the library directories to the module search path.
sys.path.append('../..')
sys.path.append('../../bteve2')

# This module provides the connector to the EVE hardware.
import apprunner

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
    #eve.LIB_CALIBRATE()

    # Start drawing test screen.
    eve.CMD_DLSTART()
    eve.CLEAR_COLOR_RGB(64,72,64)
    eve.CLEAR(1,1,1)

    eve.CMD_TEXT(100, 100, font, eve.OPT_CENTER, args.text)

    eve.DISPLAY()
    eve.CMD_SWAP()
    eve.LIB_AWAITCOPROEMPTY()
    
apprunner.run(simple)
