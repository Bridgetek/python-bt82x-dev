# Typical command line:
# python tsd.py --connector ft4222module
import sys
import math

# Add the library directories to the module search path.
sys.path.append('../..')
sys.path.append('../../bteve2')

# This module provides the connector to the EVE hardware.
import apprunner

class Chart:
    def __init__(self, eve, handle, addr, width):
        self.eve = eve
        self.handle = handle
        self.w = width

        self.addr0 = addr
        self.addr1 = addr + width
        self.eve.CMD_MEMSET(self.addr0, 0xff, 2 * width)
        self.prev_y = 255

        (w, h) = (width, 256)
        (iw, ih) = (width, 1)
        eve.BITMAP_HANDLE(self.handle)
        eve.BITMAP_SOURCE(self.addr0)
        eve.BITMAP_SIZE_H(w >> 9, h >> 9)
        eve.BITMAP_SIZE(eve.FILTER_NEAREST, eve.WRAP_BORDER, eve.WRAP_BORDER, w, h)
        eve.BITMAP_LAYOUT_H(iw >> 10, ih >> 9)
        eve.BITMAP_LAYOUT(eve.FORMAT_BARGRAPH, iw, ih)

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
        self.eve.CMD_MEMCPY(self.addr0, self.addr0 + 1, self.w * 2 - 1)

        # Add the new points on the right-hand-side
        self.eve.CMD_MEMWRITE(self.addr0 + self.w - 1, 1)
        self.eve.c4(lo)
        self.eve.CMD_MEMWRITE(self.addr1 + self.w - 1, 1)
        self.eve.c4(min(255, hi + 2))

    def draw(self, x, y):
        eve = self.eve
        eve.BEGIN(eve.BEGIN_BITMAPS)
        eve.BITMAP_HANDLE(self.handle)

        eve.COLOR_RGB(0, 255, 0)
        eve.CELL(0)
        eve.VERTEX2F(x*16, y*16)

        eve.COLOR_RGB(80, 0, 0)
        eve.CELL(1)
        eve.VERTEX2F(x*16, y*16)

def tsd(eve):

    w = 1280                # Width in pixels

    sz = 2 * w              # Each chart uses (2 * w) bytes

    charts = [Chart(eve, i, i * sz, w) for i in range(4)]
    th = [0, 0, 0, 0]

    while True:
        for (i, ch) in enumerate(charts):
            y = 0.5 + 0.3 * math.sin(th[i]) + 0.1 * math.sin(2.37 * th[i])
            ch.add(y)
            speed = 0.01 + ((i * i) / 200)
            th[i] += speed

        eve.CLEAR_COLOR_RGB(64, 64, 64)
        eve.CLEAR()
        for (i, ch) in enumerate(charts):
            ch.draw(100, i * 280)

        eve.CMD_SWAP()
        eve.CMD_DLSTART()

apprunner.run(tsd)
