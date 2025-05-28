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
sys.path.append('../../common')
import screenshot

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
def getromfontptr(gd, fontnumber):
    if family == "BT82x":
        # BT82x
        fontroot = 0x08000000 - 0x100
    else:
        # FT8xx, FT81x, BT81x
        fontroot = gd.rd32(eve.ROM_FONTROOT)
    if (fontnumber < getfontmax()):
        fontptr = gd.rd32(fontroot + (fontnumber * 4))
    else:
        fontptr = 0
    return fontptr

# Create a cache of font metrics and meta-data.
# This includes the font sizing, widths and pointers to glyph bitmaps.
def getfontinfocache(gd, fontnumber, fontptr, first_character = 32):
    # Read the first word of the font metric block.
    # This determines the format of the font and how it is handled.
    format = gd.rd32(fontptr)
    if (format == 0x0100AAFF):
        # Extended format 1 font cache.
        # Get the font pixel sizes.
        height = gd.rd32(fontptr + 28)
        width = gd.rd32(fontptr + 24)
        # Get the font bitmap sizes.
        bmheight = gd.rd32(fontptr + 20)
        bmwidth = gd.rd32(fontptr + 16)
        # Get the total number of characters in the font.
        N = gd.rd32(fontptr + 36)
        # Load character widths and glyph pointers.
        widths = [0] * N
        glyphs = [0] * N
        start_of_graphics = gd.rd32(fontptr + 32)
        for page in range(0, N // 128):
            gptr = gd.rd32(fontptr + 40 + (page * 4))
            wptr = gd.rd32(fontptr + 40 + (4 * ((N // 128))) + (page * 4))
            for ch in range(0, 127, 4):
                # Read character width as a 32 bit word.
                width4 = gd.rd32(wptr + (ch & 127))
                for w in range(0, 4):
                    widths[(page * 128) + ch + w] = (width4 >> (w * 8)) & 0xff
                    # Construct glyph pointer
                    glyphs[(page * 128) + ch + w] = start_of_graphics + gptr + ((ch + w) * bmheight * bmwidth)
        cell = False
    elif (format == 0x0200AAFF):
        # Extended format 2 font cache.
        # Get the font pixel sizes.
        height = gd.rd32(fontptr + 28)
        width = gd.rd32(fontptr + 24)
        # Get the font bitmap sizes.
        bmheight = gd.rd32(fontptr + 20)
        bmwidth = gd.rd32(fontptr + 16)
        # Get the total number of characters in the font.
        N = gd.rd32(fontptr + 36)
        # Load character widths and glyph pointers.
        widths = [0] * N
        glyphs = [0] * N
        # This only takes the unkerned character width.
        for page in range(0, N // 128):
            optr = gd.rd32(fontptr + 44 + (page * 4))
            # Skip unused pages.
            if (optr): 
                for ch in range(0, 127):
                    cdptr = gd.rd32(optr + ((ch & 127) * 4))
                    glyphs[(page * 128) + ch] = gd.rd32(cdptr)
                    widths[(page * 128) + ch] = gd.rd32(cdptr + 4)
        cell = False
    else:
        # Legacy font.
        # Get the font pixel sizes
        height = gd.rd32(fontptr + 140)
        width = gd.rd32(fontptr + 136)
        # Get the font bitmap sizes
        bmheight = height
        bmwidth = gd.rd32(fontptr + 132)
        # Get offset to glyphs.
        legacy_address = gd.rd32(fontptr + 144)
        legacy_address_int = struct.unpack_from('i', struct.pack('I', legacy_address))[0]
        # Load character widths and glyph pointers
        widths = [0] * 128
        glyphs = [0] * 128
        for ch in range(0, 127, 4):
            # Read character width as a 32 bit word.
            width4 = gd.rd32(fontptr + ch)
            for w in range(0, 4):
                widths[ch + w] = (width4 >> (w * 8)) & 0xff
                # Construct glyph pointer
                glyphs[ch + w] = legacy_address_int + ((ch + w - first_character) * bmheight * bmwidth)
        cell = True

    return (fontnumber, first_character, width, height, widths, glyphs, cell)

def getromfontinfo(gd, fontnumber, first_character = 32):
    if isromfont(fontnumber):
        fontptr = getromfontptr(gd, fontnumber)
        cache = getfontinfocache(gd, fontnumber, fontptr, first_character)
    else:
        cache = None
    return cache

def getcustomfontinfo(gd, fontnumber, address, first_character = 32):
    if (fontnumber < getfontmax()):
        cache = getfontinfocache(gd, fontnumber, address, first_character)
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
def cmd_textrotate(gd, x, y, fontcache, text):
    (handle, first_character, width, height, widths, glyphs, cell) = fontcache
    if (family == "BT82x") and False: # ignore regions for now.
        gd.CMD_REGION() # BT82x
    else:
        gd.SAVE_CONTEXT() # BT82x, BT81x, FT81x, FT80x

    # Setup the font.
    gd.VERTEX_FORMAT(2)
    gd.CELL(0)
    # Select the handle for the font.
    gd.BEGIN(gd.BEGIN_BITMAPS)
    # Manipulate the font display.
    gd.CMD_LOADIDENTITY()
    # Rotate around point width/2, height/2,
    #   rotate 90 degrees clockwise, scale factor 1.0.
    gd.CMD_ROTATEAROUND(width // 2, height // 2, 16384, 65536)
    gd.CMD_SETMATRIX()

    x1,y1 = x,y
    for ch in text:
        if cell:
            # This is a Legacy font.
            if (y > 511) or (x > 511):
                gd.VERTEX_TRANSLATE_X(x)
                gd.VERTEX_TRANSLATE_Y(y)
                gd.VERTEX2II(0, 0, handle, ord(ch))
            else:
                gd.VERTEX2II(x, y, handle, ord(ch))
        else:
            # This is a RAM font.
            gd.BITMAP_SOURCE_H(glyphs[ord(ch)] >> 24)
            gd.BITMAP_SOURCE(glyphs[ord(ch)])
            if (y > 511) or (x > 511):
                gd.VERTEX_TRANSLATE_X(x)
                gd.VERTEX_TRANSLATE_Y(y)
                gd.VERTEX2F(0, 0)
            else:
                gd.VERTEX2F(x, y)
                #gd.VERTEX2F(x // 4, y // 4)
        # Move the cursor down the y-axis.
        y = y + widths[ord(ch)]

    if (family == "BT82x") and False: # ignore regions for now.
        gd.CMD_ENDREGION(x1, y1, x, y) # BT820
    else:
        gd.RESTORE_CONTEXT() # BT820, BT817, FT81x, FT80x

# Zoom a text string by a factor.
def cmd_textzoom(gd, x, y, fontcache, zoom, text):
    (handle, first_character, width, height, widths, glyphs, cell) = fontcache
    if (family == "BT82x") and False: # ignore regions for now.
        gd.CMD_REGION() # BT82x
    else:
        gd.SAVE_CONTEXT() # BT82x, BT81x, FT81x, FT80x
    # Setup the font.
    gd.VERTEX_FORMAT(2)
    gd.CELL(0)
    # Select the handle for the font.
    gd.BEGIN(gd.BEGIN_BITMAPS)
    # Manipulate the font display.
    gd.CMD_LOADIDENTITY()
    gd.BITMAP_SIZE(gd.FILTER_NEAREST, gd.WRAP_BORDER, gd.WRAP_BORDER, int(width * zoom), int(height * zoom))
    # Apply scale to text.
    gd.CMD_SCALE(zoom * 65536, zoom * 65536)
    gd.CMD_SETMATRIX()

    x1,y1 = x,y
    for ch in text:
        if cell:
            # This is a ROM font.
            if (y > 511) or (x > 511):
                gd.VERTEX_TRANSLATE_X(x)
                gd.VERTEX_TRANSLATE_Y(y)
                gd.VERTEX2II(0, 0, handle, ord(ch))
            else:
                gd.VERTEX2II(x, y, handle, ord(ch))
        else:
            # This is a RAM font.
            gd.BITMAP_SOURCE_H(glyphs[ord(ch)] >> 24)
            gd.BITMAP_SOURCE(glyphs[ord(ch)])
            if (y > 511) or (x > 511):
                gd.VERTEX_TRANSLATE_X(x)
                gd.VERTEX_TRANSLATE_Y(y)
                gd.VERTEX2F(0, 0)
            else:
                gd.VERTEX2F(x, y)
                #gd.VERTEX2F(x // 4, y // 4)
        # Move the cursor in the x-axis accounting for zoom factor.
        x = x + (int(widths[ord(ch)] * zoom))

    if (family == "BT82x") and False: # ignore regions for now.
        gd.CMD_ENDREGION(x1, y1, x, y) # BT820
    else:
        gd.RESTORE_CONTEXT() # BT820, BT817, FT81x, FT80x

def fontmagic(gd):
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
    #gd.LIB_CALIBRATE()

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

    screenshot.setup(gd)

    print("Upload font file...")
    # Check for a relocatable font file. 
    gd.CMD_DLSTART()
    format = int.from_bytes(dd[0:4], byteorder='little')
    if format == 0x0100aa44:
        # Use loadasset for relocatable assets.
        gd.CMD_LOADASSET(address, 0)
        gd.ram_cmd(pad4(dd))
    else:
        # Load normal assets in place directly.
        gd.CMD_INFLATE(address, 0)
        gd.ram_cmd(pad4(zlib.compress(dd)))
    gd.LIB_AWAITCOPROEMPTY()
    """print(f"0x{address:x}: 0x{gd.rd32(address):08x} 0x{gd.rd32(address+4):08x} 0x{gd.rd32(address+8):08x} 0x{gd.rd32(address+12):08x}")"""

    # Update the font table with the custom font.
    print("Setfont...")
    gd.CMD_DLSTART()
    gd.CMD_SETFONT(customfont, address, first_character)
    gd.CMD_SWAP()
    gd.LIB_AWAITCOPROEMPTY()

    # Obtain details on custom installed fonts from RAM_G.
    print("Get custom font info...")
    customfontcache = getcustomfontinfo(gd, customfont, address, first_character)
    assert(customfontcache)
    print(customfontcache)

    # Obtain details of a ROM font.
    print("Get ROM font info...")
    romfontcache = getromfontinfo(gd, romfont)
    assert(romfontcache)

    print("Draw test screen...")
    # Start drawing test screen.
    gd.CMD_DLSTART()
    gd.CLEAR_COLOR_RGB(64,72,64)
    gd.CLEAR(1,1,1)
    # Restore properties of custom font.
    gd.CMD_SETFONT(customfont, address, first_character)

    if args.action == actions[0]:
        # Draw test text using the custom font.
        y = 100
        x = 100
        gd.CMD_TEXT(x, y, customfont, 0, "Custom font text")
        y += getheight(customfontcache)
        cmd_textzoom(gd, x, y, customfontcache, 2, "Custom zoomed in text!")
        y += (2 * getheight(customfontcache))
        cmd_textzoom(gd, x, y, customfontcache, 4, "Custom more zoomed in text!")
        y = 100
        x = x - getheight(customfontcache)
        cmd_textrotate(gd, x, y, customfontcache, "Custom rotated text!")
        y = 100
        x = 600
        # Draw test text using a ROM font.
        gd.CMD_TEXT(x, y, romfont, 0, "ROM font text")
        y += getheight(romfontcache)
        cmd_textzoom(gd, x, y, romfontcache, 0.5, "ROM zoomed out text!")
        y = 100
        x = x - getheight(romfontcache)
        cmd_textrotate(gd, x, y, romfontcache, "ROM rotated text!")

    elif args.action == actions[1]:
        y = 100
        # Draw test text of all ASCII characters.
        gd.CMD_TEXT(100, y, customfont, 0, "!\"#$%&'()*+,-./0123456789:;<=>?")
        y += getheight(customfontcache)
        gd.CMD_TEXT(100, y, customfont, 0, "@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_")
        y += getheight(customfontcache)
        gd.CMD_TEXT(100, y, customfont, 0, "`abcdefghijklmnopqrstuvwxyz{|}")
        y += getheight(customfontcache)
        gd.CMD_TEXT(100, y, romfont, 0, "!\"#$%&'()*+,-./0123456789:;<=>?")
        y += getheight(romfontcache)
        gd.CMD_TEXT(100, y, romfont, 0, "@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_")
        y += getheight(romfontcache)
        gd.CMD_TEXT(100, y, romfont, 0, "`abcdefghijklmnopqrstuvwxyz{|}")
        y += getheight(romfontcache)

    elif args.action == actions[2]:
        # To be used with `fnt_cvt.py` with font files create with the option 
        # for first character set to zero "-l 0". This program must be called
        # with the parameter "-l 0" as well.
        y = 100
        # Draw test text of all ASCII characters.
        gd.BEGIN(gd.BEGIN_BITMAPS)
        # Miss out \x0a since that is a carriage return to CMD_TEXT.
        gd.CMD_TEXT(100, y, customfont, eve.OPT_FILL, "\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0b\x0c\x0d\x0e\x0f" \
                    "\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f")
        y += getheight(customfontcache)
        gd.CMD_TEXT(100, y, customfont, 0, "\x20\x21\x22\x23\x24\x25\x26\x27\x28\x29\x2a\x2b\x2c\x2d\x2e\x2f" \
                    "\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3a\x3b\x3c\x3d\x3e\x3f")
        y += getheight(customfontcache)
        gd.CMD_TEXT(100, y, customfont, 0, "\x40\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e\x4f" \
                    "\x50\x51\x52\x53\x54\x55\x56\x57\x58\x59\x5a\x5b\x5c\x5d\x5e\x5f")
        y += getheight(customfontcache)
        cmd_textzoom(gd, 100, y, customfontcache, 2, "\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0b\x0c\x0d\x0e\x0f" \
                    "\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f")
        y += (2 * getheight(customfontcache))
        cmd_textzoom(gd, 100, y, customfontcache, 2, "\x20\x21\x22\x23\x24\x25\x26\x27\x28\x29\x2a\x2b\x2c\x2d\x2e\x2f" \
                    "\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3a\x3b\x3c\x3d\x3e\x3f")
        y += (2 * getheight(customfontcache))
        cmd_textzoom(gd, 100, y, customfontcache, 2, "\x40\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e\x4f" \
                    "\x50\x51\x52\x53\x54\x55\x56\x57\x58\x59\x5a\x5b\x5c\x5d\x5e\x5f")

    gd.DISPLAY()
    gd.CMD_SWAP()
    gd.LIB_AWAITCOPROEMPTY()

    
apprunner.run(fontmagic)
