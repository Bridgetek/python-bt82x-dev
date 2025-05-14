# Typical command line:
# python tsd.py --connector ft4222module
import math
import bteve2 as eve

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

class Chart:
    def __init__(self, gd, handle, addr, width):
        self.gd = gd
        self.handle = handle
        self.w = width

        self.addr0 = addr
        self.addr1 = addr + width
        self.gd.cmd_memset(self.addr0, 0xff, 2 * width)
        self.prev_y = 255

        (w, h) = (width, 256)
        (iw, ih) = (width, 1)
        gd.BitmapHandle(self.handle)
        gd.BitmapSource(self.addr0)
        gd.BitmapSizeH(w >> 9, h >> 9)
        gd.BitmapSize(eve.NEAREST, eve.BORDER, eve.BORDER, w, h)
        gd.BitmapLayoutH(iw >> 10, ih >> 9)
        gd.BitmapLayout(eve.BARGRAPH, iw, ih)

    def add(self, y : float):
        # Add a single sample, 0.0 - 1.0

        # Scale to 0-255, clip, invert Y
        yi = min(255, max(0, 255 - int(y * 255)))

        # addr0 holds the low Y, addr1 the high Y
        if yi < self.prev_y:
            (lo, hi) = (yi, self.prev_y)
        else:
            (lo, hi) = (self.prev_y, yi)
        self.prev_y = yi

        # Scroll both buffers 1 pixel left
        self.gd.cmd_memcpy(self.addr0, self.addr0 + 1, self.w * 2 - 1)

        # Add the new points on the right-hand-side
        self.gd.cmd_memwrite(self.addr0 + self.w - 1, 1)
        self.gd.c4(lo)
        self.gd.cmd_memwrite(self.addr1 + self.w - 1, 1)
        self.gd.c4(min(255, hi + 2))

    def draw(self, x, y):
        gd = self.gd
        gd.Begin(eve.BITMAPS)
        gd.BitmapHandle(self.handle)

        gd.ColorRGB(0, 255, 0)
        gd.Cell(0)
        gd.Vertex2f(x, y)

        gd.ColorRGB(80, 0, 0)
        gd.Cell(1)
        gd.Vertex2f(x, y)

def tsd(gd):

    w = 1280                # Width in pixels

    sz = 2 * w              # Each chart uses (2 * w) bytes

    charts = [Chart(gd, i, i * sz, w) for i in range(4)]
    th = [0, 0, 0, 0]

    while True:
        for (i, ch) in enumerate(charts):
            y = 0.5 + 0.3 * math.sin(th[i]) + 0.1 * math.sin(2.37 * th[i])
            ch.add(y)
            speed = 0.01 + ((i * i) / 200)
            th[i] += speed

        gd.ClearColorRGB(64, 64, 64)
        gd.Clear()
        for (i, ch) in enumerate(charts):
            ch.draw(100, i * 280)

        gd.swap()
        gd.cmd_dlstart()

apprunner.run(tsd)
