# Typical command line:
# python audioloop.py --connector ft4222module
import sys
import time
import math 
import random

# Add the library directories to the module search path.
sys.path.append('../..')
sys.path.append('../../bteve2')

# This module provides the connector to the EVE hardware.
import apprunner
# Import the patch file required by this code.
import patch_audioloop as patch

# Load the extension code from the "snippets" directory.
sys.path.append('../snippets')
import vumeter

def pad4(s):
    while len(s) % 4:
        s += b'\x00'
    return s

def audioloop(eve):

    # Calibrate screen if necessary. 
    # Don't do this for now.
    #eve.LIB_AutoCalibrate()
    
    TRACE_COUNT = 4
    TRACE_POINTS = 400
    
    HANDLE_BG = TRACE_COUNT

    # Array to hold TRACE_COUNT arrays of trace data for each sample loaded
    trace_data = []
    # Address of each of trace TRACE_COUNT data in RAM_G
    trace_addr = []
    # Current position in each sample which is playing
    trace_offset = []
    # Non-zero if a sample is currently playing
    trace_active = []
    # Sample patch number for each sample loaded
    trace_counter = []
    # Select the cell (0 or 1) alternately to prevent us updatating a bitmap that is being rendered
    trace_cell = 0

    try:
        # Load trace data from file to an array
        with open("assets/sample_1.pcm", mode='rb') as file:
            trace_data.append(file.read())
        with open("assets/sample_2.pcm", mode='rb') as file:
            trace_data.append(file.read())
        with open("assets/sample_1.pcm", mode='rb') as file:
            trace_data.append(file.read())
        with open("assets/sample_2.pcm", mode='rb') as file:
            trace_data.append(file.read())
    except:
        raise(f"Error: asset not found.")


    eve.LIB_BeginCoProList()
    eve.CMD_DLSTART()
    eve.CMD_MEMORYINIT(0x1000, 1024 * 1024)
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()

    # Program trace data into RAM_G
    eve.LIB_BeginCoProList()
    eve.CMD_DLSTART()
    for i in range(TRACE_COUNT):
        # Allocate a bitmap for each trace that is 4 times the size of the input data
        # Two cells are needed to make a subtractive overlay of one image
        # Two images are needed to prevent overwriting the image currently rendered
        trace_addr.append(eve.LIB_MemoryBitmap(eve.FORMAT_BARGRAPH, TRACE_POINTS, 2, 0))
        print(f"Graph {i} bitmap address 0x{trace_addr[i]:x}");
        # Random-ish starting point in sample
        trace_offset.append(0)
        trace_active.append(1)
        trace_counter.append(i * 10)
    eve.CMD_SWAP()
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()

    # Pseudo random start trigger for samples
    trigger_mask = 0
    trigger_active = 0xfffffffff

    # Start clock for performance calculations
    t0 = time.monotonic()
    # Count for trigger
    # Also used for average performance figures over
    trigger_offset = 100
    # Current frames in performace averaging period
    trigger_count = 0
    # Computed frames per second
    perf_fps = 0
    # Time taken to stream data to EVE
    tplotstream = 0
    # Time taken for coprocessor to run
    tcoprocend = 0

    # Sample patch number display area
    sampleh = 200
    samplew = 200

    # Audio graph trace size
    tracew = 400
    traceh = 200
    # Offset to cursor in trace position
    traceoff = 100
    # Pedal button radius
    pedalrad = 150
    # Gap around pedal
    pedalspace = 20
    
    # General border size for outlines
    border = 5

    # Draw "audio" waveform graph
    tracey = eve.EVE_DISP_HEIGHT - (pedalrad * 2) - (pedalspace * 2) - traceh

    # Draw "sample" box
    sampley = tracey - sampleh - (2 * border)

    # Draw "label" box
    labely = sampley - 60
    labelfont = 31

    scalex = int(tracew * 0x10000 / TRACE_POINTS)
    scaley = int(((traceh / 2) * 0x10000) / 256)

    # VU level gauge
    # VU display value (averaged and peaked)
    vu_level = 0
    vu_prev = 0
    vu_prev1 = None
    vu_prev2 = None
    # VU meter location
    vux1 = border * 10
    vuy = border * 10
    vuw = 300
    vuh = 200
    vux2 = vux1 + vuw + border

    # Graphic EQ gauge
    geqx = vux1 + 2 * vuw + 10 * border
    geqy = vuy
    geqw = 400
    geqh = vuh
    geqseg = 6

    # Graphics EQ "beat"
    geqbass = 0
    geqmid = 0
    geqtreb = 0
    
    eve.LIB_BeginCoProList()
    eve.CMD_DLSTART()

    while (1):
        vu_sample = 0
        vu_active = 0

        # Alternate between bitmap cells for bitmap to prevent ripping
        trace_cell = 1 if trace_cell == 0 else 0

        eve.LIB_BeginCoProList()
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
            eve.LIB_WriteDataToCMD(tracebuf)
            tend = time.monotonic()
            tplotstream += tend - tstart

        # Pixel resolution
        eve.VERTEX_FORMAT(0)
        
        eve.BEGIN(eve.BEGIN_RECTS)
        # Border for EQ
        eve.COLOR_RGB(0, 0, 0)
        eve.VERTEX2F(geqx - border, geqy - border)
        eve.VERTEX2F(geqx + (geqw * ((geqseg * 2) - 1) / (geqseg * 2)) + border, geqy + geqh + border)
        eve.END()

        eve.SAVE_CONTEXT()
        for i in range(geqseg):
            # draw the rectangular area and mark the pixel with stencil value 1
            eve.COLOR_MASK(0, 0, 0, 1)
            eve.STENCIL_FUNC(eve.TEST_ALWAYS, 1, 255)
            eve.STENCIL_OP(eve.STENCIL_INCR, eve.STENCIL_INCR)
        
            eve.BEGIN(eve.BEGIN_RECTS)
            eve.LINE_WIDTH(1 * 8)
            height = vu_level
            heightbass = ((geqseg - i - 3) * geqbass) / 256 / (geqseg - 3)
            heightmid = 0 #((i == (geqseg // 2)) * geqtreb) / 256 / geqseg
            heighttreb = ((i + 5) * geqtreb) / 256 / (geqseg + 5)
            height = max(heightbass, heightmid, heighttreb)
            eve.VERTEX2F(geqx + (geqw * (i / geqseg)),  geqy + geqh - (geqh * height))
            eve.VERTEX2F(geqx + (geqw * (i / geqseg)) + (geqw / geqseg / 2), geqy + geqh)
            eve.END()
        
        eve.COLOR_MASK(1, 1, 1, 1)
        eve.STENCIL_OP(eve.STENCIL_KEEP, eve.STENCIL_KEEP)
        eve.STENCIL_FUNC(eve.TEST_EQUAL, 1, 255)  #select the pixel with stencil value 1
        eve.CMD_GRADIENT(geqx, geqy, 0xFF0000, geqx, geqy + geqh, 0x00FF00)
        eve.RESTORE_CONTEXT()
        
        # Sample trigger progress bar
        eve.LINE_WIDTH(1 * 8)
        eve.CMD_FGCOLOR(0xff0000)
        eve.CMD_BGCOLOR(0x440000)
        progress = ((trigger_count - trigger_offset) * 256) / trigger_offset
        eve.COLOR_RGB(progress, 256 - progress, 0)
        eve.CMD_PROGRESS(border * 20, sampley - (30 * border), eve.EVE_DISP_WIDTH - (2 * border * 20), 5 * border, 0, trigger_count, trigger_offset)

        for i in range(TRACE_COUNT):
            # Centre of the trace area
            tracecx = ((eve.EVE_DISP_WIDTH // TRACE_COUNT) * i) + ((eve.EVE_DISP_WIDTH // TRACE_COUNT) // 2)
            
            # Left of the trace
            tracex = tracecx - (tracew // 2)

            # Left of the sample ares
            samplex = tracecx - (samplew // 2)

            if (trace_active[i]):
                trcolour = (0, 255, 0)
                vu_sample += trace_data[i][trace_offset[i]]
                vu_active += 1
            else:
                trcolour = (255, 100, 0)

            tracebmpx = tracex
            tracebmpw = tracew
            if trace_offset[i] < traceoff:
                tracebmpx += (traceoff - trace_offset[i])
                tracebmpw = tracew + trace_offset[i] - traceoff
            if trace_offset[i] + tracebmpw >= len(trace_data[i]):
                tracebmpw = len(trace_data[i]) - trace_offset[i]

            # Cut-outs for channels
            eve.BEGIN(eve.BEGIN_RECTS)
            eve.LINE_WIDTH(10 * 8)
            # Border for channel
            eve.COLOR_RGB(128, 128, 128)
            eve.VERTEX2F(tracex - 4 * border, labely - 4 * border)
            eve.VERTEX2F(tracex + tracew + 4 * border, tracey + traceh + 2 * pedalrad + pedalspace + 2 * border)
            # Border for trace graphs
            eve.LINE_WIDTH(2 * 8)
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
            eve.LINE_WIDTH(1 * 8)
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
            eve.POINT_SIZE(couter * 8)
            eve.VERTEX2F(pedx, pedy)
            eve.POINT_SIZE(cinner * 8)
            eve.COLOR_RGB(0, 0, 0)
            eve.VERTEX2F(pedx, pedy)
            eve.END()

            # Draw pedal glyphs
            eve.COLOR_RGB(255, 255, 255)
            eve.LINE_WIDTH(border * 8)
            if (trace_active[i]):
                # Draw a pause symbol (2 rectangles) using line strips
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
                # Draw a play symbol (triangle) using line strips
                eve.BEGIN(eve.BEGIN_LINE_STRIP)
                eve.VERTEX2F(pedx - (pedalrad // 6), pedy - (pedalrad // 4))
                eve.VERTEX2F(pedx - (pedalrad // 6), pedy + (pedalrad // 4))
                eve.VERTEX2F(pedx + (pedalrad // 4), pedy)
                eve.VERTEX2F(pedx - (pedalrad // 6), pedy - (pedalrad // 4))
                eve.END()
            
            eve.CMD_TEXT(tracecx, labely, labelfont, eve.OPT_CENTERX | eve.OPT_FORMAT, "CH: %d", i)
            eve.CMD_FGCOLOR(0xff0000)
            eve.CMD_BGCOLOR(0x440000)
            eve.CMD_SEVENSEG(samplex + (4 * border), sampley + (5 * border), samplew // 3, (trace_counter[i] // 10) % 10)
            eve.CMD_SEVENSEG(samplex + samplew - (samplew // 3) - (4 * border), sampley + (5 * border), samplew // 3, trace_counter[i] % 10)
        
        if geqbass:
            geqbass = (geqbass * 98) / 100
        if geqmid:
            geqmid = (geqmid * 5) / 10
        if geqtreb:
            geqtreb = (geqtreb * 75) / 100

        if vu_active:
            # Average channels for level
            vu_level = vu_sample * 2 // vu_active
            if (vu_level > 255): 
                vu_level = 255
        else:
            # No channels active
            vu_level = 0

        # Peak level - make EQ pulse
        if vu_level > vu_prev: 
            geqbass = 255
            geqmid = 255
            geqtreb = 255
        vu_prev = vu_level

        # Draw VU meter pointer
        vu_prev1 = vumeter.cmd_vumeter(eve, vux1, vuy, vuw, vuh, vu_level, vu_prev1, 5)
        vu_prev2 = vumeter.cmd_vumeter(eve, vux2, vuy, vuw, vuh, vu_level, vu_prev2, 5)

        if (perf_fps):
            eve.COLOR_RGB(255, 255, 255)
            eve.CMD_TEXT(eve.EVE_DISP_WIDTH, 0, 34, eve.OPT_RIGHTX | eve.OPT_FORMAT, "FPS: %d", perf_fps)

        eve.DISPLAY()
        tstart = time.monotonic()
        eve.CMD_SWAP()
        eve.LIB_EndCoProList()
        eve.LIB_AwaitCoProEmpty()
        
        tend = time.monotonic()
        tcoprocend += tend - tstart

        for i in range(TRACE_COUNT):
            if (trace_active[i]):
                trace_offset[i] = trace_offset[i] + 8
                if trace_offset[i] + traceoff > len(trace_data[i]):
                    trace_offset[i] = 0
                    trace_active[i] = 0
                    trace_counter[i] = trace_counter[i] + 1

        trigger_count += 1
        if trigger_count >= trigger_offset:
            trigger_count = 0
            trigger_mask += 1
            trigger_active ^= trigger_mask
            for i in range(TRACE_COUNT):
                trace_active[i] = (trigger_mask >> i) & 1
                if trace_active[i] == 0:
                    trace_offset[i] = 0
            t1 = time.monotonic()
            took = t1 - t0
            #print(f"{trigger_offset} frames took {took:.3f} s. {trigger_offset / took:.2f} perf_fps")
            perf_fps = int(trigger_offset / took)
            t0 = t1
            #print(f"tplotstream {tplotstream:.3f} s. {tplotstream / trigger_offset / TRACE_COUNT:.8f} s")
            #print(f"tcoprocend {tcoprocend:.3f} s. {tcoprocend / trigger_offset / TRACE_COUNT:.8f} s")
            tplotstream = 0
            tcoprocend = 0

apprunner.run(audioloop, patch)
