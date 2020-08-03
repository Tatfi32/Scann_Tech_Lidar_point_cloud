import numpy as np
import pandas as pd
import cv2
import time


__all__ = ['Projector']

"""
class: Projector
Responsibility: projects lidar point cloud to camera physical space
! Projection to matrix is in class Camera and not here
You can look up coordinate system in VLP-16 lidar user documentation
"""
class Timer:
    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start


class Projector:
    def __init__(self, camera_position=[-0.75, 0, 0]):
        # lidar position in cam coord
        self.camera_position = camera_position
        pi = np.pi
        self.angles = [-pi/2, 0, pi]
        """
        alpha: angle for roll matrix
        betta: angle for pitch matrix
        gamma: angle for yaw matrix
        """

        alpha = self.angles[0]
        betta = self.angles[1]
        gamma = self.angles[2]

        roll = [[1, 0, 0],
                [0, np.cos(alpha), -np.sin(alpha)],
                [0, np.sin(alpha), np.cos(alpha)]
                ]

        pitch = [[np.cos(betta), 0, np.sin(betta)],
                 [0, 1, 0],
                 [-np.sin(betta), 0, np.cos(betta)]
                 ]

        yaw = [[np.cos(gamma), -np.sin(gamma), 0],
               [np.sin(gamma), np.cos(gamma), 0],
               [0, 0, 1]
               ]
        # Rotation matrix
        self.r_matrix = np.dot(roll, np.dot(pitch, yaw))

    def translate(self, lidar_point):
        translated_point = [lidar_point[0] - self.camera_position[0],
                            lidar_point[1] - self.camera_position[1],
                            lidar_point[2] - self.camera_position[2]
                            ]

        return translated_point

    def rotate(self, lidar_point):
        """
        Args:
            lidar_point: points in lidar coordinates to be rotated to camera system

        Returns:
            rotated to camera system lidar point
        """
        rotated_point = np.dot(self.r_matrix, lidar_point)
        return rotated_point

    def project_point(self, lidar_point):
        """
        Args:
            lidar_point: point coordinates in lidar system

        Returns:
            projected to camera matrix point coordinates

        """

        point = self.translate(lidar_point)
        point = self.rotate(point)
        return point
    # Performs project_point for each row in a dataFrame
    # data is a pandas.DataFrame
    def project(self, data):
        with Timer() as t:
            coord = data[['X', 'Y', 'Z']].to_numpy()
        print('project finished in %.03f s' % t.interval)

        with Timer() as t:
            for i in range(len(coord)):
                coord[i, :] = self.project_point(coord[i, :])
        print('iterator finished in %.03f s' % t.interval)

        return pd.DataFrame(coord, columns=['X', 'Y', 'Z'])







