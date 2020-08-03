import matplotlib.pyplot as plt
from PIL import Image, ImageOps
import pickle

__all__ = ['Visualizator']

class Visualizator:

    def __init__(self, df):
        self.df = df

    def plot_points(self,output_path):
        fig = plt.figure()
        ax = plt.axes(projection='3d')
        ax.scatter3D(self.df.u, self.df.v, self.df.Z, c=self.df.Z, cmap='Greens')

        ax.set_title('Surface plot')
        ax.set_xlabel('u Label')
        ax.set_ylabel('v Label')
        ax.set_zlabel('Z Label')

        path = str(output_path / 'points.png')
        fig.savefig(path, dpi=100)
        plt.show()



    def plot_picture(self, image_path, output_path):
        fig, ax = plt.subplots(figsize=(20, 10), dpi=60)
        img = Image.open(image_path)
        left = 252
        top = 350
        right = 1252
        bottom = 950

        im = img.crop((left, top, right, bottom))
        plt.imshow(im, extent=[self.df.u.min(), self.df.u.max(), self.df.v.min(), self.df.v.max()], zorder=0,
                   aspect='auto')
        sc = plt.scatter(self.df.u, self.df.v, c=self.df.Z, zorder=1, s=10)
        colorize = plt.colorbar(sc, orientation="horizontal")
        colorize.set_label("Distance (m)")

        path = str(output_path / 'points_on_pic.png')
        fig.savefig(path)

        plt.show()
