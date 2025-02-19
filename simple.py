# Typical command line:
# python simple.py --connector ft4232h standard
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

def simple(gd):
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
    #gd.calibrate()

    # Start drawing test screen.
    gd.begin()
    gd.ClearColorRGB(64,72,64)
    gd.Clear(1,1,1)

    gd.cmd_text(100, 100, font, 0, args.text)

    gd.Display()
    gd.swap()
    
apprunner.run(simple)
