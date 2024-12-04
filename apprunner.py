import sys
import argparse
import importlib

# This loads BT82x family definitions only.
import bteve2 as eve

def run(app, minimal = False):
    width = 1920
    height = 1200
    parser = argparse.ArgumentParser(description="EVE demo")
    parser.add_argument("--connector", default="ft4232h", help="the connection method for EVE")
    parser.add_argument("--width", default=str(width), help="panel width in pixels")
    parser.add_argument("--height", default=str(height), help="panel height in pixels")
    (args, rem) = parser.parse_known_args()
    sys.argv = rem

    width = int(args.width, 0)
    height = int(args.height, 0)
    connector_dir = "connectors/"

    sys.path.append(connector_dir)
    try:
        connector = importlib.import_module(args.connector)
    except ModuleNotFoundError:
        print(f"Connector '{args.connector}' not found in '{connector_dir}'")
        sys.exit(1)
    # Create an connector to BT82x family devices only.
    gd = connector.EVE2()
    gd.register(gd)
    gd.eve = eve
    
    if not minimal:
        gd.cmd_regwrite(eve.REG_SC0_SIZE, 2)
        gd.cmd_regwrite(eve.REG_SC0_PTR0, 10 << 20)
        gd.cmd_regwrite(eve.REG_SC0_PTR1, 18 << 20)
        gd.panel(eve.Surface(eve.SWAPCHAIN_0, eve.RGB6, width, height))
        gd.cmd_regwrite(eve.REG_RE_DITHER, 1)
        app(gd)
        gd.finish()
    else:
        app(gd)
