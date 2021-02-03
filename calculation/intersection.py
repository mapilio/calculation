from calculation.distance import Distance


class Intersection:

    def __init__(self, intersection_lineLength, angle_wide):
        self.intersection_lineLength = intersection_lineLength
        self.intersection_angle_wide = angle_wide

    @staticmethod
    def ruleSet(c):
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

    def calcBetw(self, n):
        # n = heading
        # a = angle
        a = self.intersection_angle_wide
        t = 360 + n
        x = (-(a - t)) % 360
        y = (a + t) % 360
        # x, y hands of angle
        return x, y

    def opsDetect(self, location):
        # location noktaların bulunduğu konum
        # config ise burada line uzunluğunu belirtmek için, config dosyasından değiştirdiğimizde otomatik değişmesini sağlıyor.
        ops = []
        for i in range(0, len(location), 3):
            ops.append(Distance.destinationPoint(location[i], location[i + 1], self.intersection_lineLength,
                                                 location[i + 2]))

        return ops[0], ops[1]

    def checkLineIntersection(self, line1StartX, line1StartY, line1EndX, line1EndY, line2StartX, line2StartY, line2EndX,
                              line2EndY):
        result = {
            "x": "null",
            "y": "null",
            "l1": False,
            "l2": False,
        }

        denominator = ((line2EndY - line2StartY) * (line1EndX - line1StartX)) - (
                (line2EndX - line2StartX) * (line1EndY - line1StartY))
        if (denominator == 0):
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

        if (a > 0 and a < 1):
            result["l1"] = True

        if (b > 0 and b < 1):
            result["l2"] = True

        return result

    @classmethod
    def intersectionAverage(self, AveragePoint):
        averagePoint = []
        for keys, values in AveragePoint.items():
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
            confidence = self.ruleSet(c)

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
            averagePoint.append(total)

        return averagePoint

    @classmethod
    def bb_intersection_over_union(self, boxA, boxB):
        # determine the (x, y)-coordinates of the intersection rectangle
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])
        # compute the area of intersection rectangle
        interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
        # compute the area of both the prediction and ground-truth
        # rectangles
        boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
        boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
        # compute the intersection over union by taking the intersection
        # area and dividing it by the sum of prediction + ground-truth
        # areas - the interesection area
        iou = interArea / float(boxAArea + boxBArea - interArea)
        # print(iou, "iou")
        # exit(1)
        if iou > 0.4:
            return True
        else:
            return False
        # return the intersection over union value

    def IntersectionPointsFind(self, start_lat1, start_lon1, theta1, start_lat2, start_lon2, theta2):
        ops1, ops2 = self.opsDetect([start_lat1, start_lon1, theta1,
                                     start_lat2, start_lon2, theta2],
                                    )

        # intSection1Lat, intSection1Lon, intSection2Lat, intSection2Lon = interSections(ops1["lat"],    ops1["lon"],
        #                                                                                  ops2["lat"],
        #                                                                                  ops2["lon"])

        destinationPoint1 = [(start_lat1, start_lon1),
                             (ops1["lat"], ops1["lon"])]

        destinationPoint2 = [(start_lat2, start_lon2),
                             (ops2["lat"], ops2["lon"])]

        interSection = self.checkLineIntersection(start_lat1,
                                                  start_lon1,
                                                  ops1["lat"], ops1["lon"],

                                                  start_lat2,
                                                  start_lon2,
                                                  ops2["lat"], ops2["lon"])

        return interSection, destinationPoint1, destinationPoint2
