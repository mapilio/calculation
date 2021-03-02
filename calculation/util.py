import logging
from decimal import Decimal

NUMBER_TYPES = (int, float, Decimal)

__version__ = "0.0.2.1"
__version_info__ = (0, 0, 2, 1)

logger = logging.getLogger('calculation')

def get_version():
    return __version__
