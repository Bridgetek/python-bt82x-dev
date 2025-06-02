# Typical command line:
# python b2tf.py --connector ft4222module
import sys
import datetime

# Add the library directories to the module search path.
sys.path.append('../..')
sys.path.append('../../bteve2')

# This module provides the connector to the EVE hardware.
import apprunner

# Load the sevensegment source code from the "common" directory.
sys.path.append('../common')
import sevensegment 

def ledbox(gd, x, y, count, segsize):
    gd.VERTEX_FORMAT(2)
    gd.BEGIN(gd.BEGIN_RECTS)
    gd.VERTEX_TRANSLATE_X((x - (segsize//3)))
    gd.VERTEX_TRANSLATE_Y((y - (segsize//3)))
    gd.VERTEX2F(0, 0)
    gd.VERTEX2F(((count * (segsize + (segsize//3))) + (segsize//3)) * 4, 
                 ((2 * segsize + (segsize//3)) + (segsize//3)) * 4)
    gd.VERTEX_TRANSLATE_X(0)
    gd.VERTEX_TRANSLATE_Y(0)

def lednumber(gd, x, y, count, segsize, value, fg, bg):
    for i in range(count):
        sevensegment.cmd_sevenseg(gd, x + ((count - i - 1) * (segsize + (segsize//3))), y, segsize, int(value) % 10, fg, bg)
        value = value // 10

def tapebox(gd, x, y, w, h):
    gd.BEGIN(gd.BEGIN_RECTS)
    gd.VERTEX_TRANSLATE_X(x)
    gd.VERTEX_TRANSLATE_Y(y)
    gd.VERTEX2F(0, 0)
    gd.VERTEX_TRANSLATE_X((x + w))
    gd.VERTEX_TRANSLATE_Y((y + h))
    gd.VERTEX2F(0, 0)
    gd.VERTEX_TRANSLATE_X(0)
    gd.VERTEX_TRANSLATE_Y(0)

def gradbox(gd, x, y, w, h):
    gd.SCISSOR_XY(x, y)
    gd.SCISSOR_SIZE(w, h)
    gd.CMD_GRADIENT(x, y, 0x808080, x, y+h, 0x404040)

def b2tf(gd):

    destination = datetime.datetime(1985, 10, 26, 1, 21)
    present = datetime.datetime.now()
    lasttime = datetime.datetime.now()

    while True:
        """print('The date time is: '
              + str(now.month) + " month "
              + str(now.day) + " day "
              + str(now.year) + " year "
              + str(now.hour) + " hour "
              + str(now.minute) + " minutes "
              )"""
        
        gd.CMD_DLSTART()
        gd.CLEAR_COLOR_RGB(0x0, 0x0, 0x0)
        gd.CLEAR(1,1,1)

        segsize = 80

        # Starting point
        x = 200
        y = 120

        dx = x
        dy = y
        gd.COLOR_RGB(0x80, 0x80, 0x80)
        gd.SAVE_CONTEXT()
        gradbox(gd, dx - segsize // 2, dy - segsize // 2, 20 * segsize, segsize * 4)
        dy = dy + segsize * 4
        gradbox(gd, dx - segsize // 2, dy - segsize // 2, 20 * segsize, segsize * 4)
        dy = dy + segsize * 4
        gradbox(gd, dx - segsize // 2, dy - segsize // 2, 20 * segsize, segsize * 4)
        gd.RESTORE_CONTEXT()

        dy = y
        gd.COLOR_RGB(0, 0, 0)
        tapebox(gd, gd.w//2 - 300, dy + 5 * segsize // 2, 600, 60)
        dy = dy + segsize * 4
        tapebox(gd, gd.w//2 - 300, dy + 5 * segsize // 2, 600, 60)
        dy = dy + segsize * 4
        tapebox(gd, gd.w//2 - 300, dy + 5 * segsize // 2, 600, 60)

        dy = y
        gd.COLOR_RGB(255, 255, 255)
        gd.CMD_TEXT(gd.w//2, dy + 5 * segsize // 2 + 30, 31, gd.OPT_CENTER, "DESTINATION TIME")
        dy = dy + segsize * 4
        gd.CMD_TEXT(gd.w//2, dy + 5 * segsize // 2 + 30, 31, gd.OPT_CENTER, "PRESENT TIME")
        dy = dy + segsize * 4
        gd.CMD_TEXT(gd.w//2, dy + 5 * segsize // 2 + 30, 31, gd.OPT_CENTER, "LAST TIME DEPARTED")
        dy = dy + segsize * 4

        # Bacground colour of non-active LED segments
        gd.CMD_BGCOLOR(0x100000)
        bg = (0x10, 0, 0)

        # Red LEDs
        gd.CMD_FGCOLOR(0xff0000)
        fg = (0xff, 0, 0)

        dx = x
        dy = y
        gd.COLOR_RGB(0, 0, 0)
        ledbox(gd, dx, dy, 2, segsize)
        lednumber(gd, dx, dy, 2, segsize, destination.month, fg, bg)
        
        dx = dx + (7 * segsize // 2)
        gd.COLOR_RGB(0, 0, 0)
        ledbox(gd, dx, dy, 2, segsize)
        lednumber(gd, dx, dy, 2, segsize, destination.day, fg, bg)

        dx = dx + (7 * segsize // 2)
        gd.COLOR_RGB(0, 0, 0)
        ledbox(gd, dx, dy, 4, segsize)
        lednumber(gd, dx, dy, 4, segsize, destination.year, fg, bg)

        dx = dx + (25 * segsize // 4)
        gd.COLOR_RGB(0, 0, 0)
        ledbox(gd, dx, dy, 2, segsize)
        lednumber(gd, dx, dy, 2, segsize, destination.hour, fg, bg)

        dx = dx + (7 * segsize // 2)
        gd.COLOR_RGB(0, 0, 0)
        ledbox(gd, dx, dy, 2, segsize)
        lednumber(gd, dx, dy, 2, segsize, destination.minute, fg, bg)

        # Green LEDs
        gd.CMD_FGCOLOR(0x00ff00)
        fg = (0, 0xff, 0)

        dx = x
        dy = dy + segsize * 4

        gd.COLOR_RGB(0, 0, 0)
        ledbox(gd, dx, dy, 2, segsize)
        lednumber(gd, dx, dy, 2, segsize, present.month, fg, bg)
        
        dx = dx + (7 * segsize // 2)
        gd.COLOR_RGB(0, 0, 0)
        ledbox(gd, dx, dy, 2, segsize)
        lednumber(gd, dx, dy, 2, segsize, present.day, fg, bg)

        dx = dx + (7 * segsize // 2)
        gd.COLOR_RGB(0, 0, 0)
        ledbox(gd, dx, dy, 4, segsize)
        lednumber(gd, dx, dy, 4, segsize, present.year, fg, bg)

        dx = dx + (25 * segsize // 4)
        gd.COLOR_RGB(0, 0, 0)
        ledbox(gd, dx, dy, 2, segsize)
        lednumber(gd, dx, dy, 2, segsize, present.hour, fg, bg)

        dx = dx + (7 * segsize // 2)
        gd.COLOR_RGB(0, 0, 0)
        ledbox(gd, dx, dy, 2, segsize)
        lednumber(gd, dx, dy, 2, segsize, 88, fg, bg)

        # Amber LEDs
        gd.CMD_FGCOLOR(0xffff00)
        fg = (0xff, 0xff, 0)

        dx = x
        dy = dy + segsize * 4

        gd.COLOR_RGB(0, 0, 0)
        gd.COLOR_RGB(0, 0, 0)
        ledbox(gd, dx, dy, 2, segsize)
        lednumber(gd, dx, dy, 2, segsize, lasttime.month, fg, bg)
        
        dx = dx + (7 * segsize // 2)
        gd.COLOR_RGB(0, 0, 0)
        ledbox(gd, dx, dy, 2, segsize)
        lednumber(gd, dx, dy, 2, segsize, lasttime.day, fg, bg)

        dx = dx + (7 * segsize // 2)
        gd.COLOR_RGB(0, 0, 0)
        ledbox(gd, dx, dy, 4, segsize)
        lednumber(gd, dx, dy, 4, segsize, lasttime.year, fg, bg)

        dx = dx + (25 * segsize // 4)
        gd.COLOR_RGB(0, 0, 0)
        ledbox(gd, dx, dy, 2, segsize)
        lednumber(gd, dx, dy, 2, segsize, lasttime.hour, fg, bg)

        dx = dx + (7 * segsize // 2)
        gd.COLOR_RGB(0, 0, 0)
        ledbox(gd, dx, dy, 2, segsize)
        lednumber(gd, dx, dy, 2, segsize, lasttime.minute, fg, bg)

        gd.DISPLAY()
        gd.CMD_SWAP()
        gd.LIB_AwaitCoProEmpty()

        present = present - datetime.timedelta(hours=1)
        lasttime = datetime.datetime.now()

apprunner.run(b2tf)
