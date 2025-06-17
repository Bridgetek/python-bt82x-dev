# Typical command line:
# python segment.py --connector ft4222module 12345678 --size 100
import sys
import argparse

# Add the library directories to the module search path.
sys.path.append('../..')
sys.path.append('../../bteve2')

# Load the extension code from the "snippets" directory.
sys.path.append('../snippets')
import sevensegment

# This module provides the connector to the EVE hardware.
import apprunner

# Target EVE device.
family = "BT82x"

def segment(eve):
    # Handle for fonts to use in the test.
    size = 100
    number = 0

    parser = argparse.ArgumentParser(description="EVE simple demo")
    parser.add_argument("number", help="number to write")
    parser.add_argument("--size", help="number size", default=str(size))
    args = parser.parse_args(sys.argv[1:])

    if args.size:
        size = int(args.size, 0)
    if args.number:
        number = int(args.number, 0)
        
    # Calibrate screen if necessary. 
    # Don't do this for now.
    #eve.LIB_AutoCalibrate()

    # Start drawing test screen.
    eve.LIB_BeginCoProList()
    eve.CMD_DLSTART()
    eve.CLEAR_COLOR_RGB(0,0,0)
    eve.CLEAR(1,1,1)

    redfg = (255, 0, 0)
    redbg = (32, 0, 0)
    grnfg = (0, 255, 0)
    grnbg = (0, 32, 0)

    fg = redfg
    bg = redbg
    x = 40
    y = 40
    gap = size * 1.4
    sevensegment.cmd_sevenseg(gd, x + (gap * 0), y, size, int((number/10000000)%10), fg, bg)
    sevensegment.cmd_sevenseg(gd, x + (gap * 1), y, size, int((number/1000000)%10), fg, bg)
    sevensegment.cmd_sevenseg(gd, x + (gap * 2), y, size, int((number/100000)%10), fg, bg)
    sevensegment.cmd_sevenseg(gd, x + (gap * 3), y, size, int((number/10000)%10), fg, bg)
    sevensegment.cmd_sevenseg(gd, x + (gap * 4), y, size, int((number/1000)%10), fg, bg)
    sevensegment.cmd_sevenseg(gd, x + (gap * 5), y, size, int((number/100)%10), fg, bg)
    sevensegment.cmd_sevenseg(gd, x + (gap * 6), y, size, int((number/10)%10), fg, bg)
    sevensegment.cmd_sevenseg(gd, x + (gap * 7), y, size, int((number/1)%10), fg, bg)
    eve.DISPLAY()
    eve.CMD_SWAP()
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()

apprunner.run(segment)
