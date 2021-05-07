import requests
from calculation.distance import Distance
from io import BytesIO
from helper.exif_read import ExifRead
from helper.generator import Generator


class ExifExtractHeading:
    # TODO pointA and pointB operations will be move `helper-mapilio`
    # TODO and these variables will send heading calc function.
    @staticmethod
    def heading_calc(img_urls: list) -> dict:
        processing_format = {}
        objects_zone = []
        for key, x in enumerate(range(0, len(img_urls) - 1, 1)):
            head_url = img_urls[x]['img_url']
            tail_url = img_urls[x + 1]['img_url']
            r_head = requests.get(
                head_url)
            r_tail = requests.get(
                tail_url)
            img1_exifData = ExifRead(BytesIO(r_head.content), details=True)
            img2_exifData = ExifRead(BytesIO(r_tail.content), details=True)
            img_info_1 = Generator.get_exif_information(img1_exifData)
            img_info_2 = Generator.get_exif_information(img2_exifData)
            img_info_1['key'] = key
            img_info_2['key'] = key + 1
            pointA = (img_info_1["coordx"], img_info_1["coordy"])
            pointB = (img_info_2["coordx"], img_info_2["coordy"])
            try:
                heading = Distance.calculate_initial_compass_bearing(pointA,
                                                                     pointB)  # calculate heading from two images
            except ValueError as v:
                raise Exception(f" {v} : Check the image Exif Data some missing values")

            img_info_1['heading'] = heading
            img_info_2['heading'] = heading
            img_info_1['img_url'] = head_url
            img_info_2['img_url'] = tail_url
            objects_zone.append(img_info_1)
            if len(img_urls) - 1 == x + 1:  # if last indices set: previous heading
                objects_zone.append(img_info_2)

        processing_format["zone"] = objects_zone

        return processing_format