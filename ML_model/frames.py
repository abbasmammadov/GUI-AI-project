import cv2
import os
ROOT_DIR = os.path.abspath(os.curdir) # directory = '/Users/kalebmesfin06/Desktop/VS Code Collections'
# video_path = '/Users/kalebmesfinasfaw/Desktop/VS Code Collections/GUI-AI-project/ML_model/data'
video_path = os.path.join(ROOT_DIR, 'ML_model', 'data')
vid_name = 'ny5s_test_pyqt.mp4'
frame_rate = 5 / 151
fps = 1 / frame_rate
print(video_path)
def getFrame(frames_path, vidcap, sec, count):
    vidcap.set(cv2.CAP_PROP_POS_MSEC,sec*1000)
    hasFrames,image = vidcap.read()
    image_path = video_path
    if hasFrames:
        # cv2.imwrite("frames/image"+str(count)+".jpg", image)     # save frame as JPG file
        image_path = os.path.join(frames_path, f'image{count}.jpg')
        cv2.imwrite(image_path, image)     # save frame as JPG file
        # print(f'image{count} has been saved successfully')
    return hasFrames, image_path

def vid_to_frame(video_path, vid_name, sec=0, frameRate=frame_rate):
    vidcap = cv2.VideoCapture(video_path + '/' + vid_name)
    #//it will capture image in each 'frameRate' second
    count=1
    frames_path = os.path.join(video_path, 'frames')
    if not os.path.exists(frames_path):
        os.mkdir(frames_path)
    success, image_path = getFrame(frames_path, vidcap, sec, count)
    # image_folder = [image_path]
    while success:
        count = count + 1
        sec = sec + frameRate
        sec = round(sec, 2)
        success, image_path = getFrame(frames_path, vidcap, sec, count)
        # image_folder.append(image_path)
        print(image_path)
    return frames_path

def frame_to_video(frames_path, output_video_name, fps=fps):
    ROOT = os.path.abspath(os.getcwd())
    # pathIn= os.path.join(ROOT, 'ML_model', 'data', 'frames')
    pathIn = frames_path
    pathOut = os.path.join(ROOT, 'ML_model', 'data', output_video_name)
    frame_array = []
    files = [f[:-4] for f in os.listdir(pathIn) if os.path.isfile(os.path.join(pathIn, f)) and not f.startswith('.')]
    #for sorting the file names properly
    files.sort(key = lambda x: int(x[5:]))
    for i in range(len(files)):
        filename=os.path.join(pathIn, f'{files[i]}.jpg')
        print(filename)
        #reading each files
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width,height)
        
        #inserting the frames into an image array
        frame_array.append(img)
    out = cv2.VideoWriter(pathOut,cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), fps, size)
    for i in range(len(frame_array)):
        # writing to a image array
        out.write(frame_array[i])
    out.release()
    return pathOut
frames_path = vid_to_frame(video_path, vid_name)
# frames_path = os.path.join(video_path, 'frames')
print(frames_path)

frame_to_video(frames_path, 'my_video2.mp4')



