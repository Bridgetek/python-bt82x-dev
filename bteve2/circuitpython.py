# For Bridgetek Pte. Ltd. license see `LICENSE.txt`

import time
import struct

import time
import struct

import os
import board
import digitalio

from busio import SPI

import bteve2 as eve

def spilock(f):
    def wrapper(*args):
        spi = args[0].sp
        while not spi.try_lock():
            pass
        r = f(*args)
        spi.unlock()
        return r
    return wrapper

class connector():
    FREQUENCY = 72_000_000      # system clock frequency, in Hz
    multi_mode = False

    def __init__(self):
        print("Initialise circuitpython interface")

        mach = os.uname().machine
        if mach.startswith("Raspberry Pi Pico with rp2040"):
            self.sp = SPI(board.GP2, MOSI=board.GP3, MISO=board.GP4)
            self.pcs = self.pin(board.GP5) #cs of SPI for Eve
            self.pdn = self.pin(board.GP7) #power down pin of Eve
        elif mach.startswith("Adafruit Feather "):
            self.sp = SPI(board.D12, MOSI=board.D13, MISO=board.D11)
            self.pcs = self.pin(board.D10) #cs of SPI for Eve
            self.pdn = self.pin(board.D6) #power down pin of Eve
            #self.sp = SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
            #self.pcs = self.pin(board.D4) #cs of SPI for Eve
            #self.pdn = self.pin(board.D6) #power down pin of Eve
        else:
            self.sp = busio.SPI(board.D13, MOSI=board.D11, MISO=board.D12)
            self.pcs = self.pin(board.D8) #cs of SPI for Eve
            self.pdn = self.pin(board.D10) #power down pin of Eve
        self.setup_spi()

    def pin(self,p):
        r = digitalio.DigitalInOut(p)
        r.direction = digitalio.Direction.OUTPUT
        r.value = True
        return r

    @spilock
    def setup_spi(self):
        self.sp.configure(baudrate=20_000_000, phase=0, polarity=0)

    @spilock
    def exchange(self, wr, rd = 0):
        self.pcs.value = False
        self.sp.write(wr)
        r = None
        if rd != 0:
            r = bytearray(rd)
            self.sp.readinto(r)
        self.pcs.value = True
        return r

    def setup_flash(self):
        pass

    def sleepclocks(self, n):
        time.sleep(n / 72e6)

    abuf = bytearray(4)
    def addr(self, a):
        struct.pack_into(">I", self.abuf, 0, a)
        return self.abuf

    def rd32(self, a):
        return struct.unpack("I", self.rd(a, 4))[0]
        
    @spilock
    def rd(self, a, nn):
        assert (a & 3) == 0
        assert (nn & 3) == 0
        if nn == 0:
            return b""
        a1 = a + nn
        r = b''
        while a != a1:
            # Timeout for a read is 7uS for BT82x.
            # At a 20MHz SPI bus the timout is approximately 140 clock cycles.
            # Read a maximum of 4 bytes before the "0x01" that signifies data ready.
            n = min(a1 - a, 4 + nn)
            self.pcs.value = False
            self.sp.write(self.addr(a))
            def recv(n):
                read_buffer = bytearray(n)
                self.sp.readinto(read_buffer)
                return read_buffer
            bb = recv(4 + n)
            if 1 in list(bb):
                # Got READY byte in response
                i = list(bb).index(1)
                response = bb[i + 1:i + 1 + n]
            else:
                # Poll for READY byte
                while recv(1) == b'\x00':
                    pass
                response = b''
            # Handle case of full response not received
            if len(response) < n:
                response += recv(n - len(response))
            a += n
            r += response
            self.pcs.value = True
        return r

    @spilock
    def wr(self, a, s, inc=True):
        _ = inc
        assert (a & 3) == 0
        t = len(s)
        assert (t & 3) == 0

        self.pcs.value = False
        self.sp.write(self.addr(a | (1 << 31)))
        self.sp.write(s)
        self.pcs.value = True

    def cs(self, v):
        if v:
            self.pcs.value = False
        else:
            self.pcs.value = True

    def reset(self):
        self.pdn.value = False
        time.sleep(.1)
        self.pdn.value = True
        time.sleep(.1)

        while 1:
            # Set System PLL NS = 15 for 576MHz
            self.exchange(bytes([0xFF, 0xE4, 0x0F, 0x00, 0x00]))
            # Set System clock divider to 0x17 for 72MHz
            self.exchange(bytes([0xFF, 0xE6, 0x17, 0x00, 0x00]))
            # Set bypass BOOT_BYPASS_OTP, DDRTYPT_BYPASS_OTP and set BootCfgEn
            self.exchange(bytes([0xFF, 0xE9, 0xe1, 0x00, 0x00]))
            # Set DDR Type - 1333, DDR3L, 4096
            self.exchange(bytes([0xFF, 0xEB, 0x08, 0x00, 0x00]))
            # Set DDR, JT and AUD in Boot Control
            self.exchange(bytes([0xFF, 0xE8, 0xF0, 0x00, 0x00]))
            # CLEAR BootCfgEn
            self.exchange(bytes([0xFF, 0xE9, 0xC0, 0x00, 0x00]))
            # Perform a reset pulse
            self.exchange(bytes([0xFF, 0xE7, 0x00, 0x00, 0x00]))
            # Set ACTIVE
            self.exchange(bytes([0x00, 0x00, 0x00, 0x00, 0x00]))
            time.sleep(.2)

            bb = self.exchange(self.addr(0), 128)
            t0 = time.monotonic_ns()
            fault = False
            if 1 in list(bb):
                while self.rd32(eve.EVE2.REG_ID) != 0x7c:
                    pass
                while not fault and self.rd32(eve.EVE2.REG_BOOT_STATUS) != 0x522e2e2e:
                    fault = 1e-9 * (time.monotonic_ns() - t0) > 0.1
                if fault:
                    bs = self.rd32(eve.EVE2.REG_BOOT_STATUS)
                    print(f"[Timeout waiting for REG_BOOT_STATUS, stuck at {bs:08x}, retrying...]")
                    continue
                actual = self.rd32(eve.EVE2.REG_FREQUENCY)
                if actual != self.FREQUENCY:
                    print(f"[Requested {self.FREQUENCY/1e6} MHz, but actual is {actual/1e6} MHz after reset, retrying...]")
                    continue
                return

            print(f"[Boot fail after reset, retrying...]")

        # Disable QSPI burst mode
        #self.wr32(eve.EVE2.REG_SYS_CFG, 1 << 10)


