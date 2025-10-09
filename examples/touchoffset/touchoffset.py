# Typical command line:
# python touchoffset.py --connector ft4222module
import sys
import struct

# Add the library directories to the module search path.
sys.path.append('../..')
sys.path.append('../../bteve2')

# Use the SD card and the fssnapshot extension to take a screenshot
TAKE_SCREENSHOT = 0

import bteve2

# This module provides the connector to the EVE hardware.
import apprunner

# Import the patch file required by this code.
import patch_touchoffset as patch

class Subwindow:
    def __init__(self, pos, surf, buttons):
        self.pos = pos
        self.surf = surf
        self.buttons = buttons
        self.highlight = set()
        self.prev_tag = 0

    def run(self, gd):
        gd.LIB_BeginCoProList()
        gd.CMD_DLSTART()
        gd.CMD_TOUCHOFFSET(*self.pos)
        gd.CMD_RENDERTARGET(*self.surf)
        gd.CLEAR_TAG(0xff)
        gd.CLEAR_COLOR_RGB(100, 0, 30)
        gd.CLEAR()
        for i,ch in enumerate(self.buttons):
            x = 24 + (i % 2) * 244
            y = 24 + (i // 2) * 244
            gd.TAG(ord(ch))
            gd.CMD_FGCOLOR([0x003870, 0xd06038][ch in self.highlight])
            gd.CMD_BUTTON(x, y, 220, 220, 32, gd.OPT_FLAT,  ch)
        gd.TAG(0)
        gd.DISPLAY()
        gd.CMD_SWAP()
        gd.CMD_GRAPHICSFINISH()
        gd.CMD_ENDTOUCHOFFSET()
        gd.LIB_EndCoProList()
        gd.LIB_AwaitCoProEmpty()

        tag = chr(gd.rd32(gd.REG_TOUCH_TAG))
        if self.prev_tag == chr(0):
            if tag in self.buttons:
                self.highlight ^= {tag}
        self.prev_tag = tag

    def draw(self, gd):
        gd.CMD_SETBITMAP(*self.surf)
        gd.VERTEX2F(*self.pos)

def touchoffset(eve):
    if TAKE_SCREENSHOT:
        status = eve.LIB_SDAttach(eve.OPT_IS_SD)
        assert status == 0, "SD card not attached"

    eve.LIB_AutoCalibrate()

    subs = [
        Subwindow((100, 100), bteve2.Surface(0x1000, eve.FORMAT_RGB6, 512, 512), "ABCD"),
        Subwindow((800, 400), bteve2.Surface(0x100000, eve.FORMAT_RGB6, 512, 512), "EFGH")
    ]

    so = [eve.rd32(eve.REG_SC0_PTR0), eve.rd32(eve.REG_SC0_PTR1)]

    frame = 0
    flip = 0
    while True:
        for sub in subs:
            sub.run(eve)

        eve.LIB_BeginCoProList()
        eve.CMD_DLSTART()
        eve.CMD_RENDERTARGET(so[flip], eve.FORMAT_RGB6, eve.EVE_DISP_WIDTH, eve.EVE_DISP_HEIGHT)

        eve.CLEAR_COLOR_RGB(0, 60, 0)
        eve.CLEAR()
        eve.CMD_NUMBER(0, 0, 30, 0, frame)
        eve.VERTEX_FORMAT(0)
        eve.BEGIN(eve.BEGIN_BITMAPS)
        for sub in subs:
            sub.draw(eve)
        eve.DISPLAY()
        if TAKE_SCREENSHOT and frame == 100:
            status = eve.LIB_FSSnapShot(0x400000, "touch.bmp")
            assert status == 0, "SD card couldn't be written"

        eve.CMD_SWAP()
        eve.CMD_SYNC()
        eve.CMD_REGWRITE(eve.REG_SO_SOURCE, so[flip])
        eve.LIB_EndCoProList()
        eve.LIB_AwaitCoProEmpty()

        frame = frame + 1
        flip ^= 1

apprunner.run(touchoffset, patch)
