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

TARGET_SCREEN_RADIUS = 350

e_disabled = False
e_enabled = True

def rgb(t):
    red, green, blue = t[0], t[1], t[2]
    return ((int(red) & 255) << 16) | ((int(green) & 255) << 8) | ((int(blue) & 255))

def circ_x(scale, deg):
    return (scale * math.sin(deg/180 * math.pi))
def circ_y(scale, deg):
    return (scale * math.cos(deg/180 * math.pi))

def altwidget(eve, x, y, radius, alt):
    # Like a real altitude instrument it will never go beyond the limits
    alt = max(alt, 0)
    alt = min(alt, 10000)

    # Dimensions of the widget are detemined by the radius
    radius_outer = radius
    radius_b1 = (radius_outer * 39) // 40
    radius_b2 = (radius_outer * 37) // 40
    radius_inner = (radius_outer * 36) // 40
    radius_major = (radius_outer * 30) // 40
    radius_minor = (radius_inner + radius_major) // 2
    # Altitude indicator line widths
    alt_ref_bold = radius_outer * 2 // 10
    alt_ref_narrow = radius_outer * 1 // 10
    alt_needle = radius_outer * 5 // 10

    # Bezel colours
    bezel_col = 0x505050
    bezel_col_bright = 0xaaaaaa
    bezel_col_dark = 0x333333

    alt_reference = 0xffffff
    alt_background = 0x000000
    alt_covering = 0x202020

    eve.VERTEX_FORMAT(0)

    # Draw bezel
    eve.SAVE_CONTEXT()
    eve.CLEAR(0,1,0)
    eve.COLOR(bezel_col)
    # Draw the circles to make the bezel in three levels in the stencil buffer
    eve.STENCIL_OP(eve.STENCIL_INCR, eve.STENCIL_INCR)	# Set the stencil to increment
    eve.BEGIN(eve.BEGIN_POINTS)
    eve.POINT_SIZE(radius_outer * 16)
    eve.VERTEX2F(x, y)
    eve.POINT_SIZE(radius_b1 * 16)
    eve.VERTEX2F(x, y)
    eve.POINT_SIZE(radius_b2 * 16)
    eve.VERTEX2F(x, y)
    eve.POINT_SIZE(radius_inner * 16)
    eve.VERTEX2F(x, y)
    eve.END()
    eve.STENCIL_OP(eve.STENCIL_KEEP, eve.STENCIL_KEEP) # Stop the stencil INCR
    # Gradient (light at top) for outer of bezel
    eve.STENCIL_FUNC(eve.TEST_EQUAL, 1, 255)
    eve.CMD_GRADIENT(x - radius_outer, y + radius_outer, bezel_col_dark, x - radius_outer, y - radius_outer, bezel_col_bright)
    # Flat colour for centre of bezel
    eve.STENCIL_FUNC(eve.TEST_EQUAL, 2, 255)
    eve.POINT_SIZE(radius_outer * 16)
    eve.VERTEX2F(x, y)
    # Gradient (dark at top) for inner of bezel
    eve.STENCIL_FUNC(eve.TEST_EQUAL, 3, 255)
    eve.CMD_GRADIENT(x - radius_outer, y + radius_outer, bezel_col_bright, x - radius_outer, y - radius_outer, bezel_col_dark)
    eve.RESTORE_CONTEXT()

    # Altitude graduations
    eve.SAVE_CONTEXT()
    eve.CLEAR_STENCIL(0)
    eve.CLEAR(0,1,0)
    eve.COLOR(alt_covering)
    eve.STENCIL_OP(eve.STENCIL_KEEP, eve.STENCIL_INCR)
    # Draw ground and sky stencil
    eve.BEGIN(eve.BEGIN_POINTS)
    eve.POINT_SIZE(radius_inner * 16)
    eve.VERTEX2F(x, y)
    eve.POINT_SIZE(radius_minor * 16)
    eve.VERTEX2F(x, y)
    eve.POINT_SIZE(radius_major * 16)
    eve.VERTEX2F(x, y)
    eve.BEGIN(eve.BEGIN_LINES)
    # bold at 1000ft intervals
    eve.STENCIL_FUNC(eve.TEST_NOTEQUAL, 0, 255)
    eve.LINE_WIDTH(alt_ref_bold)
    eve.COLOR(alt_reference)
    for deg in range(0, 10):
        dx1 = x + circ_x(radius_inner, deg * 36)
        dy1 = y - circ_y(radius_inner, deg * 36)
        dx2 = x + circ_x(radius_major, deg * 36)
        dy2 = y - circ_y(radius_major, deg * 36)
        eve.VERTEX2F(dx1, dy1)
        eve.VERTEX2F(dx2, dy2)
    # narrow at 10 and 20 degrees
    eve.LINE_WIDTH(alt_ref_narrow)
    for deg in range(0, 100, 2):
        dx1 = x + circ_x(radius_inner, deg * 3.6)
        dy1 = y - circ_y(radius_inner, deg * 3.6)
        dx2 = x + circ_x(radius_minor, deg * 3.6)
        dy2 = y - circ_y(radius_minor, deg * 3.6)
        eve.VERTEX2F(dx1, dy1)
        eve.VERTEX2F(dx2, dy2)
        #print(deg, dx1, dy1, dx2, dy2)
    eve.STENCIL_FUNC(eve.TEST_ALWAYS, 0, 255)
    eve.COLOR(alt_covering)
    eve.BEGIN(eve.BEGIN_POINTS)
    eve.POINT_SIZE(radius_major * 16)
    eve.VERTEX2F(x, y)
    eve.RESTORE_CONTEXT()

    # Indicators choose a font which is about 1/5th of the radius
    font = len(eve.ROMFONT_HEIGHTS)
    for n in reversed(eve.ROMFONT_HEIGHTS):
        if n < radius_inner / 5:
            break
        font -= 1
    if font:
        font = min(font, len(eve.ROMFONT_HEIGHTS) - 1)
        for deg in range(0, 10):
            dx = x + circ_x(radius_inner * 7 / 10, deg * 36)
            dy = y - circ_y(radius_inner * 7 / 10, deg * 36)
            eve.CMD_NUMBER(dx, dy, font, eve.OPT_CENTER, deg)

        eve.CMD_TEXT(x, y - (radius_inner * 3 / 10), font, eve.OPT_CENTER, "Altitude")
        eve.CMD_TEXT(x, y + (radius_inner * 3 / 10), font, eve.OPT_CENTER, "10000ft")
    # Altitude needle
    eve.SAVE_CONTEXT()
    eve.CLEAR(0,1,0)
    eve.COLOR(alt_reference)
    eve.BEGIN(eve.BEGIN_LINES)
    degthou = alt * 360 / 10000
    deghund = (alt % 1000) * 360 / 100
    dx = x
    dy = y
    dxt1 = x + circ_x(radius_major, degthou)
    dyt1 = y - circ_y(radius_major, degthou)
    dxt2 = x + circ_x((radius_major + radius_minor) / 2, degthou)
    dyt2 = y - circ_y((radius_major + radius_minor) / 2, degthou)
    dxt3 = x + circ_x(radius_minor, degthou)
    dyt3 = y - circ_y(radius_minor, degthou)
    dxh = x + circ_x(radius_major, deghund)
    dyh = y - circ_y(radius_major, deghund)
    for c,a in ((alt_background, 32), (alt_reference, 0)):
        eve.COLOR(c)
        eve.LINE_WIDTH(alt_needle/2 + a)
        eve.VERTEX2F(dx, dy)
        eve.VERTEX2F(dxt3, dyt3)
        eve.VERTEX2F(dx, dy)
        eve.VERTEX2F(dxh, dyh)
        eve.LINE_WIDTH(alt_needle*2/3 + a)
        eve.VERTEX2F(dx, dy)
        eve.VERTEX2F(dxt2, dyt2)
        eve.LINE_WIDTH(alt_needle + a)
        eve.VERTEX2F(dx, dy)
        eve.VERTEX2F(dxt1, dyt1)
    eve.COLOR(alt_background)
    eve.BEGIN(eve.BEGIN_POINTS)
    eve.POINT_SIZE((radius_inner / 5) * 16)
    eve.VERTEX2F(x, y)
    eve.RESTORE_CONTEXT()

