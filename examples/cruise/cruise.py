# Typical command line:
# python cruise.py --connector ft4222module
import sys

# Add the library directories to the module search path.
sys.path.append('../..')
sys.path.append('../../bteve2')

# This module provides the connector to the EVE hardware.
import apprunner

# Load the sevensegment source code from the "common" directory.
sys.path.append('../common')
import sevensegment 

# Draw a stencil to show a circular display
TARGET_CIRCULAR = True
TARGET_SCREEN_RADIUS = 240
# Font for km/h or other units
UNITS_FONT = 25
# Font for action areas
ACTION_FONT = 31
# Font for extenal controls
EXT_FONT = 29
# Location for display zones
TARGET_AREA_TOP = ((TARGET_SCREEN_RADIUS * 3) // 10)
TARGET_AREA_BOTTOM = ((TARGET_SCREEN_RADIUS * 2) - TARGET_AREA_TOP)
def TARGET_SCREEN_MIRROR(x): ((TARGET_SCREEN_RADIUS * 2) - x)
# Seven segment size and gap between segments
SEGMENT_SIZE = 100
SEGMENT_GAP = (SEGMENT_SIZE + ((SEGMENT_SIZE * 4) // 10))
# Maximum speed
MAX_SPEED = 160

scrbg = (0x00, 0x00, 0x00)
dullfg = (0x80, 0x00, 0x00)
dullbg = (0x20, 0x00, 0x00)
redfg = (0xff, 0x00, 0x00)
redbg = (0x30, 0x00, 0x00)
grnfg = (0x00, 0xff, 0x00)
grnbg = (0x00, 0x30, 0x00)
blufg = (0x00, 0x00, 0xff)
blubg = (0x00, 0x00, 0x30)

e_disabled = False
e_enabled = True

def rgb(t):
    red, green, blue = t[0], t[1], t[2]
    return ((int(red) & 255) << 16) | ((int(green) & 255) << 8) | ((int(blue) & 255))

def eve_display(eve):
    set_speed = 65
    current_speed = 55

    key = 0
    keyprev = 0
    x, y = 0, 0

    cruise_arm = e_disabled
    cruise_active = e_disabled

    while True:
        eve.LIB_BeginCoProList()
        eve.CMD_DLSTART()
        eve.CLEAR_COLOR_RGB(0, 0, 0)
        eve.CLEAR(1,1,1)

        fg_setpt = (0xff, 0xff, 0xff)
        bg_setpt = (0x00, 0x00, 0x00)

        # Colour selections
        if (cruise_arm == e_disabled):
            fg_setpt = dullfg
            bg_setpt = dullbg
        elif (cruise_arm == e_enabled):
            if (cruise_active == e_disabled):
                fg_setpt = redfg
                bg_setpt = redbg
            else:
                fg_setpt = grnfg
                bg_setpt = grnbg

        if TARGET_CIRCULAR:
            # Stencil for a circular screen
            eve.COLOR_RGB(0, 0, 0)
            eve.STENCIL_OP(eve.STENCIL_KEEP, eve.STENCIL_INCR)
            eve.BEGIN(eve.BEGIN_POINTS)
            eve.POINT_SIZE(TARGET_SCREEN_RADIUS * 16)
            eve.VERTEX2F(TARGET_SCREEN_RADIUS * 16, TARGET_SCREEN_RADIUS * 16)
            eve.STENCIL_FUNC(eve.TEST_NOTEQUAL, 0, 255)

        # Top centre of action buttons
        x = TARGET_SCREEN_RADIUS
        y = (TARGET_SCREEN_RADIUS * 3 // 10)

        # Set Cancel Resume Buttons
        eve.COLOR(0xffffff)

        # Gradient at the top
        eve.SAVE_CONTEXT()
        eve.SCISSOR_XY(0, 0)
        eve.SCISSOR_SIZE(TARGET_SCREEN_RADIUS * 2, (TARGET_SCREEN_RADIUS - SEGMENT_SIZE))
        if ((cruise_arm == e_enabled) and (cruise_active == e_disabled)):
            # Resume at the top.
            eve.CMD_GRADIENT(TARGET_SCREEN_RADIUS, 0, rgb(grnfg), TARGET_SCREEN_RADIUS, SEGMENT_SIZE, rgb(scrbg))
        elif ((cruise_arm == e_disabled) or ((cruise_arm == e_enabled) and (cruise_active == e_enabled))):
            # Preset speeds when cruise disabled or active
            eve.CMD_GRADIENT(TARGET_SCREEN_RADIUS, 0, rgb(grnfg), TARGET_SCREEN_RADIUS, SEGMENT_SIZE, rgb(scrbg))
        eve.RESTORE_CONTEXT()

        # Gradients at the bottom
        eve.SAVE_CONTEXT()
        eve.SCISSOR_XY(0, (TARGET_SCREEN_RADIUS + SEGMENT_SIZE))
        eve.SCISSOR_SIZE(TARGET_SCREEN_RADIUS * 2, (TARGET_SCREEN_RADIUS - SEGMENT_SIZE) + 1)
        if (cruise_arm == e_enabled):
            if (cruise_active == e_disabled):
                # Set at the bottom.
                eve.CMD_GRADIENT(TARGET_SCREEN_RADIUS, (TARGET_SCREEN_RADIUS + SEGMENT_SIZE), rgb(scrbg), TARGET_SCREEN_RADIUS, TARGET_SCREEN_RADIUS * 2, rgb(grnfg))
            else:
                # Cancel at the bottom.
                eve.CMD_GRADIENT(TARGET_SCREEN_RADIUS, (TARGET_SCREEN_RADIUS + SEGMENT_SIZE), rgb(scrbg), TARGET_SCREEN_RADIUS, TARGET_SCREEN_RADIUS * 2, rgb(redfg))
        else:
            # Cancel at the bottom.
            pass
        eve.RESTORE_CONTEXT()

        # Buttons at the top
        if ((cruise_arm == e_enabled) and (cruise_active == e_disabled)):
            # Resume at the top.
            eve.CMD_TEXT(TARGET_SCREEN_RADIUS, (TARGET_AREA_TOP * 3) / 4, ACTION_FONT, eve.OPT_CENTER, "RESUME")
        elif ((cruise_arm == e_disabled) or ((cruise_arm == e_enabled) and (cruise_active == e_enabled))):
            # Preset speeds when cruise disabled or active
            eve.TAG(10)
            eve.CMD_TEXT(TARGET_SCREEN_RADIUS - SEGMENT_SIZE, TARGET_AREA_TOP, ACTION_FONT, eve.OPT_CENTER, "50")
            eve.TAG(11)
            eve.CMD_TEXT(TARGET_SCREEN_RADIUS, (TARGET_AREA_TOP * 3) / 4, ACTION_FONT, eve.OPT_CENTER, "80")
            eve.TAG(12)
            eve.CMD_TEXT(TARGET_SCREEN_RADIUS + SEGMENT_SIZE, TARGET_AREA_TOP, ACTION_FONT, eve.OPT_CENTER, "100")
        
        # Buttons at the bottom
        eve.TAG(20)
        if (cruise_arm == e_enabled):
            if (cruise_active == e_disabled):
                # Set at the bottom.
                eve.CMD_TEXT(TARGET_SCREEN_RADIUS, TARGET_AREA_BOTTOM, ACTION_FONT, eve.OPT_CENTER, "SET")
            else:
                # Cancel at the bottom.
                eve.CMD_TEXT(TARGET_SCREEN_RADIUS, TARGET_AREA_BOTTOM, ACTION_FONT, eve.OPT_CENTER, "CANCEL")
        else:
            # Cancel at the bottom.
            eve.CMD_TEXT(TARGET_SCREEN_RADIUS, TARGET_AREA_BOTTOM, ACTION_FONT, eve.OPT_CENTER, "DISABLED")

        # Top left of seven segment display
        x = TARGET_SCREEN_RADIUS - (((SEGMENT_GAP * 2) + SEGMENT_SIZE) // 2)
        y = TARGET_SCREEN_RADIUS - SEGMENT_SIZE

        # Main Cruise set point
        eve.COLOR(rgb(fg_setpt))
        eve.CMD_TEXT(x + (((SEGMENT_GAP * 2) + SEGMENT_SIZE) / 2), y - eve.ROMFONT_HEIGHTS[UNITS_FONT], UNITS_FONT, eve.OPT_CENTER, "km/h")
        if (cruise_arm == e_enabled):
            sevensegment.cmd_sevenseg(eve, x + (SEGMENT_GAP * 0), y, SEGMENT_SIZE, ((set_speed/100)%10), fg_setpt, bg_setpt)
            sevensegment.cmd_sevenseg(eve, x + (SEGMENT_GAP * 1), y, SEGMENT_SIZE, ((set_speed/10)%10), fg_setpt, bg_setpt)
            sevensegment.cmd_sevenseg(eve, x + (SEGMENT_GAP * 2), y, SEGMENT_SIZE, ((set_speed/1)%10), fg_setpt, bg_setpt)
        else:
            sevensegment.cmd_sevenseg(eve, x + (SEGMENT_GAP * 0), y, SEGMENT_SIZE, 16, fg_setpt, bg_setpt)
            sevensegment.cmd_sevenseg(eve, x + (SEGMENT_GAP * 1), y, SEGMENT_SIZE, 16, fg_setpt, bg_setpt)
            sevensegment.cmd_sevenseg(eve, x + (SEGMENT_GAP * 2), y, SEGMENT_SIZE, 16, fg_setpt, bg_setpt)
        
        # See through tag areas for top area
        eve.COLOR_A(0)
        eve.TAG(10)
        eve.BEGIN(eve.BEGIN_RECTS)
        eve.LINE_WIDTH(16)
        eve.VERTEX2F(0, 0)
        eve.VERTEX2F((TARGET_SCREEN_RADIUS - (SEGMENT_SIZE / 2)) * 16, (TARGET_SCREEN_RADIUS - SEGMENT_SIZE) * 16)
        eve.TAG(11)
        eve.BEGIN(eve.BEGIN_RECTS)
        eve.LINE_WIDTH(16)
        eve.VERTEX2F((TARGET_SCREEN_RADIUS - (SEGMENT_SIZE / 2)) * 16, 0)
        eve.VERTEX2F((TARGET_SCREEN_RADIUS + (SEGMENT_SIZE / 2)) * 16, (TARGET_SCREEN_RADIUS - SEGMENT_SIZE) * 16)
        eve.TAG(12)
        eve.BEGIN(eve.BEGIN_RECTS)
        eve.LINE_WIDTH(16)
        eve.VERTEX2F((TARGET_SCREEN_RADIUS + (SEGMENT_SIZE / 2)) * 16, 0)
        eve.VERTEX2F((TARGET_SCREEN_RADIUS * 2) * 16, (TARGET_SCREEN_RADIUS - SEGMENT_SIZE) * 16)
        # See through tag area for bottom area
        eve.TAG(20)
        eve.BEGIN(eve.BEGIN_RECTS)
        eve.LINE_WIDTH(16)
        eve.VERTEX2F(0, (TARGET_SCREEN_RADIUS + SEGMENT_SIZE) * 16)
        eve.VERTEX2F((TARGET_SCREEN_RADIUS * 2) * 16, (TARGET_SCREEN_RADIUS * 2) * 16)
        # Restore non see throughness
        eve.COLOR_A(255)

        if TARGET_CIRCULAR:
            eve.STENCIL_FUNC(eve.TEST_ALWAYS, 0, 255)

        # Click wheel actions
        eve.COLOR(0xffffff)
        eve.CMD_FGCOLOR(rgb(blufg))
        # Depress wheel, enable/disable cruise.
        eve.TAG(100)
        eve.CMD_BUTTON((TARGET_SCREEN_RADIUS * 2) + 50, 50, 400, (eve.ROMFONT_HEIGHTS[EXT_FONT] * 2), EXT_FONT, 0, "button click")
        # Wheel actions.
        eve.TAG(0)
        eve.CMD_TEXT((TARGET_SCREEN_RADIUS * 2) + 250, 50 + (eve.ROMFONT_HEIGHTS[EXT_FONT] * 3), EXT_FONT, eve.OPT_CENTERX, "turn wheel")
        # Turn clockwise, go faster.
        eve.TAG(101)
        eve.CMD_BUTTON((TARGET_SCREEN_RADIUS * 2) + 250, 50 + (eve.ROMFONT_HEIGHTS[EXT_FONT] * 4), 200, (eve.ROMFONT_HEIGHTS[EXT_FONT] * 2), EXT_FONT, 0, "+")
        # Turn anti-clockwise, go slower.
        eve.TAG(102)
        eve.CMD_BUTTON((TARGET_SCREEN_RADIUS * 2) + 50, 50 + (eve.ROMFONT_HEIGHTS[EXT_FONT] * 4), 200, (eve.ROMFONT_HEIGHTS[EXT_FONT] * 2), EXT_FONT, 0, "-")
        # Car inputs.
        eve.TAG(0)
        eve.CMD_TEXT((TARGET_SCREEN_RADIUS * 2) + 250, 50 + (eve.ROMFONT_HEIGHTS[EXT_FONT] * 7), EXT_FONT, eve.OPT_CENTERX, "road speed")
        eve.TAG(103)
        eve.CMD_SLIDER((TARGET_SCREEN_RADIUS * 2) + 50, 50 + (eve.ROMFONT_HEIGHTS[EXT_FONT] * 9), 400, (eve.ROMFONT_HEIGHTS[EXT_FONT] * 1), 0, (current_speed * 400) / MAX_SPEED, 400)
        eve.CMD_TRACK((TARGET_SCREEN_RADIUS * 2) + 50, 50 + (eve.ROMFONT_HEIGHTS[EXT_FONT] * 9), 400, (eve.ROMFONT_HEIGHTS[EXT_FONT] * 1), 103)
        # Brake!
        eve.TAG(104)
        eve.CMD_FGCOLOR(rgb(redfg))
        eve.CMD_BUTTON((TARGET_SCREEN_RADIUS * 2) + 50, 50 + (eve.ROMFONT_HEIGHTS[EXT_FONT] * 12), 400, (eve.ROMFONT_HEIGHTS[EXT_FONT] * 2), 28, 0, "Brake!")

        eve.DISPLAY()
        eve.CMD_SWAP()
        eve.LIB_EndCoProList()
        eve.LIB_AwaitCoProEmpty()

        #while (eve_read_tag(&key) == 0)

        # Debounce keys.
        if (key != keyprev):
            keyprev = key

            # Conditions for bottom button area
            if ((cruise_arm == e_enabled) and (cruise_active == e_disabled)):
                # SET button when cruise inactive
                if (key == 20):
                    # Update set speed to road speed
                    set_speed = current_speed
                    cruise_active = e_enabled
            elif ((cruise_arm == e_enabled) and (cruise_active == e_enabled)):
                # CANCEL button when cruise active
                if (key == 20):
                    cruise_active = e_disabled

            # Conditions for top button area
            if ((cruise_arm == e_enabled) and (cruise_active == e_disabled)):
                # RESUME button when cruise inactive
                if ((key == 10) or (key == 11) or (key == 12)):
                    # Update road speed to match set speed when active
                    current_speed = set_speed
                    cruise_active = e_enabled
            elif ((cruise_arm == e_disabled) or ((cruise_arm == e_enabled) and (cruise_active == e_enabled))):
                # Preset speeds when cruise disabled or active
                if (key == 10):
                    set_speed = current_speed = 50
                    cruise_arm = e_enabled
                    cruise_active = e_enabled
                elif (key == 11):
                    set_speed = current_speed = 80
                    cruise_arm = e_enabled
                    cruise_active = e_enabled
                elif (key == 12):
                    set_speed = current_speed = 100
                    cruise_arm = e_enabled
                    cruise_active = e_enabled

            # ENABLE/DISABLE cruise (ARM/DISARM)
            if (key == 100):
                if (cruise_arm == e_disabled):
                    cruise_arm = e_enabled
                    cruise_active = e_disabled
                elif (cruise_arm == e_enabled):
                    cruise_arm = e_disabled
            # FASTER button event
            if (key == 101):
                set_speed += 1
                if (set_speed > 120):
                    set_speed = 120
                current_speed = set_speed
            # SLOWER button event
            if (key == 102):
                set_speed -= 1
                if (set_speed < 30):
                    set_speed = 30
                current_speed = set_speed
            # Road speed slider
            if (key == 103):
                tracker = eve.rd32(eve.REG_TRACKER)
                if ((tracker & 0xff) == 103):
                    # 65535 -> MAX_SPEED
                    # 32768 -> MAX_SPEED / 2
                    # 0 -> 0 km/h
                    current_speed = ((tracker >> 16) *  MAX_SPEED) // 65535
            # BRAKE! button event
            if (key == 104):
                cruise_active = e_disabled


def cruise(eve):
    # Calibrate the display
    print("Calibrating display...")
    # Calibrate screen if necessary. 
    # Don't do this for now.
    #eve.LIB_AutoCalibrate()

    # Start example code
    print("Starting demo:")
    eve_display(eve)

apprunner.run(cruise)
