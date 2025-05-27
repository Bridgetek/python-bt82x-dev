import math

# This is the EVE library.
import bteve2 as evelib

# Set to True is cmd_region/cmd_endregion are active.
region = False

# VU Meter Widget
#
# Calling format:
#   vumeter.cmd_vumeter(eve, x, y, w, h, vu_level, vu_prev, border)
#
# Parameters:
#   eve: Handle to class of bteve2.
#   x,y: Location of top left of the VU Meter widget (in pixels).
#   w,h: Size of the VU Meter widget (in pixels).
#   vu_level: position of VU Meter dial. 0 to 255 (Full Scale Deflection)
#   vu_prev: previous position of VU Meter dial.
#   border: thickness of grey border around the VU Meter.
#
# Returns:
#   This returns the vu_prev value that must be passed the next time it is 
#   called to ensure proper animated action.
#
def cmd_vumeter(eve, x, y, w, h, vu_level, vu_prev = None, border=5):
    assert(type(eve) == evelib.EVE2)
    assert((vu_level < 256) and (vu_level >= 0))

    if vu_prev == None:
        vu_prev = vu_level
    else:
        assert((vu_prev < 256) and (vu_prev >= 0))

    if vu_level > vu_prev: 
        vu_level = ((vu_prev + vu_level) * 99) // 200
    else : 
        vu_level = (vu_prev * 98) // 100
    
    if region:
        eve.CMD_REGION()
    
    eve.SAVE_CONTEXT()

    # Pixel resolution
    eve.VERTEX_FORMAT(0)
    
    # Cut-outs for VU meters
    eve.BEGIN(eve.BEGIN_RECTS)
    # Border for trace graphs
    eve.COLOR_RGB(125, 125, 125)
    eve.VERTEX2F(x - border, y - border)
    eve.VERTEX2F(x + w + border, y + h + border)
    # Inside for trace graphs
    eve.COLOR_RGB(255, 255, 255)
    eve.VERTEX2F(x, y)
    eve.VERTEX2F(x + w, y + h)
    eve.END()

    eve.BEGIN(eve.BEGIN_LINES)
    eve.COLOR_RGB(0, 0, 0)
    eve.LINE_WIDTH(2)
    eve.VERTEX2F(x + ((w * 1) // 12), y + ((h * 4) // 12))
    eve.VERTEX2F(x + w - ((w * 4) // 12), y + ((h * 4) // 12))
    eve.VERTEX2F(x + ((w * 2) // 12), y + ((h * 4) // 12))
    eve.VERTEX2F(x + ((w * 2) // 12), y + ((h * 3) // 12))
    eve.VERTEX2F(x + ((w * 5) // 12), y + ((h * 4) // 12))
    eve.VERTEX2F(x + ((w * 5) // 12), y + ((h * 3) // 12))
    eve.VERTEX2F(x + ((w * 6) // 12), y + ((h * 4) // 12))
    eve.VERTEX2F(x + ((w * 6) // 12), y + ((h * 3) // 12))
    eve.VERTEX2F(x + ((w * 7) // 12), y + ((h * 4) // 12))
    eve.VERTEX2F(x + ((w * 7) // 12), y + ((h * 3) // 12))
    eve.VERTEX2F(x + ((w * 8) // 12), y + ((h * 4) // 12))
    eve.VERTEX2F(x + ((w * 8) // 12), y + ((h * 3) // 12))
    eve.COLOR_RGB(255, 0, 0)
    eve.LINE_WIDTH(8)
    eve.VERTEX2F(x + ((w * 8) // 12), y + ((h * 4) // 12))
    eve.VERTEX2F(x + ((w * 11) // 12), y + ((h * 4) // 12))
    eve.VERTEX2F(x + ((w * 10) // 12), y + ((h * 4) // 12))
    eve.VERTEX2F(x + ((w * 10) // 12), y + ((h * 3) // 12))
    eve.VERTEX2F(x + ((w * 11) // 12), y + ((h * 4) // 12))
    eve.VERTEX2F(x + ((w * 11) // 12), y + ((h * 3) // 12))
    eve.END()
    eve.COLOR_RGB(0, 0, 0)
    eve.BEGIN(eve.BEGIN_BITMAPS)
    eve.VERTEX2II(x + (w // 2) - 22, y + (h // 2), 24, 86)
    eve.VERTEX2II(x + (w // 2), y + (h // 2), 24, 85)
    eve.END()

    # Draw VU meter pointer
    eve.BEGIN(eve.BEGIN_LINES)
    eve.COLOR_RGB(0, 0, 0)
    eve.LINE_WIDTH(2)
    eve.VERTEX2F(x + (w // 2), y + h - border)
    eve.VERTEX2F(x + (w // 2) + ((math.sin(((vu_level - 128) / 512) * math.pi)) * (h * 3 // 4)), 
                y + h - border - ((math.cos(((vu_level - 128) / 512) * math.pi)) * (h * 3 // 4)))
    eve.END()

    if region:
        eve.CMD_ENDREGION(x - border, y - border, x + w + border, y + h + border)
    else:
        eve.RESTORE_CONTEXT()

    return vu_level