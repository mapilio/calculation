from math import radians, cos, sin, asin, sqrt, atan2, pi
from calculation.units import TO_RAD, TO_DEG, RADIUS
from trianglesolver import solve, degree
import numpy


class Distance:

    @staticmethod
    def checkValidity(a, b, c):
        """
        Triangle rule checks
        it's triangle edged as a, b, c
        Parameters
        ----------
        a
        b
        c

        Returns if is not triangle and C degree over the defined variable return False.
        -------

        """
        a, b, c, A, B, C = solve(a, b, c)
        if (a + b <= c) or (a + c <= b) or (b + c <= a):
            if not 5 < (C / degree) < 20:
                return False
        return True

    def bearing(self, startLat, startLon, destLat, destLon):
        phi1 = radians(startLat)
        phi2 = radians(destLat)
        cosPhi2 = cos(phi2)
        dLmd = radians(destLon - startLon)
        aci = atan2(sin(dLmd) * cosPhi2,
                    cos(phi1) * sin(phi2) - sin(phi1) * cosPhi2 * cos(dLmd))
        print(aci * TO_DEG)
        return aci * TO_DEG

    def haversine(self, lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        """
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
    def destinationPoint(lat1, lon1, distance, bearing):
        δ = distance / RADIUS
        θ = bearing * TO_RAD
        φ1 = radians(lat1)
        λ1 = radians(lon1)
        φ2 = asin(sin(φ1) * cos(δ) + cos(φ1) * sin(δ) * cos(θ))
        λ2 = λ1 + atan2(sin(θ) * sin(δ) * cos(φ1), cos(δ) - sin(φ1) * sin(φ2))
        λ2 = (λ2 + 3 * pi) % (2 * pi) - pi

        return {"lat": φ2 * TO_DEG, "lon": λ2 * TO_DEG}

    def checkTriangleRule(self, cornerA, cornerB, cornerC) -> bool:
        """
        triangle rule
        abs(edgeA - edgeB) < edgeC < edgeA + edgeB

        Parameters
        ----------
        cornerA
        cornerB
        cornerC

        Returns true or false
        -------

        """

        edgeAB = (self.haversine(cornerA[0], cornerA[1],
                                 cornerB[0], cornerB[1])) * 1000
        edgeAC = (self.haversine(cornerA[0], cornerA[1],
                                 cornerC[0], cornerC[1])) * 1000
        edgeBC = (self.haversine(cornerB[0], cornerB[1],
                                 cornerC[0], cornerC[1])) * 1000

        return self.checkValidity(edgeAB, edgeAC, edgeBC)

    def checkBBoxDistance(self, box, cfg):
        xmin, ymin, xmax, ymax = list(map(int, box))
        # print("Y Distances = ",np.abs(ymax-ymin),
        #       "X Distances = ", np.abs(xmax-xmin))
        if numpy.abs(ymax - ymin) < cfg.boundingBoxMinHeight \
                or numpy.abs(
            xmax - xmin) < cfg.boundingBoxMinWidth:  # these variables limited detected box in panoramic that only get this section.
            return False
        return True

    def LineToXYs(self, line):  # return first and last coordinates
        firstX, firstY = (line.firstPoint.X, line.firstPoint.Y)
        lastX, lastY = (line.lastPoint.X, line.lastPoint.Y)
        return [(firstX, firstY), (lastX, lastY)]
