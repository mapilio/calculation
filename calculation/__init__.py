"""
Mapilio Calculation is a Python library for geocoding calculation services.

Calculation makes it easy for mapilio to provide accessibilty for data sources.

Bearing
Haversine
Intersection
Distance
Angle
Destination Point
Calculate Pixel
areaCalculate
calcThetaBoxCornerPoints
previous_current_next
bb_intersection_over_union
pixCalc


Contains all above functions. Needs improvment on destination point and angle calculation. Rest works fine
"""

from calculation.area import Area  # noqa
from calculation.distance import Distance  # noqa
from calculation.intersection import Intersection  # noqa
from calculation.iterator import Iterator  # noqa
from calculation.pixel import Pixel  # noqa
from calculation.util import __version__, __version_info__, get_version  # noqa