def aiwidget(eve, x, y, radius, pitch, climb, roll):
    
    # Dimensions of the widget are detemined by the radius
    radius_outer = radius
    radius_b1 = (radius_outer * 39) // 40
    radius_b2 = (radius_outer * 37) // 40
    radius_inner = (radius_outer * 36) // 40
    radius_roll = (radius_outer * 30) // 40
    radius_bank = (radius_inner + radius_roll) // 2
    # Attitude indicator line widths
    ai_ref_bold = radius_outer * 4 // 10
    ai_ref_narrow = radius_outer * 2 // 10
    # Overlay reference line widths
    ovl_bold = radius_outer * 4 // 10
    ovl_narrow = radius_outer * 2 // 10

    # Bezel colours
    bezel_col = 0x505050
    bezel_col_bright = 0xaaaaaa
    bezel_col_dark = 0x333333
    # Attitude indicator colours for roll and pitch areas
    roll_col_ground = 0x444400
    roll_col_sky = 0x3060aa
    pitch_col_ground = 0x555500
    pitch_col_sky = 0x5070bb
    ai_reference = 0xffffff
    # Overlay reference colours
    ovl_reference = 0xffaa00
    ovl_reference_dark = 0x505050

    eve.VERTEX_FORMAT(0)

    # Draw bezel
    eve.SAVE_CONTEXT()
    eve.CLEAR(0,1,0)
    eve.COLOR(bezel_col)
    # Draw the circles to make the bezel in three levels in the stencil buffer
    eve.STENCIL_OP(eve.STENCIL_INCR, eve.STENCIL_INCR)	# Set the stencil to increment
    eve.BEGIN(eve.BEGIN_POINTS)
    eve.POINT_SIZE(radius_outer * 16)
    eve.VERTEX2F(x, y)
    eve.POINT_SIZE(radius_b1 * 16)
    eve.VERTEX2F(x, y)
    eve.POINT_SIZE(radius_b2 * 16)
    eve.VERTEX2F(x, y)
    eve.POINT_SIZE(radius_inner * 16)
    eve.VERTEX2F(x, y)
    eve.END()
    eve.STENCIL_OP(eve.STENCIL_KEEP, eve.STENCIL_KEEP) # Stop the stencil INCR
    # Gradient (light at top) for outer of bezel
    eve.STENCIL_FUNC(eve.TEST_EQUAL, 1, 255)
    eve.CMD_GRADIENT(x - radius_outer, y + radius_outer, bezel_col_dark, x - radius_outer, y - radius_outer, bezel_col_bright)
    # Flat colour for centre of bezel
    eve.STENCIL_FUNC(eve.TEST_EQUAL, 2, 255)
    eve.POINT_SIZE(radius_outer * 16)
    eve.VERTEX2F(x, y)
    # Gradient (dark at top) for inner of bezel
    eve.STENCIL_FUNC(eve.TEST_EQUAL, 3, 255)
    eve.CMD_GRADIENT(x - radius_outer, y + radius_outer, bezel_col_bright, x - radius_outer, y - radius_outer, bezel_col_dark)
    eve.RESTORE_CONTEXT()

    # Bank/Roll Index: Outer circle
    eve.SAVE_CONTEXT()
    eve.CLEAR_STENCIL(0)
    eve.CLEAR(0,1,0)
    eve.STENCIL_OP(eve.STENCIL_KEEP, eve.STENCIL_INCR)
    # Draw ground and sky stencil
    eve.BEGIN(eve.BEGIN_POINTS)
    eve.POINT_SIZE(radius_inner * 16)
    eve.VERTEX2F(x, y)
    eve.POINT_SIZE(radius_roll * 16)
    eve.VERTEX2F(x, y)
    eve.STENCIL_FUNC(eve.TEST_EQUAL, 1, 255)
    eve.BEGIN(eve.BEGIN_LINES)
    eve.LINE_WIDTH(radius_inner * 16 // 2)
    # Draw the roll sky and ground
    # These are rotated depending on the "roll"
    eve.COLOR(roll_col_ground)
    dx = x + circ_x((radius_inner/2) + (ai_ref_bold/16), -roll)
    dy = y + circ_y((radius_inner/2) + (ai_ref_bold/16), -roll)
    for deg in (-90, 90):
        dx1 = dx + circ_x(radius_inner, -roll + deg)
        dy1 = dy + circ_y(radius_inner, -roll + deg)
        eve.VERTEX2F(dx1, dy1)
    eve.COLOR(roll_col_sky)
    dx = x - circ_x((radius_inner/2) + (ai_ref_bold/16), -roll)
    dy = y - circ_y((radius_inner/2) + (ai_ref_bold/16), -roll)
    for deg in (-90, 90):
        dx1 = dx + circ_x(radius_inner, -roll + deg)
        dy1 = dy + circ_y(radius_inner, -roll + deg)
        eve.VERTEX2F(dx1, dy1)
    # Draw reference lines:
    eve.COLOR(ai_reference)
    # These are rotated depending on the "roll"
    eve.STENCIL_FUNC(eve.TEST_EQUAL, 2, 255)
    eve.BEGIN(eve.BEGIN_LINES)
    # bold at 60 and 30 degrees
    eve.LINE_WIDTH(ai_ref_bold)
    for deg in (-60, -30, 30, 60):
        dx = x + circ_x(radius_inner, deg + roll)
        dy = y - circ_y(radius_inner, deg + roll)
        eve.VERTEX2F(dx, dy)
        eve.VERTEX2F(x, y)
    # narrow at 10 and 20 degrees
    eve.LINE_WIDTH(ai_ref_narrow)
    for deg in (-20, -10, 10, 20):
        dx = x + circ_x(radius_bank, deg + roll)
        dy = y - circ_y(radius_bank, deg + roll)
        eve.VERTEX2F(dx, dy)
        eve.VERTEX2F(x, y)
    # dot at 45 degrees
    eve.BEGIN(eve.BEGIN_POINTS)
    eve.POINT_SIZE(ai_ref_narrow)
    for deg in (-45, 45):
        dx = x + circ_x(radius_bank, deg + roll)
        dy = y - circ_y(radius_bank, deg + roll)
        eve.VERTEX2F(dx, dy)
    eve.STENCIL_FUNC(eve.TEST_ALWAYS, 0, 255)
    eve.RESTORE_CONTEXT()

    # Pitch Indicator: Inner circle
    eve.SAVE_CONTEXT()
    eve.CLEAR_STENCIL(0)
    eve.CLEAR(0,1,0)
    eve.STENCIL_OP(eve.STENCIL_KEEP, eve.STENCIL_INCR)
    # Draw ground and sky stencil
    eve.BEGIN(eve.BEGIN_POINTS)
    eve.POINT_SIZE(radius_roll * 16)
    eve.VERTEX2F(x, y)
    eve.STENCIL_FUNC(eve.TEST_GEQUAL, 1, 255)
    eve.BEGIN(eve.BEGIN_LINES)
    eve.LINE_WIDTH(radius_roll * 16 / 4)
    # Draw the pitch sky and ground
    # These are rotated depending on the "pitch"
    # Offset of pitch radius_roll is pitch of +40, -radius_roll is -40
    eve.COLOR(pitch_col_ground)
    for i in range(1, 8):
        pw = ((radius_roll * i) / 4) + (ai_ref_narrow/16) + ((radius_roll * climb) / 40)
        dx = x + circ_x(pw, -pitch)
        dy = y + circ_y(pw, -pitch)
        for deg in (-90, 90):
            dx1 = dx + circ_x(radius_roll, -pitch + deg)
            dy1 = dy + circ_y(radius_roll, -pitch + deg)
            eve.VERTEX2F(dx1, dy1)
    eve.COLOR(pitch_col_sky)
    for i in range(1, 8):
        pw = ((radius_roll * i) / 4) + (ai_ref_narrow/16) - ((radius_roll * climb) / 40)
        dx = x - circ_x(pw, -pitch)
        dy = y - circ_y(pw, -pitch)
        for deg in (-90, 90):
            dx1 = dx + circ_x(radius_roll, -pitch + deg)
            dy1 = dy + circ_y(radius_roll, -pitch + deg)
            eve.VERTEX2F(dx1, dy1)
    eve.COLOR(ai_reference)
    eve.LINE_WIDTH(ai_ref_narrow)
    for i in (20, 10, -10, -20):
        pw = ((radius_roll * climb) / 40) + ((radius_roll * i) / 40)
        dx = x + circ_x(pw, -pitch)
        dy = y + circ_y(pw, -pitch)
        for deg in (-90, 90):
            dx1 = dx + circ_x(radius_roll * i / 50, -pitch + deg)
            dy1 = dy + circ_y(radius_roll * i / 50, -pitch + deg)
            eve.VERTEX2F(dx1, dy1)
    for i in (15, 5, -5, -15):
        pw = ((radius_roll * climb) / 40) + ((radius_roll * i) / 40)
        dx = x + circ_x(pw, -pitch)
        dy = y + circ_y(pw, -pitch)
        for deg in (-90, 90):
            dx1 = dx + circ_x(radius_roll / 10, -pitch + deg)
            dy1 = dy + circ_y(radius_roll / 10, -pitch + deg)
            eve.VERTEX2F(dx1, dy1)
    eve.RESTORE_CONTEXT()

    # Triangle for 0 in Pitch Indicator
    eve.SAVE_CONTEXT()
    eve.BEGIN(eve.BEGIN_LINE_STRIP)
    eve.LINE_WIDTH(ai_ref_narrow)
    eve.COLOR(ai_reference)
    dx = x + circ_x(radius_roll - (ai_ref_bold/8), roll)
    dy = y - circ_y(radius_roll - (ai_ref_bold/8), roll)
    eve.VERTEX2F(dx, dy)
    dx2 = x + circ_x(radius_inner - (ai_ref_bold/16), roll + 5)
    dy2 = y - circ_y(radius_inner - (ai_ref_bold/16), roll + 5)
    eve.VERTEX2F(dx2, dy2)
    dx1 = x + circ_x(radius_inner - (ai_ref_bold/16), roll - 5)
    dy1 = y - circ_y(radius_inner - (ai_ref_bold/16), roll - 5)
    eve.VERTEX2F(dx1, dy1)
    eve.VERTEX2F(dx, dy)
    eve.END()
    eve.RESTORE_CONTEXT()

    # Reference Overlay
    # Triangle for 0 in reference
    eve.SAVE_CONTEXT()
    eve.BEGIN(eve.BEGIN_LINE_STRIP)
    eve.LINE_WIDTH(ovl_narrow)
    eve.COLOR(ovl_reference)
    dx = x
    dy = y - radius_roll
    eve.VERTEX2F(dx, dy)
    dx2 = x - (radius_roll * 2 / 10)
    dy2 = y - (radius_roll * 8 / 10)
    eve.VERTEX2F(dx2, dy2)
    dx1 = x + (radius_roll * 2 / 10)
    dy1 = y - (radius_roll * 8 / 10)
    eve.VERTEX2F(dx1, dy1)
    eve.VERTEX2F(dx, dy)
    eve.END()
    # Centre target for reference
    eve.BEGIN(eve.BEGIN_LINE_STRIP)
    eve.LINE_WIDTH(ovl_bold)
    dx = x - ((radius_roll * 3) / 4)
    dy = y
    eve.VERTEX2F(dx, dy)
    dx = x - (radius_roll / 4)
    eve.VERTEX2F(dx, dy)
    dx = x - (radius_roll / 5)
    dy = y + (radius_roll / 10)
    eve.VERTEX2F(dx, dy)
    eve.END()
    eve.BEGIN(eve.BEGIN_LINE_STRIP)
    dx = x + (radius_roll / 5)
    dy = y + (radius_roll / 10)
    eve.VERTEX2F(dx, dy)
    dx = x + (radius_roll / 4)
    dy = y
    eve.VERTEX2F(dx, dy)
    dx = x + ((radius_roll * 3) / 4)
    dy = y
    eve.VERTEX2F(dx, dy)
    eve.END()
    # dot at 45 degrees
    eve.BEGIN(eve.BEGIN_POINTS)
    eve.POINT_SIZE(ovl_bold)
    dx = x
    dy = y
    eve.VERTEX2F(dx, dy)
    eve.RESTORE_CONTEXT()

def eve_display(eve):

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
    radius = TARGET_SCREEN_RADIUS
    # Centre the widget
    xatt = (eve.EVE_DISP_WIDTH / 4)
    yatt = (eve.EVE_DISP_HEIGHT / 2)
    xalt = (eve.EVE_DISP_WIDTH * 3 / 4)
    yalt = (eve.EVE_DISP_HEIGHT / 2)

    while True:

        eve.LIB_BeginCoProList()
        eve.CMD_DLSTART()
        eve.CLEAR_COLOR_RGB(0, 0, 0)
        eve.CLEAR(1,1,1)

        aiwidget(eve, xatt, yatt, radius, pitch, climb, roll)
        altwidget(eve, xalt, yalt, radius, alt)

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
