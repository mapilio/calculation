import numpy as np
import exifread
from decimal import Decimal, ROUND_DOWN, getcontext


class Generator:
    @staticmethod
    def get_exif_information(img_info):
        """
        :param img_info: exif object
        :return: (lat, lon), orientation, (Height, Width), FocalLength, Altitude,
        """
        information = {}
        data = img_info.extract_exif()
        try:
            information["model"] = data["model"]
            information["coordx"] = data["gps"]["latitude"]
            information["coordy"] = data["gps"]["longitude"]
            information["width"] = data["width"]
            information["height"] = data["height"]

            # Focal Length
            fLen_obj = data["gps"]["FocalLength"]
            fLen_str = f"{fLen_obj}"
            fLen_arr = fLen_str.split("/")
            fLen = float(int(fLen_arr[0]) / int(fLen_arr[1]))
            information["FocalLength"] = fLen

            hor_width = data["height"] if data["orientation"] == 1 else data["width"]
            information["orientation"] = hor_width
            # Angle of View
            aFov = np.arctan(hor_width / (2 * fLen)) * (180 / np.pi)
            information["FoV"] = aFov
        except:
            raise Exception(f"Check the image Exif Data some missing values")

        for k, v in information.items():
            if information[k] is None:
                raise Exception(f"{k} is None")
            else:
                pass

        return information


class Convertor:
    @staticmethod
    def decimal_fix(number):
        getcontext().rounding = ROUND_DOWN
        return Decimal(number).quantize(Decimal(10) ** -20)


class ExifRead:
    '''
    EXIF class for reading exif from an image
    '''

    def __init__(self, filename, details=False):
        '''
        Initialize EXIF object with FILE as filename or fileobj
        '''
        self.filename = filename
        if type(filename) == str:
            with open(filename, 'rb') as fileobj:
                self.tags = exifread.process_file(fileobj, details=details)
        else:
            self.tags = exifread.process_file(filename, details=details)


