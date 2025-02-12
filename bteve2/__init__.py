import struct
from collections import namedtuple

__version__ = '0.3.0'

from .registers import *
from sys import implementation
if implementation.name == "circuitpython":
    from _eve import _EVE
else:
    from ._eve import _EVE
    
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

class EVE2(e_EVE2, _EVE):
    pass

