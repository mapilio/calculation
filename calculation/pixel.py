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

    @classmethod
    def calcOrigin(self, y0, x0, box, height=0, width=0, horizon=0, lefBegin=0, rightBegin=0):
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

    @classmethod
    def calcThetaBoxCornerPoints(self, final_box, width, heading):
        """
        This function calculates only
        https://drive.google.com/file/d/1t21nDKLbQ1dLuiIBVbuBeL1ubxbXsxoG/view?usp=sharing
        Parameters
        ----------
        final_box
        width
        heading

        Returns
        -------

        """
        # ----start----- Calculate angle in panorma and adding heading -----

        # TODO remove decimalfix, add handler to give an error if data is not decimal
        cX = (final_box[0] + (final_box[2])) / 2.0
        per_deg = width / 360.0
        image_angle = float(cX / per_deg)
        theta = float(heading + self.decimalFix(image_angle - numpy.degrees(numpy.pi))) % 360
        # -----finish----

        cX1 = final_box[0]
        image_angle = float(cX1 / per_deg)
        theta1 = float(heading + self.decimalFix(image_angle - numpy.degrees(numpy.pi))) % 360

        cX2 = final_box[2]
        image_angle = float(cX2 / per_deg)
        theta2 = float(heading + self.decimalFix(image_angle - numpy.degrees(numpy.pi))) % 360

        cX3 = final_box[2] - (final_box[3] - final_box[1])
        image_angle = float(cX3 / per_deg)
        theta3 = float(heading + self.decimalFix(image_angle - numpy.degrees(numpy.pi))) % 360

        return [theta, theta1, theta2, theta3]

    @classmethod
    def tileImageCalc(self, cropImage, numrows, numcols):
        tileHeight = int(cropImage.shape[0] / numrows)
        tileWidth = int(cropImage.shape[1] / numcols)
        return tileHeight, tileWidth

    @classmethod
    def AverageBboxCoord(bbox_coords1, bbox_coords2):
        result = []
        [result.append((a + b) / 2) for a, b in zip(bbox_coords1, bbox_coords2)]
        return result