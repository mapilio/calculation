import logging
from decimal import Decimal

NUMBER_TYPES = (int, float, Decimal)

__version__ = "0.0.3"
__version_info__ = (0, 0, 3)

logger = logging.getLogger('calculation')

def get_version():
    return __version__
