import math
from typing import Callable, Tuple, List

from calculation.distance import Distance
from calculation.utilities import Convertor

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
        for (theta, max_theta, min_theta) in frameFilters:

            theta_norm = (360 + theta) % 360
            # If max_theta is smaller than min_theta, unnormalize theta_norm and max_theta, it provides to use formula.
            if max_theta < min_theta:
                result = (max_theta + 360) >= (theta_norm + 360) >= min_theta
            else:
                result = max_theta >= theta_norm >= min_theta
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
            min_theta = n - a / 2
            max_theta = n + a / 2
            min_theta_norm = (min_theta + 360) % 360
            max_theta_norm = (max_theta + 360) % 360
            # x, y hands of angle
            ret.append([min_theta_norm, max_theta_norm])

        anglesArr = [item for sublist in ret for item in sublist]
        assert len(anglesArr) >= 4, "Check your Thetas"
        angles = Dict({
            'min1Ahead': anglesArr[0],
            'max1Ahead': anglesArr[1],
            'min2Ahead': anglesArr[2],
            'max2Ahead': anglesArr[3],
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
                                                  theta=loc[i + 2]))
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
            "x": 0,
            "y": 0,
            "z": 0,
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
        pointsMerged, matched_object_id, matched_paired = [], [], []

        objects = collections.defaultdict(list)
        i = 0
        confidence = 0
        for matches in groupMatches:
            i += 2
            matches = Dict(matches)
            objects['Lat_center'].append((matches.intersectCenter['x']))
            objects['Lon_center'].append((matches.intersectCenter['y']))
            objects['Alt_center'].append((matches.intersectCenter['z']))

            objects['Lat_cornerA'].append((matches.intersectCornerA['x']))
            objects['Lon_cornerA'].append((matches.intersectCornerA['y']))
            objects['Alt_cornerA'].append((matches.intersectCornerA['z']))

            objects['Lat_cornerB'].append((matches.intersectCornerB['x']))
            objects['Lon_cornerB'].append((matches.intersectCornerB['y']))
            objects['Alt_cornerB'].append((matches.intersectCornerB['z']))

            objects['Lat_cornerC'].append((matches.intersectCornerC['x']))
            objects['Lon_cornerC'].append((matches.intersectCornerC['y']))
            objects['Alt_cornerC'].append((matches.intersectCornerC['z']))

            objects['Lat_cornerD'].append((matches.intersectCornerD['x']))
            objects['Lon_cornerD'].append((matches.intersectCornerD['y']))
            objects['Alt_cornerD'].append((matches.intersectCornerD['z']))

            objects['avg_score'].append(float(matches.score_1))
            objects['avg_score'].append(float(matches.score_2))

            total[i]['detectedPath_1'] = matches.detectedPath_1
            total[i]['detectedPath_2'] = matches.detectedPath_2

            total[i]['imgUrl_1'] = matches.imgUrl_1
            total[i]['imgUrl_2'] = matches.imgUrl_2

            total[i]['objId_1'] = matches.objId_1
            total[i]['objId_2'] = matches.objId_2
            total['match_id'] = matches.match

            total['classname'] = matches.classname_1  # doesn't matter same classname_1 and classname_2

            total['feature'] = matches.feature_1 or matches.feature_2

            # creating geo json format according to paired points
            geojsonParams = geojsonFormatFunc(matches, type="Point")

            pointsMerged.append(geojsonParams)
            confidence = self.apply_confidence_rule(i)

            total['isValid'] = i > 0

            # added because of visualization matched paired objects
            matched_object_id.append(matches.objId_1)
            matched_object_id.append(matches.objId_2)
            matched_paired.append([matches.intersectCenter['x'],
                                   matches.intersectCenter['y']])

        for k, v in objects.items():
            counter = 0
            for c in v:
                if c == 0:
                    counter += 1
            if counter == len(v):
                counter = 0
            if k in ["Alt_cornerB", "Alt_cornerC", "Alt_cornerD", "Alt_cornerA"]:
                total[k] = float(sum(v) / (len(v) - counter))
            else:
                total[k] = float(sum(v) / len(v))

        total['confidence'] = (total['avg_score'] + confidence) * 0.5
        del objects
        return total, pointsMerged, matched_object_id, matched_paired

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
            if interSection['l1'] and interSection['l2']:
                interSection['z'] = self.calc_intersect_z(points.start_lon1, points.start_lat1, points.start_alt1,
                                                          points.phi1,
                                                          points.start_lon2, points.start_lat2, points.start_alt2,
                                                          points.phi2,
                                                          interSection)

            return interSection, destinationPoint1, destinationPoint2

        if points.type == "area":
            corners = {}
            for th1, th2, ph1, ph2, corner_id in zip(points.theta1, points.theta2,
                                                     points.phi1, points.phi2,
                                                     points.corners_id):
                ops1, ops2 = self.ops_detect(loc=[points.start_lat1, points.start_lon1, th1,
                                                  points.start_lat2, points.start_lon2, th2])

                is_intersect = self.check_line_intersection(line1StartX=points.start_lat1,
                                                            line1StartY=points.start_lon1,
                                                            line1EndX=ops1["lat"],
                                                            line1EndY=ops1["lon"],

                                                            line2StartX=points.start_lat2,
                                                            line2StartY=points.start_lon2,
                                                            line2EndX=ops2["lat"],
                                                            line2EndY=ops2["lon"]
                                                            )
                if is_intersect['l1'] and is_intersect['l2']:
                    is_intersect['z'] = self.calc_intersect_z(points.start_lon1, points.start_lat1, points.start_alt1,
                                                              ph1,
                                                              points.start_lon2, points.start_lat2, points.start_alt2,
                                                              ph2,
                                                              is_intersect)

                corners[corner_id] = is_intersect
            return corners

    def calc_intersect_z(self, start_lon1, start_lat1, start_alt1, phi1,
                         start_lon2, start_lat2, start_alt2, phi2,
                         is_intersect
                         ):

        distance_between_panoroma_first_and_intersected_point = Distance.haversine(
            lon1=start_lon1, lat1=start_lat1,
            lon2=is_intersect['y'], lat2=is_intersect['x'])
        # it changes cos range as 0-90 and altitude always increases according this formula
        # ph1 = 180 - ph1 if ph1 > 90 else ph1
        # ph2 = 180 - ph2 if ph2 > 90 else ph2

        # https://mathinsight.org/spherical_coordinates
        center_altA = (math.cos(
            math.radians(phi1)) * distance_between_panoroma_first_and_intersected_point +
                       float(start_alt1))

        distance_between_panoroma_second_and_intersected_point = Distance.haversine(
            lon1=start_lon2, lat1=start_lat2,
            lon2=is_intersect['y'], lat2=is_intersect['x'])

        center_altB = (math.cos(
            math.radians(phi2)) * distance_between_panoroma_second_and_intersected_point +
                       float(start_alt2))

        return (center_altA + center_altB) / 2


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