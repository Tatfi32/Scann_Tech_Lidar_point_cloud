import matplotlib.pyplot as plt
from PIL import Image, ImageOps
import pickle
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
from scipy import misc

__all__ = ['Visualizator']


class Visualizator:

    def __init__(self, output_path, df):
        self.df = df
        self.output_path = output_path

    # plot 3D scatter based on certain  X,Y,Z,Depth values

    def plot_scatter_one_seq(self, ):
        fig = plt.figure()
        """
        ax_1 = fig.add_subplot(131, projection='3d')
        pnt3d_1 = ax_1.scatter(x, y, z, c=depth, cmap=plt.cm.BuPu_r)
        ax_1.set_xlabel('x Label')
        ax_1.set_ylabel('y Label')
        ax_1.set_zlabel('Z Label')
        cbar_1 = plt.colorbar(pnt3d_1)

        ax_3 = fig.add_subplot(133, projection='3d')
        pnt3d_3 = ax_3.scatter(z, x, y, c=depth, cmap=plt.cm.BuPu_r)
        cbar_3 = plt.colorbar(pnt3d_3)
        ax_3.set_xlabel('Z Label')
        ax_3.set_ylabel('x Label')
        ax_3.set_zlabel('y Label')
        """

        ax_2 = fig.add_subplot(111, projection='3d')

        pnt3d_2 = ax_2.scatter(self.df.Y, self.df.Z, self.df.X, c=self.df.D, cmap=plt.cm.BuPu_r)
        cbar_2 = plt.colorbar(pnt3d_2)
        ax_2.set_xlabel('y Label')
        ax_2.set_ylabel('Z Label')
        ax_2.set_zlabel('x Label')

        path = str(self.output_path / 'sequence_3D_points.png')
        fig.savefig(path, dpi=100)
        #plt.show()

    def plot_seq_points(self, df):
        fig = plt.figure()
        ax = plt.axes(projection='3d')

        categories = np.unique(df['seq_number'])
        colors = np.linspace(0, 1, len(categories))
        colordict = dict(zip(categories, colors))

        df["Color"] = df['seq_number'].apply(lambda x: colordict[x])
        sc = ax.scatter3D(df.v, df.u, df.Z, c=df.Color)
        colorize = plt.colorbar(sc, orientation="horizontal")
        colorize.set_label("Sequence number")

        ax.set_title('Sequence surface plot')
        ax.set_xlabel('v Label')
        ax.set_ylabel('u Label')
        ax.set_zlabel('Z Label')

        path = str(self.output_path / 'sequence_points.png')
        fig.savefig(path, dpi=100)
        plt.show()

    def plot_picture(self, image_path):
        fig, ax = plt.subplots(figsize=(20, 10), dpi=60)
        img = Image.open(image_path)
        width, height = img.size

        left = width / 2 + self.df.u.min()  # 252
        upper = height / 2 - self.df.v.max()  # 350
        right = width / 2 + self.df.u.max()  # 1252
        lower = height / 2 - self.df.v.min()  # 950

        im = img.crop((left, upper, right, lower))
        plt.imshow(im, extent=[self.df.u.min(), self.df.u.max(), self.df.v.min(), self.df.v.max()], zorder=0,
                   aspect='auto')
        sc = plt.scatter(self.df.u, self.df.v, c=self.df.Z, zorder=1, s=10)
        colorize = plt.colorbar(sc, orientation="horizontal")
        colorize.set_label("Distance (m)")

        path = str(self.output_path / 'points_on_image.png')
        fig.savefig(path)
        plt.show()

    # not used class functions
    """
    #Plot 3D scatter from Visualizator.class dataframe       
    def plot_points(self, ):
        fig = plt.figure()
        ax = plt.axes(projection='3d')
        ax.scatter3D(self.df.v, self.df.u, self.df.Z, cmap="Purples")

        ax.set_title('Surface plot')
        ax.set_xlabel('v Label')
        ax.set_ylabel('u Label')
        ax.set_zlabel('Z Label')

        path = str(self.output_path / 'points.png')
        fig.savefig(path, dpi=100)
        plt.show()

    """
