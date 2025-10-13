# Typical command line:
# python fontmagic.py --connector ft4232h ascii fonts\L4\Roboto-BoldCondensed_50_L4.raw -d 0x400 -l 32
import sys
import os
import re
import struct
import zlib
import argparse
import subprocess
import time

# Add the library directories to the module search path.
sys.path.append('../..')
sys.path.append('../../bteve2')

# Load the extension code from the "common" directory.
sys.path.append('../snippets')

# This module provides the connector to the EVE hardware.
import apprunner
# Import the patch file required by this code.
import patch_entrybot as patch

def pad4(s):
    while len(s) % 4:
        s += b'\x00'
    return s

titleaddress = "Makatoni Plaza Directory"

fontfiles = [(3, "assets/Roboto-BoldCondensed_32_L4.reloc")]
imagefiles = [(4, ["assets/face_2.png",
              "assets/smart_toy.png",
              "assets/dialpad.png",
              "assets/door_open.png",
              "assets/lock.png",
              "assets/lock_open.png",
              "assets/patient_list.png",
              "assets/support_agent.png",
              "assets/qr_code_scanner.png"])]
logofiles = [(2, ["assets/nature_800x480-0.jpg"])]

tenants = ["Ellis, Harry", "Gary, David", "Gennero, Holly", "Gfeller, Bruce", "Gruber, Hans", 
    "Maas, Stanley", "Mabry, Ann", "Mabus, Fredrick", "McAdam, M. J.", "MacAluso, D. L.", 
    "MacBeth, Christine", "MacCarthy, M. L.", "MacConnel, F. R.", "MacDaniels, Helen", "Man, M. R.",
    "Martinez, Martin", "McAlee, Charles", "McMurry, Gregory", "Means, Bernardo", "Meehan, Daniel",
    "Meeks, David", "Miller, Terry", "Moody, Margaret",
    "Quarterback, Theo", "Takagi, Joe", "Thornburg, Richard", 
    "Vreski, Karl", "Vreski, Tony", "Wallens, Gail", "Powell, Al", "Robinson, D. T.", "Argyle, Chauffeur",
    "Henchman, Alexander", "Henchman, Heinrich", "Henchman, Fritz", "Henchman, James","Henchman, Uli", 
    "Henchman, Kristoff", "Henchman, Marco", "Babysitter, Paulina",
    "Johnson, Big", "Johnson, Little", "Johnson, Harvery", "McClane, John"
]
tenants.sort()

imagecell = {}
logocell = {}
fontcell = {}

LVDS_RES = 1080

if LVDS_RES == 1080:

    # Incoming signal is 1920 x 1080
    LVDSRX_W = 1920
    LVDSRX_H = 1080

    LVDSRX_CODE_SETUP_VALUE = 0x03   # 2 channels, two pixels per clock
    LVDSRX_SETUP_VALUE      = 0x17   # One pixel per clock, 2 channels, VESA 24
    LVDSRX_CTRL_VALUE       = 0x8c8c # Ch0 Deskew 0x8, Ch0 clock sel, Frange 0x2

else:
    # 1080P only supported
    raise "1080P only supported"

# Handle for incoming video bitmap
HND_LVDSRX = 1
HND_VIDEO = 5

def drawbanner(eve):
    # Pixel addressing.
    eve.VERTEX_FORMAT(0)
    eve.COLOR_RGB(255, 255, 255)
    h,c = imagecell["smart_toy"]
    eve.BITMAP_HANDLE(h)
    eve.CELL(c)
    eve.BEGIN(eve.BEGIN_BITMAPS)
    eve.VERTEX2II(0, 0, h, c)
    eve.CMD_TEXTSCALE(256, 128, fontcell["Roboto-BoldCondensed_32_L4"], eve.OPT_CENTERY, 0x40000, "EntryBot")
    eve.CMD_TEXTSCALE(10, 256, fontcell["Roboto-BoldCondensed_32_L4"], 0, 0x20000, titleaddress)
    eve.CELL(0)

def drawbutton(eve, x, y, w, h, image, name):
    # Pixel addressing.
    eve.VERTEX_FORMAT(0)
    eve.BEGIN(eve.BEGIN_RECTS)
    eve.LINE_WIDTH(2 * 8)
    eve.COLOR_RGB(30, 30, 30)
    eve.VERTEX2F(x, y)
    eve.VERTEX2F(x + w, y + h)

    eve.BEGIN(eve.BEGIN_BITMAPS)
    eve.COLOR_RGB(255, 255, 255)
    handle,cell = imagecell[image]
    eve.BITMAP_HANDLE(handle)
    eve.CELL(cell)
    eve.VERTEX2F(x + w/2 - 256/2, y + h/2 - 256/2)
    eve.CMD_TEXT(x + w/2, y + h/2 + 256/2, fontcell["Roboto-BoldCondensed_32_L4"], eve.OPT_CENTERX, name)

