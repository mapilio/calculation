import math

def get_aspect_ratio(width: int, height: int):

    """
    Calculates the aspect ratio from given width and height.

    Args:
         width (int): width in pixels
         height (int): height in pixels

    Returns:
         Calculated aspect ratio.

    """

    aspect_ratio = width / height if width > height else height / width

    return aspect_ratio


def calculate_vfov(fov: float, width: int, height: int):

    """
    Calculates vfov from given width, height and hvof.

    Args:
        hfov (float): horizontal fov in degrees
        width (int): width in pixels
        height (int): height in pixels

    Returns:
        Calculated vertical fov in degrees.

    """
    hfov = math.radians(fov)
    vfov = 2 * math.atan(
        math.tan(hfov / 2) / get_aspect_ratio(width, height))
    vfov = math.degrees(vfov)

    return vfov
