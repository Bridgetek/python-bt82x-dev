# Typical command line:
# python teapot.py --connector ft4222module
import sys
import argparse

import math
import sys
import time
import struct
import gc
import json
import ctypes

import numpy as np

# This module provides the connector (gd) to the EVE hardware.
import apprunner

# Target EVE device.
family = "BT82x"

# EVE family support check.
device_families = ["FT80x", "FT81x", "BT81x", "BT82x"]
assert(family in device_families)

if family == "BT82x":
    # This loads BT82x family definitions only.
    import bteve2 as eve
else:
    # This loads FT80x, FT81x, BT81x family definitions.
    import bteve as eve

# Target EVE device.
family = "BT82x"

from assets import teapot_trackball

def setup_scroll(gd):
    gd.BITMAP_HANDLE(63)
    #gd.CMD_LOADIMAGE(0xffffffff, 0)
    gd.CMD_LOADIMAGE(80 << 20, 0)
    with open("assets/teapot_logo.png", "rb") as f:
        gd.load(f)
    gd.BITMAP_SIZE(gd.FILTER_NEAREST, gd.WRAP_REPEAT, gd.WRAP_BORDER, 0, 129)
    gd.BITMAP_SIZE_H(0, 0)

def draw_scroll(gd, frame):
    gd.CLEAR_COLOR_RGB(0x1a, 0x1a, 0x1a)
    gd.CLEAR(1,1,1)

    gd.SAVE_CONTEXT()
    gd.VERTEX_FORMAT(0)
    gd.BITMAP_HANDLE(63)
    gd.BEGIN(gd.BEGIN_BITMAPS)

    gd.COLOR_RGB(0x80, 0x80, 0x80)
    gd.BITMAP_TRANSFORM_C(frame*256)
    for i in (0, 2, 4):
        gd.VERTEX2F(0, 40 + 200 * i)
    gd.BITMAP_TRANSFORM_C(-frame*256)
    for i in (1, 3, 5):
        gd.VERTEX2F(0, 40 + 200 * i)
    gd.RESTORE_CONTEXT()

def teapot(gd):

    def c4(i):
        return struct.pack("I", i)

    def xform(xyz):
        rr = teapot_trackball.build_rotmatrix(curquat)
        x = np.dot(xyz, rr[0])
        y = -np.dot(xyz, rr[1])
        if 0:
            z = np.dot(xyz, rr[2])
            D = 300
            d = D / (D - z)
            q = 8 * (gd.h / 150) * d
        else:
            q = 8 * (gd.h / 150)
        return (
            np.array(x * q, dtype = np.int32),
            np.array(y * q, dtype = np.int32)
        )

    (vertices, strips) = json.load(open("assets/teapot_geometry.json"))
    curquat = teapot_trackball.trackball(0, 0, 0, 0)

    gd.CMD_DLSTART()
    gd.CLEAR()
    setup_scroll(gd)
    gd.CMD_SWAP()
    gd.LIB_AwaitCoProEmpty()

    vertex_array    = 0x000000
    draw_list       = 0x4040000

    gd.CMD_NEWLIST(draw_list)
    gd.COLOR_RGB(255, 255, 255)
    gd.VERTEX_TRANSLATE_X(gd.w // 2)
    gd.VERTEX_TRANSLATE_Y(gd.h // 2)
    gd.LINE_WIDTH(gd.w / 2000)
    for s in strips:
        gd.BEGIN(gd.BEGIN_LINE_STRIP)
        for i in s:
            gd.CMD_APPEND(vertex_array + 4 * i, 4)
    gd.CMD_ENDLIST()
    gd.CMD_SWAP()
    gd.LIB_AwaitCoProEmpty()

    xyz = np.array(vertices)

    gc.collect()

    prev_touch = None
    spin = teapot_trackball.trackball(-.04, -.04, 0, 0)

    t0 = time.monotonic()
    N = 3000
    frame = 0
    scroll_frame = 0            
    while frame < N:
        # Calculate the vertexes of the teapot.
        (sx, sy) = xform(xyz)
        # Format into a list of tuples.
        vtx = list(zip(sx, sy))
        # Make VERTEX2F commands from the tuples.
        vxybuf = b''
        for (vx, vy) in vtx:
            vxybuf += c4((0x1 << 30) | ((vx & 32767) << 15) | (vy & 32767) ) 
        # Write the VERTEX2F commands to RAMG
        gd.CMD_MEMWRITE(0, len(vxybuf))
        gd.ram_cmd(vxybuf)
        gd.LIB_AwaitCoProEmpty()

        gd.CMD_DLSTART()
        gd.CLEAR()
        draw_scroll(gd, scroll_frame)
        gd.VERTEX_FORMAT(3)
        gd.CMD_CALLLIST(draw_list)
        gd.CMD_SWAP()
        gd.LIB_AwaitCoProEmpty() 

        (ty, tx) = struct.unpack("hh", gd.rd(gd.REG_TOUCH_SCREEN_XY, 4))
        touching = (tx != -32768)
        sx = (2 * tx - gd.w) / gd.w
        sy = (gd.h - 2 * ty) / gd.h
        if touching:
            if prev_touch is not None:
                spin = teapot_trackball.trackball(prev_touch[0], prev_touch[1], sx, sy)
                spin *= 8
                frame = 0
            prev_touch = (sx, sy)
        else:
            frame = frame + 1
            prev_touch = None
        curquat = teapot_trackball.add_quats(curquat, spin)
        scroll_frame += 1

        gd.CMD_GRAPHICSFINISH()
        gd.LIB_AwaitCoProEmpty()

    t1 = time.monotonic()
    took = t1 - t0
    print(f"{N} frames took {took:.3f} s. {N / took:.2f} fps")

apprunner.run(teapot)
