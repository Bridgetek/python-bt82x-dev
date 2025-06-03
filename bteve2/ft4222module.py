import time
import struct
import sys
import argparse

from ft4222 import ft4222, SysClock
from ft4222.SPI import Cpha, Cpol
from ft4222.SPIMaster import Mode, Clock, SlaveSelect
from ft4222.GPIO import Port, Dir

import bteve2 as eve

class connector():
    FREQUENCY = 72_000_000      # system clock frequency, in Hz
    multi_mode = False

    def __init__(self):
        print("Initialise FT4222 interface")

        # Configure the first interface (IF/1) of the FTDI device as a SPI master
        try:
            # open 'device' with default description 'FT4222 A'
            self.devA = ft4222.openByDescription('FT4222 A')
            # and the second 'device' on the same chip
            self.devB = ft4222.openByDescription('FT4222 B')
        except: 
            raise Exception("Sorry, no FTDI FT4222H device for SPI master")

        # init spi master at a 20MHz SPI clock (80MHz / 4)
        self.devA.spiMaster_Init(Mode.SINGLE, Clock.DIV_4, Cpol.IDLE_LOW, Cpha.CLK_LEADING, SlaveSelect.SS0)
        self.devA.setClock(SysClock.CLK_80)   # system clock = 80Mhz

        # also use gpio
        self.devB.gpio_Init(gpio0 = Dir.OUTPUT)

    def setup_flash(self):
        pass

    def sleepclocks(self, n):
        time.sleep(n / 72e6)

    def addr(self, a):
        return struct.pack(">I", a)

    def rd32(self, a):
        return struct.unpack("I", self.rd(a, 4))[0]
        
    def rd(self, a, nn):
        assert (a & 3) == 0
        assert (nn & 3) == 0
        
        self.devA.spiMaster_EndTransaction()

        if nn == 0:
            return b""
        a1 = a + nn
        r = b''
        while a != a1:
            # Timeout for a read is 7uS for BT82x.
            # At a 20MHz SPI bus the timout is approximately 140 clock cycles.
            # On FT4222H the spiMaster_EndTransaction will take 11uS.
            # This is T0 (12.5nS for 80MHz clock) * 880 clocks from Datasheet.
            # Read a maximum of 8 bytes before the "0x01" that signifies data ready.
            n = min(a1 - a, 8 + nn)
            if self.multi_mode:
                bb = self.devA.spiMaster_MultiReadWrite(b'', self.addr(a), 8 + n)
                if 1 in bb:
                    # Got READY byte in response
                    i = bb.index(1)
                    if i >= 8: print(f"Oh dear {i}")
                    response = bb[i + 1:i + 1 + n]
                else:
                    # There is no recovery here.
                    print("recover")
                    response = b''
            else:
                self.devA.spiMaster_SingleWrite(self.addr(a), False)
                def recv(n):
                    return self.devA.spiMaster_SingleRead(n, False)
                bb = recv(8 + n)
                if 1 in bb:
                    # Got READY byte in response
                    i = bb.index(1)
                    response = bb[i + 1:i + 1 + n]
                else:
                    # Recovery: Poll for READY byte
                    while recv(1) == b'\x00':
                        pass
                    response = b''
            # Handle case of full response not received
            if len(response) < n:
                #print("Padd")
                response += recv(n - len(response))
            self.devA.spiMaster_EndTransaction()
            a += n
            r += response
        return r

    def wr32(self, a, v):
        self.wr(a, struct.pack("I", v))

    def wr(self, a, s, inc=True):
        _ = inc
        assert (a & 3) == 0
        t = len(s)
        assert (t & 3) == 0
        while t:
            n = min(0xf000, t)
            if self.multi_mode:
                self.devA.spiMaster_MultiReadWrite(b'', self.addr(a | (1 << 31)) + s[:n], 0)
            else:
                self.devA.spiMaster_SingleWrite(self.addr(a | (1 << 31)), False)
                if t > 0:
                    self.devA.spiMaster_SingleWrite(s[:n], True)
                else:
                    self.devA.spiMaster_EndTransaction()
            a += n
            t -= n
            s = s[n:]

    def cs(self, v):
        if v:
            # No action. CS automatically actioned.
            pass
        else:
            # End of transaction. Send cumulated buffer contents.
            self.devA.spiMaster_EndTransaction()

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
            # CLEAR BootCfgEn
            exchange(bytes([0xFF, 0xE9, 0xC0, 0x00, 0x00]), True)
            # Perform a reset pulse
            exchange(bytes([0xFF, 0xE7, 0x00, 0x00, 0x00]), True)
            # Set ACTIVE
            exchange(bytes([0x00, 0x00, 0x00, 0x00, 0x00]), True)
            time.sleep(.2)

            self.devA.spiMaster_SingleWrite(self.addr(0), False)
            def recv(n):
                return self.devA.spiMaster_SingleRead(n, True)
            bb = recv(128)
            t0 = time.monotonic_ns()
            
            fault = False
            if 1 in bb:
                # Wait for the REG_ID register to be set to 0x7c to
                while self.rd32(eve.EVE2.REG_ID) != 0x7c:
                    pass
                while not fault and self.rd32(eve.EVE2.REG_BOOT_STATUS) != 0x522e2e2e:
                    fault = 1e-9 * (time.monotonic_ns() - t0) > 0.1
                if fault:
                    print(f"[Timeout waiting for REG_BOOT_STATUS, stuck at {self.rd32(eve.EVE2.BOOT_STATUS):08x}, retrying...]")
                    continue
                actual = self.rd32(eve.EVE2.REG_FREQUENCY)
                if actual != self.FREQUENCY:
                    print(f"[Requested {self.FREQUENCY/1e6} MHz, but actual is {actual/1e6} MHz after reset, retrying...]")
                    continue
                break

            print(f"[Boot fail after reset, retrying...]")

        # Disable QSPI burst mode
        #self.wr32(self.EVE2.REG_SYS_CFG, 1 << 10)

        parser = argparse.ArgumentParser(description="ft4222 module")
        parser.add_argument("--mode", help="spi mode", default="0")     # 0: single, 1: dual, 2: quad
        (args, rem) = parser.parse_known_args(sys.argv[1:])
        # Extract --mode and keep the rest in sys.argv
        sys.argv = [sys.argv[0]] + rem

        if args.mode:
            spi_mode = int(args.mode, 0)
            # Enable Dual/Quad SPI
            if spi_mode in [1,2]:
                cfg = self.rd32(eve.EVE2.REG_SYS_CFG) & ~(0x3 << 8)
                # Turn SPI_WIDTH to DUAL/QUAD
                cfg = cfg | (spi_mode << 8)
                self.wr32(eve.EVE2.REG_SYS_CFG, cfg)
                # Instruct ft4222 library to switch to Dual/Quad SPI
                self.devA.spiMaster_SetLines(Mode.DUAL if spi_mode == 1 else Mode.QUAD)
                # change to multi mode
                self.multi_mode = True
