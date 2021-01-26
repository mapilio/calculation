import unittest

from calculation.area import Area

area = Area()


class TestSimple(unittest.TestCase):

    def testcalc(self):
        lat1 = 41.10533557420524139222309123
        lon1 = 28.79019722714666874798530411

        lat2 = 41.10533608004852696633352822
        lon2 = 28.79020145244865013810331905

        lat3 = 41.10157400753364043765526407
        lon3 = 28.78824794801683097119125112

        result = area.calc(lat1, lon1, lat2, lon2, lat3, lon3)
        print(result)


if __name__ == '__main__':
    unittest.main()