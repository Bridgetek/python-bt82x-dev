# Generated file by extensionutil.py 

import struct
from sys import implementation
if implementation.name != "circuitpython":
    import os
    circuitpython = False
else:
    circuitpython = True

def pad4(s):
    while len(s) % 4:
        s += b'\x00'
    return s

# From patch1 */

# CMD_REGION
def CMD_REGION(eve, *args):
    eve.cmd0(0x8f)

# CMD_ENDREGION
def CMD_ENDREGION(eve, *args):
    eve.cmd0(0x90)
    eve.cc(pad4(struct.pack("hhhh", *args[0:4])))

# CMD_TOUCHOFFSET
def CMD_TOUCHOFFSET(eve, *args):
    eve.cmd0(0xae)
    eve.cc(pad4(struct.pack("hh", *args[0:2])))

# CMD_ENDTOUCHOFFSET
def CMD_ENDTOUCHOFFSET(eve, *args):
    eve.cmd0(0xaf)

def loadpatch(eve):
    if not circuitpython:
        patchfile = os.path.join(os.path.dirname(__file__), "patch_base.bin")
        chunk = 256
    else:
        patchfile = "patch_base.bin"
        chunk = 16
    actual = ""
    expected = "patch_base;1.0;"
    # Load extension code to BT82x
    eve.LIB_BeginCoProList()
    eve.CMD_DLSTART()
    eve.CMD_LOADPATCH(0)
    try:
        with open(patchfile, "rb") as f:
            while True:
                patchdata = f.read(chunk)
                eve.LIB_WriteDataToCMD(patchdata)
                if len(patchdata) < chunk:
                    break
                pass
    except OSError:
        raise RuntimeError("Could not find: \"%s\"" % (patchfile))
    eve.LIB_EndCoProList()
    eve.LIB_AwaitCoProEmpty()
    actual = eve.LIB_GetCoProException()

    # Double check that the loaded patch versions match the expected versions
    verexpected = expected.split(';')
    verexpected.sort()
    veractual = actual.split(';')
    veractual.sort()
    if (verexpected != veractual):
        raise RuntimeError("Loaded file mismatch: \"%s\" should be \"%s\"" % (actual, expected))
