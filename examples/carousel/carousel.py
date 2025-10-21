# Typical command line:
# python carousel.py --connector ft4232h standard
import sys

# Add the library directories to the module search path.
sys.path.append('../..')
sys.path.append('../../bteve2')

# This module provides the connector to the EVE hardware.
import apprunner

logo_handle =  7

def error_screen(eve, message):
        print(message)
        # Start drawing test screen.
        eve.LIB_BeginCoProList()
        eve.CMD_DLSTART()
        eve.CLEAR_COLOR_RGB(0, 0, 0)
        eve.CLEAR(1,1,1)
        eve.COLOR_RGB(255, 255, 255)
        eve.CMD_TEXT(eve.EVE_DISP_WIDTH // 2, eve.EVE_DISP_HEIGHT // 2, 34, eve.OPT_CENTER, message)
        eve.DISPLAY()
        eve.CMD_SWAP()
        eve.LIB_EndCoProList()
        eve.LIB_AwaitCoProEmpty()
        while True:
            pass

def eve_display(eve):
    counter = 0
    key = 0
    keyprev = 0

    eve.LIB_BeginCoProList()
    eve.LIB_EndCoProList()
    result = eve.LIB_SDAttach(eve.OPT_IS_SD)
    print("CMD_SDATTACH result", result)

    eve.LIB_BeginCoProList()
    eve.LIB_EndCoProList()
    # Load a huge amount of file data into RAMG
    result = eve.LIB_FSDir(0, 100*1024, "")
    print("CMD_FSDIR result", result)

    dirlist = []
    ptr = 0
    ptr_a = ptr

    while True:
        # Longest file name is 256 characters (aligned)
        chunk = eve.LIB_ReadDataFromRAMG(256 + 4, ptr_a)
        # Dealign chunk
        chunk_a = chunk[ptr - ptr_a:]
        # Find first nul terminator
        for i,c in enumerate(chunk_a):
            if c == 0:
                chunk_a = chunk_a[:i]
                break
        # Decode to a string
        file = chunk_a.decode('utf-8', 'ignore')
        # Add to file list if valid
        if len(file):
            dirlist.append(file)
            ptr += 1
            ptr += len(file)
            ptr_a = ptr & (~3)
        else:
            break

    # Filter image files on the SD card
    imagelist = []
    for f in dirlist:
        if f.upper().endswith('.JPG'):
            imagelist.append(f)
        if f.upper().endswith('.PNG'):
            imagelist.append(f)

    # List available files on the SD card
    print("Image files: ", end="")
    for i in imagelist:
        print(i, end=" ")
    print()

    if len(imagelist) == 0:
        error_screen(eve, "No image files on disk")

    address = 0
    imageprops = []
    
    for i, img in enumerate(imagelist):
        print(imagelist[i])

        eve.LIB_BeginCoProList()
        result = eve.LIB_FSSource(imagelist[i])
        print("CMD_FSSOURCE result", result)

        eve.LIB_BeginCoProList()
        eve.BEGIN(eve.BEGIN_BITMAPS)
        eve.BITMAP_HANDLE(logo_handle)
        eve.CMD_LOADIMAGE(address, eve.OPT_FS | eve.OPT_FULLSCREEN)
        eve.DISPLAY()
        eve.CMD_SWAP()
        eve.LIB_EndCoProList()
        eve.LIB_AwaitCoProEmpty()

        eve.LIB_BeginCoProList()
        props = eve.LIB_GetProps()

        (ptr, width, height) = props
        print(f"Get Props for {imagelist[counter]} ptr = {ptr:x} width {width} height {height}")
        if width > 0 and height > 0:
            imageprops.append(props)

        eve.LIB_BeginCoProList()
        next = eve.LIB_GetPtr()
        
        address = next

    if len(imageprops) == 0:
        error_screen(eve, "No valid image files on disk")

    # Force an update on first pass
    keyprev = -1
    key = 100
    
    while True:
        props = imageprops[counter]
        (ptr, width, height) = props

        # Start drawing test screen.
        eve.LIB_BeginCoProList()
        eve.CMD_DLSTART()
        eve.CLEAR_COLOR_RGB(0, 0, 0)
        eve.CLEAR(1,1,1)
        eve.COLOR_RGB(255, 255, 255)

        eve.TAG(100)
        eve.BEGIN(eve.BEGIN_BITMAPS)
        eve.BITMAP_HANDLE(logo_handle)
        eve.CMD_SETBITMAP(ptr, eve.FORMAT_RGB565, width, height)
        eve.VERTEX2F(0, 0)

        eve.DISPLAY()
        eve.CMD_SWAP()
        eve.LIB_EndCoProList()
        eve.LIB_AwaitCoProEmpty()

        # Read the tag register on the device
        key = eve.rd32(eve.REG_TOUCH_TAG)

        # Debounce keys.
        if (key != keyprev):
            keyprev = key

            if (key == 100):
                counter += 1
                if counter == len(imageprops):
                    counter = 0

                props = imageprops[counter]
                (ptr, width, height) = props
                print(f"Carousel Props for {imagelist[counter]} ptr = {ptr:x} width {width} height {height}")
                
def carousel(eve):
    font_end = None

    # Calibrate the display
    print("Calibrating display...\n")
    # Calibrate screen if necessary.
    eve.LIB_AutoCalibrate()

    # Start example code
    print("Starting demo:")
    eve_display(eve)

apprunner.run(carousel)
