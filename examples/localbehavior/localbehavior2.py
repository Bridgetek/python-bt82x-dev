# Typical command line:
# python localbehavior2.py --connector ft4222module
import sys

# Add the library directories to the module search path.
sys.path.append('../..')
sys.path.append('../../bteve2')

# This module provides the connector to the EVE hardware.
import apprunner

class Builder(apprunner.bteve2.EVE2):
    def __init__(self):
        self.buf = bytearray()
        super(Builder).__init__()
        self.cs = []

    def cc(self, s):
        self.buf += s

    def here(self):
        # Current location
        return len(self.buf)

    def resolve(self):
        # Resolve a forward jump to the current location
        m = self.cs.pop()
        o = self.here() - m
        self.buf[m-4:m] = o.to_bytes(4, 'little')

    def inverse(self, func):
        return {
            self.TEST_LESS:       self.TEST_GEQUAL,
            self.TEST_LEQUAL:     self.TEST_GREATER,
            self.TEST_GREATER:    self.TEST_LEQUAL,
            self.TEST_GEQUAL:     self.TEST_LESS,
            self.TEST_EQUAL:      self.TEST_NOTEQUAL,
            self.TEST_NOTEQUAL:   self.TEST_EQUAL,
        }[func]

    def _if(self, a, func, ref, mask = 0xffffffff):
        self.CMD_SKIPCOND(a, self.inverse(func), ref, mask, 0)
        self.cs.append(self.here())

    def _else(self):
        self.CMD_SKIPCOND(0, self.TEST_ALWAYS, 0, 0, 0)
        self.resolve()
        self.cs.append(self.here())

    def _endif(self):
        self.resolve()

    def _begin(self):
        self.cs.append(self.here())

    def _again(self):
        o = self.cs.pop() - (self.here() + 24)
        self.CMD_SKIPCOND(0, self.TEST_ALWAYS, 0, 0, o & 0xffffffff)

def localbehavior_2(eve):
    eve.LIB_BeginCoProList()
    eve.CMD_WATCHDOG(36000000)  # watchdog at 500ms
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()
    eve.LIB_AutoCalibrate()

    prev_tag = 0x1000
    state    = 0x1004

    eve.LIB_BeginCoProList()
    eve.CMD_MEMZERO(state,  5 * 4)

    bd = Builder()
    bd._begin()
    bd.CLEAR_COLOR_RGB(20, 20, 20)
    bd.CLEAR()
    w = 1920 // 5
    for i in range(5):
        bd.TAG(1 + i)
        bd._if(state + 4 * i, eve.TEST_NOTEQUAL, 0)         # {
        bd.CMD_FGCOLOR(0x404080)
        bd.COLOR_RGB(255, 200, 0)
        bd._else()                                          # }{
        bd.CMD_FGCOLOR(0x202020)
        bd.COLOR_RGB(60, 60, 60)
        bd._endif()                                         # }

        bd.CMD_BUTTON(i * w, 800, w - 10, 300, 34, eve.OPT_FLAT,  "ABCDE"[i])

    bd._if(prev_tag, eve.TEST_EQUAL, 0)                     # {
    for i in range(5):
        bd._if(eve.REG_TOUCH_TAG, eve.TEST_EQUAL, i + 1)    # {
        s = state + 4 * i
        bd._if(s, eve.TEST_EQUAL, 0)                        # {
        bd.CMD_MEMWRITE(s, 4)
        bd.c4(1)
        bd._else()                                          # }{
        bd.CMD_MEMWRITE(s, 4)
        bd.c4(0)
        bd._endif()                                         # }
        bd._endif()                                         # }
    bd._endif()                                             # }

    bd.CMD_MEMCPY(prev_tag, eve.REG_TOUCH_TAG, 4)

    bd.DISPLAY()
    bd.CMD_SWAP()
    bd.CMD_DLSTART()
    bd._again()
    bd.CMD_RETURN()

    eve.cs(True)
    eve.wr(0, bd.buf)
    eve.cs(False)
    eve.CMD_CALLLIST(0)
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()

apprunner.run(localbehavior_2)
