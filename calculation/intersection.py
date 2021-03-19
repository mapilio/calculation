from calculation.distance import Distance
from addict import Dict
from decimal import Decimal, ROUND_DOWN, getcontext
import collections


class Intersection:

    def __init__(self, **kwargs):
        """
        intersection_lineLength=self.config.intersection.lineLength,
        angle_wide=self.config.intersection.angle_wide
        """
        self.__dict__.update(kwargs)

        self.intersection_lineLength = self.intersection_rule.lineLength
        self.intersection_angle_wide = self.intersection_rule.angle_wide

    @staticmethod
    def apply_confidence_rule(c):
        confidence_rate = (1 - 1 / c) if c else "{} can't null".format({c})

        return confidence_rate

    @staticmethod
    def angle_between(n, a, b):
        ## n = chech between a and b parameter
        ## a start point angle
        ## b finish point angle
        n = int(n)
        a = int(a)
        b = int(b)
        n = (360 + (n % 360)) % 360
        a = (3600000 + a) % 360
        b = (3600000 + b) % 360
        if a < b:
            return a <= n and n <= b
        return a <= n or n <= b

    def calc_between_heading_angle(self, n):
        # n = heading
        # a = angle
        a = self.intersection_angle_wide
        t = 360 + n
        x = (-(a - t)) % 360
        y = (a + t) % 360
        # x, y hands of angle
        return x, y

    def ops_detect(self, loc):
        """
        location location of points
        intersection_lineLength: on the other hand, allows it to change automatically
        when we change it from the config file to specify the line length here.
        """
        ops = []
        for i in range(0, len(loc), 3):
            ops.append(Distance.destination_point(lat=loc[i], lon=loc[i + 1], distance=self.intersection_lineLength,
                                                  bearing=loc[i + 2]))

        return ops[0], ops[1]

    def check_line_intersection(self, **kwargs):

        points = Dict(kwargs)
        line1StartX = points.line1StartX
        line1StartY = points.line1StartY
        line1EndX = points.line1EndX
        line1EndY = points.line1EndY
        line2StartX = points.line2StartX
        line2StartY = points.line2StartY
        line2EndX = points.line2EndX
        line2EndY = points.line2EndY

        result = {
            "x": "null",
            "y": "null",
            "l1": False,
            "l2": False,
        }

        # We check whether any variable is decimal or not,
        # because the heading calculation in requests from the web can be decimal,
        # and the one from the database can be decimal.
        if isinstance(line1StartX, float):
            line1StartX, line1StartY, \
            line2StartX, line2StartY = intersection_float_to_decimal(line1StartX,
                                                                     line1StartY,
                                                                     line2StartX, line2StartY)
        if isinstance(line1EndX, float):
            line1EndX, line1EndY, \
            line2EndX, line2EndY = intersection_float_to_decimal(line1EndX,
                                                                 line1EndY,
                                                                 line2EndX,
                                                                 line2EndY)

        denominator = ((line2EndY - line2StartY) * (line1EndX - line1StartX)) - (
                (line2EndX - line2StartX) * (line1EndY - line1StartY))

        if denominator == 0:
            return result

        a = line1StartY - line2StartY
        b = line1StartX - line2StartX
        numerator1 = ((line2EndX - line2StartX) * a) - ((line2EndY - line2StartY) * b)
        numerator2 = ((line1EndX - line1StartX) * a) - ((line1EndY - line1StartY) * b)
        a = numerator1 / denominator
        b = numerator2 / denominator

        # if we cast these lines infinitely in both directions, they intersect here:
        result['x'] = line1StartX + (a * (line1EndX - line1StartX))
        result['y'] = line1StartY + (a * (line1EndY - line1StartY))

        if 0 < a < 1:
            result["l1"] = True

        if 0 < b < 1:
            result["l2"] = True

        return result

    def intersection_points_average(self, groupMatches, geoFunc):
        total = Dict({})
        total['isValid'] = False
        mergedPoints = []
        objects = collections.defaultdict(list)
        i = 0
        confidence = 0
        for matches in groupMatches:
            i += 2
            k = Dict(matches)
            objects['Lat_center'].append(float(k.intersectCenter['x']))
            objects['Lon_center'].append(float(k.intersectCenter['y']))

            objects['Lat_cornerA'].append(float(k.intersectCornerA['x']))
            objects['Lon_cornerA'].append(float(k.intersectCornerA['y']))

            objects['Lat_cornerB'].append(float(k.intersectCornerB['x']))
            objects['Lon_cornerB'].append(float(k.intersectCornerB['y']))

            objects['Lat_cornerC'].append(float(k.intersectCornerC['x']))
            objects['Lon_cornerC'].append(float(k.intersectCornerC['y']))

            objects['avg_score'].append(float(k.score_1))
            objects['avg_score'].append(float(k.score_2))

            total['detectedPath_1'] = k.detectedPath_1
            total['detectedPath_2'] = k.detectedPath_2

            total['imgUrl_1'] = k.imgUrl_1
            total['imgUrl_2'] = k.imgUrl_2

            total['objId_1'] = k.objId_1
            total['objId_2'] = k.objId_2
            total['match_id'] = k.match

            total['classname'] = k.classname_1 # doesn't matter same classname_1 and classname_2

            geojsonParams = {
                "lat"           : float(k.intersectCenter['x']),
                "lon"           : float(k.intersectCenter['y']),
                "score_1"       : k.score_1,
                "score_2"       : k.score_2,
                "objId_1"       : k.objId_1,
                "objId_2"       : k.objId_2,
                "bbox_1"        : k.bbox_1,
                "bbox_2"        : k.bbox_2,
                "segmentation_1": k.segmentation_1,
                "segmentation_2": k.segmentation_2,
                "panoId_1"      : k.panoId_1,
                "panoId_2"      : k.panoId_2,
                "type"          : "Point",
                "format"        : "paired"
            }

            mergedPoints.append(geoFunc(**geojsonParams))
            confidence = self.apply_confidence_rule(i)


            total['isValid'] = i > 0


        for k, v in objects.items():
            total[k] = float(sum(v) / len(v))

        total['matchedPoints'] = mergedPoints
        total['confidence'] = (total['avg_score'] + confidence) * 0.5

        return total

    def intersection_points_find(self, **kwargs):

        points = Dict(kwargs)
        start_lat1 = points.start_lat1
        start_lon1 = points.start_lon1
        theta1 = points.theta1
        start_lat2 = points.start_lat2
        start_lon2 = points.start_lon2
        theta2 = points.theta2
        type = points.type

        if type == "center":
            ops1, ops2 = self.ops_detect(loc=[start_lat1, start_lon1, theta1,
                                              start_lat2, start_lon2, theta2])

            destinationPoint1 = [(start_lat1, start_lon1),
                                 (ops1["lat"], ops1["lon"])]

            destinationPoint2 = [(start_lat2, start_lon2),
                                 (ops2["lat"], ops2["lon"])]

            interSection = self.check_line_intersection(line1StartX=start_lat1,
                                                        line1StartY=start_lon1,
                                                        line1EndX=ops1["lat"],
                                                        line1EndY=ops1["lon"],

                                                        line2StartX=start_lat2,
                                                        line2StartY=start_lon2,
                                                        line2EndX=ops2["lat"],
                                                        line2EndY=ops2["lon"])
            return interSection, destinationPoint1, destinationPoint2
        if type == "corner":
            interSectionPoints = []
            for first, second in zip(theta1, theta2):
                ops1, ops2 = self.ops_detect(loc=[start_lat1, start_lon1, first,
                                                  start_lat2, start_lon2, second])

                interSection = self.check_line_intersection(line1StartX=start_lat1,
                                                            line1StartY=start_lon1,
                                                            line1EndX=ops1["lat"],
                                                            line1EndY=ops1["lon"],

                                                            line2StartX=start_lat2,
                                                            line2StartY=start_lon2,
                                                            line2EndX=ops2["lat"],
                                                            line2EndY=ops2["lon"])
                interSectionPoints.append(interSection)

            return interSectionPoints


def decimal_fix(number):
    getcontext().rounding = ROUND_DOWN
    return Decimal(number).quantize(Decimal(10) ** -9)


def intersection_float_to_decimal(lat1, lon1, lat2, lon2):
    """

    Parameters
    ----------
    lat1
    lon1
    lat2
    lon2

    Returns points convert decimal format
    -------

    """
    lat1 = decimal_fix(lat1)
    lon1 = decimal_fix(lon1)
    lat2 = decimal_fix(lat2)
    lon2 = decimal_fix(lon2)

    return lat1, lon1, lat2, lon2