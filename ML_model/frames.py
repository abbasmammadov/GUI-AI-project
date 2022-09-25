import cv2
import os
ROOT_DIR = os.path.abspath(os.curdir) # directory = '/Users/kalebmesfin06/Desktop/VS Code Collections'
# video_path = '/Users/kalebmesfinasfaw/Desktop/VS Code Collections/GUI-AI-project/ML_model/data'
video_path = os.path.join(ROOT_DIR, 'GUI-AI-project', 'ML_model', 'data')
vid_name = 'ny5s_test_pyqt.mp4'
print(video_path)
def getFrame(video_path, vidcap, sec, count):
    vidcap.set(cv2.CAP_PROP_POS_MSEC,sec*1000)
    hasFrames,image = vidcap.read()
    image_path = video_path
    if hasFrames:
        # cv2.imwrite("frames/image"+str(count)+".jpg", image)     # save frame as JPG file
        image_path = os.path.join(video_path, f'frames/image{count}.jpg')
        cv2.imwrite(image_path, image)     # save frame as JPG file
        # print(f'image{count} has been saved successfully')
    return hasFrames, image_path

def vid_to_frame(video_path, vid_name, sec=0, frameRate=0.5):
    vidcap = cv2.VideoCapture(video_path + '/' + vid_name)
    #//it will capture image in each 'frameRate' second
    count=1
    success, image_path = getFrame(video_path, vidcap, sec, count)
    image_folder = [image_path]
    while success:
        count = count + 1
        sec = sec + frameRate
        sec = round(sec, 2)
        success, image_path = getFrame(video_path, vidcap, sec, count)
        image_folder.append(image_path)
    return image_folder
# print(vid_to_frame(video_path, vid_name))


