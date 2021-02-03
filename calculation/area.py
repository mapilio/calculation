from geopy.distance import geodesic

class Area:

    @classmethod
    def calc(self,interSection_A_lat, interSection_A_lon,
                      interSection_B_lat, interSection_B_lon,
                      interSection_C_lat, interSection_C_lon):
        width = geodesic([interSection_A_lat, interSection_A_lon],
                         [interSection_B_lat, interSection_B_lon]).m

        height = geodesic([interSection_C_lat, interSection_C_lon],
                          [interSection_B_lat, interSection_B_lon]).m

        area = height * width

        return width, height, area