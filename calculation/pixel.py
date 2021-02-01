"""
Refers as pixCalc
"""
import numpy
from decimal import *

class Pixel:

    # @property
    def decimalFix(self, number):
        getcontext().rounding = ROUND_DOWN
        return Decimal(number).quantize(Decimal(10) ** -9)

    @staticmethod
    def calcOrigin(y0, x0, box, height=0, width=0, horizon=0, lefBegin=0, rightBegin=0):
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
    def tileImageCalc(cropImage, numrows, numcols):
        tileHeight = int(cropImage.shape[0] / numrows)
        tileWidth = int(cropImage.shape[1] / numcols)
        return tileHeight, tileWidth

    @staticmethod
    def AverageBboxCoord(bbox_coords1, bbox_coords2):
        result = []
        [result.append((a + b) / 2) for a, b in zip(bbox_coords1, bbox_coords2)]
        return result