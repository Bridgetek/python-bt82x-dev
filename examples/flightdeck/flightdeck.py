# Typical command line:
# python attitude.py --connector ft4222module
import sys
import math

# Add the library directories to the module search path.
sys.path.append('../..')
sys.path.append('../../bteve2')

# This module provides the connector to the EVE hardware.
import apprunner

# Load source code from the "snippets" directory.
sys.path.append('../snippets')
import eveflightcontrols

e_disabled = False
e_enabled = True

def rgb(t):
    red, green, blue = t[0], t[1], t[2]
    return ((int(red) & 255) << 16) | ((int(green) & 255) << 8) | ((int(blue) & 255))

def eve_display(eve):

    # Size of the indicators on the dashboard
    dial_radius = min(eve.EVE_DISP_HEIGHT, eve.EVE_DISP_WIDTH) // 3

    key = 0
    keyprev = 0

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
    # Centre the widgets
    xatt = (eve.EVE_DISP_WIDTH / 4)
    yatt = (eve.EVE_DISP_HEIGHT / 2)
    xalt = (eve.EVE_DISP_WIDTH * 3 / 4)
    yalt = (eve.EVE_DISP_HEIGHT / 2)

    while True:

        eve.LIB_BeginCoProList()
        eve.CMD_DLSTART()
        eve.CLEAR_COLOR_RGB(0, 0, 0)
        eve.CLEAR(1,1,1)

        eve.CMD_CGRADIENT(eve.CGRADIENT_CORNER_ZERO, 0, 0, eve.EVE_DISP_WIDTH, eve.EVE_DISP_HEIGHT, 0x000020, 0x000080)

        eveflightcontrols.aiwidget(eve, xatt, yatt, dial_radius, pitch, climb, roll)
        eveflightcontrols.altwidget(eve, xalt, yalt, dial_radius, alt)

        eve.DISPLAY()
        eve.CMD_SWAP()
        eve.LIB_EndCoProList()
        eve.LIB_AwaitCoProEmpty()

        pitch = max_pitch * math.sin(anim * (math.pi/360) * anim_pitch)
        climb = max_climb * math.sin(anim * (math.pi/360) * anim_climb)
        roll = max_roll * math.sin(anim * (math.pi/360) * anim_roll)
        alt = (max_alt / 2) + (max_alt / 2) * math.sin(anim * (math.pi/360) * anim_alt)
        anim+=1

        # No keypresses involved yet
        #while (eve_read_tag(&key) == 0)

        # Debounce keys.
        if (key != keyprev):
            keyprev = key


def attitude(eve):
    # Calibrate the display
    print("Calibrating display...")
    # Calibrate screen if necessary. 
    # Don't do this for now.
    #eve.LIB_AutoCalibrate()

    # Start example code
    print("Starting demo:")
    eve_display(eve)

apprunner.run(attitude)
