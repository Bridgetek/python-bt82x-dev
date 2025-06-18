# Typical command line:
# python localbehavior1.py --connector ft4222module
import sys

# Add the library directories to the module search path.
sys.path.append('../..')
sys.path.append('../../bteve2')

# This module provides the connector to the EVE hardware.
import apprunner

def localbehavior_1(eve):
    eve.LIB_BeginCoProList()
    eve.CMD_WATCHDOG(36000000)  # watchdog at 500ms
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()
    eve.LIB_AutoCalibrate()

    prev_tag = 0
    state = [0 for i in range(5)]
    while True:
        eve.LIB_BeginCoProList()
        eve.CMD_DLSTART()
        eve.CLEAR_COLOR_RGB(20, 20, 20)
        eve.CLEAR()
        w = 1920 // 5
        for i in range(5):
            eve.TAG(1 + i)
            if state[i]:
                eve.COLOR_RGB(255, 200, 0)
            else:
                eve.COLOR_RGB(40, 40, 40)
            eve.CMD_BUTTON(i * w, 800, w - 10, 300, 34, eve.OPT_FLAT,  "ABCDE"[i])

        eve.DISPLAY()
        eve.CMD_SWAP()
        eve.LIB_EndCoProList()
        eve.LIB_AwaitCoProEmpty()

        tag = eve.rd32(eve.REG_TOUCH_TAG)
        if (prev_tag == 0) and (tag != 0):
            state[tag - 1] ^= 1
        prev_tag = tag

apprunner.run(localbehavior_1)
