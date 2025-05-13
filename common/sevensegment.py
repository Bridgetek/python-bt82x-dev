# This is the EVE library.
import bteve2 as eve

def cmd_sevenseg(gd, x, y, size, digit, fgcolour, bgcolour):
    def fg():
        r,g,b = fgcolour
        gd.COLOR_RGB(r, g, b)
    def bg():
        r,g,b = bgcolour
        gd.COLOR_RGB(r, g, b)

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
            ]
        if (map[digit][pos]):
            fg()
        else:
            bg()

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

    gd.VERTEX_FORMAT(2)
    gd.COLOR_MASK(0, 0, 0, 1)
    gd.BLEND_FUNC(1, 4)
    # Top segment
    gd.BEGIN(gd.BEGIN_LINES)
    gd.LINE_WIDTH(width)
    gd.VERTEX2F(left, top)
    gd.VERTEX2F(right, top)
    # Top left segment
    gd.BEGIN(gd.BEGIN_LINES)
    gd.LINE_WIDTH(width)
    gd.VERTEX2F(left, top)
    gd.VERTEX2F(left, centre)
    # Top right segment
    gd.BEGIN(gd.BEGIN_LINES)
    gd.LINE_WIDTH(width)
    gd.VERTEX2F(right, top)
    gd.VERTEX2F(right, centre)
    # Centre segment
    gd.BEGIN(gd.BEGIN_LINES)
    gd.LINE_WIDTH(width)
    gd.VERTEX2F(left, centre)
    gd.VERTEX2F(right, centre)
    # Bottom left segment
    gd.BEGIN(gd.BEGIN_LINES)
    gd.LINE_WIDTH(width)
    gd.VERTEX2F(left, centre)
    gd.VERTEX2F(left, bottom)
    # Bottom right segment
    gd.BEGIN(gd.BEGIN_LINES)
    gd.LINE_WIDTH(width)
    gd.VERTEX2F(right, centre)
    gd.VERTEX2F(right, bottom)
    # Bottom segment
    gd.BEGIN(gd.BEGIN_LINES)
    gd.LINE_WIDTH(width)
    gd.VERTEX2F(left, bottom)
    gd.VERTEX2F(right, bottom)

    # Draw mesh frame for segments
    gd.BLEND_FUNC(0, 4)
    gd.LINE_WIDTH(width * 0.9)
    gd.BEGIN(gd.BEGIN_LINE_STRIP)
    gd.VERTEX2F(pt0lx, pt0ly)
    gd.VERTEX2F(pt2lx, pt2ly)
    gd.VERTEX2F(pt1lx, pt3ly)
    gd.VERTEX2F(pt0lx, pt2ly)
    gd.VERTEX2F(pt2lx, pt0ly)
    gd.BEGIN(gd.BEGIN_LINE_STRIP)
    gd.VERTEX2F(pt0lx, pt3ly)
    gd.VERTEX2F(pt2lx, pt1ly)
    gd.VERTEX2F(pt1lx, pt0ly)
    gd.VERTEX2F(pt0lx, pt1ly)
    gd.VERTEX2F(pt2lx, pt3ly)

    gd.COLOR_MASK(1, 1, 1, 0)
    gd.BLEND_FUNC(3, 1)
    # Top segment
    seg(digit, 0)
    gd.BEGIN(gd.BEGIN_LINES)
    gd.LINE_WIDTH(width)
    gd.VERTEX2F(left, top)
    gd.VERTEX2F(right, top)
    # Top left segment
    seg(digit, 1)
    gd.BEGIN(gd.BEGIN_LINES)
    gd.LINE_WIDTH(width)
    gd.VERTEX2F(left, top)
    gd.VERTEX2F(left, centre)
    # Top right segment
    seg(digit, 2)
    gd.BEGIN(gd.BEGIN_LINES)
    gd.LINE_WIDTH(width)
    gd.VERTEX2F(right, top)
    gd.VERTEX2F(right, centre)
    # Centre segment
    seg(digit, 3)
    gd.BEGIN(gd.BEGIN_LINES)
    gd.LINE_WIDTH(width)
    gd.VERTEX2F(left, centre)
    gd.VERTEX2F(right, centre)
    # Bottom left segment
    seg(digit, 4)
    gd.BEGIN(gd.BEGIN_LINES)
    gd.LINE_WIDTH(width)
    gd.VERTEX2F(left, centre)
    gd.VERTEX2F(left, bottom)
    # Bottom right segment
    seg(digit, 5)
    gd.BEGIN(gd.BEGIN_LINES)
    gd.LINE_WIDTH(width)
    gd.VERTEX2F(right, centre)
    gd.VERTEX2F(right, bottom)
    # Bottom segment
    seg(digit, 6)
    gd.BEGIN(gd.BEGIN_LINES)
    gd.LINE_WIDTH(width)
    gd.VERTEX2F(left, bottom)
    gd.VERTEX2F(right, bottom)
    gd.BLEND_FUNC(1, 4)
    gd.RESTORE_CONTEXT()
