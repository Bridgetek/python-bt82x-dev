# Typical command line:
# python ledclock.py --connector ft4222module
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
    eve.VERTEX2F(((count * (segsize + (segsize//3)))) * 4, 
                 ((2 * segsize + (segsize//3)) + (segsize//3)) * 4)
    eve.VERTEX_TRANSLATE_X(0)
    eve.VERTEX_TRANSLATE_Y(0)

def lednumber(eve, x, y, count, segsize, value, fg, bg, opt):
    _ = fg
    _ = bg
    for i in range(count):
        cmd = (int(value) % 10) + opt
        sevensegment.cmd_sevenseg(eve, x + ((count - i - 1) * (segsize + (segsize//3))), y, segsize, cmd)
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

def ledclock(eve):

    while True:
        present = datetime.datetime.now()
       
        eve.LIB_BeginCoProList()
        eve.CMD_DLSTART()
        eve.CLEAR_COLOR_RGB(0, 0, 0)
        eve.CLEAR(1,1,1)

        segsize = 150

        # Starting point
        x = eve.w//2
        y = 120

        dx = x
        dy = y
        eve.COLOR_RGB(0x80, 0x80, 0x80)
        eve.SAVE_CONTEXT()
        gradbox(eve, dx - 4 * segsize, dy - segsize // 2, 8 * segsize, segsize * 4)
        eve.RESTORE_CONTEXT()

        dy = y
        eve.COLOR_RGB(0, 0, 0)
        tapebox(eve, eve.w//2 - 300, dy + 5 * segsize // 2, 600, 60)

        dy = y
        eve.COLOR_RGB(255, 255, 255)
        eve.CMD_TEXT(eve.w//2, dy + 5 * segsize // 2 + 30, 31, eve.OPT_CENTER, "CURRENT TIME")

        # Bacground colour of non-active LED segments
        eve.CMD_BGCOLOR(0x100000)
        bg = (0x10, 0, 0)

        # Red LEDs
        eve.CMD_FGCOLOR(0xff0000)
        fg = (0xff, 0, 0)

        dx = x
        dy = y

        fill = eve.OPT_FILL if present.microsecond > 500000 else 0
        dx = dx - (3 * segsize)
        eve.COLOR_RGB(0, 0, 0)
        ledbox(eve, dx, dy, 5, segsize)
        dx = dx + (segsize // 3)
        lednumber(eve, dx, dy, 1, segsize, present.hour / 10, fg, bg, 0)
        dx = dx + (3 * segsize // 2)
        lednumber(eve, dx, dy, 1, segsize, present.hour, fg, bg, 0)
        dx = dx + (3 * segsize // 2)
        lednumber(eve, dx, dy, 1, segsize, present.minute / 10, fg, bg, 0)
        dx = dx + (3 * segsize // 2)
        lednumber(eve, dx, dy, 1, segsize, present.minute, fg, bg, 0)

        eve.DISPLAY()
        eve.CMD_SWAP()
        eve.LIB_EndCoProList()
        eve.LIB_AwaitCoProEmpty()

apprunner.run(ledclock)
