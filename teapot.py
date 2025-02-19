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
    gd.BitmapHandle(63)
    #gd.cmd_loadimage(0xffffffff, 0)
    gd.cmd_loadimage(80 << 20, 0)
    with open("assets/teapot_logo.png", "rb") as f:
        gd.load(f)
    gd.BitmapSize(eve.NEAREST, eve.REPEAT, eve.BORDER, 0, 129)
    gd.BitmapSizeH(0, 0)

def draw_scroll(gd, frame):
    gd.ClearColorRGB(0x1a, 0x1a, 0x1a)
    gd.Clear(1,1,1)

    gd.SaveContext()
    gd.VertexFormat(0)
    gd.BitmapHandle(63)
    gd.Begin(eve.BITMAPS)

    gd.ColorRGB(0x80, 0x80, 0x80)
    gd.BitmapTransformC(frame*256)
    for i in (0, 2, 4):
        gd.Vertex2f(0, 40 + 200 * i)
    gd.BitmapTransformC(-frame*256)
    for i in (1, 3, 5):
        gd.Vertex2f(0, 40 + 200 * i)
    gd.RestoreContext()

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

    gd.begin()
    gd.Clear()
    setup_scroll(gd)
    gd.swap()

    vertex_array    = 0x000000
    draw_list       = 0x4040000

    gd.cmd_newlist(draw_list)
    gd.ColorRGB(255, 255, 255)
    gd.VertexTranslateX(gd.w // 2)
    gd.VertexTranslateY(gd.h // 2)
    gd.LineWidth(gd.w / 2000)
    for s in strips:
        gd.Begin(eve.LINE_STRIP)
        for i in s:
            gd.cmd_append(vertex_array + 4 * i, 4)
    gd.cmd_endlist()
    gd.swap()

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
        gd.cmd_memwrite(0, len(vxybuf))
        gd.ram_cmd(vxybuf)
        gd.finish()

        gd.begin()
        gd.Clear()
        draw_scroll(gd, scroll_frame)
        gd.VertexFormat(3)
        gd.cmd_calllist(draw_list)
        gd.swap() 

        (ty, tx) = struct.unpack("hh", gd.rd(eve.REG_TOUCH_SCREEN_XY, 4))
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

        gd.cmd_graphicsfinish()
        gd.finish()

    t1 = time.monotonic()
    took = t1 - t0
    print(f"{N} frames took {took:.3f} s. {N / took:.2f} fps")

apprunner.run(teapot)
