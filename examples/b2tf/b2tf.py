# Typical command line:
# python b2tf.py --connector ft4222module
import sys
import datetime

# Add the library directories to the module search path.
sys.path.append('../..')
sys.path.append('../../bteve2')

# This module provides the connector to the EVE hardware.
import apprunner

# Load the sevensegment source code from the "snippets" directory.
sys.path.append('../snippets')
import sevensegment 

def ledbox(eve, x, y, count, segsize):
    eve.VERTEX_FORMAT(2)
    eve.BEGIN(eve.BEGIN_RECTS)
    eve.VERTEX_TRANSLATE_X((x - (segsize//3)) * 16)
    eve.VERTEX_TRANSLATE_Y((y - (segsize//3)) * 16)
    eve.VERTEX2F(0, 0)
    eve.VERTEX2F(((count * (segsize + (segsize//3))) + (segsize//3)) * 4, 
                 ((2 * segsize + (segsize//3)) + (segsize//3)) * 4)
    eve.VERTEX_TRANSLATE_X(0)
    eve.VERTEX_TRANSLATE_Y(0)

def lednumber(eve, x, y, count, segsize, value, fg, bg):
    for i in range(count):
        sevensegment.cmd_sevenseg(eve, x + ((count - i - 1) * (segsize + (segsize//3))), y, segsize, int(value) % 10, fg, bg)
        value = value // 10

def tapebox(eve, x, y, w, h):
    eve.BEGIN(eve.BEGIN_RECTS)
    eve.VERTEX_TRANSLATE_X(x * 16)
    eve.VERTEX_TRANSLATE_Y(y * 16)
    eve.VERTEX2F(0, 0)
    eve.VERTEX_TRANSLATE_X((x + w) * 16)
    eve.VERTEX_TRANSLATE_Y((y + h) * 16)
    eve.VERTEX2F(0, 0)
    eve.VERTEX_TRANSLATE_X(0)
    eve.VERTEX_TRANSLATE_Y(0)

def gradbox(eve, x, y, w, h):
    eve.SCISSOR_XY(x, y)
    eve.SCISSOR_SIZE(w, h)
    eve.CMD_GRADIENT(x, y, 0x808080, x, y+h, 0x404040)

def b2tf(eve):

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
        
        eve.LIB_BeginCoProList()
        eve.CMD_DLSTART()
        eve.CLEAR_COLOR_RGB(0x0, 0x0, 0x0)
        eve.CLEAR(1,1,1)

        segsize = 80

        # Starting point
        x = 200
        y = 120

        dx = x
        dy = y
        eve.COLOR_RGB(0x80, 0x80, 0x80)
        eve.SAVE_CONTEXT()
        gradbox(eve, dx - segsize // 2, dy - segsize // 2, 20 * segsize, segsize * 4)
        dy = dy + segsize * 4
        gradbox(eve, dx - segsize // 2, dy - segsize // 2, 20 * segsize, segsize * 4)
        dy = dy + segsize * 4
        gradbox(eve, dx - segsize // 2, dy - segsize // 2, 20 * segsize, segsize * 4)
        eve.RESTORE_CONTEXT()

        dy = y
        eve.COLOR_RGB(0, 0, 0)
        tapebox(eve, eve.w//2 - 300, dy + 5 * segsize // 2, 600, 60)
        dy = dy + segsize * 4
        tapebox(eve, eve.w//2 - 300, dy + 5 * segsize // 2, 600, 60)
        dy = dy + segsize * 4
        tapebox(eve, eve.w//2 - 300, dy + 5 * segsize // 2, 600, 60)

        dy = y
        eve.COLOR_RGB(255, 255, 255)
        eve.CMD_TEXT(eve.w//2, dy + 5 * segsize // 2 + 30, 31, eve.OPT_CENTER, "DESTINATION TIME")
        dy = dy + segsize * 4
        eve.CMD_TEXT(eve.w//2, dy + 5 * segsize // 2 + 30, 31, eve.OPT_CENTER, "PRESENT TIME")
        dy = dy + segsize * 4
        eve.CMD_TEXT(eve.w//2, dy + 5 * segsize // 2 + 30, 31, eve.OPT_CENTER, "LAST TIME DEPARTED")
        dy = dy + segsize * 4

        # Bacground colour of non-active LED segments
        eve.CMD_BGCOLOR(0x100000)
        bg = (0x10, 0, 0)

        # Red LEDs
        eve.CMD_FGCOLOR(0xff0000)
        fg = (0xff, 0, 0)

        dx = x
        dy = y
        eve.COLOR_RGB(0, 0, 0)
        ledbox(eve, dx, dy, 2, segsize)
        lednumber(eve, dx, dy, 2, segsize, destination.month, fg, bg)
        
        dx = dx + (7 * segsize // 2)
        eve.COLOR_RGB(0, 0, 0)
        ledbox(eve, dx, dy, 2, segsize)
        lednumber(eve, dx, dy, 2, segsize, destination.day, fg, bg)

        dx = dx + (7 * segsize // 2)
        eve.COLOR_RGB(0, 0, 0)
        ledbox(eve, dx, dy, 4, segsize)
        lednumber(eve, dx, dy, 4, segsize, destination.year, fg, bg)

        dx = dx + (25 * segsize // 4)
        eve.COLOR_RGB(0, 0, 0)
        ledbox(eve, dx, dy, 2, segsize)
        lednumber(eve, dx, dy, 2, segsize, destination.hour, fg, bg)

        dx = dx + (7 * segsize // 2)
        eve.COLOR_RGB(0, 0, 0)
        ledbox(eve, dx, dy, 2, segsize)
        lednumber(eve, dx, dy, 2, segsize, destination.minute, fg, bg)

        # Green LEDs
        eve.CMD_FGCOLOR(0x00ff00)
        fg = (0, 0xff, 0)

        dx = x
        dy = dy + segsize * 4

        eve.COLOR_RGB(0, 0, 0)
        ledbox(eve, dx, dy, 2, segsize)
        lednumber(eve, dx, dy, 2, segsize, present.month, fg, bg)
        
        dx = dx + (7 * segsize // 2)
        eve.COLOR_RGB(0, 0, 0)
        ledbox(eve, dx, dy, 2, segsize)
        lednumber(eve, dx, dy, 2, segsize, present.day, fg, bg)

        dx = dx + (7 * segsize // 2)
        eve.COLOR_RGB(0, 0, 0)
        ledbox(eve, dx, dy, 4, segsize)
        lednumber(eve, dx, dy, 4, segsize, present.year, fg, bg)

        dx = dx + (25 * segsize // 4)
        eve.COLOR_RGB(0, 0, 0)
        ledbox(eve, dx, dy, 2, segsize)
        lednumber(eve, dx, dy, 2, segsize, present.hour, fg, bg)

        dx = dx + (7 * segsize // 2)
        eve.COLOR_RGB(0, 0, 0)
        ledbox(eve, dx, dy, 2, segsize)
        lednumber(eve, dx, dy, 2, segsize, 88, fg, bg)

        # Amber LEDs
        eve.CMD_FGCOLOR(0xffff00)
        fg = (0xff, 0xff, 0)

        dx = x
        dy = dy + segsize * 4

        eve.COLOR_RGB(0, 0, 0)
        eve.COLOR_RGB(0, 0, 0)
        ledbox(eve, dx, dy, 2, segsize)
        lednumber(eve, dx, dy, 2, segsize, lasttime.month, fg, bg)
        
        dx = dx + (7 * segsize // 2)
        eve.COLOR_RGB(0, 0, 0)
        ledbox(eve, dx, dy, 2, segsize)
        lednumber(eve, dx, dy, 2, segsize, lasttime.day, fg, bg)

        dx = dx + (7 * segsize // 2)
        eve.COLOR_RGB(0, 0, 0)
        ledbox(eve, dx, dy, 4, segsize)
        lednumber(eve, dx, dy, 4, segsize, lasttime.year, fg, bg)

        dx = dx + (25 * segsize // 4)
        eve.COLOR_RGB(0, 0, 0)
        ledbox(eve, dx, dy, 2, segsize)
        lednumber(eve, dx, dy, 2, segsize, lasttime.hour, fg, bg)

        dx = dx + (7 * segsize // 2)
        eve.COLOR_RGB(0, 0, 0)
        ledbox(eve, dx, dy, 2, segsize)
        lednumber(eve, dx, dy, 2, segsize, lasttime.minute, fg, bg)

        eve.DISPLAY()
        eve.CMD_SWAP()
        eve.LIB_EndCoProList()
        eve.LIB_AwaitCoProEmpty()

        present = present - datetime.timedelta(hours=1)
        lasttime = datetime.datetime.now()

apprunner.run(b2tf)
