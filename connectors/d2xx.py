import sys
import ctypes
import struct
import time

import bteve2 as eve

FREQUENCY = 36_000_000      # system clock frequency, in Hz

def check(f):
    if f != 0:
        names = [
            "FT_OK",
            "FT_INVALID_HANDLE",
            "FT_DEVICE_NOT_FOUND",
            "FT_DEVICE_NOT_OPENED",
            "FT_IO_ERROR",
            "FT_INSUFFICIENT_RESOURCES",
            "FT_INVALID_PARAMETER",
            "FT_INVALID_BAUD_RATE",
            "FT_DEVICE_NOT_OPENED_FOR_ERASE",
            "FT_DEVICE_NOT_OPENED_FOR_WRITE",
            "FT_FAILED_TO_WRITE_DEVICE",
            "FT_EEPROM_READ_FAILED",
            "FT_EEPROM_WRITE_FAILED",
            "FT_EEPROM_ERASE_FAILED",
            "FT_EEPROM_NOT_PRESENT",
            "FT_EEPROM_NOT_PROGRAMMED",
            "FT_INVALID_ARGS",
            "FT_NOT_SUPPORTED",
            "FT_OTHER_ERROR"]
        raise IOError("Error in MPSSE function (status %d: %s)" % (f, names[f]))

def bseq(*a):
    return bytes(a)

