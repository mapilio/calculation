import unittest

from calculation.distance import Distance

distance = Distance()

class TestSimple(unittest.TestCase):

    def testCheckValidity(self):

        print(distance.checkValidity(5,6,7))


if __name__ == '__main__':
    unittest.main()