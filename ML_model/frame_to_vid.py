import cv2
import numpy as np
import os
from os.path import isfile, join
ROOT = os.path.abspath(os.getcwd())
pathIn= os.path.join(ROOT, 'ML_model', 'data', 'frames')
pathOut = os.path.join(ROOT, 'ML_model', 'data', 'ny5s_test_pyqt.mp4')

video = cv2.VideoCapture(pathOut)
duration = video.get(cv2.CAP_PROP_POS_MSEC)
frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
fps = video.get(cv2.CAP_PROP_FPS)
duration2 = frame_count / fps
print(duration, frame_count, duration2, fps)