class EVE2(eve.EVE2):
    def __init__(self):
        if sys.platform.startswith('linux'):
            self.d2xx = ctypes.cdll.LoadLibrary("/usr/local/lib/libftd2xx.so")
        elif sys.platform.startswith('darwin'):
            self.d2xx = ctypes.cdll.LoadLibrary("libftd2xx.1.1.0.dylib")
        else:
            self.d2xx = ctypes.windll.LoadLibrary("ftd2xx")

        print('D2XX loaded:')
        library_version = ctypes.c_uint32()
        self.d2xx.FT_GetLibraryVersion(ctypes.byref(library_version))
        print('     FT_GetLibraryVersion: %06x' % library_version.value)

        dwNumDevs = ctypes.c_uint32()
        self.d2xx.FT_CreateDeviceInfoList(ctypes.byref(dwNumDevs))
        print('dwNumDevs', dwNumDevs.value)

        SerialNumber = ctypes.create_string_buffer(256)
        Description = ctypes.create_string_buffer(256)
        dwFlags = ctypes.c_uint32()
        dwType = ctypes.c_uint32()
        dwID = ctypes.c_uint32()
        dwLocId = ctypes.c_uint32()
        ftHandle = ctypes.c_void_p()

        devices = []
        for i in range(dwNumDevs.value):
            self.d2xx.FT_GetDeviceInfoDetail(i,
                                             ctypes.byref(dwFlags),
                                             ctypes.byref(dwType),
                                             ctypes.byref(dwID),
                                             ctypes.byref(dwLocId),
                                             SerialNumber,
                                             Description,
                                             ctypes.byref(ftHandle))
            # print(i, dwFlags, dwType, dwID, dwLocId, repr(SerialNumber.value), Description.value)
            if Description.value == b"VA800A-SPI":
                devices.append((SerialNumber.value, i))
            if Description.value == b"UMFTPD2A A":
                devices.append((SerialNumber.value, i))
        devices = sorted(devices)
        select = 0
        if len(devices) > 0:
            print("Found", len(devices), "VA800A-SPI devices:")
            for i,(s,d) in enumerate(devices):
                ispicked = ["", "[SELECTED]"][i == select]
                print("    ", i, s, ispicked)
        (_, devnum) = devices[select]

        self.ftHandle = ctypes.c_void_p()
        check(self.d2xx.FT_Open(devnum, ctypes.byref(self.ftHandle)))

        # Procedure from p.12 of
        #   http://www.ftdichip.com/Support/Documents/AppNotes/AN_135_MPSSE_Basics.pdf

        check(self.d2xx.FT_ResetDevice(self.ftHandle))                          # 1
        check(self.d2xx.FT_SetUSBParameters(self.ftHandle, 16384, 16384))       # 2
        check(self.d2xx.FT_SetChars(self.ftHandle, False, 0, False, 0))         # 3
        check(self.d2xx.FT_SetTimeouts(self.ftHandle, 0, 5000))                 # 4
        # check(self.d2xx.FT_SetLatencyTimer(self.ftHandle, 1))                   # 5
        # check(self.d2xx.FT_SetFlowControl(self.ftHandle, 0, 0, 0))              # 6
        check(self.d2xx.FT_SetBitMode(self.ftHandle, 0, 0))                     # 7
        check(self.d2xx.FT_SetBitMode(self.ftHandle, 0, 2))                     # 8

        time.sleep(0.050)   # wait for USB stuff ?!?

        self.s = ctypes.create_string_buffer(65536)

        # OK, now device is in MPSSE mode, so can 
        # use AN_108 system

        self.silent(bseq(0x84))                      # Loopback enable
        self.raw_write(bseq(0xab))                       # Send bogus command 0xab

        while self.npending() < 2:
            pass
        rd = self.raw_read(self.npending())
        if rd != [b'\xfa', b'\xab']:
            print("Error in synchronizing the MPSSE:")
            print(rd)
            assert 0

        self.silent(bseq(0x85))                     # Disable internal loop-back
        self.silent(bseq(0x8a))                     # Disable divide by 5
        self.silent(bseq(0x97))                     # Turn off adaptive clocking
        self.silent(bseq(0x8d))                     # Turn off three-phase clocking

        if 0:
            # 6 MHz
            self.silent(bseq(0x86, 0x04, 0x00))
        else:
            # 15 MHz
            self.silent(bseq(0x86, 0x01, 0x00))

        self.assert_reset(1)

        self.boot()

    def npending(self):
        dwNumBytesToRead = ctypes.c_uint()
        check(self.d2xx.FT_GetQueueStatus(self.ftHandle, ctypes.byref(dwNumBytesToRead)))
        return dwNumBytesToRead.value
    def raw_read(self, n):
        dwNumBytesRead = ctypes.c_uint()
        check(self.d2xx.FT_Read(self.ftHandle, self.s, n, ctypes.byref(dwNumBytesRead)))
        assert n == dwNumBytesRead.value
        return list(self.s)[:n]
    def raw_write(self, s):
        assert type(s) == bytes
        if s:
            dwNumBytesSent = ctypes.c_uint()
            check(self.d2xx.FT_Write(self.ftHandle, s, len(s), ctypes.byref(dwNumBytesSent)))
            # print('raw_write:', dwNumBytesSent, "\n" + hexdump(s))
    def silent(self, s): # send a silent command - one that expects no response
        self.raw_write(s)
        if self.npending() != 0:
            def hd(s):
                return "[" + ",".join(["%02x" % ord(c) for c in s]) + "]"
            print("Error after %s - MPSSE receive buffer should be empty, but contains %s" % (hd(s), hd(self.raw_read(self.npending()))))

    def csel(self):
        return (bseq(0x80, 0x80, 0x9b))

    def cunsel(self):
        return (bseq(0x80, 0x88, 0x9b))

    # From MPSSE SPI module:
    #   http://www.ftdichip.com/Support/Documents/DataSheets/Modules/DS_VA800A-SPI_MPSSE_Module.pdf
    # reset signal (PDN#) is ADBUS7. On MPSSE cable:
    #   http://www.ftdichip.com/Support/Documents/DataSheets/Cables/DS_C232HM_MPSSE_CABLE.PDF
    # this is the BLUE wire

    def assert_reset(self, sense):
        if sense:
            self.silent(bseq(0x80, 0x08, 0x9b))
        else:
            self.silent(bseq(0x80, 0x88, 0x9b))

    def scu(self, b0, b1 = 0, b2 = 0):
        msg = struct.pack("<BH", 0x11, 2) + bytes([b0, b1, b2])
        self.raw_write(self.csel() + msg + self.cunsel()) # SCU wake
        time.sleep(.001)

    def addr(self, a):
        return struct.pack(">I", a)

    def reset(self):
        while True:
            self.assert_reset(1)
            time.sleep(0.001)
            self.assert_reset(0)

            def exchange(bb):
                msg = struct.pack("<BH", 0x11, len(bb) - 1) + bb
                self.raw_write(self.csel() + msg + self.cunsel()) # SCU wake
                
            # Set System PLL NS = 15 for 72MHz
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

            msg = (struct.pack("<BH", 0x11, 3) + self.addr(0))
            self.raw_write(self.csel() + msg)
            n = 128
            #self.raw_write(struct.pack("<BH", 0x20, n - 1))
            while self.npending() < n:
                pass
            r = b''.join(self.raw_read(n))
            print(r)
            self.raw_write(self.cunsel())
            if 1 in r:
                while self.rd32(eve.REG_ID) != 0x7c:
                    pass
                print(f"Boot status: 0x{self.rd32(eve.BOOT_STATUS):x}")
                if self.rd32(eve.BOOT_STATUS) == 0x522e2e2e:
                    break
            print("[Boot fail after reset, retrying...]")

    def rd(self, a, nn):
        if nn == 0:
            return b""
        if a & 3:
            e = a & 3
            return self.rdstr(a - e, nn + e)[e:]
        if nn & 3:
            return self.rdstr(a, (nn + 3) & ~3)[:nn]
        a1 = a + nn
        r = b''
        while a != a1:
            n = min(a1 - a, 32)
            # print("reading %x %d" %(a, n))
            msg = (struct.pack("<BH", 0x11, 3) + self.addr(a))
            self.raw_write(self.csel() + msg)
            def recv(n):
               self.raw_write(struct.pack("<BH", 0x20, n - 1))
               while self.npending() < n:
                   pass
               r = b''.join(self.raw_read(n))
               # print('recv (%d)\n%s' % (n, hexdump(r)))
               return r
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
            self.raw_write(self.cunsel())
            a += n
            r += response
        return r

    def wr(self, a, s):
        assert (a & 3) == 0
        assert (len(s) & 3) == 0

        t = len(s)
        ww = []
        while t:
            n = min(64000, t)
            msg = struct.pack("<BH", 0x11, 4 + n - 1) + self.addr((2**31) | a) + s[:n]
            ww.append(self.csel() + msg + self.cunsel())
            a += n
            t -= n
            s = s[n:]
        self.raw_write(b''.join(ww))
