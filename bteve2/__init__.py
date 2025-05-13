import os
import sys
import importlib
from collections import namedtuple

__version__ = '0.3.0'

from .registers import REG, KEYS, OPT, BITMAP_FORMAT, PRIMATIVE, TEST, FILTER, WRAP, BLEND, STENCIL, TOUCHMODE, TOUCH, DLSWAP, INT, SAMPLES, CHANNEL, ADC, ANIM, CGRADIENT_SHAPE, CTOUCH_MODE, FLASH_STATUS
from sys import implementation
if implementation.name == "circuitpython":
    #from _eve import _EVE
    pass
else:
    #from ._eve import _EVE
    pass
    
from .eve import align4, CoprocessorException, EVE2 as e_EVE2

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

Surface = namedtuple('Surface', ['addr', 'fmt', 'w', 'h'])

class EVE2(e_EVE2, REG, KEYS, OPT, BITMAP_FORMAT, PRIMATIVE, TEST, 
           FILTER, WRAP, BLEND, STENCIL, TOUCHMODE, TOUCH, 
           DLSWAP, INT, SAMPLES, CHANNEL, ADC, ANIM, 
           CGRADIENT_SHAPE, CTOUCH_MODE, FLASH_STATUS):

    def __init__(self, connector):
        connector_dir = os.path.join(os.path.dirname(__file__), "connectors")

        sys.path.append(connector_dir)
        try:
            self.connector = importlib.import_module(connector)
            print(f"Connector '{connector}' loaded")
        except ModuleNotFoundError:
            print(f"Connector '{connector}' not found in '{connector_dir}'")
            sys.exit(1)

        # Initialise all the classes containing constants
        self.REG = REG
        self.OPT = OPT
        self.KEYS = KEYS
        self.BITMAP_FORMAT = BITMAP_FORMAT
        self.PRIMATIVE = PRIMATIVE
        self.TEST = TEST
        self.FILTER = FILTER
        self.WRAP = WRAP
        self.BLEND = BLEND
        self.STENCIL = STENCIL
        self.TOUCHMODE = TOUCHMODE
        self.TOUCH = TOUCH
        self.DLSWAP = DLSWAP
        self.INT = INT
        self.SAMPLES = SAMPLES
        self.CHANNEL = CHANNEL
        self.ADC = ADC
        self.ANIM = ANIM
        self.CGRADIENT_SHAPE = CGRADIENT_SHAPE
        self.CTOUCH_MODE = CTOUCH_MODE
        self.FLASH_STATUS = FLASH_STATUS

        # Initialise connector interface
        connection = self.connector.EVE2()
        self.setup_flash = connection.setup_flash
        self.sleepclocks = connection.sleepclocks
        self.addr = connection.addr
        self.rd = connection.rd
        self.wr = connection.wr
        self.cs = connection.cs
        self.reset = connection.reset

        # Start connection to the BT82x
        self.boot()
