import struct
from collections import namedtuple

__version__ = '0.2.1'

from .registers import *
from sys import implementation
if implementation.name == "circuitpython":
    from _eve import _EVE
else:
    from ._eve import _EVE
    
from .eve import align4, CoprocessorException, EVE2 as e_EVE2

Surface = namedtuple('Surface', ['addr', 'fmt', 'w', 'h'])

class EVE2(e_EVE2, _EVE):
    pass

