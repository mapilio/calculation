import numpy as np
import cv2
from helper.convertor import Convertor

class ImageTransformer(object):
    """ Perspective transformation class for image
        with shape (height, width, #channels) """

    def __init__(self, image):
        self.image = image

        self.height = self.image.shape[0]
        self.width = self.image.shape[1]
        self.num_channels = self.image.shape[2]

    """ Wrapper of Rotating a Image """

    def rotate_along_axis(self, pitch,roll=0, yaw=0, dx=0, dy=0, dz=1):
        # Get radius of rotation along 3 axes
        # roll : x-axis
        # pitch : y-axis
        # yaw : z-axis
        cc = Convertor()
        rpitch, rroll, ryaw = cc.get_rad(pitch, roll, yaw=0)

        # Get ideal focal length on z axis
        # NOTE: Change this section to other axis if needed
        d = np.sqrt(self.height ** 2 + self.width ** 2)
        self.focal = d / (2 * np.sin(yaw) if np.sin(yaw) != 0 else 1)
        dz = self.focal

        # Get projection matrix
        mat = self.get_M(rroll, rpitch, ryaw, dx, dy, dz)

        return cv2.warpPerspective(self.image.copy(), mat, (self.width, self.height))

    """ Get Perspective Projection Matrix """

    def get_M(self, roll, pitch, yaw, dx, dy, dz):
        w = self.width
        h = self.height
        f = self.focal

        # Projection 2D -> 3D matrix
        A1 = np.array([[1, 0, -w / 2],
                       [0, 1, -h / 2],
                       [0, 0, 1],
                       [0, 0, 1]])

        # Rotation matrices around the X, Y, and Z axis
        RX = np.array([[1, 0, 0, 0],
                       [0, np.cos(roll), -np.sin(roll), 0],
                       [0, np.sin(roll), np.cos(roll), 0],
                       [0, 0, 0, 1]])

        RY = np.array([[np.cos(pitch), 0, -np.sin(pitch), 0],
                       [0, 1, 0, 0],
                       [np.sin(pitch), 0, np.cos(pitch), 0],
                       [0, 0, 0, 1]])

        RZ = np.array([[np.cos(yaw), -np.sin(yaw), 0, 0],
                       [np.sin(yaw), np.cos(yaw), 0, 0],
                       [0, 0, 1, 0],
                       [0, 0, 0, 1]])

        # Composed rotation matrix with (RX, RY, RZ)
        R = np.dot(np.dot(RX, RY), RZ)
        # dz = (f - 0) / 1 ** 2

        # Translation matrix
        T = np.array([[1, 0, 0, dx],
                      [0, 1, 0, dy],
                      [0, 0, 1, dz],
                      [0, 0, 0, 1]])

        # Projection 3D -> 2D matrix
        A2 = np.array([[f, 0, w / 2, 0],
                       [0, f, h / 2, 0],
                       [0, 0, 1, 0]])

        # Final transformation matrix
        return np.dot(A2, np.dot(T, np.dot(R, A1)))
