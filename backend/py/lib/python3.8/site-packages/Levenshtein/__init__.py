try:
    from . import _levenshtein
    from ._levenshtein import *
except ImportError:
    _levenshtein = None
else:
    __doc__ = _levenshtein.__doc__

__version__ = "0.13.1"
__author__ = "Antti Haapala"
