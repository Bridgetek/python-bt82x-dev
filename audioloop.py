# Typical command line:
# python audioloop.py --connector ft4222module
import sys

import sys
import time

# This module provides the connector (eve) to the EVE hardware.
import apprunner

# Load the extension code from the "common" directory.
sys.path.append('common')
import extplotmem 

def pad4(s):
    while len(s) % 4:
        s += b'\x00'
    return s

def audioloop(eve):

    print("Patch: ", extplotmem.loadpatch(eve))

    # Calibrate screen if necessary. 
    # Don't do this for now.
    #eve.calibrate()
    
    TRACE_COUNT = 4
    TRACE_POINTS = 512
    
    trace_data = []
    trace_addr = []
    trace_offset = []
    trace_active = []
    trace_cell = 0

    with open("assets/sample_1.pcm", mode='rb') as file:
        trace_data.append(file.read())
    with open("assets/sample_2.pcm", mode='rb') as file:
        trace_data.append(file.read())
    with open("assets/sample_1.pcm", mode='rb') as file:
        trace_data.append(file.read())
    with open("assets/sample_2.pcm", mode='rb') as file:
        trace_data.append(file.read())

    eve.LIB_BEGINCOPROLIST()
    eve.CMD_DLSTART()
    eve.CMD_MEMORYINIT(0x1000, 512 * 1024)
    eve.LIB_ENDCOPROLIST()
    eve.LIB_AWAITCOPROEMPTY()

    eve.LIB_BEGINCOPROLIST()
    eve.CMD_DLSTART()
    for i in range(TRACE_COUNT):
        # Allocate a bitmap for each trace that is 4 times the size of the input data
        # Two cells are needed to make a subtractive overlay of one image
        # Two images are needed to prevent overwriting the image currently rendered
        trace_addr.append(eve.LIB_MEMORYBITMAP(eve.FORMAT_BARGRAPH, TRACE_POINTS, 2))
        print(f"Graph {i} bitmap address 0x{trace_addr[i]:x}");
        # Random-ish starting point in sample
        trace_offset.append(trace_addr[i] % len(trace_data[i]))
        trace_active.append(1)
    eve.LIB_ENDCOPROLIST()
    eve.LIB_AWAITCOPROEMPTY()

    t0 = time.monotonic()
    tmask = 0
    tsample = 100
    tcount = 0
    tactive = 0xfffffffff

    fps = 0
    tplotstream = 0
    tcoprocend = 0

    while (1):
        # Alternate between bitmap cells for bitmap to prevent ripping
        trace_cell = 1 if trace_cell == 0 else 0

        eve.LIB_BEGINCOPROLIST()
        eve.CMD_DLSTART()
        eve.CLEAR_COLOR_RGB(30, 30, 90)
        eve.CLEAR(1,1,1)

        # Obviously need to have 2 bitmap buffers to prevent flickering
        for i in range(TRACE_COUNT):
            tstart = time.monotonic()
            # Target an alternating cell
            eve.CMD_PLOTBITMAP(trace_addr[i] + (trace_cell * TRACE_POINTS), TRACE_POINTS, 0, i)
            tracepoint = trace_offset[i]
            remainder = min(TRACE_POINTS, len(trace_data[i]) - tracepoint);
            tracebuf = trace_data[i][tracepoint:tracepoint + remainder]
            if (remainder != TRACE_POINTS):
                tracebuf += trace_data[i][0:TRACE_POINTS - remainder]
            eve.LIB_WRITEDATATORAMG(tracebuf)
            tend = time.monotonic()
            tplotstream += tend - tstart

        eve.VERTEX_FORMAT(0)
        
        # Draw "audio" waveform graph
        width = 1024
        height = 200
        scalex = int(width * 0x10000 / TRACE_POINTS)
        scaley = int(((height / 2) * 0x10000) / 256)

        eve.BEGIN(eve.BEGIN_BITMAPS)
        eve.SAVE_CONTEXT()
        for i in range(TRACE_COUNT):
            tracey = ((i * height * 3) // 2)
            if (trace_active[i]):
                eve.COLOR_RGB(0, 255, 0)
            else:
                eve.COLOR_RGB(255, 0, 0)

            # Scale bitmap to fit where it needs to be
            eve.BITMAP_HANDLE(i)
            # Top half
            eve.BITMAP_SIZE_H(width >> 9, height >> 9)
            eve.BITMAP_SIZE(eve.FILTER_NEAREST, eve.WRAP_BORDER, eve.WRAP_BORDER, width, height)
            eve.CMD_LOADIDENTITY()
            eve.CMD_SCALE(scalex, scaley)
            eve.CMD_SETMATRIX()
            eve.VERTEX2F(0, tracey)
            # Bottom half
            eve.CMD_LOADIDENTITY()
            eve.CMD_TRANSLATE(0, int((height / 2) * 0x10000))
            eve.CMD_SCALE(scalex, -scaley)
            eve.CMD_SETMATRIX()
            eve.VERTEX2F(0, tracey + (height // 2))
        eve.RESTORE_CONTEXT()

        eve.COLOR_RGB(255, 255, 255)
        eve.BEGIN(eve.BEGIN_LINES)
        tracey = ((TRACE_COUNT * height * 3) // 2) + height
        eve.VERTEX2F(100, 0)
        eve.VERTEX2F(100, tracey)
        eve.END()

        if (fps):
            eve.CMD_TEXT(eve.EVE_DISP_WIDTH, 0, 34, eve.OPT_RIGHTX | eve.OPT_FORMAT, "FPS: %d", fps)

        eve.DISPLAY()
        tstart = time.monotonic()
        eve.CMD_SWAP()
        eve.LIB_AWAITCOPROEMPTY()
        tend = time.monotonic()
        tcoprocend += tend - tstart

        for i in range(TRACE_COUNT):
            if (trace_active[i]):
                trace_offset[i] = trace_offset[i] + 8
                if trace_offset[i] > len(trace_data[i]):
                    trace_offset[i] -= len(trace_data[i])

        tcount += 1
        if tcount >= tsample:
            tcount = 0
            tmask += 1
            tactive ^= tmask
            for i in range(TRACE_COUNT):
                trace_active[i] = (tmask >> i) & 1
            t1 = time.monotonic()
            took = t1 - t0
            #print(f"{tsample} frames took {took:.3f} s. {tsample / took:.2f} fps")
            fps = int(tsample / took)
            t0 = t1
            #print(f"tplotstream {tplotstream:.3f} s. {tplotstream / tsample / TRACE_COUNT:.8f} s")
            #print(f"tcoprocend {tcoprocend:.3f} s. {tcoprocend / tsample / TRACE_COUNT:.8f} s")
            tplotstream = 0
            tcoprocend = 0

apprunner.run(audioloop)
