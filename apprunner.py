import sys
from sys import implementation

# This loads BT82x family definitions only.
import bteve2

if implementation.name != "circuitpython":
    import argparse

class run:
    def __init__(self, app, patch=None, autotouch=True, minimal=False, connector=None, panel="WUXGA"):
        if implementation.name != "circuitpython":
            if connector == None: 
                connector = "ft4222module"
            progname = sys.argv[0]
            
            # Parse arguments
            parser = argparse.ArgumentParser(description="EVE demo")
            parser.add_argument("--connector", help="the connection method for EVE")
            parser.add_argument("--panel", default=str("WUXGA"), help="panel type")
            parser.add_argument("--ram", default="1G", choices=['512M', '1G', '2G', '4G'], help="size of RAM_G in Gbits")
            (args, rem) = parser.parse_known_args()
            # Persist arguments to target program
            rem.insert(0, progname)
            sys.argv = rem
            # Update any arguments that match
            if (args.connector): connector = args.connector
            if (args.panel): paneltype = args.panel
            if (args.ram): ramsize = args.ram
        elif implementation.name == "circuitpython":
            connector = "circuitpython"
            paneltype = "WUXGA"
            ramsize = "1G"

        # Create an connector to BT82x family devices only.
        eve = bteve2.EVE2(connector)
        # Use default (auto discovered) touch controller
        touch = None

        if paneltype == "WQVGA":

            surface = bteve2.Surface(eve.SWAPCHAIN_0, eve.FORMAT_RGB6, 480, 272)
            panel = bteve2.Panel(eve.WQVGA, 548, 43, 0, 41, 292, 12, 0, 10, 5, 0, 1, 0, 1, None)
            if not autotouch: touch = bteve2.Touch("Focaltech FT5206", 0x38, 1)

        elif paneltype == "WVGA":

            surface = bteve2.Surface(eve.SWAPCHAIN_0, eve.FORMAT_RGB6, 800, 480)
            panel = bteve2.Panel(eve.WVGA, 928, 88, 0, 48, 525, 32, 0, 3, 2, 0, 1, 0, 1, None)
            if not autotouch: touch = bteve2.Touch("Focaltech FT5206", 0x38, 1)

        elif paneltype == "WSVGA":

            surface = bteve2.Surface(eve.SWAPCHAIN_0, eve.FORMAT_RGB6, 1024, 600)
            panel = bteve2.Panel(eve.WSVGA, 1344, 160, 0, 100, 635, 23, 0, 10, 1, 0, 1, 0, 1, 0xd12)
            if not autotouch: touch = bteve2.Touch("Focaltech FT5206", 0x38, 1)
        
        elif paneltype == "WXGA":

            surface = bteve2.Surface(eve.SWAPCHAIN_0, eve.FORMAT_RGB6, 1280, 800)
            panel = bteve2.Panel(eve.WXGA, 1411, 120, 0, 100, 815, 14, 0, 10, 1, 0, 0, 0, 0, 0x8b1)
            if not autotouch: touch = bteve2.Touch("Focaltech FT5206", 0x38, 1)
        
        elif paneltype == "WUXGA":

            surface = bteve2.Surface(eve.SWAPCHAIN_0, eve.FORMAT_RGB6, 1920, 1200)
            panel = bteve2.Panel(eve.WUXGA, 2100,50, 0, 30, 1245,10, 0, 3, 2, 0, 0, 0, 1)
            if not autotouch: touch = bteve2.Touch("Goodix GT911", 0x5d, 2)

        elif paneltype == "FHD":

            surface = bteve2.Surface(eve.SWAPCHAIN_0, eve.FORMAT_RGB6, 1920, 1080)
            panel = bteve2.Panel(eve.FHD, 2140,220, 0, 20, 1108,28, 0, 4, 1, 0, 0, 0, 1)
            if not autotouch: touch = bteve2.Touch("Ilitek IL2510", 0x41, 4)    # require touch entension 

        else:
            raise (f"panel type unknown")
            
        # Check that there is a write method for the connector.
        eve.register(eve)
        match ramsize:
            case "4G":
                eve.ramgsize = (1 << 29)
            case "2G":
                eve.ramgsize = (1 << 28)
            case "1G":
                eve.ramgsize = (1 << 27)
            case "512M":
                eve.ramgsize = (1 << 26)
            case _:
                raise (f"ram size unknown")
        # The top 0x280000 of RAM_G is reserved
        eve.ramgtop = eve.ramgsize - 0x280000

        if not minimal:
            # Screen memory size
            scrsize = (surface.w * surface.h * 3)
            # Available top of memory is below screen scanchain
            top = eve.ramgtop - (2 * scrsize)

            eve.LIB_BeginCoProList()
            eve.CMD_REGWRITE(eve.REG_SC0_SIZE, 2)
            eve.CMD_REGWRITE(eve.REG_SC0_PTR0, top)
            eve.CMD_REGWRITE(eve.REG_SC0_PTR1, top + scrsize)
            eve.LIB_EndCoProList()
            eve.LIB_AwaitCoProEmpty()

            eve.panel(surface, panel, touch, top)

        # If there is no patch specified then load the base patch
        if patch == None:
            import patch_base as patch

        # Test that the patch file has a "loadpatch" function
        try:
            for attr in dir(patch): 
                # Only load declared functions
                if not attr.startswith('__'):
                    setattr(type(eve), attr, getattr(patch, attr))
            # The flash commands are mapped load the patch into the device
            eve.loadpatch()
        except:
            raise Exception("patch \"%s\" requires a loadpatch function" % patch.__name__)

        app(eve)
