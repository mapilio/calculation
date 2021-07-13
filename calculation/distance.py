from math import radians, cos, sin, asin, sqrt, atan2, pi
from calculation.units import TO_RAD, TO_DEG, RADIUS
from trianglesolver import solve, degree
import numpy
import math

from addict import Dict


class Distance:

    def __init__(self):
        pass

    @staticmethod
    def checkValidity(a: float, b: float, c: float) -> bool:
        """
        Triangle rule checks it's triangle edged as a, b, c
        Args:
            a: edge
            b: edge
            c: edge
        Returns:
            if is not triangle and C degree over the defined variable return False.
        """
        a, b, c, A, B, C = solve(a, b, c)
        if (a + b <= c) or (a + c <= b) or (b + c <= a):
            if not 5 < (C / degree) < 20:
                return False
        return True

    @staticmethod
    def bearing(**kwargs):
        """
        Calculate bearing(direction) from two points
        Args:
            **kwargs:
             -> startLat
             -> startLon
             -> destLat
             -> destLon
        Returns:
            Angle calculate from two point
        """
        """
        

        :param startLat:
        :param startLon:
        :param destLat:
        :param destLon:
        :return:
        """

        points = Dict(kwargs)
        startLat = points.startLat
        startLon = points.startLon
        destLat = points.destLat
        destLon = points.destLon

        phi1 = radians(startLat)
        phi2 = radians(destLat)
        cosPhi2 = cos(phi2)
        dLmd = radians(destLon - startLon)
        aci = atan2(sin(dLmd) * cosPhi2,
                    cos(phi1) * sin(phi2) - sin(phi1) * cosPhi2 * cos(dLmd))
        print(aci * TO_DEG)
        return aci * TO_DEG

    @staticmethod
    def haversine(**kwargs):
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        Args:
            **kwargs:
            -> lon1
            -> lat1
            -> lon2
            -> lat2

        Returns:
            distance between two points
        """
        points = Dict(kwargs)
        lon1 = points.lon1
        lat1 = points.lat1
        lon2 = points.lon2
        lat2 = points.lat2

        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        # r = 6371  # Radius of earth in kilometers. Use 3956 for miles
        return c * RADIUS

    @staticmethod
    def destination_point(lat, lon, distance, bearing):
        """
        :lat :
        :lon :
        :distance :
        bearing :
        """

        δ = distance / RADIUS
        θ = bearing * TO_RAD
        φ1 = radians(lat)
        λ1 = radians(lon)
        φ2 = asin(sin(φ1) * cos(δ) + cos(φ1) * sin(δ) * cos(θ))
        λ2 = λ1 + atan2(sin(θ) * sin(δ) * cos(φ1), cos(δ) - sin(φ1) * sin(φ2))
        λ2 = (λ2 + 3 * pi) % (2 * pi) - pi

        return {"lat": φ2 * TO_DEG, "lon": λ2 * TO_DEG}

    def check_triangle_rule(self, cornerA, cornerB, cornerC) -> bool:
        """
            abs(edgeA - edgeB) < edgeC < edgeA + edgeB
        Args:
            cornerA: edge
            cornerB: edge
            cornerC: edge

        Returns:
            true or false
        """
        edgeAB = (self.haversine(lon1=cornerA[0], lat1=cornerA[1],
                                 lon2=cornerB[0], lat2=cornerB[1])) * 1000
        edgeAC = (self.haversine(lon1=cornerA[0], lat1=cornerA[1],
                                 lon2=cornerC[0], lat2=cornerC[1])) * 1000
        edgeBC = (self.haversine(lon1=cornerB[0], lat1=cornerB[1],
                                 lon2=cornerC[0], lat2=cornerC[1])) * 1000

        return self.checkValidity(edgeAB, edgeAC, edgeBC)



    @staticmethod
    def line_to_XYs(line):
        # return first and last coordinates
        firstX, firstY = (line.firstPoint.X, line.firstPoint.Y)
        lastX, lastY = (line.lastPoint.X, line.lastPoint.Y)
        return [(firstX, firstY), (lastX, lastY)]

    @staticmethod
    def calculate_initial_compass_bearing(pointA, pointB):
        """
        Calculates the bearing between two points.
        The formulae used is the following:
            θ = atan2(sin(Δlong).cos(lat2),
                      cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))
        Args:
            pointA: The tuple representing the latitude/longitude for the
                    first point. Latitude and longitude must be in decimal degrees
            pointB: The tuple representing the latitude/longitude for the
                    second point. Latitude and longitude must be in decimal degrees

        Returns:
            Angle calculate from two point
        """
        if (type(pointA) != tuple) or (type(pointB) != tuple):
            raise TypeError("Only tuples are supported as arguments")

        lat1 = math.radians(pointA[0])
        lat2 = math.radians(pointB[0])

        diffLong = math.radians(pointB[1] - pointA[1])

        x = math.sin(diffLong) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
                                               * math.cos(lat2) * math.cos(diffLong))

        initial_bearing = math.atan2(x, y)

        # Now we have the initial bearing but math.atan2 return values
        # from -180° to + 180° which is not what we want for a compass bearing
        # The solution is to normalize the initial bearing as shown below
        initial_bearing = math.degrees(initial_bearing)
        compass_bearing = (initial_bearing + 360) % 360

        return compass_bearing

    @staticmethod
    def distance_between_points(origin, destination):

        lat1, lon1 = origin
        lat2, lon2 = destination
        radius = 6371  # km

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) \
            * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = radius * c

        return d
