import cv2
import numpy as np
import os
from os.path import isfile, join
ROOT = os.path.abspath(os.getcwd())
pathIn= os.path.join(ROOT, 'ML_model', 'data', 'frames')
pathOut = os.path.join(ROOT, 'ML_model', 'data', 'my_video2.mp4')

video = cv2.VideoCapture(pathOut)
duration = video.get(cv2.CAP_PROP_POS_MSEC)
frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
print(duration, frame_count)