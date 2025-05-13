import os
import sys
import importlib
from collections import namedtuple

__version__ = '0.3.0'

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

class EVE2(e_EVE2):

    def __init__(self, connector):
        connector_dir = os.path.join(os.path.dirname(__file__), "connectors")

        sys.path.append(connector_dir)
        try:
            self.connector = importlib.import_module(connector)
            print(f"Connector '{connector}' loaded")
        except ModuleNotFoundError:
            print(f"Connector '{connector}' not found in '{connector_dir}'")
            sys.exit(1)

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
