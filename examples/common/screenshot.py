import os
import struct

# This is the EVE library.
import bteve2 as evelib

oneshot = True

# Screenshot Widget
#
# Calling format:
#   screenshot.cmd_screenshot(eve, filename)
#
# Parameters:
#   eve: Handle to class of bteve2.
#   filename: Name of file to write on SD card.
#   address: An optional safe RAM_G address to render the display
#       before writing to the file. Default is 0x10000.
#
# Description:
#   Add a call to this function BEFORE the CMD_SWAP call when a 
#   display list has been completed.
#
#        eve.DISPLAY()
#        screenshot.cmd_screenshot(eve, "test.bmp")
#        eve.CMD_SWAP()
#        eve.LIB_AwaitCoProEmpty()
#
#   The bitmap of the display list will be saved into the file.
#
def cmd_screenshot(eve, filename, address=0x10000):
    assert(type(eve) == evelib.EVE2)
    global oneshot 
    if (oneshot):
        oneshot = False

        print(f"Writing screenshot to file \"{filename}\"...")
        with open(filename, "wb") as f:

            # Store the values in REG_RE_DEST and REG_RE_FORMAT
            # Use a safe place - the RAM_REPORT register should not be touched
            # during normal operation of the coprocessor.
            eve.CMD_REGREAD(eve.REG_RE_DEST, 0)
            eve.CMD_RESULT(eve.RAM_REPORT + 64)
            eve.CMD_REGREAD(eve.REG_RE_FORMAT, 0)
            eve.CMD_RESULT(eve.RAM_REPORT + 68)

            # Set the format to RGB8 and the render destination to the specified
            # place in RAM_G
            eve.CMD_REGWRITE(eve.REG_RE_DEST, address)
            eve.CMD_REGWRITE(eve.REG_RE_FORMAT, eve.FORMAT_RGB8)
            
            # Draw the screen to the RAM_G destination
            eve.DISPLAY()
            eve.CMD_GRAPHICSFINISH()
            eve.CMD_SWAP()
            
            # Wait until render engin completes
            eve.CMD_DLSTART()

            # BMP values are stored little endian.
            # BMP Header
            # Offset 0x0, 2 bytes - ID field (42h, 4Dh)
            h = b'\x42\x4d'
            # Offset 0x2, 4 bytes - File size including header.
            # Work out the size of the screen dump.
            # Multiply width x height x number of byts per pixel, add on header size.
            px = eve.EVE_DISP_WIDTH * eve.EVE_DISP_HEIGHT * 3 # FORMAT_RGB8 is 24 bit graphics
            h += struct.pack("I", px + 128)
            # pad
            h += b'\x00\x00\x00\x00'
            # Offset 0x0a, 4 bytes - Offset to bitmap data
            h += b'\x80\x00\x00\x00'
            # DIB header
            # Offset 0x0e, 4 bytes - Number of bytes in header
            h += b'\x6c\x00\x00\x00'
            # Offset 0x12, 4 bytes - Width
            h += struct.pack("I", eve.EVE_DISP_WIDTH)
            # Offset 0x16, 4 bytes - Height
            h += struct.pack("I", (eve.EVE_DISP_HEIGHT +-1) ^ 0xffffffff)
            # Offset 0x1a, 2 bytes - Number of colour planes.
            h += b'\xff\xff'
            # Offset 0x1c, 2 bytes - Number of bits per pixel.
            h += b'\x18\x00'
            # Offset 0x1e, 4 bytes - Compression. BI_BITFIELDS
            h += b'\x03\x00\x00\x00'
            # Offset 0x22, 4 bytes - Size of raw bitmap data.
            h += struct.pack("I", px)
            # Offset 0x26 and 0x2a, 4 bytes - DPI
            h += b'\x13\x0b\x00\x00'
            h += b'\x13\x0b\x00\x00'
            # Pad
            h += b'\x00\x00\x00\x00\x00\x00\x00\x00'
            # Offset 0x36, 4 bytes - Red bitmask
            h += b'\x00\x00\xff\x00'
            # Offset 0x3a, 4 bytes - Green bitmask
            h += b'\x00\xff\x00\x00'
            # Offset 0x3a, 4 bytes - Blue bitmask
            h += b'\xff\x00\x00\x00'
            # Pad
            h += b'\x00\x00\x00\x00'
            # Offset 0x46, 4 bytes - Colour space "Win "
            h += b' niW'
            # Pad header to 128 bytes
            while (len(h) < 128):
                h += b'\x00'
            
            # Read bitmap data from RAM_G
            s = eve.LIB_ReadDataFromRAMG(px, address)
            
            # Write header to file
            f.write(h)
            # Write bitmap data to file
            f.write(s)

            # Revert the render destination and format
            eve.CMD_DLSTART()
            eve.CMD_REGREAD(eve.RAM_REPORT + 64, 0)
            eve.CMD_RESULT(eve.REG_RE_DEST)
            eve.CMD_REGREAD(eve.RAM_REPORT + 68, 0)
            eve.CMD_RESULT(eve.REG_RE_FORMAT)
            eve.LIB_AwaitCoProEmpty()
        
        print(f"completed.")
