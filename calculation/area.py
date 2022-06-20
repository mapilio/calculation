import math


class Area:

    # Deprecated
    @staticmethod
    def area_measurement(interSection_A_lat, interSection_A_lon,
                         interSection_B_lat, interSection_B_lon,
                         interSection_C_lat, interSection_C_lon):
        pass

    @staticmethod
    def calc_area_heron(a: float, b: float, c: float) -> float:
        """
             A _______ B
            |    X    |
            D _______ C

        Args:
            a: triangle edge ABC
            b: triangle edge BCD
            c: triangle edge CAD

        Returns:
            area float
        """

        s = (a + b + c) / 2
        return math.sqrt(abs(s * (s - a) * (s - b) * (s - c)))