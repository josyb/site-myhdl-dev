
from __future__ import division
from __future__ import print_function

from myhdl import *

class MDArray(object):
    """ This is a simple object that takes
    """
    def __init__(self, stype, dim=(1,1,1)):
        total_elements = 1
        for ee in dim:
            total_elements *= ee
            
        self._mem = [Signal(stype) for _ in range(total_elements)]

        self.dim = dim