def eve_display(eve):
    global imagecell
    global logocell
    global fontcell

    # Starting page
    page = 0

    # Start clock for performance calculations.
    frame_last_time = time.monotonic()
    # Count for trigger
    # Also used for average performance figures over.
    trigger_offset = 40
    # Current frames in performace averaging period.
    trigger_count = 0
    # Computed frames per second.
    perf_fps = 0

    # Current scroll position for tenants list.
    tenant_offset = 0

    # Start clock for performance calculations.
    animation_last_time = time.monotonic()

    eve.LIB_BeginCoProList()
    # Amount of memory to allocate to heap
    eve.CMD_MEMORYINIT(0, eve.topmem)
    eve.LIB_AwaitCoProEmpty()

    # Install any custom fonts. 
    # This must be installed in RAM_G memory before the details of the font
    # are read as it may be a relocatable file which is compressed in the 
    # font resource file.
    for fh, fn in fontfiles:
        print(f"Load font {fn} as handle {fh}...")
        try:
            with open(fn, "rb") as f:
                fontdata = f.read()
        except:
            print(f"Error: file {fn} not found.")
            sys.exit(1)

        # Check for a custom font file. It is highly recommended that
        # a relocatable font format is used since the 
        eve.LIB_BeginCoProList()
        eve.CMD_DLSTART()
        format = int.from_bytes(fontdata[0:4], byteorder='little')
        if format == 0x0100aa44:
            size = int.from_bytes(fontdata[4:8], byteorder='little')
            # Memory allocation for font
            # (This must be alinged on a 64 byte boundary and support CMD_INFLATE padding to the next 32 byte boundary).
            faddrraw = eve.LIB_MemoryMalloc(size + 64 + 32)
            faddr = faddrraw + 64 & (~63)
            print(f"Relocatable Font address: 0x{faddr:x} 0x{size:x}")
            # Use loadasset for relocatable assets.
            eve.CMD_LOADASSET(faddr, 0)
            eve.LIB_WriteDataToCMD(fontdata)
        else:
            # Memory allocation for font 
            # (Pad the size to next 64 byte boundary since CMD_INFLATE requires this).
            faddr = eve.LIB_MemoryMalloc((len(fontdata) + 64))
            print(f"Fixed Font address: 0x{faddr:x} 0x{len(fontdata):x} - warning the offset of the must must match EAB")
            # Load normal assets in place directly.
            eve.CMD_INFLATE(faddr, 0)
            eve.LIB_WriteDataToCMD(pad4(zlib.compress(fontdata)))
        # Update the font table with the custom font.
        eve.CMD_SETFONT(fh, faddr, 32)
        eve.CMD_SWAP()
        eve.LIB_AwaitCoProEmpty()
        dictname, _ = os.path.splitext(os.path.basename(fn))
        fontcell[dictname] = fh

    # Load the set of image files to a single bitmap with the same handle.
    # The images are selected with the CELL command. They must all be the
    # exact same size and format.
    for ih, inames in imagefiles:
        print(f"Load {len(inames)} multi-images as handle {ih}...")
        # Memory allocation for images (all must be the same width, height and format).
        iaddr = eve.LIB_MemoryBitmap(eve.FORMAT_ARGB4, 256 * len(inames), 256, 64)
        print(f"Image address: {iaddr:x} { 256 * len(inames) * 256 * 2:x}")

        eve.LIB_BeginCoProList()
        eve.CMD_DLSTART()
        eve.BITMAP_HANDLE(ih)
        for i, iname in enumerate(inames):
            eve.CMD_LOADIMAGE(iaddr + (i * 256 * 256 * 2) , 0)
            print(iname)
            with open(iname, "rb") as f:
                eve.load(f)
            # Add handle and cell number to image dictionary.
            dictname, _ = os.path.splitext(os.path.basename(iname))
            imagecell[dictname] = (ih, i)
        eve.BITMAP_SOURCE(iaddr & 0xffffff)
        eve.BITMAP_SOURCE_H(iaddr >> 24)
        eve.DISPLAY()
        eve.CMD_SWAP()
        eve.LIB_AwaitCoProEmpty()

    # Load the set of logo files to a single bitmap with the same handle.
    # The images are selected with the CELL command. They must all be the
    # exact same size and format.
    for lh, lnames in logofiles:
        print(f"Load {len(lnames)} multi-images as handle {lh}...")
        # Memory allocation for images (all must be the same width, height and format).
        iaddr = eve.LIB_MemoryBitmap(eve.FORMAT_RGB565, 800, 480 * len(lnames), 64)
        print(f"Image address: {iaddr:x} { 800 * len(lnames) * 480 * 2:x}")

        eve.LIB_BeginCoProList()
        eve.CMD_DLSTART()
        eve.BITMAP_HANDLE(lh)
        for i, iname in enumerate(lnames):
            eve.CMD_LOADIMAGE(iaddr + (i * 800 * 480 * 2) , 0)
            print(iname)
            with open(iname, "rb") as f:
                eve.load(f)
            # Add handle and cell number to image dictionary.
            dictname, _ = os.path.splitext(os.path.basename(iname))
            logocell[dictname] = (lh, i)
        eve.BITMAP_SOURCE(iaddr & 0xffffff)
        eve.BITMAP_SOURCE_H(iaddr >> 24)
        eve.DISPLAY()
        eve.CMD_SWAP()
        eve.LIB_AwaitCoProEmpty()

    directorysize = eve.LIB_TextSize(32, 0, "Directory")
    directoryheight = directorysize & 0xffff
    directorywidth = directorysize >> 16
    
    ticker = 0
    tickerwords = "Fire Alarm test on Friday Morning at 10:00... Please close the door behind you... "#Mrs Jackson has lost her cat... Amazon please leave all parcels at reception... Uber Eats don't spill anything please..."
    tickersize = eve.LIB_TextSize(34, 0, tickerwords)
    tickerheight = tickersize & 0xffff
    tickerwidth = tickersize >> 16

    tenant_dir = 0
    logosel = 0
    keypress = 0
    keypress_debounce = 0
    extension = ""
    contact = ""
    calling = False

    while True:

        eve.LIB_BeginCoProList()
        eve.CMD_DLSTART()
        eve.CMD_SETROTATE(2)
        eve.CLEAR_COLOR_RGB(30, 30, 90)
        eve.CLEAR(1,1,1)
        eve.CMD_FGCOLOR_RGB(0x00, 0x38, 0x70)
        eve.CMD_BGCOLOR_RGB(0x00, 0x38, 0xc0)

        eve.TAG_MASK(1)
        eve.TAG(99)
        drawbanner(eve)
        eve.TAG_MASK(0)

        if page == 0:
            
            # Page 0 - Home page

            eve.BEGIN(eve.BEGIN_BITMAPS)
            h,c = logocell["nature_800x480-0"]
            eve.BITMAP_HANDLE(h)
            eve.CELL(c)
            eve.VERTEX2F(200, 1300)

            eve.TAG_MASK(1)
            eve.TAG(1)
            drawbutton(eve, 100, 350, 400, 400, "qr_code_scanner", "QR Code Entry")
            eve.TAG(2)
            drawbutton(eve, 700, 350, 400, 400, "patient_list", "Lookup Tenants")
            eve.TAG(3)
            drawbutton(eve, 100, 850, 400, 400, "dialpad", "Contact Appartment")
            eve.TAG(4)
            drawbutton(eve, 700, 850, 400, 400, "support_agent", "Contact Reception")
            eve.TAG_MASK(0)

            eve.CMD_TEXTTICKER(0, eve.EVE_DISP_WIDTH - tickerheight, eve.EVE_DISP_HEIGHT, 100, 34, 0, ticker & 0xffffffff, tickerwords)

            animation_timer = time.monotonic()
            took = animation_timer - animation_last_time
            if took > 10:
                animation_last_time = animation_timer

                logosel += 1
                if logosel >= len(logocell): logosel = 0

            ticker += 5
            if ticker >= tickerwidth:
                ticker = -1200

        elif page == 4:
            
            # Page 4 - Contact Reception
            eve.CMD_MESSAGEBOX(34, eve.OPT_FLAT | eve.OPT_MSGBGALPHA, "Incomplete")

        elif page == 1:
            
            # Page 1 - QR Code Entry
            eve.CMD_MESSAGEBOX(34, eve.OPT_FLAT | eve.OPT_MSGBGALPHA, "Incomplete")

        elif page == 2:

            # Page 2 - Contacts page

            if (keypress >= ord("A") and keypress <= ord("Z")):
                contact = chr(keypress)
                animation_last_time = time.monotonic()

            tenants_filter = []
            if contact != "":
                for t in tenants:
                    if t.startswith(contact):
                        tenants_filter.append(t)

                animation_timer = time.monotonic()
                took = animation_timer - animation_last_time
                if took > 5:
                    contact = ""
            else:
                tenants_filter = tenants

            if ((directoryheight * len(tenants_filter)) > 900):
                # Scroll list of tenants.
                if tenant_dir == 0: tenant_offset += 2
                else: tenant_offset -= 2

                # Switch directions at the end of the list.
                if tenant_dir == 0 and tenant_offset >= (directoryheight * len(tenants_filter)) - 900:
                    tenant_dir = 1
                elif tenant_dir == 1 and tenant_offset <= 0:
                    tenant_dir = 0
            else: 
                tenant_dir = 0
                tenant_offset = 0

            eve.CMD_FGCOLOR_RGB(30, 30, 30)
            eve.SAVE_CONTEXT()
            eve.SCISSOR_XY(300,350)
            eve.SCISSOR_SIZE(600,900)
            for i,t in enumerate(tenants_filter):
                ypos = -tenant_offset + (directoryheight * i)
                if ypos > -(directoryheight) and ypos < (directoryheight * len(tenants_filter)):
                    eve.CMD_TEXT(300, 350 + ypos, 32, 0, t)
            eve.RESTORE_CONTEXT()
            option = eve.OPT_FLAT 
            if contact != "":
                option |= ord(contact)
            eve.CMD_KEYBOARD(100, 1300, 1000, 480, 32, option, "QWERTYUIOP\nASDFGHJKL\nZXCVBNM")
            eve.CMD_FGCOLOR_RGB(0x00, 0x38, 0x70)
       
        elif page == 3:

            # Page 3 - Dial Extension Number page

            if keypress == 100:
                extension = ""
            if keypress == 101:
                calling = True
                animation_last_time = time.monotonic()

            if len(extension) < 4:
                if (keypress >= ord("0") and keypress <= ord("9")) or \
                    (keypress >= ord("A") and keypress <= ord("B")):
                        extension = extension + chr(keypress)

            eve.CMD_TEXT(600, 350, 32, eve.OPT_CENTERX, "Type Extension Number")

            eve.VERTEX_FORMAT(0)
            eve.BEGIN(eve.BEGIN_RECTS)
            eve.LINE_WIDTH(2 * 8)
            eve.COLOR_RGB(30, 30, 30)
            eve.VERTEX2F(300, 460)
            eve.VERTEX2F(900, 600)

            eve.COLOR_RGB(255, 255, 255)
            eve.CMD_TEXT(600, 490, 34, eve.OPT_CENTERX, extension)
            eve.CMD_KEYBOARD(300, 700, 600, 800, 32, eve.OPT_FLAT | eve.OPT_MAP_SPECIAL_KEYS , "123\n456\n789\nA0B")
            eve.TAG_MASK(1)
            eve.TAG(100)
            eve.CMD_BUTTON(100, 1600, 400, 200, 34, eve.OPT_FLAT, "Clear")
            eve.TAG(101)
            eve.CMD_BUTTON(700, 1600, 400, 200, 34, eve.OPT_FLAT, "Call")
            eve.TAG_MASK(0)

            if calling:
                eve.CMD_FGCOLOR_RGB(0x30, 0xc0, 0x30)

                message = f"Calling extension:\n{extension}"
                eve.CMD_MESSAGEBOX(34, eve.OPT_FLAT | eve.OPT_MSGBGALPHA, message)
                
                eve.CMD_FGCOLOR_RGB(0x00, 0x38, 0x70)
                
                animation_timer = time.monotonic()
                took = animation_timer - animation_last_time
                if took > 2:
                    calling = False
                    extension = ""

        # Display the performance indicator of frame updates per second.
        if (perf_fps):
            eve.COLOR_RGB(255, 255, 255)
            eve.CMD_TEXT(eve.EVE_DISP_HEIGHT, 0, 34, eve.OPT_RIGHTX | eve.OPT_FORMAT, "FPS: %d", perf_fps)

        eve.DISPLAY()
        eve.CMD_SWAP()
        eve.CMD_REGREAD(eve.REG_TOUCH_TAG, 0)
        eve.LIB_AwaitCoProEmpty()
        tag = eve.LIB_GetResult()

        if (tag > 0) and (tag < 5):
            page = tag
            extension = ""
            contact = ""
        elif tag == 99:
            page = 0
            extension = ""
            contact = ""
        else:
            keypress = tag
        
        if keypress == keypress_debounce:
            keypress = 0
        else:
            keypress_debounce = keypress
        
        # Calculate frames update per second.
        trigger_count += 1
        if trigger_count >= trigger_offset:
            trigger_count = 0
            frame_timer = time.monotonic()
            took = frame_timer - frame_last_time
            print(f"{trigger_offset} frames took {took:.3f} s. {trigger_offset / took:.2f} perf_fps")
            perf_fps = int(trigger_offset / took)
            frame_last_time = frame_timer

def entrybot(eve):
    # Calibrate the display
    print("Calibrating display...")
    # Calibrate screen if necessary. 
    eve.LIB_AutoCalibrate()
    # Start example code
    print("Starting demo:")

    eve_display(eve)

apprunner.run(entrybot, patch)
