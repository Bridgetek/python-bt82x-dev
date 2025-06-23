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

# Add the library directories to the module search path.
sys.path.append('../..')
sys.path.append('../../bteve2')

# This module provides the connector to the EVE hardware.
import apprunner

from assets import teapot_trackball

def setup_scroll(eve):
    eve.BITMAP_HANDLE(63)
    #eve.CMD_LOADIMAGE(0xffffffff, 0)
    eve.CMD_LOADIMAGE(80 << 20, 0)
    with open("assets/teapot_logo.png", "rb") as f:
        eve.load(f)
    eve.BITMAP_SIZE(eve.FILTER_NEAREST, eve.WRAP_REPEAT, eve.WRAP_BORDER, 0, 129)
    eve.BITMAP_SIZE_H(0, 0)

def draw_scroll(eve, frame):
    eve.CLEAR_COLOR_RGB(0x1a, 0x1a, 0x1a)
    eve.CLEAR(1,1,1)

    eve.SAVE_CONTEXT()
    eve.VERTEX_FORMAT(0)
    eve.BITMAP_HANDLE(63)
    eve.BEGIN(eve.BEGIN_BITMAPS)

    eve.COLOR_RGB(0x80, 0x80, 0x80)
    eve.BITMAP_TRANSFORM_C(frame*256)
    for i in (0, 2, 4):
        eve.VERTEX2F(0, 40 + 200 * i)
    eve.BITMAP_TRANSFORM_C(-frame*256)
    for i in (1, 3, 5):
        eve.VERTEX2F(0, 40 + 200 * i)
    eve.RESTORE_CONTEXT()

def teapot(eve):

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
            q = 8 * (eve.h / 150) * d
        else:
            q = 8 * (eve.h / 150)
        return (
            np.array(x * q, dtype = np.int32),
            np.array(y * q, dtype = np.int32)
        )

    (vertices, strips) = json.load(open("assets/teapot_geometry.json"))
    curquat = teapot_trackball.trackball(0, 0, 0, 0)

    eve.LIB_BeginCoProList()
    eve.CMD_DLSTART()
    eve.CLEAR()
    setup_scroll(eve)
    eve.CMD_SWAP()
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()

    vertex_array    = 0x000000
    draw_list       = 0x4040000

    eve.LIB_BeginCoProList()
    eve.CMD_NEWLIST(draw_list)
    eve.COLOR_RGB(255, 255, 255)
    eve.VERTEX_TRANSLATE_X((eve.w // 2) * 16)
    eve.VERTEX_TRANSLATE_Y((eve.h // 2) * 16)
    eve.LINE_WIDTH((eve.w / 2000) * 8)
    for s in strips:
        eve.BEGIN(eve.BEGIN_LINE_STRIP)
        for i in s:
            eve.CMD_APPEND(vertex_array + 4 * i, 4)
    eve.CMD_ENDLIST()
    eve.CMD_SWAP()
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()

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
        eve.LIB_BeginCoProList()
        eve.CMD_MEMWRITE(0, len(vxybuf))
        eve.LIB_WriteDataToCMD(vxybuf)
        eve.LIB_EndCoProList()
        eve.LIB_AwaitCoProEmpty()

        eve.LIB_BeginCoProList()
        eve.CMD_DLSTART()
        eve.CLEAR()
        draw_scroll(eve, scroll_frame)
        eve.VERTEX_FORMAT(3)
        eve.CMD_CALLLIST(draw_list)
        eve.CMD_SWAP()
        eve.LIB_EndCoProList()
        eve.LIB_AwaitCoProEmpty() 

        eve.LIB_BeginCoProList()
        (ty, tx) = eve.LIB_GetTouch()
        touching = (tx != -32768)
        sx = (2 * tx - eve.w) / eve.w
        sy = (eve.h - 2 * ty) / eve.h
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

        eve.CMD_GRAPHICSFINISH()
        eve.LIB_EndCoProList()
        eve.LIB_AwaitCoProEmpty()

    t1 = time.monotonic()
    took = t1 - t0
    print(f"{N} frames took {took:.3f} s. {N / took:.2f} fps")

apprunner.run(teapot)
