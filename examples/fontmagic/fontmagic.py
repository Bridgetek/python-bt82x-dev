# Typical command line:
# python fontmagic.py --connector ft4232h ascii fonts\L4\Roboto-BoldCondensed_50_L4.raw -d 0x400 -l 32
import sys
import struct
import zlib
import argparse

# Add the library directories to the module search path.
sys.path.append('../..')
sys.path.append('../../bteve2')

# Load the extension code from the "common" directory.
sys.path.append('../common')

# This module provides the connector to the EVE hardware.
import apprunner

# Target EVE device.
family = "BT82x"

# Valid program actions.
actions = ["standard", "ascii", "symbol"]

# Align an array to a multiple of 4 bytes (32 bits).
# Required for writing block data to EVE.
def pad4(s):
    while len(s) % 4:
        s += b'\x00'
    return s

# Get the maximum number of fonts supported by a platform.
def getfontmax():
    if family == "BT82x":
        # BT82x
        fontcount = 64
    else:
        # FT8xx, FT81x, BT81x
        fontcount = 34
    return fontcount

# Check a ROM font is supported by a platform.
def isromfont(fontnumber):
    if family == "FT80x":
        # FT8xx
        if (fontnumber <= 31) and (fontnumber >= 16):
            return True
    else:
        # FT81x, BT81x, BT82x
        if (fontnumber <= 34) and (fontnumber >= 16):
            return True
    return False

# Obtain the address of a ROM font. Platform specific.
# If the  ROM font will return a pointer of zero.
def getromfontptr(eve, fontnumber):
    if family == "BT82x":
        # BT82x
        fontroot = 0x08000000 - 0x100
    else:
        # FT8xx, FT81x, BT81x
        fontroot = eve.rd32(eve.ROM_FONTROOT)
    if (fontnumber < getfontmax()):
        fontptr = eve.rd32(fontroot + (fontnumber * 4))
    else:
        fontptr = 0
    return fontptr

