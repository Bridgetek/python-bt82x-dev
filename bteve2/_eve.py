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
