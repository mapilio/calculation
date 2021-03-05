"""
Refers as pixCalc
"""
import numpy


class Pixel:

    @staticmethod
    def calc_origin(y0, x0, box, height=0, width=0, horizon=0, lefBegin=0, rightBegin=0):
        if len(box) == 4:
            ymin = horizon + y0 + int(round(box[1] * height))
            xmin = x0 + int(round(box[0] * width + lefBegin))
            ymax = horizon + y0 + int(round(box[3] * height))
            xmax = x0 + int(round(box[2] * width + rightBegin))
            return [xmin, ymin, xmax, ymax]
        elif len(box) == 2:
            ymin = horizon + y0 + int(round(box[1] * height))
            xmin = x0 + int(round(box[0] * width + lefBegin))
            return [xmin, ymin]
        else:
            if len(box):
                try:
                    segmentation = []
                    for index in range(0, len(box) - 1, 2):
                        segmentation.append([x0 + int(round(box[index] * width + lefBegin)),
                                             horizon + y0 + int(round(box[index + 1] * height))
                                             ])
                    contours = [numpy.array(segmentation
                                            , dtype=numpy.int32)]
                except:
                    raise ValueError("Check out box size")

            return contours

    @staticmethod
    def calc_image_tile(cropImage, numRows, numCols):
        tileHeight = int(cropImage.shape[0] / numRows)
        tileWidth = int(cropImage.shape[1] / numCols)
        return tileHeight, tileWidth

    @staticmethod
    def calc_average_bbox_coord(bbox_coords1, bbox_coords2):
        result = []
        [result.append((a + b) / 2) for a, b in zip(bbox_coords1, bbox_coords2)]
        return result

    @staticmethod
    def calc_bb_intersection_over_union(boxA, boxB):
        """
        :return: the intersection over union value
        """
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

        # TODO threshold will be dynamic
        if iou > 0.4:
            return True
        else:
            return False
