import time
import struct
import argparse

import ft4222
from ft4222.SPI import Cpha, Cpol
from ft4222.SPIMaster import Mode, Clock, SlaveSelect
from ft4222.GPIO import Port, Dir

import bteve2 as eve

FREQUENCY = 72_000_000      # system clock frequency, in Hz

class EVE2(eve.EVE2):
    def __init__(self):

        # Configure the first interface (IF/1) of the FTDI device as a SPI master
        try:
            # open 'device' with default description 'FT4222 A'
            self.devA = ft4222.openByDescription('FT4222 A')
            # and the second 'device' on the same chip
            self.devB = ft4222.openByDescription('FT4222 B')
        except: 
            raise Exception("Sorry, no FTDI FT4222H device for SPI master")

        # init spi master
        self.devA.spiMaster_Init(Mode.SINGLE, Clock.DIV_8, Cpol.IDLE_LOW, Cpha.CLK_LEADING, SlaveSelect.SS0)
        # also use gpio
        self.devB.gpio_Init(gpio0 = Dir.OUTPUT)
        self.boot()

    transmit_buffer = bytearray()

    def setup_flash(self):
        pass

    def sleepclocks(self, n):
        time.sleep(n / 72e6)

    def transmit(self, end=True):
        towrite = len(self.transmit_buffer)
        if (towrite > 0):
            #print(f"transmit {towrite} {end}: ", end="")
            #for ch in self.transmit_buffer:
            #    print(f"{ch:02x} ", end="")
            #print()
            self.devA.spiMaster_SingleWrite(self.transmit_buffer, end)
        else:
            if (end):
                self.devA.spiMaster_EndTransaction()
        self.transmit_buffer = bytearray()
        return towrite

    def append(self, data, end=False):
        self.transmit_buffer.extend(data)
        towrite = len(self.transmit_buffer)
        return towrite

    def addr(self, a):
        return struct.pack(">I", a)

    def rd(self, a, nn):
        assert (a & 3) == 0
        assert (nn & 3) == 0
        
        self.transmit(False)

        if nn == 0:
            return b""
        a1 = a + nn
        r = b''
        while a != a1:
            n = min(a1 - a, 32)
            self.devA.spiMaster_SingleWrite(self.addr(a), False)
            def recv(n):
                return self.devA.spiMaster_SingleRead(n, False)
            bb = recv(32 + n)
            if 1 in bb:             
                # Got READY byte in response
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
            self.devA.spiMaster_EndTransaction()
            a += n
            r += response
        return r

    def wr(self, a, s):
        assert (a & 3) == 0
        t = len(s)
        assert (t & 3) == 0
        self.append(self.addr(a | (1 << 31)))
        self.append(s)

    def cs(self, v):
        if v:
            # No action. CS automatically actioned.
            pass
        else:
            # End of transaction. Send cumulated buffer contents.
            self.transmit(True)

    def reset(self):
        self.devB.gpio_Write(Port.P0, 0)
        time.sleep(.1)
        self.devB.gpio_Write(Port.P0, 1)
        time.sleep(.1)

        while 1:
            exchange = self.devA.spiMaster_SingleWrite
            # Set System PLL NS = 15 for 576MHz
            exchange(bytes([0xFF, 0xE4, 0x0F, 0x00, 0x00]), True)
            # Set System clock divider to 0x17 for 72MHz
            exchange(bytes([0xFF, 0xE6, 0x17, 0x00, 0x00]), True)
            # Set bypass BOOT_BYPASS_OTP, DDRTYPT_BYPASS_OTP and set BootCfgEn
            exchange(bytes([0xFF, 0xE9, 0xe1, 0x00, 0x00]), True)
            # Set DDR Type - 1333, DDR3L, 4096
            exchange(bytes([0xFF, 0xEB, 0x08, 0x00, 0x00]), True)
            # Set DDR, JT and AUD in Boot Control
            exchange(bytes([0xFF, 0xE8, 0xF0, 0x00, 0x00]), True)
            # Clear BootCfgEn
            exchange(bytes([0xFF, 0xE9, 0xC0, 0x00, 0x00]), True)
            # Perform a reset pulse
            exchange(bytes([0xFF, 0xE7, 0x00, 0x00, 0x00]), True)
            time.sleep(.2)

            self.devA.spiMaster_SingleWrite(self.addr(0), False)
            def recv(n):
                return self.devA.spiMaster_SingleRead(n, True)
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
