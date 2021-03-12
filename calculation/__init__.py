"""
Mapilio Calculation is a Python library for geocoding calculation services.

Calculation makes it easy for mapilio to provide accessibility for data sources.

Contains all above functions. Needs improvement on destination point and angle calculation. Rest works fine
"""


from .area import Area
from .distance import Distance
from .intersection import Intersection
from .iterator import Iterator
from .pixel import Pixel

from .util import __version__, __major__, __minor__, __patch__