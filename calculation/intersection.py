from typing import Callable, Tuple, List

from calculation.distance import Distance
from helper.convertor import Convertor

from addict import Dict
import collections


class Intersection:

    def __init__(self, **kwargs):
        """

        Args:
            **kwargs:
            -> intersection_lineLength=self.config.intersection.lineLength,
            -> angle_wide=self.config.intersection.angle_wide
        """
        self.__dict__.update(kwargs)

        self.intersection_lineLength = self.intersection_rule.lineLength
        self.intersection_angle_wide = self.intersection_rule.angle_wide

    @staticmethod
    def apply_confidence_rule(c):
        """

        Args:
            c: detected car location

        Returns:
            it's score for how many has captured car locations and calculate 0 < result < 100
        """
        confidence_rate = (1 - 1 / c) if c else "{} can't null".format({c})

        return confidence_rate

    @staticmethod
    def angle_between(frameFilters: list) -> list:
        """
            calculated theta is it between define angle hands
        Args:
            # TODO car1 and car2 [ theta1, theta2, angleMIN, angleMAX]
            frameFilters:  car1 = [theta1, angleMIN, angleMAX], car2 = [theta1, angleMIN, angleMAX]
        Returns:
            only two position cars calculate and return such as [True, False],  [False, False]
        """
        rets = []
        for params in frameFilters:
            ## n = chech between a and b parameter
            ## a start point angle
            ## b finish point angle
            n = int(params[0])
            a = int(params[1])
            b = int(params[2])
            n = (360 + (n % 360)) % 360
            a = (3600000 + a) % 360
            b = (3600000 + b) % 360
            if a < b:
                result = a <= n <= b
                rets.append(result)
            else:
                result = a <= n or n <= b
                rets.append(result)

        return rets

    def calc_between_heading_angle(self, nArr: list) -> Dict:
        """
         angle with heading relations check for intersection angle wide
         Example1 :
            angle  = 120 and heading = 75  result {theta must be between max 195 min 45}
         Example2 :
            angle  = 50 and heading = 320  result {theta must be between max 270 min 30}
        Args:
            nArr: its list and include headings

        Returns:
            up limit and down limit for theta degrees.
        """

        a = self.intersection_angle_wide
        ret = []
        for n in nArr:
            t = 360 + n
            x = (-(a - t)) % 360
            y = (a + t) % 360
            # x, y hands of angle
            ret.append([x, y])

        anglesArr = [item for sublist in ret for item in sublist]
        assert len(anglesArr) >= 4, "Check your Thetas"
        angles = Dict({
            'max1Ahead': anglesArr[0],
            'min1Ahead': anglesArr[1],
            'max2Ahead': anglesArr[2],
            'min2Ahead': anglesArr[3]
        })
        del anglesArr
        return angles

    def ops_detect(self, loc):
        """
        location location of points
        intersection_lineLength: on the other hand, allows it to change automatically
        when we change it from the config file to specify the line length here.
        Args:
            loc: calculated coordinates

        Returns:

        """
        ops = []
        for i in range(0, len(loc), 3):
            ops.append(Distance.destination_point(lat=loc[i], lon=loc[i + 1], distance=self.intersection_lineLength,
                                                  bearing=loc[i + 2]))

        return ops[0], ops[1]

    @staticmethod
    def check_line_intersection(**kwargs) -> Dict:
        """
        Calculate from two points intersected locations

        Args:
            **kwargs:
            -> line1StartX
            -> line1StartY
            -> line1EndX
            -> line1EndY
            -> line2StartX
            -> line2StartY
            -> line2EndX
            -> line2EndY

        Returns:

        """

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
            line2StartX, line2StartY = intersection_float_to_decimal(line1StartX, line1StartY,
                                                                     line2StartX, line2StartY)
        if isinstance(line1EndX, float):
            line1EndX, line1EndY, \
            line2EndX, line2EndY = intersection_float_to_decimal(line1EndX, line1EndY,
                                                                 line2EndX, line2EndY)

        posit1 = ((line2EndY - line2StartY) * (line1EndX - line1StartX))
        posit2 = ((line2EndX - line2StartX) * (line1EndY - line1StartY))
        denominator = posit1 - posit2

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

    def intersection_points_average(self, groupMatches: list, geojsonFormatFunc: Callable) -> Tuple[
        Dict, list, list, List[list]]:
        """

        Args:
            groupMatches: matched objects same class, same points
            geojsonFormatFunc: it's function for creating geojson format

        Returns:
            It calculates a single point by taking the averages of all the detected intersections.
        """
        total = Dict({
            'isValid': False
        })
        pointsMerged = []
        mathed_object_id = []
        matched_paired = []
        objects = collections.defaultdict(list)
        i = 0
        confidence = 0
        for matches in groupMatches:
            i += 2
            k = Dict(matches)
            objects['Lat_center'].append((k.intersectCenter['x']))
            objects['Lon_center'].append((k.intersectCenter['y']))

            objects['Lat_cornerA'].append((k.intersectCornerA['x']))
            objects['Lon_cornerA'].append((k.intersectCornerA['y']))

            objects['Lat_cornerB'].append((k.intersectCornerB['x']))
            objects['Lon_cornerB'].append((k.intersectCornerB['y']))

            objects['Lat_cornerC'].append((k.intersectCornerC['x']))
            objects['Lon_cornerC'].append((k.intersectCornerC['y']))

            objects['avg_score'].append(float(k.score_1))
            objects['avg_score'].append(float(k.score_2))

            total['detectedPath_1'] = k.detectedPath_1
            total['detectedPath_2'] = k.detectedPath_2

            total['imgUrl_1'] = k.imgUrl_1
            total['imgUrl_2'] = k.imgUrl_2

            total['objId_1'] = k.objId_1
            total['objId_2'] = k.objId_2
            total['match_id'] = k.match

            total['classname'] = k.classname_1  # doesn't matter same classname_1 and classname_2

            # creating geo json format according to paired points
            geojsonParams = geojsonFormatFunc(k, type="Point")

            pointsMerged.append(geojsonParams)
            confidence = self.apply_confidence_rule(i)

            total['isValid'] = i > 0

            # added because of visualization matched paired objects
            mathed_object_id.append(k.objId_1)
            mathed_object_id.append(k.objId_2)
            matched_paired.append([k.intersectCenter['x'],
                                   k.intersectCenter['y']])

        for k, v in objects.items():
            total[k] = float(sum(v) / len(v))

        total['confidence'] = (total['avg_score'] + confidence) * 0.5
        del objects

        return total, pointsMerged, mathed_object_id, matched_paired

    def intersection_points_find(self, **kwargs):
        """
        from two points calculate intersection
        Args:
            **kwargs:
            -> start_lat1
            -> start_lon1
            -> theta1
            -> start_lat2
            -> start_lon2
            -> theta2
            -> type : intersect or area

        Returns:
            get coordinates
        """
        points = Dict(kwargs)

        if points.type == "intersect":
            ops1, ops2 = self.ops_detect(loc=[points.start_lat1, points.start_lon1, points.theta1,
                                              points.start_lat2, points.start_lon2, points.theta2])

            destinationPoint1 = [(points.start_lat1, points.start_lon1),
                                 (ops1["lat"], ops1["lon"])]

            destinationPoint2 = [(points.start_lat2, points.start_lon2),
                                 (ops2["lat"], ops2["lon"])]

            interSection = self.check_line_intersection(line1StartX=points.start_lat1,
                                                        line1StartY=points.start_lon1,
                                                        line1EndX=ops1["lat"],
                                                        line1EndY=ops1["lon"],

                                                        line2StartX=points.start_lat2,
                                                        line2StartY=points.start_lon2,
                                                        line2EndX=ops2["lat"],
                                                        line2EndY=ops2["lon"])

            return interSection, destinationPoint1, destinationPoint2

        if points.type == "area":
            corners = []
            for first, second in zip(points.theta1, points.theta2):
                ops1, ops2 = self.ops_detect(loc=[points.start_lat1, points.start_lon1, first,
                                                  points.start_lat2, points.start_lon2, second])

                interSection = self.check_line_intersection(line1StartX=points.start_lat1,
                                                            line1StartY=points.start_lon1,
                                                            line1EndX=ops1["lat"],
                                                            line1EndY=ops1["lon"],

                                                            line2StartX=points.start_lat2,
                                                            line2StartY=points.start_lon2,
                                                            line2EndX=ops2["lat"],
                                                            line2EndY=ops2["lon"])
                corners.append(interSection)

            return corners



def intersection_float_to_decimal(lat1, lon1, lat2, lon2) -> Tuple:
    """

    Args:
        lat1:
        lon1:
        lat2:
        lon2:

    Returns:
        points convert decimal format
    """

    lat1 = Convertor.decimal_fix(lat1)
    lon1 = Convertor.decimal_fix(lon1)
    lat2 = Convertor.decimal_fix(lat2)
    lon2 = Convertor.decimal_fix(lon2)

    return lat1, lon1, lat2, lon2