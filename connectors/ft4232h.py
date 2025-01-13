import time
import struct
import argparse

# Use the PyFtdi library to interface with an FT4232H device. See
# https://eblot.github.io/pyftdi/ for more information.
# "pip install pyftdi" to add the module to python.
from pyftdi.spi import SpiController, SpiIOError
from pyftdi.ftdi import Ftdi

# IMPORTANT - WINDOWS
# For use on Windows the libusb-win32 driver MUST be installed in place of
# the FTDI driver. To do this, the easiest way is to use Zadig. See the
# webpage and instructions at https://zadig.akeo.ie or
# https://eblot.github.io/pyftdi/installation.html#windows

# For use with the UMFTPD2A board (based on the FT4232H) see the schematics
# in https://brtchip.com/wp-content/uploads/sites/3/2022/07/DS_UMFTPD2A.pdf
# for the SPI connection details on UMFTPD2A board using the CN2 connector.

import bteve2 as eve

FREQUENCY = 72_000_000      # system clock frequency, in Hz

class EVE2(eve.EVE2):
    def __init__(self):
        spi = SpiController()

        # Configure the first interface (IF/1) of the FTDI device as a SPI master
        try:
            spi.configure('ftdi://ftdi:4232h/1')
            print("Using Interface 1 on FT4232H")
        except: 
            # Configure the second interface (IF/2) of the FTDI device as a SPI master
            try:
                spi.configure('ftdi://ftdi:4232h/2')
                print("Using Interface 2 on FT4232H")
            except: 
                raise Exception("Sorry, no FTDI FT4232H device for SPI master")
        # Note MPSSE is required and there are 2 MPSSE channels on FT4232H.

        # Get a port to a SPI slave w/ /CS on A*BUS3 and SPI mode 0 @ 12MHz
        self.slave = spi.get_port(cs=0, freq = 15E6, mode=0)
        self.gpio = spi.get_gpio()
        self.gpio.set_direction(0x80, 0x80)
        spi.ftdi.set_latency_timer(1)
        self.boot()

    def setup_flash(self):
        pass

    def sleepclocks(self, n):
        time.sleep(n / 72e6)

    def addr(self, a):
        return struct.pack(">I", a)

    def rd(self, a, nn):
        assert (a & 3) == 0
        assert (nn & 3) == 0
        if nn == 0:
            return b""
        a1 = a + nn
        r = b''
        while a != a1:
            n = min(a1 - a, 32)
            self.slave.write(self.addr(a), start = True, stop = False)
            def recv(n):
                return self.slave.read(n, start = False, stop = False)
            bb = recv(32 + n)
            if 1 in bb:             # Got READY byte in response
                i = bb.index(1)
                response = bb[i + 1:i + 1 + n]
            else:
                                    # Poll for READY byte
                while recv(1) == b'\x00':
                    pass
                response = b''
                                    # Handle case of full response not received
            if len(response) < n:
                response += recv(n - len(response))
            self.slave.write(b'', start = False, stop = True)
            a += n
            r += response
        return r

    def wr(self, a, s):
        assert (a & 3) == 0
        t = len(s)
        assert (t & 3) == 0

        while t:
            n = min(0xf000, t)
            self.slave.write(self.addr(a | (1 << 31)) + s[:n])
            a += n
            t -= n
            s = s[n:]

    def cs(self, v):
        if v:
            self.slave.force_select(0)
        else:
            self.slave.force_select(1)

    def reset(self):
        while 1:
            # self.gpio.write(0x00)
            # time.sleep(.1)
            self.gpio.write(0x80)
            # time.sleep(.1)

            exchange = self.slave.exchange
            # Set System PLL NS = 15 for 576MHz
            exchange(bytes([0xFF, 0xE4, 0x0F, 0x00, 0x00]))
            # Set System clock divider to 0x17 for 72MHz
            exchange(bytes([0xFF, 0xE6, 0x17, 0x00, 0x00]))
            # Set bypass BOOT_BYPASS_OTP, DDRTYPT_BYPASS_OTP and set BootCfgEn
            exchange(bytes([0xFF, 0xE9, 0xe1, 0x00, 0x00]))
            # Set DDR Type - 1333, DDR3L, 4096
            exchange(bytes([0xFF, 0xEB, 0x08, 0x00, 0x00]))
            # Set DDR, JT and AUD in Boot Control
            exchange(bytes([0xFF, 0xE8, 0xF0, 0x00, 0x00]))
            # Clear BootCfgEn
            exchange(bytes([0xFF, 0xE9, 0xC0, 0x00, 0x00]))
            # Perform a reset pulse
            exchange(bytes([0xFF, 0xE7, 0x00, 0x00, 0x00]))  
            time.sleep(.1)

            self.slave.write(self.addr(0), start = True, stop = False)
            def recv(n):
                return self.slave.read(n, start = False, stop = True)
            bb = recv(128)
            t0 = time.monotonic_ns()
            fault = False
            if 1 in bb:
                # Wait for the REG_ID register to be set to 0x7c to
                while self.rd32(eve.REG_ID) != 0x7c:
                    pass
                while not fault and self.rd32(eve.BOOT_STATUS) != 0x522e2e2e:
                    fault = 1e-9 * (time.monotonic_ns() - t0) > 0.1
                if fault:
                    print(f"[Timeout waiting for BOOT_STATUS, stuck at {self.rd32(eve.BOOT_STATUS):08x}, retrying...]")
                    continue
                actual = self.rd32(eve.REG_FREQUENCY)
                if actual != FREQUENCY:
                    print(f"[Requested {FREQUENCY/1e6} MHz, but actual is {actual/1e6} MHz after reset, retrying...]")
                    continue
                return

            print(f"[Boot fail after reset, retrying...]")
