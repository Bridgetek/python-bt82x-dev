import sys
import argparse
import importlib

# This loads BT82x family definitions only.
import bteve2

def run(app, minimal = False, connector=None):
    progname = sys.argv[0]
    # Default screen size
    width = 1920
    height = 1200
    # Parse arguments
    parser = argparse.ArgumentParser(description="EVE demo")
    parser.add_argument("--connector", help="the connection method for EVE")
    parser.add_argument("--width", default=str(width), help="panel width in pixels")
    parser.add_argument("--height", default=str(height), help="panel height in pixels")
    (args, rem) = parser.parse_known_args()
    # Persist arguments to target program
    rem.insert(0, progname)
    sys.argv = rem
    # Update any arguments that match
    if (args.connector): connector = args.connector
    width = int(args.width, 0)
    height = int(args.height, 0)

    # Create an connector to BT82x family devices only.
    eve = bteve2.EVE2(connector)
    # Check that there is a write method for the connector.
    eve.register(eve)

    if not minimal:
        eve.CMD_REGWRITE(eve.REG.SC0_SIZE, 2)
        eve.CMD_REGWRITE(eve.REG.SC0_PTR0, 10 << 20)
        eve.CMD_REGWRITE(eve.REG.SC0_PTR1, 18 << 20)
        eve.panel(bteve2.Surface(eve.REG.SWAPCHAIN_0, eve.BITMAP_FORMAT.RGB6, width, height))
        eve.CMD_REGWRITE(eve.REG.RE_DITHER, 1)
        app(eve)
        eve.LIB_AwaitCoProEmpty()
    else:
        app(eve)
