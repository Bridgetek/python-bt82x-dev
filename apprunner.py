import sys
from sys import implementation

# This loads BT82x family definitions only.
import bteve2

if implementation.name != "circuitpython":
    import argparse

class run:
    def __init__(self, app, minimal = False, connector=None, panel="HD"):
        if implementation.name != "circuitpython":
            if connector == None: 
                connector = "ft4222module"
            progname = sys.argv[0]
            
            # Parse arguments
            parser = argparse.ArgumentParser(description="EVE demo")
            parser.add_argument("--connector", help="the connection method for EVE")
            parser.add_argument("--panel", default=str("HD"), help="panel type")
            (args, rem) = parser.parse_known_args()
            # Persist arguments to target program
            rem.insert(0, progname)
            sys.argv = rem
            # Update any arguments that match
            if (args.connector): connector = args.connector
            if (args.panel): paneltype = args.panel
        elif implementation.name == "circuitpython":
            connector = "circuitpython"
            paneltype = "HD"

        # Create an connector to BT82x family devices only.
        eve = bteve2.EVE2(connector)

        if paneltype == "WQVGA":

            surface = bteve2.Surface(eve.SWAPCHAIN_0, eve.FORMAT_RGB6, 480, 272)
            panel = bteve2.Panel(eve.WQVGA, 548, 43, 0, 41, 292, 12, 0, 10, 5, 0, 1, 0, 1, None)
            touch = bteve2.Touch("Focaltech FT5206", 0x38, 1)

        elif paneltype == "WVGA":

            surface = bteve2.Surface(eve.SWAPCHAIN_0, eve.FORMAT_RGB6, 800, 480)
            panel = bteve2.Panel(eve.WVGA, 928, 88, 0, 48, 525, 32, 0, 3, 2, 0, 1, 0, 1, None)
            touch = bteve2.Touch("Focaltech FT5206", 0x38, 1)

        elif paneltype == "WSVGA":

            surface = bteve2.Surface(eve.SWAPCHAIN_0, eve.FORMAT_RGB6, 1024, 600)
            panel = bteve2.Panel(eve.WSVGA, 1344, 160, 0, 100, 635, 23, 0, 10, 1, 0, 1, 0, 1, 0xd12)
            touch = bteve2.Touch("Focaltech FT5206", 0x38, 1)
        
        elif paneltype == "WXGA":

            surface = bteve2.Surface(eve.SWAPCHAIN_0, eve.FORMAT_RGB6, 1280, 800)
            panel = bteve2.Panel(eve.WXGA, 1411, 120, 0, 100, 815, 14, 0, 10, 1, 0, 0, 0, 0, 0x8b1)
            touch = bteve2.Touch("Focaltech FT5206", 0x38, 1)
        
        elif paneltype == "HD":

            surface = bteve2.Surface(eve.SWAPCHAIN_0, eve.FORMAT_RGB6, 1920, 1200)
            panel = bteve2.Panel(eve.HD, 2100,50, 0, 30, 1245,10, 0, 3, 2, 0, 0, 0, 1)
            touch = bteve2.Touch("Goodix GT911", 0x5d, 2)

        else:
            raise (f"panel type unknown")
            
        # Check that there is a write method for the connector.
        eve.register(eve)

        if not minimal:
            eve.CMD_REGWRITE(eve.REG_SC0_SIZE, 2)
            eve.CMD_REGWRITE(eve.REG_SC0_PTR0, 10 << 20)
            eve.CMD_REGWRITE(eve.REG_SC0_PTR1, 18 << 20)
            eve.panel(surface, panel, touch)
            app(eve)
            eve.LIB_AWAITCOPROEMPTY()
        else:
            app(eve)
