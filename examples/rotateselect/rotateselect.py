# Typical command line:
# python rotateselect.py --connector ft4222module
import sys
import time
import datetime
import struct
import argparse
import zlib
import math

# Add the library directories to the module search path.
sys.path.append('../..')
sys.path.append('../../bteve2')

# This module provides the connector to the EVE hardware.
import apprunner
# Import the patch file required by this code.
import patch_rotate as patch

# Install a custom font. 
class customfont:
    address = None
    width = None
    height = None
    handle = None
    eve = None

    # This must be installed in RAM_G memory before the details of the font
    # are read as it may be a relocatable file which is compressed in the 
    # font resource file.
    def __init__(self, eve, fonthandle, fontpath, verbose = 0):
        #self.eve = eve
        self.handle = fonthandle
        
        try:
            with open(fontpath, "rb") as f:
                dd = f.read()
        except:
            print(f"Error: {fontpath} not found.")
            sys.exit(1)

        # Check for a relocatable font file. 
        format = int.from_bytes(dd[0:4], byteorder='little')
        if format == 0x0100aa44:
            # Get the expanded size of the asset.
            assetsize = int.from_bytes(dd[4:8], byteorder='little')
            if verbose: print(f"Relocatable asset 0x{format:x}.")
        else:
            # Size is the number of bytes in the file.
            assetsize = len(dd)
            if verbose: print(f"Normal asset 0x{format:x}.")
        if verbose: print(f"Font size: 0x{assetsize:x} bytes.")
        self.address = eve.LIB_MemoryMalloc(assetsize + 16)
        address16a = (self.address + 16) & (~15)
        if verbose: print(f"Font address: 0x{address16a:x}.")
        if format == 0x0100aa44:
            # Use loadasset for relocatable assets.
            if verbose: print(f"Load asset to 0x{address16a:x}...")
            eve.CMD_LOADASSET(address16a, 0)
            eve.LIB_WriteDataToCMD(dd)
        else:
            # Load normal assets in place directly.
            if verbose: print(f"Inflate to 0x{address16a:x}...")
            eve.CMD_INFLATE(address16a, 0)
            eve.LIB_WriteDataToCMD(zlib.compress(dd))
        eve.LIB_EndCoProList()
        eve.LIB_AwaitCoProEmpty()

        # Update the font table with the custom font.
        eve.LIB_BeginCoProList()
        eve.CMD_DLSTART()
        eve.CMD_SETFONT(self.handle, address16a, 32)
        eve.CMD_SWAP()
        eve.LIB_EndCoProList()
        eve.LIB_AwaitCoProEmpty()

        fontformat = eve.rd32(address16a)
        if verbose: print(f"Font format: 0x{fontformat:x}")
        if (fontformat == 0x0200aaff):
            # Extended 2 format
            self.width = fontformat = eve.rd32(address16a + 24)
            self.height = fontformat = eve.rd32(address16a + 28)
        elif (fontformat == 0x0100aaff):
            # Extended 1 format
            self.width = fontformat = eve.rd32(address16a + 24)
            self.height = fontformat = eve.rd32(address16a + 28)
        else:
            # Legacy format
            self.width = fontformat = eve.rd32(address16a + 136)
            self.height = fontformat = eve.rd32(address16a + 140)
        
        if verbose: print(f"Font width {self.width} height {self.height}")

    def free(self):
        if (self.address != None):
            self.eve.LIB_MemoryFree(self.address)
        self.address = None

    def getnumber(self):
        return self.handle

    def getwidth(self):
        return self.width
    
    def getheight(self):
        return self.height
    
    def getfontsize(self):
        return (self.width, self.height)

