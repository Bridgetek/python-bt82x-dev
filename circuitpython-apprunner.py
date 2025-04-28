import bteve2 as eve

import time
import struct

import board
import busio
import digitalio

import sdcardio
import storage

# from rpsoftspi import SPI
# from rppiospi import SPI
from busio import SPI

FREQUENCY = 72_000_000      # system clock frequency, in Hz

def spilock(f):
    def wrapper(*args):
        spi = args[0].sp
        while not spi.try_lock():
            pass
        r = f(*args)
        spi.unlock()
        return r
    return wrapper

class EVE2(eve.EVE2):
    def __init__(self):

        self.sp = SPI(board.GP2, MOSI=board.GP3, MISO=board.GP4)
        self.cs = self.pin(board.GP5) #cs of SPI for Eve
        self.pdn = self.pin(board.GP7) #power down pin of Eve

        self.setup_spi()
        print('SD', self.setup_sd())
        self.boot()

    def pin(self,p):
        r = digitalio.DigitalInOut(p)
        r.direction = digitalio.Direction.OUTPUT
        r.value = True
        return r

    @spilock
    def setup_spi(self):
        self.sp.configure(baudrate=20_000_000, phase=0, polarity=0)

    def setup_sd(self):
        """ Setup sdcard"""
        spi_sdcard = busio.SPI(board.GP10, MOSI=board.GP11, MISO=board.GP12)
        sdcs = board.GP13 #cs of SPI for SD card
        try:
            self.sdcard = sdcardio.SDCard(spi_sdcard, sdcs)
        except OSError:
            return False
        self.vfs = storage.VfsFat(self.sdcard)
        storage.mount(self.vfs, "/sd")
        return True

    @spilock
    def transfer(self, wr, rd = 0):
        self.cs.value = False
        self.sp.write(wr)
        r = None
        if rd != 0:
            r = bytearray(rd)
            self.sp.readinto(r)
        self.cs.value = True
        return r

    abuf = bytearray(4)
    def addr(self, a):
        struct.pack_into(">I", self.abuf, 0, a)
        return self.abuf

    def reset(self):
        while 1:
            # Set System PLL NS = 15 for 576MHz
            self.transfer(bytes([0xFF, 0xE4, 0x0F, 0x00, 0x00]))
            # Set System clock divider to 0x17 for 72MHz
            self.transfer(bytes([0xFF, 0xE6, 0x17, 0x00, 0x00]))
            # Set bypass BOOT_BYPASS_OTP, DDRTYPT_BYPASS_OTP and set BootCfgEn
            self.transfer(bytes([0xFF, 0xE9, 0xe1, 0x00, 0x00]))
            # Set DDR Type - 1333, DDR3L, 4096
            self.transfer(bytes([0xFF, 0xEB, 0x08, 0x00, 0x00]))
            # Set DDR, JT and AUD in Boot Control
            self.transfer(bytes([0xFF, 0xE8, 0xF0, 0x00, 0x00]))
            # Clear BootCfgEn
            self.transfer(bytes([0xFF, 0xE9, 0xC0, 0x00, 0x00]))
            # Perform a reset pulse
            self.transfer(bytes([0xFF, 0xE7, 0x00, 0x00, 0x00]))  
            time.sleep(.1)

            bb = self.transfer(self.addr(0), 128)
            t0 = time.monotonic_ns()
            fault = False
            if 1 in list(bb):
                while self.rd32(eve.REG_ID) != 0x7c:
                    pass
                while not fault and self.rd32(eve.REG_BOOT_STATUS) != 0x522e2e2e:
                    fault = 1e-9 * (time.monotonic_ns() - t0) > 0.1
                if fault:
                    bs = self.rd32(eve.REG_BOOT_STATUS)
                    print(f"[Timeout waiting for REG_BOOT_STATUS, stuck at {bs:08x}, retrying...]")
                    continue
                actual = self.rd32(eve.REG_FREQUENCY)
                if actual != FREQUENCY:
                    print(f"[Requested {FREQUENCY/1e6} MHz, but actual is {actual/1e6} MHz after reset, retrying...]")
                    continue
                return

            print(f"[Boot fail after reset, retrying...]")

    @spilock
    def rd(self, a, nn):
        assert (a & 3) == 0
        assert (nn & 3) == 0
        if nn == 0:
            return b''
        a1 = a + nn
        r = b''
        while a != a1:
            n = min(a1 - a, 32)
            self.cs.value = False
            self.sp.write(self.addr(a))
            def recv(n):
                read_buffer = bytearray(n)
                self.sp.readinto(read_buffer)
                return read_buffer
            bb = recv(32 + n)
            if 1 in list(bb):            # Got READY byte in response
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
            self.cs.value = True
        return r

    @spilock
    def wr(self, a, s):
        assert (a & 3) == 0
        t = len(s)
        assert (t & 3) == 0

        self.cs.value = False
        self.sp.write(self.addr(a | (1 << 31)))
        self.sp.write(s)
        self.cs.value = True

    def sleepclocks(self, n):
        time.sleep(n / 36e6)

    def setup_flash(self):
        pass

def run(app, minimal = False):
    gd = EVE2()
    gd.register(gd)

    if minimal == False:
        gd.cmd0(0)

        gd.cmd_regwrite(eve.REG_SC0_SIZE, 2)
        gd.cmd_regwrite(eve.REG_SC0_PTR0, 10 << 20)
        gd.cmd_regwrite(eve.REG_SC0_PTR1, 18 << 20)
        gd.panel(eve.Surface(eve.SWAPCHAIN_0, eve.RGB8, 1920, 1200))
        gd.finish()

    app(gd)
    gd.finish()
