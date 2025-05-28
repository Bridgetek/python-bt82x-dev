import sys

# This is the EVE library.
import bteve2 as evelib

# EVE Image Properties
#
# Calling format:
#   eveimageproperties.get(eve, img_data)
#
# Description:
#   Classify an image file as it will be loaded by CMD_LOADIMAGE.
#   Obtain the width and height of the image and the default
#   bitmap format that CMD_LOADIMAGE will assign to it in RAM_G.
#
# Parameters:
#   eve: Handle to class of bteve2.
#   img_data: array containing binary data from image file.
#
# Returns:
#   This returns a tuple with the width, height and imagetype.
#   If the format is not supported then it will raise an exception.
#
def get(eve, img_data, verbose = 0):
    # Check for file types and get width and heights
    if img_data[0:8] == b'\x89PNG\x0d\x0a\x1a\x0a':
        # PNG File
        chunk = 8
        while chunk < len(img_data):
            clen = int.from_bytes(img_data[chunk:chunk+4], byteorder='big')
            ctype = img_data[chunk+4:chunk+8]
            if (ctype == b'IHDR'):
                # get height and width
                width = int.from_bytes(img_data[chunk+8:chunk+12], byteorder='big')
                height = int.from_bytes(img_data[chunk+12:chunk+16], byteorder='big')
                # Get image type b&w/truecolour
                colourd = int(img_data[chunk+14])
                if colourd == 0: imagetype = eve.L8
                elif colourd == 2: imagetype = eve.FORMAT_RGB565
                elif colourd == 3: imagetype = eve.FORMAT_PALETTEDARGB8
                elif colourd == 4: imagetype = eve.FORMAT_LA8
                elif colourd == 6: imagetype = eve.FORMAT_ARGB4
                else: raise (f"Unsupported PNG colour depth {colourd}")
            chunk += (clen + 12)
    elif (img_data[0:4] == b'\xff\xd8\xff\xe0') and (img_data[6:10] == b'JFIF'):
        # JPG File
        chunk = 0
        p = 0
        for i,d in enumerate(img_data):
            if p == 0xff and d != 0xff:
                # Start of a segment marker (after the 0xff)
                if d == 0xc0: 
                    height = int.from_bytes(img_data[i+4:i+6], byteorder='big')
                    width = int.from_bytes(img_data[i+6:i+8], byteorder='big')
                    # Get image tpye b&w/truecolour
                    colourd = int(img_data[i+8])
                    if colourd == 0: imagetype = eve.FORMAT_L8
                    elif colourd == 3: imagetype = eve.FORMAT_RGB565
                    else: raise (f"Unsupported JPG colour depth {colourd}")
            p = d
    else:
        raise (f"Unsupported image format")
    
    if verbose: print(f"Image type: {imagetype}")
    if verbose: print(f"Image size: {width} x {height} pixels.")

    return (width, height, imagetype)