# Home demo
class fhome:
    eve = None
    counter = 0
    t_on = False

    def __init__(self, eve):
        self.eve = eve
    
    def draw(self, x1, y1, x2, y2, fade):
        self.eve.COLOR_A(fade)
        if (self.counter == 0):
            self.eve.CMD_TEXT((x2 + x1) // 2, (y2 + y1) // 2, 28, self.eve.OPT_CENTER, "Home Demo\nGoes Here!")
        else:
            self.eve.CMD_TEXT((x2 + x1) // 2, (y2 + y1) // 2, 28, self.eve.OPT_CENTER, f"{self.counter} touches!")

    def touch_on(self, x, y):
        if (not self.t_on):
            self.counter += 1
            self.t_on = True

    def touch_off(self):
        self.t_on = False

class frotate:
    eve = None

    def __init__(self, eve):
        self.eve = eve
    
    def draw(self, x1, y1, x2, y2, fade):
        self.eve.COLOR_A(fade)
        self.eve.CMD_TEXT((x2 + x1) // 2, (y2 + y1) // 2, 28, self.eve.OPT_CENTER, "Rotate Demo\nGoes Here!")

    def touch_on(self, x, y):
        if (not self.t_on):
            self.t_on = True

    def touch_off(self):
        self.t_on = False

class fterminal:
    eve = None

    def __init__(self, eve):
        self.eve = eve
    
    def draw(self, x1, y1, x2, y2, fade):
        self.eve.COLOR_A(fade)
        self.eve.CMD_TEXT((x2 + x1) // 2, (y2 + y1) // 2, 28, self.eve.OPT_CENTER, "Terminal Demo\nGoes Here!")

    def touch_on(self, x, y):
        if (not self.t_on):
            self.t_on = True

    def touch_off(self):
        self.t_on = False

class fheart:
    eve = None

    def __init__(self, eve):
        self.eve = eve
    
    def draw(self, x1, y1, x2, y2, fade):
        self.eve.COLOR_A(fade)
        self.eve.CMD_TEXT((x2 + x1) // 2, (y2 + y1) // 2, 28, self.eve.OPT_CENTER, "Heart Demo\nGoes Here!")

    def touch_on(self, x, y):
        if (not self.t_on):
            self.t_on = True

    def touch_off(self):
        self.t_on = False

class fshapes:
    eve = None

    def __init__(self, eve):
        self.eve = eve
    
    def draw(self, x1, y1, x2, y2, fade):
        self.eve.COLOR_A(fade)
        self.eve.CMD_TEXT((x2 + x1) // 2, (y2 + y1) // 2, 28, self.eve.OPT_CENTER, "Shapes Demo\nGoes Here!")

    def touch_on(self, x, y):
        if (not self.t_on):
            self.t_on = True

    def touch_off(self):
        self.t_on = False

class fsettings:
    eve = None

    def __init__(self, eve):
        self.eve = eve
    
    def draw(self, x1, y1, x2, y2, fade):
        self.eve.COLOR_A(fade)
        self.eve.CMD_TEXT((x2 + x1) // 2, (y2 + y1) // 2, 28, self.eve.OPT_CENTER, "Settings Demo\nGoes Here!")

    def touch_on(self, x, y):
        if (not self.t_on):
            self.t_on = True

    def touch_off(self):
        self.t_on = False

class fkey:
    eve = None

    def __init__(self, eve):
        self.eve = eve
    
    def draw(self, x1, y1, x2, y2, fade):
        self.eve.COLOR_A(fade)
        self.eve.CMD_TEXT((x2 + x1) // 2, (y2 + y1) // 2, 28, self.eve.OPT_CENTER, "Key Demo\nGoes Here!")

    def touch_on(self, x, y):
        if (not self.t_on):
            self.t_on = True

    def touch_off(self):
        self.t_on = False

class ClickWheel:
    eve = None
    cradius = None # Click wheel radius
    # Click wheel screen locations
    cw = None
    ch = None
    cx = None
    cy = None
    # Click wheel effective radius for centre of band
    cr = None
    couter = None # Size of outside of band (2 * radius)
    cinner = None # Size of inner of band
    cfont = None # Font for glyphs
    
    def __init__(self, eve, radius, font):
        self.eve = eve
        self.cradius = radius
        self.cfont = font
        self.cw = self.cradius * 2
        self.ch = self.cradius * 2
        self.cr = (self.cw * 9) // 20
        self.cc = (self.cw // 2, self.ch // 2)
        self.csw = (self.cw * 1) // 10
        self.couter = (self.cr * 2) + self.csw
        self.cinner = (self.cr * 2) - self.csw

    def setpos(self, x, y):
        self.cx = x + self.cradius
        self.cy = y + self.cradius

    def inner(self):
        # inner wheel radius
        return self.cinner // 2

    def draw(self):
        # Draw scroll wheel band
        self.eve.SAVE_CONTEXT()
        self.eve.BEGIN(self.eve.BEGIN_POINTS)
        self.eve.VERTEX_TRANSLATE_X(self.cx - self.cradius)
        self.eve.VERTEX_TRANSLATE_Y(self.cy - self.cradius)
        self.eve.STENCIL_OP(self.eve.STENCIL_INCR, self.eve.STENCIL_INCR)
        self.eve.COLOR_A(0)
        self.eve.POINT_SIZE(self.couter)
        self.eve.VERTEX2F(self.cradius, self.cradius)
        self.eve.POINT_SIZE(self.cinner)
        self.eve.VERTEX2F(self.cradius, self.cradius)
        self.eve.STENCIL_FUNC(self.eve.TEST_EQUAL, 1, 255)
        self.eve.COLOR_A(255)
        self.eve.COLOR_RGB(0x00, 0x00, 0x10)
        self.eve.POINT_SIZE(self.couter)
        self.eve.VERTEX2F(self.cradius, self.cradius)
        self.eve.RESTORE_CONTEXT()

    def glyph(self, angle, glyph):
        # Draw glyphs ontop of band
        (fw, fh) = self.cfont.getfontsize()
        self.eve.SAVE_CONTEXT()
        self.eve.BEGIN(self.eve.BEGIN_BITMAPS)
        self.eve.BITMAP_HANDLE(1)
        self.eve.CMD_LOADIDENTITY()
        self.eve.CMD_ROTATEAROUND(fw // 2, fh // 2, angle, 0x10000)
        # Apply transformation matrix to text.
        self.eve.CMD_SETMATRIX()
        # Angle of 0x0000 furmans is x = -1 units, y = 0 units.
        # Angle of 0x4000 furmans is x = 0 units, y = +1 units.
        x = int((-math.cos(angle * 2 * math.pi / 0x10000)) * self.cr) + self.cx
        y = int((-math.sin(angle * 2 * math.pi / 0x10000)) * self.cr) + self.cy
        self.eve.CMD_TEXT(x, y, self.cfont.getnumber(), self.eve.OPT_CENTER, glyph) 
        self.eve.RESTORE_CONTEXT()

class Demo:
    eve = None

    # List of Demo classes
    options = []
    # Angles at which each demo changes
    foption = 0
    fselect = 0
    
    # Demo screen area w, h, x and y
    dw = None
    dh = None
    dx = None
    dy = None
    # Demo select wheel
    wheel = None
    wheel_radius = None
    wheel_x = None
    wheel_y = None
    # Demo select font
    font_icon = None
    # Persistent variables
    frot = 0x0000 # Current wheel rotation
    fprev = None # Previous wheel rotation
    tprev = None # Previous touch
    aoption = -1 # Active option in wheel
    soption = -1 # Selected option in wheel
    demostateanim = 0 # Animation component during selection/deselection
    demostateanimsteps = 20 # Pixel steps per animation frame
    # State machine for animations/demos
    demostate_select = 0 # Waiting for a demo to select
    demostate_selecting = 1 # Animation when selected
    demostate_demo = 2 # Demo in progress
    demostate_demoending = 3 # Demo finishing
    demostate = demostate_select # Current selection state of demo
    
    # Status bar area
    dhb = None # Height of status bar
    dyb = None # Y axis for top of status bar

    def __init__(self, eve, dw, dh, radius = 200, bottom = 50, verbose=0):
        self.eve = eve
        # Demo screen size is 800 x 480
        self.dw = dw
        self.dh = dh
        self.wheel_radius = radius
        self.verbose = verbose

        # Top left coordinate of demo area
        self.dx = (eve.w // 2) - (self.dw // 2)
        self.dy = (eve.h // 2) - (self.dh // 2)
        self.dhb = bottom
        self.dyb = self.dy + self.dh - (self.dhb)

        # Location of wheel
        self.wheel_x = self.dx + self.dw - (2 * self.wheel_radius)
        self.wheel_y = self.dy

        # Load the font
        self.font_icon = customfont(self.eve, 1, "assets/MaterialSymbolsSharp-Regular_26_L4.reloc", verbose)

        # Load the click wheel
        self.wheel = ClickWheel(self.eve, self.wheel_radius, self.font_icon)
        self.wheel_inner = self.wheel.inner()

    # Add a demo class to the list of demos
    def adddemo(self, glyph, name, object):
        self.options.append([glyph, name, object])
        self.foption = 0x10000//len(self.options)
        self.fselect = (self.foption // 4)

    # Perform draw of demo menu screen (and handle touches) also call demo classes when they are active.
    def draw(self):
        fade = 255
        # Animate depending on state.
        if (self.demostate == self.demostate_select):
            pcx = self.wheel_x
            pcy = self.wheel_y
            self.demostateanim = 0
        elif (self.demostate == self.demostate_selecting):
            self.demostateanim += (self.wheel_inner // self.demostateanimsteps)
            pcx = self.wheel_x + self.demostateanim
            pcy = self.wheel_y
            fade = self.demostateanim * 255 // (self.wheel_inner * 2)
            if (self.demostateanim >= self.wheel_inner * 2):
                self.demostate = self.demostate_demo
        elif (self.demostate == self.demostate_demo):
            pcx = self.wheel_x + self.demostateanim
            pcy = self.wheel_y
            fade = 255
        elif (self.demostate == self.demostate_demoending):
            self.demostateanim -= (self.wheel_inner // self.demostateanimsteps)
            pcx = self.wheel_x + self.demostateanim
            pcy = self.wheel_y
            fade = self.demostateanim * 255 // (self.wheel_inner * 2)
            if (self.demostateanim <= 0):
                self.demostate = self.demostate_select

        self.eve.LIB_BeginCoProList()
        self.eve.CMD_DLSTART()
        # Pixel addressing resolution.
        self.eve.VERTEX_FORMAT(0)
        self.eve.CLEAR_COLOR_RGB(0x00, 0x00, 0x00)
        self.eve.CLEAR(1,1,1)
        # Limit drawing to the demo screen area.
        self.eve.CLEAR_COLOR_RGB(0xff, 0xff, 0xff)
        self.eve.SCISSOR_XY(self.dx, self.dy)
        self.eve.SCISSOR_SIZE(self.dw, self.dh)
        self.eve.CLEAR(1,1,1)
        # Appealing gradient over the screen.
        self.eve.CMD_GRADIENT(self.dx, self.dy, 0x000030, self.dx, self.dy + self.dh, 0x000060)

        # Draw frame at bottom
        self.eve.SAVE_CONTEXT()
        self.eve.BEGIN(self.eve.BEGIN_RECTS)
        self.eve.VERTEX_TRANSLATE_X(self.dx)
        self.eve.VERTEX_TRANSLATE_Y(self.dyb)
        self.eve.COLOR_RGB(0xff, 0xff, 0xff)
        rounding = self.font_icon.getwidth() // 2
        self.eve.LINE_WIDTH(rounding)
        self.eve.VERTEX2F(rounding // 2, rounding // 2)
        self.eve.VERTEX2F(self.dw - rounding // 2, (self.dhb) - (rounding // 2))
        self.eve.COLOR_RGB(0x00, 0x00, 0x80)
        self.eve.VERTEX2F(2 + rounding // 2, 2 + rounding // 2)
        self.eve.VERTEX2F(self.dw - 2 - rounding // 2, (self.dhb) - 2 - (rounding // 2))
        self.eve.COLOR_RGB(0x00, 0x00, 0x20)
        self.eve.VERTEX2F(4 + rounding // 2, 4 + rounding // 2)
        self.eve.VERTEX2F(self.dw - 4 - rounding // 2, (self.dhb) - 4 - (rounding // 2))
        self.eve.RESTORE_CONTEXT()

        self.wheel.setpos(pcx, pcy)
        self.eve.SAVE_CONTEXT()
        self.wheel.draw()
        self.eve.COLOR_RGB(255, 255, 255)
        for i,o in enumerate(self.options):
            self.eve.COLOR_RGB(255, 255, 255)
            self.wheel.glyph(self.frot - (self.foption * i), o[0])
        self.eve.RESTORE_CONTEXT()

        # Draw select pointer and label 
        self.eve.SAVE_CONTEXT()
        self.eve.CMD_TEXT(pcx, pcy + self.wheel_radius, self.font_icon.getnumber(), self.eve.OPT_CENTER, "\uF81C")
        self.aoption = -1
        for i,o in enumerate(self.options):
            # Start/end of one active between each segment
            fcentre = (self.foption * i)
            fstart = (fcentre - (self.foption // 2)) & 0xffff
            fend = (fcentre + (self.foption // 2)) & 0xffff
            if ((self.frot > fstart) and (self.frot < fend)) or ((fstart > fend) and ((self.frot < fend) or (self.frot > fstart))):
                if ((fstart > fend) and (self.frot > fstart)):
                    fdiff = abs(self.foption//2 - (self.frot - fstart))
                else:
                    fdiff = abs(self.frot - fcentre)
                if fdiff < self.fselect:
                    # Draw menu name brightly.
                    self.eve.TAG(1)
                    self.eve.COLOR_RGB(0x00, 0xff, 0x00)
                    self.eve.COLOR_A(255)
                    self.aoption = i
                else:
                    # Fade menu name in and out.
                    self.eve.COLOR_RGB(0x80, 0x80, 0x80)
                    self.eve.COLOR_A(255 - (((fdiff - self.fselect)*255) // self.foption))
                self.eve.CMD_TEXT(pcx + self.wheel_radius, pcy + self.wheel_radius, self.font_icon.getnumber(), self.eve.OPT_CENTER, o[1])
        self.eve.RESTORE_CONTEXT()

        demo_option = None
        self.eve.COLOR_A(255)
        self.eve.COLOR_RGB(0x00, 0xff, 0x00)
        if (self.soption >= 0):
            o = self.options[self.soption]
            self.eve.CMD_TEXT(self.dx + self.dw//2, self.dy + self.dh - self.font_icon.getheight(), self.font_icon.getnumber(), self.eve.OPT_CENTER, o[1] + " Demo")
            if (self.demostate != self.demostate_select):
                # Select demo class
                demo_option = o[2]

        if demo_option != None: demo_option.draw(self.dx, self.dy, pcx, self.dyb, fade)

        self.eve.DISPLAY()
        self.eve.CMD_SWAP()
        self.eve.LIB_EndCoProList()
        self.eve.LIB_AwaitCoProEmpty()

        # Work out rotation from touch screen position.
        txy = self.eve.rd32(self.eve.REG_TOUCH_SCREEN_XY)
        (tx, ty) = (txy >> 16, txy & 0xffff)
        touch_on = (tx != 32768)
        if touch_on:
            # Proceed to check when we are in the wheel.
            if ((tx >= pcx) and (tx <= pcx + (2 * self.wheel_radius))) and ((ty >= pcy) and (ty <= pcy + (2 * self.wheel_radius))):
                if (self.tprev == False):
                    if (self.demostate == self.demostate_select):
                        # Calculate the point relative to the centre of the wheel.
                        sx = tx - (pcx + self.wheel_radius)
                        sy = ty - (pcy + self.wheel_radius)
                        # atan2 gets the angle from the centre in radians.
                        fthis = int((math.atan2(sy, sx) / (2 * math.pi)) * 0x10000)
                        if (self.fprev == None):
                            # Look for a press on the centre of the wheel.
                            r = int(math.sqrt((sx)**2 + (sy)**2))
                            if (r < self.wheel_inner // 2):
                                self.soption = self.aoption
                                self.demostate = self.demostate_selecting
                                fthis = None
                                self.tprev = True
                        else:
                            if (self.fprev != None):
                                self.frot = (self.frot + (fthis - self.fprev)) & 0xffff
                        if (fthis != None):
                            self.fprev = fthis
                    else:
                        if (self.tprev == False):
                            self.tprev = True
                        self.demostate = self.demostate_demoending
            else:
                if demo_option != None: demo_option.touch_on(tx, ty)

        else:
            self.fprev = None
            self.tprev = False
            if demo_option != None: demo_option.touch_off()
        
        if self.aoption != self.soption:
            self.soption = -1

def rotateselect(eve):

    parser = argparse.ArgumentParser(description="EVE menu demo")
    parser.add_argument('-v', '--verbose',
                    action='store_true')
    args = parser.parse_args(sys.argv[1:])

    verbose = 0
    if args.verbose: 
        verbose = 1

    # Calibrate the display
    print("Calibrating display...")
    # Calibrate screen if necessary. 
    eve.LIB_AutoCalibrate()

    # Area of memory to use for testing.
    start = 0
    # Available size of memory. 
    size = (10 << 20) - start

    # Initialise the memory service and obtain the available size.
    eve.CMD_MEMORYINIT(start, size)
    
    # Start an instance of the demo class.
    # Draw on 800x480 canvas (centered on larger screens)
    demo = Demo(eve, 800, 480, 200, 50, verbose)

    # Add some random demos
    demo.adddemo("\uE88A", "home", fhome(eve))
    demo.adddemo("\uE577", "rotate", frotate(eve))
    demo.adddemo("\uEB8E", "terminal", fterminal(eve))
    demo.adddemo("\uF60A", "heart check", fheart(eve))
    demo.adddemo("\uF437", "shapes", fshapes(eve))
    demo.adddemo("\uE8B8", "settings", fsettings(eve))
    demo.adddemo("\uF51A", "key", fkey(eve))

    while True:
        demo.draw()

apprunner.run(rotateselect, patch)
