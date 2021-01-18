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

from calculation.area import Area
from calculation.distance import Distance
from calculation.intersection import Intersection
from calculation.iterator import Iterator
from calculation.pixel import Pixel

from calculation.util import __version__, __version_info__, get_version