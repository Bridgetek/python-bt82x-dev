# Typical command line:
# python dronefpv.py --connector ft4222module
import sys
import math
import struct
import time

# Add the library directories to the module search path.
sys.path.append('../..')
sys.path.append('../../bteve2')

# This module provides the connector to the EVE hardware.
import apprunner
# Import the patch file required by this code.
import patch_dronefpv as patch

# Load source code from the "snippets" directory.
sys.path.append('../snippets')
import eveflightcontrols

# Set to non-zero to take a screenshot to SD card after
# the number of frames set in the value.
take_screenshot = 0

HND_LVDSRX = 1

# Select the mode for the input signal on LVDS
dualchannel = False

if dualchannel:
    # Incoming signal is dual channel LVDS at 1920 x 1080
    # Jumpers on HDMI to LVDS Converter Board CN27: S0 on, S1 off, S2 off, S3 on
    LVDSRX_W = 1920
    LVDSRX_H = 1080
    LVDSRX_CORE_SETUP_VALUE = 0x03   # 2 channels, two pixels per clock
    LVDSRX_SETUP_VALUE      = 0x17   # One pixel per clock, 2 channels, VESA 24
    LVDSRX_CTRL_VALUE       = 0x8c8c # Ch0 Deskew 0x8, Ch0 clock sel, Frange 0x2
else:
    # Incoming signal is single channel LVDS at 1024 x 768
    # Jumpers on HDMI to LVDS Converter Board CN27: S0 off, S1 on, S2 off, S3 off
    LVDSRX_W = 1024
    LVDSRX_H = 768
    LVDSRX_CORE_SETUP_VALUE = 0x00   # 1 channels, one pixel per clock
    LVDSRX_SETUP_VALUE      = 0x14   # One pixel per clock, 1 channel, VESA 24
    LVDSRX_CTRL_VALUE       = 0x008c # Ch0 Deskew 0x8, Ch0 clock sel, Frange 0x2

def sdattach(eve):
    r = eve.LIB_SDAttach(eve.OPT_IS_SD)
    if r != 0:
        print(f"Could not attach SD card.")
        print(eve.LIB_SDCardError(r))
    return r

def screenshot(eve, filename):
    print(f"Writing screenshot to file \"{filename}\"...")
    r = eve.LIB_FSSnapShot(eve, 0x10000, filename)
    if r != 0:
        print(f"Could not write screenshot to file \"{filename}\".")
        print(eve.LIB_SDCardError(r))
    return r

# Display video with overlays

