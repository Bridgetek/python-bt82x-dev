# Typical command line:
# python segment --connector ft4222module 12345678 --size 100
import sys
import argparse

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

# Load the sevensegment source code from the "common" directory.
sys.path.append('common')
import sevensegment

def segment(gd):
    # Handle for fonts to use in the test.
    size = 100
    number = 0

    parser = argparse.ArgumentParser(description="EVE simple demo")
    parser.add_argument("number", help="number to write")
    parser.add_argument("--size", help="number size", default=str(size))
    args = parser.parse_args(sys.argv)

    if args.size:
        size = int(args.size, 0)
    if args.number:
        number = int(args.number, 0)
        
    # Calibrate screen if necessary. 
    # Don't do this for now.
    #gd.calibrate()

    # Start drawing test screen.
    gd.begin()
    gd.ClearColorRGB(64,72,64)
    gd.Clear(1,1,1)

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

    gd.Display()
    gd.swap()

apprunner.run(segment)
