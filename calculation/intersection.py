from calculation.distance import Distance
from calculation.pixel import Pixel
from addict import Dict
from decimal import Decimal, ROUND_DOWN, getcontext


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

    def intersection_points_average(self, averagePoint):
        averagePoint_arr = []
        for keys, values in averagePoint.items():
            total = {'Lat_center': 0, 'Lon_center': 0,
                     'Lat_cornerA': 0, 'Lon_cornerA': 0,
                     'Lat_cornerB': 0, 'Lon_cornerB': 0,
                     'Lat_cornerC': 0, 'Lon_cornerC': 0,
                     'score': 0, 'isValid': 0,
                     'avg_score': 0,
                     'area': 0,
                     'point': 0, 'match_id': 0, 'detectedObjectPath': None,
                     'imgUrl': None}
            c = len(values)
            confidence = self.apply_confidence_rule(c)

            # TODO refactor
            for j in range(c):
                total['classname'] = values[j][1]
                total['score'] += values[j][2]
                total['imgid'] = values[j][3]

                total['Lat_center'] += float(values[j][4])
                total['Lon_center'] += float(values[j][5])

                total['Lat_cornerA'] += float(values[j][6])
                total['Lon_cornerA'] += float(values[j][7])

                total['Lat_cornerB'] += float(values[j][8])
                total['Lon_cornerB'] += float(values[j][9])

                total['Lat_cornerC'] += float(values[j][10])
                total['Lon_cornerC'] += float(values[j][11])

                total['detectedObjectPath'] = values[j][12]
                total['imgUrl'] = values[j][13]

                total['match_id'] = values[j][-1]

            total['Lat_center'] = total['Lat_center'] / c
            total['Lon_center'] = total['Lon_center'] / c

            total['Lat_cornerA'] = total['Lat_cornerA'] / c
            total['Lon_cornerA'] = total['Lon_cornerA'] / c

            total['Lat_cornerB'] = total['Lat_cornerB'] / c
            total['Lon_cornerB'] = total['Lon_cornerB'] / c

            total['Lat_cornerC'] = total['Lat_cornerC'] / c
            total['Lon_cornerC'] = total['Lon_cornerC'] / c

            total['area'] = total['area'] / c
            total['avg_score'] = (total['score'] / c)
            total['point'] = (total['avg_score'] + confidence) * 0.5
            total['isValid'] = c > 1
            averagePoint_arr.append(total)

        return averagePoint_arr

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