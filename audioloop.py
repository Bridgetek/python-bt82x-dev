# Typical command line:
# python audioloop.py --connector ft4222module
import sys
import time

# This module provides the connector (eve) to the EVE hardware.
import apprunner

# Load the extension code from the "common" directory.
sys.path.append('common')
import extplotmemsevenseg

def pad4(s):
    while len(s) % 4:
        s += b'\x00'
    return s

def audioloop(eve):

    print("Patch: ", extplotmemsevenseg.loadpatch(eve))

    # Calibrate screen if necessary. 
    # Don't do this for now.
    #eve.LIB_CALIBRATE()
    
    TRACE_COUNT = 4
    TRACE_POINTS = 400
    
    trace_data = []
    trace_addr = []
    trace_offset = []
    trace_active = []
    trace_counter = []
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
        trace_offset.append(0)
        trace_active.append(1)
        trace_counter.append(i * 10)
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

    sampleh = 300
    samplew = 300

    tracew = 400
    traceh = 200
    traceoff = 100
    pedalrad = 150
    pedalspace = 20
    border = 5

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
            tracepoint = trace_offset[i] - traceoff
            if tracepoint < 0: tracepoint = 0
            remainder = min(TRACE_POINTS, len(trace_data[i]) - tracepoint);
            tracebuf = trace_data[i][tracepoint:tracepoint + remainder]
            if (remainder != TRACE_POINTS):
                tracebuf += trace_data[i][0:TRACE_POINTS - remainder]
            eve.LIB_WRITEDATATORAMG(tracebuf)
            tend = time.monotonic()
            tplotstream += tend - tstart

        # Pixel resolution
        eve.VERTEX_FORMAT(0)
        
        # Draw "audio" waveform graph
        tracey = eve.EVE_DISP_HEIGHT - (pedalrad * 2) - (pedalspace * 2) - traceh

        # Draw "sample" box
        sampley = tracey - sampleh - (2 * border)

        # Draw "label" box
        labely = sampley - 60
        labelfont = 31

        scalex = int(tracew * 0x10000 / TRACE_POINTS)
        scaley = int(((traceh / 2) * 0x10000) / 256)

        for i in range(TRACE_COUNT):
            # Centre of the trace area
            tracecx = ((eve.EVE_DISP_WIDTH // TRACE_COUNT) * i) + ((eve.EVE_DISP_WIDTH // TRACE_COUNT) // 2)
            
            # Left of the trace
            tracex = tracecx - (tracew // 2)

            # Left of the sample ares
            samplex = tracecx - (samplew // 2)

            if (trace_active[i]):
                trcolour = (0, 255, 0)
            else:
                trcolour = (255, 100, 0)

            tracebmpx = tracex
            tracebmpw = tracew
            if trace_offset[i] < traceoff:
                tracebmpx += (traceoff - trace_offset[i])
                tracebmpw = tracew + trace_offset[i] - traceoff
            if trace_offset[i] + tracebmpw >= len(trace_data[i]):
                tracebmpw = len(trace_data[i]) - trace_offset[i]

            # Cut-outs for displays
            eve.BEGIN(eve.BEGIN_RECTS)
            # Border for trace graphs
            eve.COLOR_RGB(trcolour[0], trcolour[1], trcolour[2])
            eve.VERTEX2F(tracex - border, tracey - border)
            eve.VERTEX2F(tracex + tracew + border, tracey + traceh + border)
            # Inside for trace graphs
            eve.COLOR_RGB(0, 0, 0)
            eve.VERTEX2F(tracex, tracey)
            eve.VERTEX2F(tracex + tracew, tracey + traceh)
            # Inside for sample number
            eve.COLOR_RGB(0, 0, 0)
            eve.VERTEX2F(samplex, sampley)
            eve.VERTEX2F(samplex + samplew, sampley + ((2 * samplew) // 3) + (10 * border))
            eve.END()

            # Trace graph
            eve.SAVE_CONTEXT()
            eve.BEGIN(eve.BEGIN_BITMAPS)
            eve.COLOR_RGB(trcolour[0], trcolour[1], trcolour[2])
            # Scale bitmap to fit where it needs to be
            eve.BITMAP_HANDLE(i)
            # Top half
            eve.BITMAP_SIZE_H(tracebmpw >> 9, traceh >> 9)
            eve.BITMAP_SIZE(eve.FILTER_NEAREST, eve.WRAP_BORDER, eve.WRAP_BORDER, tracebmpw, traceh)
            # Bottom half
            eve.CMD_LOADIDENTITY()
            eve.CMD_TRANSLATE(0, int((traceh / 2) * 0x10000))
            eve.CMD_SCALE(scalex, -scaley)
            eve.CMD_SETMATRIX()
            eve.VERTEX2F(tracebmpx, tracey + (traceh // 2))
            eve.CMD_LOADIDENTITY()
            eve.CMD_SCALE(scalex, scaley)
            eve.CMD_SETMATRIX()
            eve.VERTEX2F(tracebmpx, tracey)
            eve.END()
            eve.RESTORE_CONTEXT()

            # Sample current point marker
            eve.COLOR_RGB(255, 255, 255)
            eve.BEGIN(eve.BEGIN_LINES)
            eve.LINE_WIDTH(1)
            eve.VERTEX2F(tracex + traceoff, tracey)
            eve.VERTEX2F(tracex + traceoff, tracey + traceh)
            eve.END()

            # Draw pedal
            pedx = tracecx
            pedy = tracey + traceh + pedalrad + pedalspace
            cinner = (pedalrad * 2) - (border * 2)
            couter = pedalrad * 2
            eve.BEGIN(eve.BEGIN_POINTS)
            eve.COLOR_RGB(trcolour[0], trcolour[1], trcolour[2])
            eve.POINT_SIZE(couter)
            eve.VERTEX2F(pedx, pedy)
            eve.POINT_SIZE(cinner)
            eve.COLOR_RGB(0, 0, 0)
            eve.VERTEX2F(pedx, pedy)
            eve.END()

            # Draw ARC for delay start for channel
            #eve.CMD_ARC()

            # Draw pedal glyphs
            eve.COLOR_RGB(255, 255, 255)
            eve.LINE_WIDTH(border)
            if (trace_active[i]):
                eve.BEGIN(eve.BEGIN_LINE_STRIP)
                eve.VERTEX2F(pedx - (pedalrad // 4), pedy - (pedalrad // 4))
                eve.VERTEX2F(pedx - (pedalrad // 4), pedy + (pedalrad // 4))
                eve.VERTEX2F(pedx - (pedalrad // 12), pedy + (pedalrad // 4))
                eve.VERTEX2F(pedx - (pedalrad // 12), pedy - (pedalrad // 4))
                eve.VERTEX2F(pedx - (pedalrad // 4), pedy - (pedalrad // 4))
                eve.END()
                eve.BEGIN(eve.BEGIN_LINE_STRIP)
                eve.VERTEX2F(pedx + (pedalrad // 4), pedy - (pedalrad // 4))
                eve.VERTEX2F(pedx + (pedalrad // 4), pedy + (pedalrad // 4))
                eve.VERTEX2F(pedx + (pedalrad // 12), pedy + (pedalrad // 4))
                eve.VERTEX2F(pedx + (pedalrad // 12), pedy - (pedalrad // 4))
                eve.VERTEX2F(pedx + (pedalrad // 4), pedy - (pedalrad // 4))
                eve.END()
            else:
                eve.BEGIN(eve.BEGIN_LINE_STRIP)
                eve.VERTEX2F(pedx - (pedalrad // 6), pedy - (pedalrad // 4))
                eve.VERTEX2F(pedx - (pedalrad // 6), pedy + (pedalrad // 4))
                eve.VERTEX2F(pedx + (pedalrad // 4), pedy)
                eve.VERTEX2F(pedx - (pedalrad // 6), pedy - (pedalrad // 4))
                eve.END()
            
            eve.CMD_TEXT(tracecx, labely, labelfont, eve.OPT_CENTERX | eve.OPT_FORMAT, "CH: %d", i)
            eve.CMD_FGCOLOR(0xff0000)
            eve.CMD_BGCOLOR(0x440000)
            eve.CMD_SEVENSEG(samplex + (5 * border), sampley + (5 * border), samplew // 3, (trace_counter[i] // 10) % 10)
            eve.CMD_SEVENSEG(samplex + (15 * border) + (samplew // 3), sampley + (5 * border), samplew // 3, trace_counter[i] % 10)
            

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
                if trace_offset[i] + traceoff > len(trace_data[i]):
                    trace_offset[i] = 0
                    trace_active[i] = 0
                    trace_counter[i] = trace_counter[i] + 1

        tcount += 1
        if tcount >= tsample:
            tcount = 0
            tmask += 1
            tactive ^= tmask
            for i in range(TRACE_COUNT):
                trace_active[i] = (tmask >> i) & 1
                if trace_active[i] == 0:
                    trace_offset[i] = 0
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
