import cv2
import os
from os.path import exists, isfile, splitext, split, isdir, join
from pathlib import Path

__all__ = ['Parser']

class Parser:
    def __init__(self, path):
        print("Processing video file from",path)
        self.path = path

    def proc_video_file(self, f):
        """
        :param f: video file to be processed
        cut all video files to frames inside created "frames" folder
        """
        cap = cv2.VideoCapture(f)
        #print('Opening video file ', f, '... ', cap.isOpened())
        nFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if (0 < nFrames):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        vfname = split(splitext(f)[0])[-1]
        iframe = 0
        res, i = cap.read()
        while res:
            if (iframe - 0) % 1 == 0:
                dir = str(self.path/ 'frames' )
                cv2.imwrite(dir +'/%s.%06d.bmp' % (vfname, iframe), i)
            res, i = cap.read()
            iframe += 1

    def read(self):
        """"
        read all folder video files and processed each of them with proc_video_file
        """
        videoFName = self.path
        files = [videoFName]
        if isdir(videoFName):
            paths = [join(videoFName, f) for f in os.listdir(videoFName)]
            file = [f for f in paths if is_video_file(f)][0]

        if len(files) > 0:
            dir = str(self.path / 'frames')
            if not exists(dir) or not isdir(dir):
                os.mkdir(dir)

        self.proc_video_file(file)


def is_video_file(path):
    return exists(path) and isfile(path) and splitext(path)[-1] == '.avi'




