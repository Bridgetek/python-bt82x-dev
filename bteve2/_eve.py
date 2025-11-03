import struct

class _EVE:

    buf = bytearray()
    bufptr = 0
    
    # Add commands to the co-processor buffer.
    # It is only sent when flush is called or the buffer exceeds
    # the size of the FIFO.
    def cc(self, s):
        assert (len(s) % 4) == 0, "Coprocessor commands must be a multiple of 4 bytes"
        for b in s: 
            self.buf[self.bufptr] = b
            self.bufptr += 1
            #assert (self.bufptr % 4) == 0, "Coprocessor command buffer must be a multiple of 4 bytes"
            # Flush the co-processor buffer to the EVE device.
            if self.bufptr >= self.FIFO_MAX - 16:
                self.flush()

    # Send a 32-bit basic graphic command to the EVE.
    def cmd0(self, num):
        self.cc(int(0xffffff00 | num).to_bytes(4, "little"))

    # Send a 32-bit basic graphic command and parameters to the EVE.
    def cmd(self, num, fmt, args):
        self.cc(int(0xffffff00 | num).to_bytes(4, "little"))
        self.cc(struct.pack(fmt, *args))

    def register(self, sub):
        self.buf = bytearray(self.FIFO_MAX)
        self.bufptr = 0
        assert (len(self.buf) == self.FIFO_MAX)
        getattr(sub, 'write') # Confirm that there is a write method

    # Send the co-processor buffer to the EVE device.
    def flush(self):
        if self.bufptr:
            self.write(self.buf[:self.bufptr])
            self.bufptr = 0
    def PaletteSource(self, addr):
        self.cI((42 << 24) | (((addr) & 0xffffff)))
    def PaletteSourceH(self, addr):
        self.cI((50 << 24) | (((addr >> 24) & 255)))
    def BitmapHandle(self, handle):
        self.cI((5 << 24) | ((handle & 63)))
    def Tag(self, s):
        self.cI((3 << 24) | ((s & 0xffffff)))

    def AlphaFunc(self, func,ref):
        self.c4((9 << 24) | ((int(func) & 7) << 8) | ((int(ref) & 255)))
    def Begin(self, prim):
        self.c4((31 << 24) | ((int(prim) & 15)))
    def BitmapExtFormat(self, fmt):
        self.c4((46 << 24) | (int(fmt) & 65535))
    def BitmapHandle(self, handle):
        self.c4((5 << 24) | ((int(handle) & 63)))
    def BitmapLayout(self, format,linestride,height):
        self.c4((7 << 24) | ((int(format) & 31) << 19) | ((int(linestride) & 1023) << 9) | ((int(height) & 511)))
    def BitmapLayoutH(self, linestride,height):
        self.c4((40 << 24) | (((linestride) & 3) << 2) | (((height) & 3)))
    def BitmapSize(self, filter,wrapx,wrapy,width,height):
        self.c4((8 << 24) | ((int(filter) & 1) << 20) | ((int(wrapx) & 1) << 19) | ((int(wrapy) & 1) << 18) | ((int(width) & 511) << 9) | ((int(height) & 511)))
    def BitmapSizeH(self, width,height):
        self.c4((41 << 24) | (((width) & 3) << 2) | (((height) & 3)))
    def BitmapSource(self, addr):
        self.c4((1 << 24) | ((int(addr) & 0xffffff)))
    def BitmapSourceH(self, addr):
        self.c4((49 << 24) | ((int(addr) & 0xff)))
    def BitmapSwizzle(self, r, g, b, a):
        self.c4((47 << 24) | ((int(r) & 7) << 9) | ((int(g) & 7) << 6) | ((int(b) & 7) << 3) | ((int(a) & 7)))
    def BitmapTransformA(self, p, a):
        self.c4((21 << 24) | ((int(p) & 1) << 17) | ((int(a) & 131071)))
    def BitmapTransformB(self, p, b):
        self.c4((22 << 24) | ((int(p) & 1) << 17) | ((int(b) & 131071)))
    def BitmapTransformC(self, c):
        self.c4((23 << 24) | (int(c) & 16777215))
    def BitmapTransformD(self, p, d):
        self.c4((24 << 24) | ((int(p) & 1) << 17) | ((int(d) & 131071)))
    def BitmapTransformE(self, p, e):
        self.c4((25 << 24) | ((int(p) & 1) << 17) | ((int(e) & 131071)))
    def BitmapTransformF(self, f):
        self.c4((26 << 24) | (int(f) & 16777215))
    #def BitmapZorder(self,o):
    #    self.c4((51 << 24) | (int(o) & 255))
    def BlendFunc(self, src,dst):
        self.c4((11 << 24) | ((int(src) & 7) << 3) | ((int(dst) & 7)))
    def Call(self, dest):
        self.c4((29 << 24) | ((int(dest) & 65535)))
    def Cell(self, cell):
        self.c4((6 << 24) | ((int(cell) & 127)))
    def ClearColorA(self, alpha):
        self.c4((15 << 24) | ((int(alpha) & 255)))
    def ClearColorRGB(self, red,green,blue):
        self.c4((2 << 24) | ((int(red) & 255) << 16) | ((int(green) & 255) << 8) | ((int(blue) & 255)))
    def Clear(self, c = 1,s = 1,t = 1):
        self.c4((38 << 24) | ((int(c) & 1) << 2) | ((int(s) & 1) << 1) | ((int(t) & 1)))
    def ClearStencil(self, s):
        self.c4((17 << 24) | ((int(s) & 255)))
    def ClearTag(self, s):
        self.c4((18 << 24) | ((int(s) & 0xffffff)))
    def ColorA(self, alpha):
        self.c4((16 << 24) | ((int(alpha) & 255)))
    def ColorMask(self, r,g,b,a):
        self.c4((32 << 24) | ((int(r) & 1) << 3) | ((int(g) & 1) << 2) | ((int(b) & 1) << 1) | ((int(a) & 1)))
    def ColorRGB(self, red,green,blue):
        self.c4((4 << 24) | ((int(red) & 255) << 16) | ((int(green) & 255) << 8) | ((int(blue) & 255)))
    def Display(self):
        self.c4((0 << 24))
    def End(self):
        self.c4((33 << 24))
    def Jump(self, dest):
        self.c4((30 << 24) | ((int(dest) & 65535)))
    def LineWidth(self, width):
        self.c4((14 << 24) | ((int(width) & 4095)))
    def Macro(self, m):
        self.c4((37 << 24) | ((int(m) & 1)))
    def Nop(self):
        self.c4((45 << 24))
    def PaletteSource(self, addr):
        self.c4((42 << 24) | (((addr) & 0xffffff)))
    def PaletteSourceH(self, addr):
        self.c4((50 << 24) | (((addr >> 24) & 255)))
    def PointSize(self, size):
        self.c4((13 << 24) | ((int(size) & 8191)))
    def Region(self,y,h,dest):
        self.c4((52 << 24) | ((int(y) & 63) << 18) | ((int(h) & 63 ) << 12) | (int(dest) & 4095))
    def RestoreContext(self):
        self.c4((35 << 24))
    def Return(self):
        self.c4((36 << 24))
    def SaveContext(self):
        self.c4((34 << 24))
    def ScissorSize(self, width,height):
        self.c4((28 << 24) | ((int(width) & 4095) << 12) | ((int(height) & 4095)))
    def ScissorXY(self, x,y):
        self.c4((27 << 24) | ((int(x) & 2047) << 11) | ((int(y) & 2047)))
    def StencilFunc(self, func,ref,mask):
        self.c4((10 << 24) | ((int(func) & 7) << 16) | ((int(ref) & 255) << 8) | ((int(mask) & 255)))
    def StencilMask(self, mask):
        self.c4((19 << 24) | ((int(mask) & 255)))
    def StencilOp(self, sfail,spass):
        self.c4((12 << 24) | ((int(sfail) & 7) << 3) | ((int(spass) & 7)))
    def TagMask(self, mask):
        self.c4((20 << 24) | ((int(mask) & 1)))
    def Tag(self, s):
        self.c4((3 << 24) | ((int(s) & 0xffffff)))
    def VertexFormat(self, frac):
        self.c4((39 << 24) | (int(frac) & 7))
    def Vertex2f(self, x, y):
        self.c4(0x40000000 | ((int(x) & 32767) << 15) | (int(y) & 32767))
    def Vertex2ii(self, x, y, handle = 0, cell = 0):
        self.c4((2 << 30) | ((int(x) & 511) << 21) | ((int(y) & 511) << 12) | ((int(handle) & 31) << 7) | ((int(cell) & 127)))
    def VertexTranslateX(self, x):
        self.c4((43 << 24) | (((int(x)) & 131071)))
    def VertexTranslateY(self, y):
        self.c4((44 << 24) | (((int(y)) & 131071)))

