import numpy as np
import pandas as pd

__all__ = ['Camera']

"""
class: Camera
Responsibility: projects points from physical space to camera matrix (to photo image if you want)
! Coordinate system is assumed to be in the optical center
"""

class Camera:
    def __init__(self, image_path=None,
                 constraints={'x_min': -1920 / 2, 'x_max': 1920 / 2, 'y_min': -1080 / 2, 'y_max': 1080 / 2}):
        self.image_path = image_path
        # Limits matrix size counting from optical center
        self.constraints = constraints

        # K is a diagonal matrix, so coordinates begin in the center of the camera matrix
        # "-1" is a fundamental constant
        self.K = [[-1390, 0, 0],
                  [0, -1390, 0],
                  [0, 0, 1]
                  ]
        if np.count_nonzero(self.K - np.diag(np.diagonal(self.K))) != 0:
            print('Matrix K is supposed to be diagonal!')
            raise ValueError

    # Projects one point from physical space to camera matrix
    # Returns pixel
    def project_point(self, point):
        """
        Args:
            point: point in camera coordinates system to be projected on camera matrix

        Returns:
            coordinates of projected to matrix point (pixel)
        """
        if type(point) != np.ndarray:
            point = np.array(point)
        if point[2] != 0:
            point[0] /= point[2]
            point[1] /= point[2]
            pixel = np.dot(self.K, point)
            if (self.constraints['x_min'] <= pixel[0] <= self.constraints['x_max'] and
                    self.constraints['y_min'] <= pixel[1] <= self.constraints['y_max']):
                pixel[0] = np.round(pixel[0], 0)
                pixel[1] = np.round(pixel[1], 0)
                # Distance is not rounded to 0 digits
                pixel[2] = np.round(pixel[2], 4)
                return pixel
        return None

    # Performs project_point for each row in a dataFrame
    # data is a pandas.DataFrame
    def project(self, data):
        coord = data[['X', 'Y', 'Z']].to_numpy()

        for i in range(len(coord)):
            coord[i, :] = self.project_point(coord[i, :])

        return pd.DataFrame(coord, columns=['u', 'v', 'Z']).dropna()

    # Convenience method to look up camera angles
    def angles(self):
        print('x_max/z: ', self.x_max / self.K[0][0])
        print('y_max/z: ', self.y_max / self.K[1][1])
