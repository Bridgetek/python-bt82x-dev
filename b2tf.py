# Typical command line:
# python b2tf.py --connector ft4222module
import sys
import time
import datetime

# This module provides the connector (gd) to the EVE hardware.
import apprunner

# Target EVE device.
family = "BT82x"

# EVE family support check.
device_families = ["FT80x", "FT81x", "BT81x", "BT82x"]
assert(family in device_families)

if family == "BT82x":
    # This loads BT82x family definitions only.
    import bteve2 as eve
else:
    # This loads FT80x, FT81x, BT81x family definitions.
    import bteve as eve

# Load the sevensegment source code from the "common" directory.
sys.path.append('common')
import sevensegment 

def ledbox(gd, x, y, count, segsize):
    gd.Begin(eve.RECTS)
    gd.VertexTranslateX((x - (segsize//3)))
    gd.VertexTranslateY((y - (segsize//3)))
    gd.Vertex2f(0, 0)
    gd.Vertex2f(((count * (segsize + (segsize//3))) + (segsize//3)) * 4, 
                 ((2 * segsize + (segsize//3)) + (segsize//3)) * 4)
    gd.VertexTranslateX(0)
    gd.VertexTranslateY(0)

def lednumber(gd, x, y, count, segsize, value, fg, bg):
    for i in range(count):
        sevensegment.cmd_sevenseg(gd, x + ((count - i - 1) * (segsize + (segsize//3))), y, segsize, int(value) % 10, fg, bg)
        value = value // 10

def tapebox(gd, x, y, w, h):
    gd.Begin(eve.RECTS)
    gd.VertexTranslateX(x)
    gd.VertexTranslateY(y)
    gd.Vertex2f(0, 0)
    gd.VertexTranslateX((x + w))
    gd.VertexTranslateY((y + h))
    gd.Vertex2f(0, 0)
    gd.VertexTranslateX(0)
    gd.VertexTranslateY(0)

def gradbox(gd, x, y, w, h):
    gd.ScissorXY(x, y)
    gd.ScissorSize(w, h)
    gd.cmd_gradient(x, y, 0x808080, x, y+h, 0x404040)

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
        
        gd.cmd_dlstart()
        gd.ClearColorRGB(0x0, 0x0, 0x0)
        gd.Clear(1,1,1)

        segsize = 80

        # Starting point
        x = 200
        y = 120

        dx = x
        dy = y
        gd.ColorRGB(0x80, 0x80, 0x80)
        gd.SaveContext()
        gradbox(gd, dx - segsize // 2, dy - segsize // 2, 20 * segsize, segsize * 4)
        dy = dy + segsize * 4
        gradbox(gd, dx - segsize // 2, dy - segsize // 2, 20 * segsize, segsize * 4)
        dy = dy + segsize * 4
        gradbox(gd, dx - segsize // 2, dy - segsize // 2, 20 * segsize, segsize * 4)
        gd.RestoreContext()

        dy = y
        gd.ColorRGB(0, 0, 0)
        tapebox(gd, gd.w//2 - 300, dy + 5 * segsize // 2, 600, 60)
        dy = dy + segsize * 4
        tapebox(gd, gd.w//2 - 300, dy + 5 * segsize // 2, 600, 60)
        dy = dy + segsize * 4
        tapebox(gd, gd.w//2 - 300, dy + 5 * segsize // 2, 600, 60)

        dy = y
        gd.ColorRGB(255, 255, 255)
        gd.cmd_text(gd.w//2, dy + 5 * segsize // 2 + 30, 31, eve.OPT_CENTER, "DESTINATION TIME")
        dy = dy + segsize * 4
        gd.cmd_text(gd.w//2, dy + 5 * segsize // 2 + 30, 31, eve.OPT_CENTER, "PRESENT TIME")
        dy = dy + segsize * 4
        gd.cmd_text(gd.w//2, dy + 5 * segsize // 2 + 30, 31, eve.OPT_CENTER, "LAST TIME DEPARTED")
        dy = dy + segsize * 4

        gd.cmd_bgcolor(0x100000)
        bg = (0x10, 0, 0)

        # Red LEDs
        gd.cmd_fgcolor(0xff0000)
        fg = (0xff, 0, 0)

        dx = x
        dy = y
        gd.ColorRGB(0, 0, 0)
        ledbox(gd, dx, dy, 2, segsize)
        lednumber(gd, dx, dy, 2, segsize, destination.month, fg, bg)
        
        dx = dx + (7 * segsize // 2)
        gd.ColorRGB(0, 0, 0)
        ledbox(gd, dx, dy, 2, segsize)
        lednumber(gd, dx, dy, 2, segsize, destination.day, fg, bg)

        dx = dx + (7 * segsize // 2)
        gd.ColorRGB(0, 0, 0)
        ledbox(gd, dx, dy, 4, segsize)
        lednumber(gd, dx, dy, 4, segsize, destination.year, fg, bg)

        dx = dx + (25 * segsize // 4)
        gd.ColorRGB(0, 0, 0)
        ledbox(gd, dx, dy, 2, segsize)
        lednumber(gd, dx, dy, 2, segsize, destination.hour, fg, bg)

        dx = dx + (7 * segsize // 2)
        gd.ColorRGB(0, 0, 0)
        ledbox(gd, dx, dy, 2, segsize)
        lednumber(gd, dx, dy, 2, segsize, destination.minute, fg, bg)

        # Green LEDs
        gd.cmd_fgcolor(0x00ff00)
        fg = (0, 0xff, 0)

        dx = x
        dy = dy + segsize * 4

        gd.ColorRGB(0, 0, 0)
        ledbox(gd, dx, dy, 2, segsize)
        lednumber(gd, dx, dy, 2, segsize, present.month, fg, bg)
        
        dx = dx + (7 * segsize // 2)
        gd.ColorRGB(0, 0, 0)
        ledbox(gd, dx, dy, 2, segsize)
        lednumber(gd, dx, dy, 2, segsize, present.day, fg, bg)

        dx = dx + (7 * segsize // 2)
        gd.ColorRGB(0, 0, 0)
        ledbox(gd, dx, dy, 4, segsize)
        lednumber(gd, dx, dy, 4, segsize, present.year, fg, bg)

        dx = dx + (25 * segsize // 4)
        gd.ColorRGB(0, 0, 0)
        ledbox(gd, dx, dy, 2, segsize)
        lednumber(gd, dx, dy, 2, segsize, present.hour, fg, bg)

        dx = dx + (7 * segsize // 2)
        gd.ColorRGB(0, 0, 0)
        ledbox(gd, dx, dy, 2, segsize)
        lednumber(gd, dx, dy, 2, segsize, 88, fg, bg)

        # Amber LEDs
        gd.cmd_fgcolor(0xffff00)
        fg = (0xff, 0xff, 0)

        dx = x
        dy = dy + segsize * 4

        gd.ColorRGB(0, 0, 0)
        gd.ColorRGB(0, 0, 0)
        ledbox(gd, dx, dy, 2, segsize)
        lednumber(gd, dx, dy, 2, segsize, lasttime.month, fg, bg)
        
        dx = dx + (7 * segsize // 2)
        gd.ColorRGB(0, 0, 0)
        ledbox(gd, dx, dy, 2, segsize)
        lednumber(gd, dx, dy, 2, segsize, lasttime.day, fg, bg)

        dx = dx + (7 * segsize // 2)
        gd.ColorRGB(0, 0, 0)
        ledbox(gd, dx, dy, 4, segsize)
        lednumber(gd, dx, dy, 4, segsize, lasttime.year, fg, bg)

        dx = dx + (25 * segsize // 4)
        gd.ColorRGB(0, 0, 0)
        ledbox(gd, dx, dy, 2, segsize)
        lednumber(gd, dx, dy, 2, segsize, lasttime.hour, fg, bg)

        dx = dx + (7 * segsize // 2)
        gd.ColorRGB(0, 0, 0)
        ledbox(gd, dx, dy, 2, segsize)
        lednumber(gd, dx, dy, 2, segsize, lasttime.minute, fg, bg)

        gd.Display()
        gd.swap()

        present = present - datetime.timedelta(hours=1)
        lasttime = datetime.datetime.now()

apprunner.run(b2tf)
