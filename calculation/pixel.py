"""
Refers as pixCalc
"""
from typing import Tuple

import numpy as np
import cv2
from scipy.spatial import distance


class Pixel:

    @staticmethod
    def calc_origin(y0, x0, box, height=0, width=0, horizon=0, lefBegin=0, rightBegin=0):
        """
            basically it does the process of converting prediction from pictures taken as tile to
            pixel coordinates on panoramic images.
        Args:
            y0: tiled panoramic image column number
            x0: tiled panoramic image row number
            box: tiled image detected object bounding box
            height:
            width:
            horizon:
            lefBegin:
            rightBegin:

        Returns:

        """
        if len(box) == 4:
            xmin = x0 + int(round(box[0] * width + lefBegin))
            ymin = horizon + y0 + int(round(box[1] * height))
            xmax = x0 + int(round(box[2] * width + rightBegin))
            ymax = horizon + y0 + int(round(box[3] * height))
            return [xmin, ymin, xmax, ymax]
        elif len(box) == 2:
            coordx = x0 + int(round(box[0] * width + lefBegin))
            coordy = horizon + y0 + int(round(box[1] * height))
            return [coordx, coordy]

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

    @staticmethod
    def get_angle_pca(detectedObject: np.ndarray) -> float:
        # extract the PCA from segmentation object

        img_gray = cv2.cvtColor(detectedObject, cv2.IMREAD_GRAYSCALE)  # convert to grayscale
        # _, thresh = cv2.threshold(img_gray, 255, 1, cv2.THRESH_BINARY_INV)
        imag_arr = np.array(img_gray)
        mat = np.argwhere(imag_arr == 255)
        mat[:, [0, 1]] = mat[:, [1, 0]]
        mat = np.array(mat).astype(np.float32)  # have to convert type for PCA
        m, e = cv2.PCACompute(mat, mean=np.array([]))

        center = tuple(m[0])
        center = (int(center[0]), int(center[1]))

        # endpoint1 = tuple(m[0] + e[0] * 100)
        # endpoint1 = (int(endpoint1[0]), int(endpoint1[1]))

        endpoint2 = tuple(m[0] + e[1] * 50)
        endpoint2 = (int(endpoint2[0]), int(endpoint2[1]))

        x = center
        y = (center[0], center[1] + 50)
        z = endpoint2

        b = distance.euclidean(x, y)
        c = distance.euclidean(x, z)
        a = distance.euclidean(y, z)
        cos_alpha = (b * b + c * c - a * a) / (2 * b * c)
        pca_angle = float(np.degrees(np.arccos(cos_alpha)))

        return pca_angle

    @staticmethod
    def calc_image_scale_limiter(detect_bbox1: list, detect_bbox2: list) -> bool:
        """
        This function check bbox scale ratio between two bbox
        """
        # print(f"First Bbox = {detect_bbox1}")
        # print(f"Second Bbox = {detect_bbox2}")

        first_w, first_h = detect_bbox1[2] - detect_bbox1[0], detect_bbox1[3] - detect_bbox1[1]
        second_w, second_h = detect_bbox2[2] - detect_bbox2[0], detect_bbox2[3] - detect_bbox2[1]

        if any(x < 0 for x in [first_w, first_h, second_w, second_h]):
            raise Exception("Check detected Bbox ")

        # half_scale_w, half_scale_h = first_w * 0.75, first_h * 0.75
        # double_scale_w, double_scale_h = first_w * 2.0, first_h * 2.0
        w_rate = first_w / second_w if first_w > second_w else second_w / first_w
        h_rate = first_h / second_h if first_h > second_h else second_h / first_h

        # eğer bbox width'i büyümüş ise height büyümesi beklenir ve bunlar maximum 2 katı oranında
        return True if 1 <= w_rate <= 2 and 1 <= h_rate <= 2 else False

    @staticmethod
    def check_bbox_size(box, cfg):
        """
        it's check bbox size from taken config params
        Args:
            box: detected objects bounding box
            cfg: criterion such as bboxHeight, bboxWidth

        Returns:

        """
        xmin, ymin, xmax, ymax = list(map(int, box))
        # print("Y Distances = ",np.abs(ymax-ymin),
        #       "X Distances = ", np.abs(xmax-xmin))
        if np.abs(ymax - ymin) < cfg.boundingBoxMinHeight \
                or np.abs(
            xmax - xmin) < cfg.boundingBoxMinWidth:  # these variables limited detected box in panoramic that only get this section.
            return False
        return True

    @staticmethod
    def calc_predict_tile(row: int, col: int, tileHeight: int, tileWidth: int, intersection_size: int,
                          height: int, width: int) -> Tuple:

        y0 = row * tileHeight
        y1 = y0 + tileHeight
        x0 = (col * tileWidth)
        x1 = x0 + tileWidth

        y1 = y1 + intersection_size
        x1 = x1 + intersection_size

        if row == 0 and col == 0:
            y0 = 0
            x0 = 0
            y1 = (y0 + tileHeight) + intersection_size
            x1 = (x0 + tileWidth) + intersection_size

        if y1 > height:
            y1 = height
            y0 = y0 - intersection_size

        if x1 > width:
            x1 = width
            x0 = x0 - intersection_size

        if x0 < 0:
            x0 = 0
        if y0 < 0:
            y0 = 0

        return x0, x1, y0, y1
