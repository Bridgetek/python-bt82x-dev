# This is the EVE library.
import bteve2 as eve

def cmd_sevenseg(gd, x, y, size, digit, fgcolour, bgcolour):
    def fg():
        r,g,b = fgcolour
        gd.ColorRGB(r, g, b)
    def bg():
        r,g,b = bgcolour
        gd.ColorRGB(r, g, b)

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

    top = y
    centre = y + size
    bottom = y + (2 * size)
    left = x
    right = x + size

    pt0lx = x - (0.5 * size)
    pt0ly = y - (0.5 * size)

    pt1lx = x + (0.5 * size)
    pt1ly = y + (0.5 * size)

    pt2lx = x + (1.5 * size)
    pt2ly = y + (1.5 * size)

    pt3ly = y + (2.5 * size)

    width = (size * 0.64)/8

    gd.VertexFormat(2)
    gd.Vertex2f = gd.Vertex2f_4
    gd.ColorMask(0, 0, 0, 1)
    gd.BlendFunc(1, 4)
    # Top segment
    gd.Begin(eve.LINES)
    gd.LineWidth(width)
    gd.Vertex2f(left, top)
    gd.Vertex2f(right, top)
    # Top left segment
    gd.Begin(eve.LINES)
    gd.LineWidth(width)
    gd.Vertex2f(left, top)
    gd.Vertex2f(left, centre)
    # Top right segment
    gd.Begin(eve.LINES)
    gd.LineWidth(width)
    gd.Vertex2f(right, top)
    gd.Vertex2f(right, centre)
    # Centre segment
    gd.Begin(eve.LINES)
    gd.LineWidth(width)
    gd.Vertex2f(left, centre)
    gd.Vertex2f(right, centre)
    # Bottom left segment
    gd.Begin(eve.LINES)
    gd.LineWidth(width)
    gd.Vertex2f(left, centre)
    gd.Vertex2f(left, bottom)
    # Bottom right segment
    gd.Begin(eve.LINES)
    gd.LineWidth(width)
    gd.Vertex2f(right, centre)
    gd.Vertex2f(right, bottom)
    # Bottom segment
    gd.Begin(eve.LINES)
    gd.LineWidth(width)
    gd.Vertex2f(left, bottom)
    gd.Vertex2f(right, bottom)

    # Draw mesh frame for segments
    gd.BlendFunc(0, 4)
    gd.LineWidth(width * 0.9)
    gd.Begin(eve.LINE_STRIP)
    gd.Vertex2f(pt0lx, pt0ly)
    gd.Vertex2f(pt2lx, pt2ly)
    gd.Vertex2f(pt1lx, pt3ly)
    gd.Vertex2f(pt0lx, pt2ly)
    gd.Vertex2f(pt2lx, pt0ly)
    gd.Begin(eve.LINE_STRIP)
    gd.Vertex2f(pt0lx, pt3ly)
    gd.Vertex2f(pt2lx, pt1ly)
    gd.Vertex2f(pt1lx, pt0ly)
    gd.Vertex2f(pt0lx, pt1ly)
    gd.Vertex2f(pt2lx, pt3ly)

    gd.ColorMask(1, 1, 1, 0)
    gd.BlendFunc(3, 1)
    # Top segment
    seg(digit, 0)
    gd.Begin(eve.LINES)
    gd.LineWidth(width)
    gd.Vertex2f(left, top)
    gd.Vertex2f(right, top)
    # Top left segment
    seg(digit, 1)
    gd.Begin(eve.LINES)
    gd.LineWidth(width)
    gd.Vertex2f(left, top)
    gd.Vertex2f(left, centre)
    # Top right segment
    seg(digit, 2)
    gd.Begin(eve.LINES)
    gd.LineWidth(width)
    gd.Vertex2f(right, top)
    gd.Vertex2f(right, centre)
    # Centre segment
    seg(digit, 3)
    gd.Begin(eve.LINES)
    gd.LineWidth(width)
    gd.Vertex2f(left, centre)
    gd.Vertex2f(right, centre)
    # Bottom left segment
    seg(digit, 4)
    gd.Begin(eve.LINES)
    gd.LineWidth(width)
    gd.Vertex2f(left, centre)
    gd.Vertex2f(left, bottom)
    # Bottom right segment
    seg(digit, 5)
    gd.Begin(eve.LINES)
    gd.LineWidth(width)
    gd.Vertex2f(right, centre)
    gd.Vertex2f(right, bottom)
    # Bottom segment
    seg(digit, 6)
    gd.Begin(eve.LINES)
    gd.LineWidth(width)
    gd.Vertex2f(left, bottom)
    gd.Vertex2f(right, bottom)
    gd.BlendFunc(1, 4)
    gd.RestoreContext()