def video_LVDS(eve):
    global take_screenshot

    print("Starting LVDS...")
    eve.LIB_BeginCoProList()
    eve.CMD_DLSTART()
    eve.CLEAR_COLOR_RGB(0, 80, 0)
    eve.CLEAR(1,1,1)
    eve.CMD_TEXT(eve.EVE_DISP_WIDTH//2, eve.EVE_DISP_HEIGHT//2, 28, eve.OPT_CENTER, "Starting LVDS...")
    eve.DISPLAY()
    eve.CMD_SWAP()
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()

    # Size of the overlay controls
    dial_radius = 200

    # Variables detemining how the animation of the widget appears
    anim_pitch = 1.5
    anim_climb = 0.3
    anim_roll = 1
    # Limits of animation positions
    max_pitch = 60
    max_climb = 20
    max_roll = 50
    # Animation counter
    anim = 0

    # Variables to have attitude indicator readings
    pitch = 0
    climb = 0
    roll = 0
    
    if take_screenshot:
        if sdattach(eve) != 0:
            return
    
    lvds_connected = 1

    eve.LIB_BeginCoProList()
    # LVDSRX System registers
    # This must be swapchain2
    eve.CMD_REGWRITE(eve.REG_LVDSRX_CORE_DEST, eve.SWAPCHAIN_2)
    eve.CMD_REGWRITE(eve.REG_LVDSRX_CORE_FORMAT, eve.FORMAT_RGB8)
    eve.CMD_REGWRITE(eve.REG_LVDSRX_CORE_DITHER, 0)
    eve.CMD_REGWRITE(eve.REG_LVDSRX_CORE_CAPTURE, 1)

    # LVDSRX_CORE_SETUP register
    eve.CMD_REGWRITE(eve.REG_LVDSRX_CORE_SETUP, LVDSRX_CORE_SETUP_VALUE)
    eve.CMD_REGWRITE(eve.REG_LVDSRX_CORE_ENABLE, 1)

    # LVDS startup
    eve.CMD_LVDSSETUP(LVDSRX_SETUP_VALUE, LVDSRX_CTRL_VALUE)
    eve.CMD_LVDSSTART()

    # Get the memory address of the SWAPCHAIN_2 buffer
    eve.CMD_WAITCOND(eve.REG_SC2_STATUS, eve.TEST_EQUAL, 1, 1)
    eve.CMD_REGWRITE(eve.REG_SC2_STATUS, 0x3)
    eve.CMD_REGREAD(eve.REG_SC2_ADDR, 0)
    eve.LIB_EndCoProList()
    lvdsrx_data_addr_prev = 0
    lvdsrx_data_addr_new = 0
    lvdsrx_data_addr = eve.LIB_GetResult()

    # Variables detemining how the animation of the widget appears
    anim_pitch = 1.5
    anim_climb = 0.3
    anim_roll = 1
    anim_alt = 0.05
    # Limits of animation positions
    max_pitch = 60
    max_climb = 20
    max_roll = 50
    max_alt = 9500
    # Animation counter
    anim = 0

    # Variables to have attitude indicator readings
    pitch = 0
    climb = 0
    roll = 0
    alt = 0
    
    # Variables for size and position
    # Centre the widgets on the incoming video
    xatt = dial_radius
    yatt = LVDSRX_H - dial_radius
    xalt = LVDSRX_W - dial_radius
    yalt = LVDSRX_H - dial_radius

    # Performance counter
    count = 0

    print("Starting Main Loop...")
    eve.LIB_BeginCoProList()
    eve.CMD_DLSTART()
    eve.CLEAR_COLOR_RGB(0, 80, 0)
    eve.CLEAR(1,1,1)
    eve.CMD_TEXT(eve.EVE_DISP_WIDTH//2, eve.EVE_DISP_HEIGHT//2, 28, eve.OPT_CENTER, "Starting Main Loop...")
    eve.DISPLAY()
    eve.CMD_SWAP()
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()

    # Main loop
    while 1:
        frames = 30
        if (count == 0):
            tic = time.perf_counter()
        if (count == frames):
            toc = time.perf_counter()
            print(f"{frames} takes {toc - tic:0.3f} seconds")
            count = 0
        else:
            count = count + 1

        use_ext = True
        # Test for LVDS connection
        # Get the memory address of the current SWAPCHAIN_2 buffer
        eve.LIB_BeginCoProList()
        eve.CMD_WAITCOND(eve.REG_SC2_STATUS, eve.TEST_EQUAL, 3, 3)
        eve.CMD_REGWRITE(eve.REG_SC2_STATUS, 0x3)
        eve.CMD_REGREAD(eve.REG_SC2_ADDR, 0)
        if use_ext:
            eve.CMD_LVDSCONN(0)
        eve.LIB_EndCoProList()
        eve.LIB_AwaitCoProEmpty()

        if use_ext:
            conn = eve.LIB_GetResult(1)
            lvdsrx_data_addr_new = eve.LIB_GetResult(3)
        else:
            conn = 0
            lvdsrx_data_addr_new = eve.LIB_GetResult(1)

        stat = eve.rd32(eve.REG_LVDSRX_STAT)
        setup = eve.rd32(eve.REG_LVDSRX_SETUP)
        
        if not use_ext:
            c1 = ((stat >> 28) != 0)
            if False:
                c2 = (((stat >> 24) & 3) == 3)
            else:
                c2 = (((setup & 2) + 1) & (stat >> 24) != 0)
            c3 = ((stat & 0xffffff) == 0)
            if c1 and c2 and c3:
                conn = 1
            print(f"{conn} {lvds_connected} {stat:x} {setup:x} {c1} {c2} {c3}")
        else:
            print(f"{conn} {lvds_connected} {stat:x} {setup:x}")

        if (conn == 0):
            # Not connected or synced
            if (lvds_connected == 2) : 
                # Disable LVDS
                print("LVDS sync lost stopped")
                eve.LIB_BeginCoProList()
                eve.CMD_LVDSSTOP()
                eve.LIB_EndCoProList()
                eve.LIB_AwaitCoProEmpty()
                print("stopped")
                lvds_connected = 0
            if (lvds_connected == 0) : 
                # Enable LVDS
                print("LVDS re-start")
                eve.LIB_BeginCoProList()
                eve.CMD_LVDSSTART()
                eve.LIB_EndCoProList()
                eve.LIB_AwaitCoProEmpty()
                print("started")
                lvds_connected = 1
        else:
            if (lvds_connected == 1) : 
                # Sync established
                print("LVDS re-synced")
                # 2 is normal connected state
                lvds_connected = 2

        if (lvdsrx_data_addr != lvdsrx_data_addr_new):

            lvdsrx_data_addr_prev = lvdsrx_data_addr
            lvdsrx_data_addr = lvdsrx_data_addr_new

            eve.LIB_BeginCoProList()
            eve.CMD_DLSTART()
            eve.CLEAR_COLOR_RGB(0, 80, 0)
            eve.CLEAR(1,1,1)

            if (lvds_connected == 2):
                eve.BEGIN(eve.BEGIN_BITMAPS) 
                eve.BITMAP_HANDLE(HND_LVDSRX)
                eve.CMD_SETBITMAP(lvdsrx_data_addr_prev, eve.FORMAT_RGB8, LVDSRX_W, LVDSRX_H)
                eve.VERTEX2F(0, 0)

            eveflightcontrols.attwidget(eve, xatt, yatt, dial_radius, pitch, climb, roll)
            eveflightcontrols.altwidget(eve, xalt, yalt, dial_radius, alt)

            eve.DISPLAY()
            if take_screenshot:
                take_screenshot -= 1
                if take_screenshot == 0:
                    tic = time.perf_counter()
                    screenshot(eve, "dronefpv.bmp")
                    toc = time.perf_counter()
                    print(f"Screenshot takes {toc - tic:0.3f} seconds")
            eve.CMD_SWAP()
            eve.LIB_EndCoProList()
            eve.LIB_AwaitCoProEmpty()

            pitch = max_pitch * math.sin(anim * (math.pi/360) * anim_pitch)
            climb = max_climb * math.sin(anim * (math.pi/360) * anim_climb)
            roll = max_roll * math.sin(anim * (math.pi/360) * anim_roll)
            alt = (max_alt / 2) + (max_alt / 2) * math.sin(anim * (math.pi/360) * anim_alt)
            anim+=1

def eve_display(eve):

    eve.LIB_BeginCoProList()
    eve.CMD_REGWRITE(eve.REG_SC2_SIZE, 2)
    # Start the swapchain 2 buffer at 0x1000000 - second buffer immediately after
    # VM820C board has maximum address of 0x2000000 - 0x280000 = 0x1D80000
    # SC2 will be between addresses 0x400 and 0xbddc00
    eve.CMD_REGWRITE(eve.REG_SC2_PTR0, (1 << 24));
    eve.CMD_REGWRITE(eve.REG_SC2_PTR1, (1 << 24) + (LVDSRX_W * LVDSRX_H * 3));
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()
    print(f"Swapchain 2: 0x{eve.rd32(eve.REG_SC2_PTR0):x} and 0x{eve.rd32(eve.REG_SC2_PTR1):x} to 0x{(1 << 24) + (LVDSRX_W * LVDSRX_H * 3 * 2):x}")

    video_LVDS(eve)
    
def attitude(eve):
    # Calibrate the display
    print("Calibrating display...")
    # Calibrate screen if necessary. 
    # Don't do this for now.
    #eve.LIB_AutoCalibrate()

    # Start example code
    print("Starting demo:")
    eve.LIB_BeginCoProList()
    eve.CMD_DLSTART()
    eve.CLEAR_COLOR_RGB(0, 80, 0)
    eve.CLEAR(1,1,1)
    eve.CMD_TEXT(eve.EVE_DISP_WIDTH//2, eve.EVE_DISP_HEIGHT//2, 28, eve.OPT_CENTER, "Starting Demo...")
    eve.DISPLAY()
    eve.CMD_SWAP()
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()

    eve_display(eve)

apprunner.run(attitude, patch)
