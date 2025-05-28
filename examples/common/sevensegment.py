# This is the EVE library.
import bteve2 as evelib

# Set to True is cmd_region/cmd_endregion are active.
region = False

# Seven Segment LED Widget
#
# Calling format:
#   sevenseg.cmd_sevenseg(x, y, size, digit, fgcolour, bgcolour)
#
# Parameters:
#   x,y: Location of top left of the seven segment LED widget (in pixels).
#   size: Size of a segment of the seven segment LED widget (in pixels).
#   digit: Number to display on seven segment LED. Range 0-16.
#       0 to 9, 10 for 'a' to 15 for 'f', and 16 for '-'.
#   fgcolour: Tuple with (R,G,B) colour for active segment.
#   bgcolour: Tuple with (R,G,B) colour for inactive segment.
#
def cmd_sevenseg(eve, x, y, size, digit, fgcolour = (255,0,0), bgcolour = (20,0,0)):
    def fg():
        r,g,b = fgcolour
        eve.COLOR_RGB(r, g, b)
    def bg():
        r,g,b = bgcolour
        eve.COLOR_RGB(r, g, b)

    def seg(digit, pos):
        map = [[1,1,1,0,1,1,1], #0
            [0,0,1,0,0,1,0], #1
            [1,0,1,1,1,0,1], #2
            [1,0,1,1,0,1,1], #3
            [0,1,1,1,0,1,0], #4
            [1,1,0,1,0,1,1], #5
            [1,1,0,1,1,1,1], #6
            [1,0,1,0,0,1,0], #7
            [1,1,1,1,1,1,1], #8
            [1,1,1,1,0,1,0], #9
            [1,1,1,1,1,1,0], #a
            [0,1,0,1,1,1,1], #b
            [1,1,0,0,1,0,1], #c
            [0,0,1,1,1,1,1], #d
            [1,1,1,1,1,0,1], #e
            [1,1,0,1,1,0,0], #f
            [0,0,0,1,0,0,0], #-
            ]
        if (map[digit][pos]):
            fg()
        else:
            bg()

    assert(type(eve) == evelib.EVE2)
    
    format = 4
    top = (y) * 4
    centre = (y + size) * 4
    bottom = (y + (2 * size)) * 4
    left = (x) * 4
    right = (x + size) * 4

    pt0lx = (x - (0.5 * size)) * 4
    pt0ly = (y - (0.5 * size)) * 4

    pt1lx = (x + (0.5 * size)) * 4
    pt1ly = (y + (0.5 * size)) * 4

    pt2lx = (x + (1.5 * size)) * 4
    pt2ly = (y + (1.5 * size)) * 4

    pt3ly = (y + (2.5 * size)) * 4

    width = (size * 0.64)/8

    if region:
        eve.CMD_REGION()
    
    eve.SAVE_CONTEXT()

    eve.VERTEX_FORMAT(2)
    eve.COLOR_MASK(0, 0, 0, 1)
    eve.BLEND_FUNC(1, 4)
    # Top segment
    eve.BEGIN(eve.BEGIN_LINES)
    eve.LINE_WIDTH(width)
    eve.VERTEX2F(left, top)
    eve.VERTEX2F(right, top)
    # Top left segment
    eve.BEGIN(eve.BEGIN_LINES)
    eve.LINE_WIDTH(width)
    eve.VERTEX2F(left, top)
    eve.VERTEX2F(left, centre)
    # Top right segment
    eve.BEGIN(eve.BEGIN_LINES)
    eve.LINE_WIDTH(width)
    eve.VERTEX2F(right, top)
    eve.VERTEX2F(right, centre)
    # Centre segment
    eve.BEGIN(eve.BEGIN_LINES)
    eve.LINE_WIDTH(width)
    eve.VERTEX2F(left, centre)
    eve.VERTEX2F(right, centre)
    # Bottom left segment
    eve.BEGIN(eve.BEGIN_LINES)
    eve.LINE_WIDTH(width)
    eve.VERTEX2F(left, centre)
    eve.VERTEX2F(left, bottom)
    # Bottom right segment
    eve.BEGIN(eve.BEGIN_LINES)
    eve.LINE_WIDTH(width)
    eve.VERTEX2F(right, centre)
    eve.VERTEX2F(right, bottom)
    # Bottom segment
    eve.BEGIN(eve.BEGIN_LINES)
    eve.LINE_WIDTH(width)
    eve.VERTEX2F(left, bottom)
    eve.VERTEX2F(right, bottom)

    # Draw mesh frame for segments
    eve.BLEND_FUNC(0, 4)
    eve.LINE_WIDTH(width * 0.9)
    eve.BEGIN(eve.BEGIN_LINE_STRIP)
    eve.VERTEX2F(pt0lx, pt0ly)
    eve.VERTEX2F(pt2lx, pt2ly)
    eve.VERTEX2F(pt1lx, pt3ly)
    eve.VERTEX2F(pt0lx, pt2ly)
    eve.VERTEX2F(pt2lx, pt0ly)
    eve.BEGIN(eve.BEGIN_LINE_STRIP)
    eve.VERTEX2F(pt0lx, pt3ly)
    eve.VERTEX2F(pt2lx, pt1ly)
    eve.VERTEX2F(pt1lx, pt0ly)
    eve.VERTEX2F(pt0lx, pt1ly)
    eve.VERTEX2F(pt2lx, pt3ly)

    eve.COLOR_MASK(1, 1, 1, 0)
    eve.BLEND_FUNC(3, 1)
    # Top segment
    seg(digit, 0)
    eve.BEGIN(eve.BEGIN_LINES)
    eve.LINE_WIDTH(width)
    eve.VERTEX2F(left, top)
    eve.VERTEX2F(right, top)
    # Top left segment
    seg(digit, 1)
    eve.BEGIN(eve.BEGIN_LINES)
    eve.LINE_WIDTH(width)
    eve.VERTEX2F(left, top)
    eve.VERTEX2F(left, centre)
    # Top right segment
    seg(digit, 2)
    eve.BEGIN(eve.BEGIN_LINES)
    eve.LINE_WIDTH(width)
    eve.VERTEX2F(right, top)
    eve.VERTEX2F(right, centre)
    # Centre segment
    seg(digit, 3)
    eve.BEGIN(eve.BEGIN_LINES)
    eve.LINE_WIDTH(width)
    eve.VERTEX2F(left, centre)
    eve.VERTEX2F(right, centre)
    # Bottom left segment
    seg(digit, 4)
    eve.BEGIN(eve.BEGIN_LINES)
    eve.LINE_WIDTH(width)
    eve.VERTEX2F(left, centre)
    eve.VERTEX2F(left, bottom)
    # Bottom right segment
    seg(digit, 5)
    eve.BEGIN(eve.BEGIN_LINES)
    eve.LINE_WIDTH(width)
    eve.VERTEX2F(right, centre)
    eve.VERTEX2F(right, bottom)
    # Bottom segment
    seg(digit, 6)
    eve.BEGIN(eve.BEGIN_LINES)
    eve.LINE_WIDTH(width)
    eve.VERTEX2F(left, bottom)
    eve.VERTEX2F(right, bottom)
    eve.BLEND_FUNC(1, 4)
    
    if region:
        eve.CMD_ENDREGION(left - width, top - width, right + width, bottom + width)
    else:
        eve.RESTORE_CONTEXT()
