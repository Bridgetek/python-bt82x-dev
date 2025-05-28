import os

# This is the EVE library.
import bteve2 as evelib

def _result(eve, r):
    if r != 0:
        exception = eve.LIB_SDCARD_ERROR(r)
        print(f"Error 0x{r:x}: {exception}")

# Screenshot Widget
#
# Calling format:
#   screenshot.cmd_screenshot(eve, filename)
#
# Parameters:
#   eve: Handle to class of bteve2.
#   filename: Name of file to write on SD card.
#
# Returns:
#   Status value from cmd_fssnapshot
#
def cmd_screenshot(eve, filename):
    assert(type(eve) == evelib.EVE2)

    print(f"Writing screenshot to file \"{filename}\"...")
    r = eve.LIB_FSSNAPSHOT(0x10000, filename)
    if r != 0:
        print(f"Could not write screenshot to file \"{filename}\".")
        _result(eve, r)
    return r

# Screenshot Widget Setup
#
# Calling format:
#   screenshot.setup(eve)
#
# Parameters:
#   eve: Handle to class of bteve2.
#
# Returns:
#   Status value from cmd_sdattach
#
def setup(eve):
    assert(type(eve) == evelib.EVE2)
    cdir = os.path.dirname(os.path.realpath(__file__))
    pfile = os.path.join(cdir, "screenshot.patch")

    eve.LIB_BEGINCOPROLIST()
    eve.CMD_DLSTART()
    eve.CMD_LOADPATCH(0)
    with open(pfile, "rb") as f:
        eve.load(f)
    eve.LIB_ENDCOPROLIST()
    eve.LIB_AWAITCOPROEMPTY()
    versions = eve.LIB_GETCOPROEXCEPTION()
    print(versions)

    eve.LIB_BEGINCOPROLIST()
    eve.CMD_DLSTART()
    r = eve.LIB_SDATTACH(eve.OPT_IS_SD)
    if r != 0:
        print(f"Could not attach SD card.")
        _result(eve, r)
    return r