# Create a cache of font metrics and meta-data.
# This includes the font sizing, widths and pointers to glyph bitmaps.
def getfontinfocache(eve, fontnumber, fontptr, first_character = 32):
    # Read the first word of the font metric block.
    # This determines the format of the font and how it is handled.
    format = eve.rd32(fontptr)
    if (format == 0x0100AAFF):
        # Extended format 1 font cache.
        # Get the font pixel sizes.
        height = eve.rd32(fontptr + 28)
        width = eve.rd32(fontptr + 24)
        # Get the font bitmap sizes.
        bmheight = eve.rd32(fontptr + 20)
        bmwidth = eve.rd32(fontptr + 16)
        # Get the total number of characters in the font.
        N = eve.rd32(fontptr + 36)
        # Load character widths and glyph pointers.
        widths = [0] * N
        glyphs = [0] * N
        start_of_graphics = eve.rd32(fontptr + 32)
        for page in range(0, N // 128):
            gptr = eve.rd32(fontptr + 40 + (page * 4))
            wptr = eve.rd32(fontptr + 40 + (4 * ((N // 128))) + (page * 4))
            for ch in range(0, 127, 4):
                # Read character width as a 32 bit word.
                width4 = eve.rd32(wptr + (ch & 127))
                for w in range(0, 4):
                    widths[(page * 128) + ch + w] = (width4 >> (w * 8)) & 0xff
                    # Construct glyph pointer
                    glyphs[(page * 128) + ch + w] = start_of_graphics + gptr + ((ch + w) * bmheight * bmwidth)
        cell = False
    elif (format == 0x0200AAFF):
        # Extended format 2 font cache.
        # Get the font pixel sizes.
        height = eve.rd32(fontptr + 28)
        width = eve.rd32(fontptr + 24)
        # Get the font bitmap sizes.
        bmheight = eve.rd32(fontptr + 20)
        bmwidth = eve.rd32(fontptr + 16)
        # Get the total number of characters in the font.
        N = eve.rd32(fontptr + 36)
        # Load character widths and glyph pointers.
        widths = [0] * N
        glyphs = [0] * N
        # This only takes the unkerned character width.
        for page in range(0, N // 128):
            optr = eve.rd32(fontptr + 44 + (page * 4))
            # Skip unused pages.
            if (optr): 
                for ch in range(0, 127):
                    cdptr = eve.rd32(optr + ((ch & 127) * 4))
                    glyphs[(page * 128) + ch] = eve.rd32(cdptr)
                    widths[(page * 128) + ch] = eve.rd32(cdptr + 4)
        cell = False
    else:
        # Legacy font.
        # Get the font pixel sizes
        height = eve.rd32(fontptr + 140)
        width = eve.rd32(fontptr + 136)
        # Get the font bitmap sizes
        bmheight = height
        bmwidth = eve.rd32(fontptr + 132)
        # Get offset to glyphs.
        legacy_address = eve.rd32(fontptr + 144)
        legacy_address_int = struct.unpack_from('i', struct.pack('I', legacy_address))[0]
        # Load character widths and glyph pointers
        widths = [0] * 128
        glyphs = [0] * 128
        for ch in range(0, 127, 4):
            # Read character width as a 32 bit word.
            width4 = eve.rd32(fontptr + ch)
            for w in range(0, 4):
                widths[ch + w] = (width4 >> (w * 8)) & 0xff
                # Construct glyph pointer
                glyphs[ch + w] = legacy_address_int + ((ch + w - first_character) * bmheight * bmwidth)
        cell = True

    return (fontnumber, first_character, width, height, widths, glyphs, cell)

def getromfontinfo(eve, fontnumber, first_character = 32):
    if isromfont(fontnumber):
        fontptr = getromfontptr(eve, fontnumber)
        cache = getfontinfocache(eve, fontnumber, fontptr, first_character)
    else:
        cache = None
    return cache

def getcustomfontinfo(eve, fontnumber, address, first_character = 32):
    if (fontnumber < getfontmax()):
        cache = getfontinfocache(eve, fontnumber, address, first_character)
    else:
        cache = None
    return cache

# Get the font height from the font metrics cache.
def getheight(fontcache):
    (_, _, _, height, _, _, _) = fontcache
    return height

# Get the font width from the font metrics cache.
def getwidth(fontcache):
    (_, _, width, _, _, _, _) = fontcache
    return width

# Rotate a text string by 90 degrees clockwise.
def cmd_textrotate(eve, x, y, fontcache, text):
    (handle, first_character, width, height, widths, glyphs, cell) = fontcache
    if (family == "BT82x") and False: # ignore regions for now.
        eve.CMD_REGION() # BT82x
    else:
        eve.SAVE_CONTEXT() # BT82x, BT81x, FT81x, FT80x

    # Setup the font.
    eve.VERTEX_FORMAT(2)
    eve.CELL(0)
    # Select the handle for the font.
    eve.BEGIN(eve.BEGIN_BITMAPS)
    # Manipulate the font display.
    eve.CMD_LOADIDENTITY()
    # Rotate around point width/2, height/2,
    #   rotate 90 degrees clockwise, scale factor 1.0.
    eve.CMD_ROTATEAROUND(width // 2, height // 2, 16384, 65536)
    eve.CMD_SETMATRIX()

    x1,y1 = x,y
    for ch in text:
        if cell:
            # This is a Legacy font.
            if (y > 511) or (x > 511):
                eve.VERTEX_TRANSLATE_X(x * 16)
                eve.VERTEX_TRANSLATE_Y(y * 16)
                eve.VERTEX2II(0, 0, handle, ord(ch))
            else:
                eve.VERTEX2II(x, y, handle, ord(ch))
        else:
            # This is a RAM font.
            eve.BITMAP_SOURCE_H(glyphs[ord(ch)] >> 24)
            eve.BITMAP_SOURCE(glyphs[ord(ch)])
            if (y > 511) or (x > 511):
                eve.VERTEX_TRANSLATE_X(x * 16)
                eve.VERTEX_TRANSLATE_Y(y * 16)
                eve.VERTEX2F(0, 0)
            else:
                eve.VERTEX2F(x, y)
        # Move the cursor down the y-axis.
        y = y + widths[ord(ch)]

    if (family == "BT82x") and False: # ignore regions for now.
        eve.CMD_ENDREGION(x1, y1, x, y) # BT820
    else:
        eve.RESTORE_CONTEXT() # BT820, BT817, FT81x, FT80x

# Zoom a text string by a factor.
def cmd_textzoom(eve, x, y, fontcache, zoom, text):
    (handle, first_character, width, height, widths, glyphs, cell) = fontcache
    if (family == "BT82x") and False: # ignore regions for now.
        eve.CMD_REGION() # BT82x
    else:
        eve.SAVE_CONTEXT() # BT82x, BT81x, FT81x, FT80x
    # Setup the font.
    eve.VERTEX_FORMAT(2)
    eve.CELL(0)
    # Select the handle for the font.
    eve.BEGIN(eve.BEGIN_BITMAPS)
    # Manipulate the font display.
    eve.CMD_LOADIDENTITY()
    eve.BITMAP_SIZE(eve.FILTER_NEAREST, eve.WRAP_BORDER, eve.WRAP_BORDER, int(width * zoom), int(height * zoom))
    # Apply scale to text.
    eve.CMD_SCALE(zoom * 65536, zoom * 65536)
    eve.CMD_SETMATRIX()

    x1,y1 = x,y
    for ch in text:
        if cell:
            # This is a ROM font.
            if (y > 511) or (x > 511):
                eve.VERTEX_TRANSLATE_X(x * 16)
                eve.VERTEX_TRANSLATE_Y(y * 16)
                eve.VERTEX2II(0, 0, handle, ord(ch))
            else:
                eve.VERTEX2II(x, y, handle, ord(ch))
        else:
            # This is a RAM font.
            eve.BITMAP_SOURCE_H(glyphs[ord(ch)] >> 24)
            eve.BITMAP_SOURCE(glyphs[ord(ch)])
            if (y > 511) or (x > 511):
                eve.VERTEX_TRANSLATE_X(x * 16)
                eve.VERTEX_TRANSLATE_Y(y * 16)
                eve.VERTEX2F(0, 0)
            else:
                eve.VERTEX2F(x, y)
        # Move the cursor in the x-axis accounting for zoom factor.
        x = x + (int(widths[ord(ch)] * zoom))

    if (family == "BT82x") and False: # ignore regions for now.
        eve.CMD_ENDREGION(x1, y1, x, y) # BT820
    else:
        eve.RESTORE_CONTEXT() # BT820, BT817, FT81x, FT80x

def fontmagic(eve):
    # Default/unset parameters.
    address = 0
    first_character = 32
    # Handles for fonts to use in the test.
    romfont = 24
    customfont = 3

    parser = argparse.ArgumentParser(description="EVE fontmagic demo")
    parser.add_argument("action", help="demo action", choices=actions)
    parser.add_argument("font", help="custom font file, this can be a .raw or .reloc file")
    parser.add_argument("-d", "--address", default="0", 
                        help="address to load the custom font file in RAM_G")
    parser.add_argument("-l", "--first-character", default="32", 
                        help="first character in font file for \"Legacy\" fonts")
    args = parser.parse_args(sys.argv[1:])

    # Test parameters.
    if args.address:
        address = int(args.address, 0)
    if args.first_character:
        first_character = int(args.first_character, 0)

    # Parameter checking.
    if (args.font == None):
        print(f"Error: Must specify a font file.")
        parser.print_usage()
        sys.exit(1)
    if (not args.action in actions):
        print(f"Error: action must be one of:", " ".join(a for a in actions))
        parser.print_usage()
        sys.exit(1)

    # Calibrate screen if necessary. 
    # Don't do this for now.
    #eve.LIB_AutoCalibrate()

    # Install a custom font. 
    # This must be installed in RAM_G memory before the details of the font
    # are read as it may be a relocatable file which is compressed in the 
    # font resource file.
    try:
        with open(args.font, "rb") as f:
            dd = f.read()
    except:
        print(f"Error: {args.font} not found.")
        parser.print_usage()
        sys.exit(1)

    print("Upload font file...")
    # Check for a relocatable font file. 
    eve.LIB_BeginCoProList()
    eve.CMD_DLSTART()
    format = int.from_bytes(dd[0:4], byteorder='little')
    if format == 0x0100aa44:
        # Use loadasset for relocatable assets.
        eve.CMD_LOADASSET(address, 0)
        eve.LIB_WriteDataToCMD(pad4(dd))
    else:
        # Load normal assets in place directly.
        eve.CMD_INFLATE(address, 0)
        eve.LIB_WriteDataToCMD(pad4(zlib.compress(dd)))
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()
    """print(f"0x{address:x}: 0x{eve.rd32(address):08x} 0x{eve.rd32(address+4):08x} 0x{eve.rd32(address+8):08x} 0x{eve.rd32(address+12):08x}")"""

    # Update the font table with the custom font.
    print("Setfont...")
    eve.LIB_BeginCoProList()
    eve.CMD_DLSTART()
    eve.CMD_SETFONT(customfont, address, first_character)
    eve.CMD_SWAP()
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()

    # Obtain details on custom installed fonts from RAM_G.
    print("Get custom font info...")
    customfontcache = getcustomfontinfo(eve, customfont, address, first_character)
    assert(customfontcache)
    print(customfontcache)

    # Obtain details of a ROM font.
    print("Get ROM font info...")
    romfontcache = getromfontinfo(eve, romfont)
    assert(romfontcache)

    print("Draw test screen...")
    # Start drawing test screen.
    eve.LIB_BeginCoProList()
    eve.CMD_DLSTART()
    eve.CLEAR_COLOR_RGB(64,72,64)
    eve.CLEAR(1,1,1)
    # Restore properties of custom font.
    eve.CMD_SETFONT(customfont, address, first_character)

    if args.action == actions[0]:
        # Draw test text using the custom font.
        y = 100
        x = 100
        eve.CMD_TEXT(x, y, customfont, 0, "Custom font text")
        y += getheight(customfontcache)
        cmd_textzoom(eve, x, y, customfontcache, 2, "Custom zoomed in text!")
        y += (2 * getheight(customfontcache))
        cmd_textzoom(eve, x, y, customfontcache, 4, "Custom more zoomed in text!")
        y = 100
        x = x - getheight(customfontcache)
        cmd_textrotate(eve, x, y, customfontcache, "Custom rotated text!")
        y = 100
        x = 600
        # Draw test text using a ROM font.
        eve.CMD_TEXT(x, y, romfont, 0, "ROM font text")
        y += getheight(romfontcache)
        cmd_textzoom(eve, x, y, romfontcache, 0.5, "ROM zoomed out text!")
        y = 100
        x = x - getheight(romfontcache)
        cmd_textrotate(eve, x, y, romfontcache, "ROM rotated text!")

    elif args.action == actions[1]:
        y = 100
        # Draw test text of all ASCII characters.
        eve.CMD_TEXT(100, y, customfont, 0, "!\"#$%&'()*+,-./0123456789:;<=>?")
        y += getheight(customfontcache)
        eve.CMD_TEXT(100, y, customfont, 0, "@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_")
        y += getheight(customfontcache)
        eve.CMD_TEXT(100, y, customfont, 0, "`abcdefghijklmnopqrstuvwxyz{|}")
        y += getheight(customfontcache)
        eve.CMD_TEXT(100, y, romfont, 0, "!\"#$%&'()*+,-./0123456789:;<=>?")
        y += getheight(romfontcache)
        eve.CMD_TEXT(100, y, romfont, 0, "@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_")
        y += getheight(romfontcache)
        eve.CMD_TEXT(100, y, romfont, 0, "`abcdefghijklmnopqrstuvwxyz{|}")
        y += getheight(romfontcache)

    elif args.action == actions[2]:
        # To be used with `fnt_cvt.py` with font files create with the option 
        # for first character set to zero "-l 0". This program must be called
        # with the parameter "-l 0" as well.
        y = 100
        # Draw test text of all ASCII characters.
        eve.BEGIN(eve.BEGIN_BITMAPS)
        # Miss out \x0a since that is a carriage return to CMD_TEXT.
        eve.CMD_TEXT(100, y, customfont, eve.OPT_FILL, "\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0b\x0c\x0d\x0e\x0f" \
                    "\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f")
        y += getheight(customfontcache)
        eve.CMD_TEXT(100, y, customfont, 0, "\x20\x21\x22\x23\x24\x25\x26\x27\x28\x29\x2a\x2b\x2c\x2d\x2e\x2f" \
                    "\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3a\x3b\x3c\x3d\x3e\x3f")
        y += getheight(customfontcache)
        eve.CMD_TEXT(100, y, customfont, 0, "\x40\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e\x4f" \
                    "\x50\x51\x52\x53\x54\x55\x56\x57\x58\x59\x5a\x5b\x5c\x5d\x5e\x5f")
        y += getheight(customfontcache)
        cmd_textzoom(eve, 100, y, customfontcache, 2, "\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0b\x0c\x0d\x0e\x0f" \
                    "\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f")
        y += (2 * getheight(customfontcache))
        cmd_textzoom(eve, 100, y, customfontcache, 2, "\x20\x21\x22\x23\x24\x25\x26\x27\x28\x29\x2a\x2b\x2c\x2d\x2e\x2f" \
                    "\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3a\x3b\x3c\x3d\x3e\x3f")
        y += (2 * getheight(customfontcache))
        cmd_textzoom(eve, 100, y, customfontcache, 2, "\x40\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e\x4f" \
                    "\x50\x51\x52\x53\x54\x55\x56\x57\x58\x59\x5a\x5b\x5c\x5d\x5e\x5f")

    eve.DISPLAY()
    eve.CMD_SWAP()
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()

apprunner.run(fontmagic)
