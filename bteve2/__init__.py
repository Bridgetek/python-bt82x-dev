# For Bridgetek Pte. Ltd. license see `LICENSE.txt`

from collections import namedtuple

__version__ = '1.3.0'

from sys import implementation
if implementation.name == "circuitpython":
    from .circuitpython import connector as connectorcp

try:
    from _eve import _EVE
except:
    from ._eve import _EVE
  
from .eve import CoprocessorException, EVE2 as e_EVE2

"""
This module is designed to be used as a subclass of a superclass that 
provides the methods reset, wr and rd, which provide raw byte 
read/write to the EVE2 hardware.

    reset()          Strobe the reset pin
    rd(a, n)         Read bytes
    wr(a, s, inc)    Write bytes

It has 2 subclasses, EVE2 and _EVE. 

The _EVE class is in the file _eve.py. This contains all the display
list command definitions and low-level methods for formatting commands
for the EVE display list and co-processor. Commands are added to a 
buffer which is then flushed to the EVE device using the raw read/write
methods.

The EVE2 class is in the file eve.py. This is the co-processor file and
has code to manage the co-processor operation and the RAM_CMD area. 
It uses the raw read/write methods to access co-processor registers.

"""

# Set the size and the display format of the display
Surface = namedtuple('Surface', ['addr', 'fmt', 'w', 'h'])
# Optional panel settings for the display (if not set then use best guess)
Panel = namedtuple('Panel', ['display_res','hcycle','hoffset','hsync0','hsync1','vcycle','voffset','vsync0','vsync1','swizzle','pclk_pol','cspread','dither','pclk_freq'])
# Optional touch screen settings
Touch = namedtuple('Touch', ['description','address','type'])

class EVE2(e_EVE2, _EVE):
        
    def __init__(self, connector):

        print(f"Connector is {connector}")
        if implementation.name != "circuitpython":
            if (connector == "ft4222module"):
                from .ft4222module import connector as connector4222
                self.connector = connector4222()
            if (connector == "ft232h"):
                from .ft232h import connector as connector232
                self.connector = connector232()
            if (connector == "ft4232h"):
                from .ft4232h import connector as connector4232
                self.connector = connector4232()
            if (connector == "d2xx"):
                from .d2xx import connector as connectord2xx
                self.connector = connectord2xx()
        else:
            self.connector = connectorcp()

        # Initialise connector interface
        self.setup_flash = self.connector.setup_flash
        self.sleepclocks = self.connector.sleepclocks
        self.addr = self.connector.addr
        self.rd = self.connector.rd
        self.wr = self.connector.wr
        self.cs = self.connector.cs
        self.reset = self.connector.reset
        self.getcalibration = self.connector.getcalibration
        self.setcalibration = self.connector.setcalibration

        # Start connection to the BT82x
        self.boot()
