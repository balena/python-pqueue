__author__ = 'G. B. Versiani'
__license__ = 'BSD'
__version__ = '0.1.7'

import sys
if sys.version_info < (3, 0):
    from Queue import Empty, Full
else:
    from queue import Empty, Full

from .pqueue import Queue

__all__ = [Queue, Empty, Full, __author__, __license__, __version__]
