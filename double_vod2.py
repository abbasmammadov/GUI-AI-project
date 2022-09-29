from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import QDir, Qt, QUrl, QSize, QObject, pyqtSignal, QThread
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel, QMainWindow,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar, QTabWidget)
from multiprocessing import Process, Pool
from threading import Thread
from queue import Queue

import argparse
import os
import platform
import sys
from pathlib import Path

import torch

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
# ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative
ROOT = Path(os.path.abspath(ROOT))  # absolute
from ML_model.models.common import DetectMultiBackend
from ML_model.utils.dataloaders import IMG_FORMATS, VID_FORMATS, LoadImages, LoadStreams
from ML_model.utils.general import (LOGGER, Profile, check_file, check_img_size, check_imshow, check_requirements, colorstr, cv2,
                           increment_path, non_max_suppression, print_args, scale_coords, strip_optimizer, xyxy2xywh)
from ML_model.utils.plots import Annotator, colors, save_one_box
from ML_model.utils.torch_utils import select_device, smart_inference_mode

@smart_inference_mode()
def run(
        weights=ROOT / 'yolov5s.pt',  # model.pt path(s)
        source=ROOT / 'data/ny5s_test_pyqt.mp4',  # file/dir/URL/glob, 0 for webcam
        data=ROOT / 'data/coco128.yaml',  # dataset.yaml path
        imgsz=(640, 640),  # inference size (height, width)
        conf_thres=0.25,  # confidence threshold
        iou_thres=0.45,  # NMS IOU threshold
        max_det=1000,  # maximum detections per image
        device='',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
        view_img=True,  # show results (True)
        save_txt=True,  # save results to *.txt (True)
        save_conf=False,  # save confidences in --save-txt labels
        save_crop=True,  # save cropped prediction boxes (True)
        nosave=False,  # do not save images/videos
        classes=None,  # filter by class: --class 0, or --class 0 2 3
        agnostic_nms=False,  # class-agnostic NMS
        augment=False,  # augmented inference
        visualize=False,  # visualize features
        update=False,  # update all models
        project=ROOT / 'runs/detect',  # save results to project/name
        name='exp',  # save results to project/name
        exist_ok=False,  # existing project/name ok, do not increment
        line_thickness=3,  # bounding box thickness (pixels)
        hide_labels=True,  # hide labels
        hide_conf=False,  # hide confidences
        half=False,  # use FP16 half-precision inference
        dnn=False,  # use OpenCV DNN for ONNX inference
        vid_stride=1,  # video frame-rate stride
):
    source = str(source)
    save_img = not nosave and not source.endswith('.txt')  # save inference images
    is_file = Path(source).suffix[1:] in (IMG_FORMATS + VID_FORMATS)
    is_url = source.lower().startswith(('rtsp://', 'rtmp://', 'http://', 'https://'))
    webcam = source.isnumeric() or source.endswith('.txt') or (is_url and not is_file)
    if is_url and is_file:
        source = check_file(source)  # download

    # Directories
    save_dir = increment_path(Path(project) / name, exist_ok=exist_ok)  # increment run
    (save_dir / 'labels' if save_txt else save_dir).mkdir(parents=True, exist_ok=True)  # make dir

    # Load model
    device = select_device(device)
    model = DetectMultiBackend(weights, device=device, dnn=dnn, data=data, fp16=half)
    stride, names, pt = model.stride, model.names, model.pt
    imgsz = check_img_size(imgsz, s=stride)  # check image size

    # Dataloader
    if webcam:
        view_img = check_imshow()
        dataset = LoadStreams(source, img_size=imgsz, stride=stride, auto=pt, vid_stride=vid_stride)
        bs = len(dataset)  # batch_size
    else:
        dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt, vid_stride=vid_stride)
        bs = 1  # batch_size
        # dataset is a list of (img, img_path, vid_cap) tuples
    vid_path, vid_writer = [None] * bs, [None] * bs

    # Run inference
    model.warmup(imgsz=(1 if pt else bs, 3, *imgsz))  # warmup
    seen, windows, dt = 0, [], (Profile(), Profile(), Profile())
    count = 0
    output_frames = [] # list of output frames
    for path, im, im0s, vid_cap, s in dataset:
        with dt[0]:
            im = torch.from_numpy(im).to(device)
            im = im.half() if model.fp16 else im.float()  # uint8 to fp16/32
            im /= 255  # 0 - 255 to 0.0 - 1.0
            if len(im.shape) == 3:
                im = im[None]  # expand for batch dim

        # Inference
        with dt[1]:
            visualize = increment_path(save_dir / Path(path).stem, mkdir=True) if visualize else False
            pred = model(im, augment=augment, visualize=visualize)

        # NMS
        with dt[2]:
            pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
        # Second-stage classifier (optional)
        # pred = utils.general.apply_classifier(pred, classifier_model, im, im0s)

        # Process predictions
        for i, det in enumerate(pred):  # per image
            count+=1
            seen += 1
            if webcam:  # batch_size >= 1
                p, im0, frame = path[i], im0s[i].copy(), dataset.count
                s += f'{i}: '
            else:
                p, im0, frame = path, im0s.copy(), getattr(dataset, 'frame', 0)

            p = Path(p)  # to Path
            save_path = str(save_dir / p.name)  # im.jpg
            txt_path = str(save_dir / 'labels' / p.stem) + ('' if dataset.mode == 'image' else f'_{frame}')  # im.txt
            s += '%gx%g ' % im.shape[2:]  # print string
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            imc = im0.copy() if save_crop else im0  # for save_crop
            annotator = Annotator(im0, line_width=line_thickness, example=str(names))
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(im.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                for c in det[:, 5].unique():
                    n = (det[:, 5] == c).sum()  # detections per class
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                # Write results
                for *xyxy, conf, cls in reversed(det):
                    if save_txt:  # Write to file
                        xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                        line = (cls, *xywh, conf) if save_conf else (cls, *xywh)  # label format
                        with open(f'{txt_path}.txt', 'a') as f:
                            f.write(('%g ' * len(line)).rstrip() % line + '\n')

                    if save_img or save_crop or view_img:  # Add bbox to image
                        c = int(cls)  # integer class
                        label = None if hide_labels else (names[c] if hide_conf else f'{names[c]} {conf:.2f}')
                        annotator.box_label(xyxy, label, color=colors(c, True))
                    if save_crop:
                        save_one_box(xyxy, imc, file=save_dir / 'crops' / names[c] / f'{p.stem}.jpg', BGR=True)

            # Stream results
            im0 = annotator.result()
            # Image.fromarray(im0[:, :, ::-1]).save(f'{save_dir}/image{count}.jpg') # the type of im0 is numpy.ndarray
            # to_be_appended = os.path.join(save_dir, f'{save_dir}/image{count}.jpg')
            # output_frames.append(to_be_appended) # append output frame
            if view_img:
                if platform.system() == 'Linux' and p not in windows:
                    windows.append(p)
                    cv2.namedWindow(str(p), cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)  # allow window resize (Linux)
                    cv2.resizeWindow(str(p), im0.shape[1], im0.shape[0])
                cv2.imshow(str(p), im0)
                cv2.waitKey(1)  # 1 millisecond

            # Save results (image with detections)
            if save_img:
                if dataset.mode == 'image':
                    cv2.imwrite(save_path, im0)
                else:  # 'video' or 'stream'
                    if vid_path[i] != save_path:  # new video
                        vid_path[i] = save_path
                        if isinstance(vid_writer[i], cv2.VideoWriter):
                            vid_writer[i].release()  # release previous video writer
                        if vid_cap:  # video
                            fps = vid_cap.get(cv2.CAP_PROP_FPS)
                            w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        else:  # stream
                            fps, w, h = 30, im0.shape[1], im0.shape[0]
                        save_path = str(Path(save_path).with_suffix('.mp4'))  # force *.mp4 suffix on results videos
                        vid_writer[i] = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
                    vid_writer[i].write(im0)

        # Print time (inference-only)
        LOGGER.info(f"{s}{'' if len(det) else '(no detections), '}{dt[1].dt * 1E3:.1f}ms")
    # return output_frames
    # Print results
    t = tuple(x.t / seen * 1E3 for x in dt)  # speeds per image
    LOGGER.info(f'Speed: %.1fms pre-process, %.1fms inference, %.1fms NMS per image at shape {(1, 3, *imgsz)}' % t)
    if save_txt or save_img:
        s = f"\n{len(list(save_dir.glob('labels/*.txt')))} labels saved to {save_dir / 'labels'}" if save_txt else ''
        LOGGER.info(f"Results saved to {colorstr('bold', save_dir)}{s}")
    if update:
        strip_optimizer(weights[0])  # update model (to fix SourceChangeWarning)
    return save_dir

#changed by Kaleb
filename = ''
def filename_retrieve():
    if filename ==  '':
        return 'No file selected'
    return filename

saved_dir = ''
def saved_dir_retrieve():
    if saved_dir ==  '':
        return 'No directory selected'
    return saved_dir

def wrapper(func, arg, queue):
    queue.put(func(arg))

# multithreading -> create a worker code

class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def run_analyze(self):
        """Long running task - analyzing"""
        print (str(ROOT))        
        filenm = filename_retrieve()
        # sources = 0 if camerabutton.isChecked() else str(filenm)
        # weights has made global
        datayml = str(ROOT) + '/data/coco128.yaml'
        print(filenm)
        print(wgths)
        print(datayml)
        def parse_opt():
            parser = argparse.ArgumentParser()
            parser.add_argument('--weights', nargs='+', type=str, default=str(wgths), help='model path(s)')
            parser.add_argument('--source', type=str, default=str(filenm), help='file/dir/URL/glob, 0 for webcam')
            parser.add_argument('--data', type=str, default=str(datayml), help='(optional) dataset.yaml path')
            parser.add_argument('--imgsz', '--img', '--img-size', nargs='+', type=int, default=[1280], help='inference size h,w')
            parser.add_argument('--conf-thres', type=float, default=0.25, help='confidence threshold')
            parser.add_argument('--iou-thres', type=float, default=0.45, help='NMS IoU threshold')
            parser.add_argument('--max-det', type=int, default=1000, help='maximum detections per image')
            parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
            parser.add_argument('--view-img', action='store_true', help='show results')
            parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
            parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
            parser.add_argument('--save-crop', action='store_true', help='save cropped prediction boxes')
            parser.add_argument('--nosave', action='store_true', help='do not save images/videos')
            parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --classes 0, or --classes 0 2 3')
            parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
            parser.add_argument('--augment', action='store_true', help='augmented inference')
            parser.add_argument('--visualize', action='store_true', help='visualize features')
            parser.add_argument('--update', action='store_true', help='update all models')
            parser.add_argument('--project', default=(str(ROOT) + '/runs'), help='save results to project/name')
            parser.add_argument('--name', default='exp', help='save results to project/name')
            parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
            parser.add_argument('--line-thickness', default=3, type=int, help='bounding box thickness (pixels)')
            parser.add_argument('--hide-labels', default=False, action='store_true', help='hide labels')
            parser.add_argument('--hide-conf', default=False, action='store_true', help='hide confidences')
            parser.add_argument('--half', action='store_true', help='use FP16 half-precision inference')
            parser.add_argument('--dnn', action='store_true', help='use OpenCV DNN for ONNX inference')
            opt = parser.parse_args()
            opt.imgsz *= 2 if len(opt.imgsz) == 1 else 1  # expand
            return opt

        opt = parse_opt()
        save_dir = run(**vars(opt))
        global saved_dir
        # saved_dir = frame_to_video('output.mp4', 30, output_frames)
        # how to run the above 2 functions in parallel
        # q1, q2 = Queue(), Queue()
        # Thread(target=wrapper, args=(run, opt, q1)).start()
        # output_frames = q1.get()
        # Thread(target=wrapper, args=(frame_to_video, output_frames, 30, q2)).start()
        saved_dir = save_dir
        # saved_dir = q2.get()
        # self.mediaPlayerResult = QMediaPlayer()
        # fileName = str(saved_dir_retrieve())
        # print(fileName)


class VideoAnalyzerButton(QPushButton, QMainWindow):
    def __init__(self, parent=None):
        super(VideoAnalyzerButton, self).__init__(parent)
        self.setAccessibleName("analyze_button")
        self.setToolTip("Apply ML Model")
        self.setStatusTip("Apply ML Model")
        self.setFixedHeight(24)
        self.setIconSize(QSize(16, 16))
        self.setFont(QFont("Noto Sans", 8))
        self.setIcon(QIcon("analyze.png"))
        self.clicked.connect(self.analyze)

    def analyze(self):
        # Create a QThread object
        self.thread = QThread()
        # Create a worker object
        self.worker = Worker()
        # Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Connect signals and slots
        self.thread.started.connect(self.worker.run_analyze)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # Start the thread
        self.thread.start()

        # Final resets
        self.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.stepLabel.setText("Long-Running Step: 0")
        )
   

class VideoPlayer(QWidget):

    def __init__(self, parent=None):
        super(VideoPlayer, self).__init__(parent)
        
        self.mediaPlayer = QMediaPlayer()
        self.mediaPlayerResult = QMediaPlayer()

        btnSize = QSize(16, 16)
        videoWidget = QVideoWidget()
        # start
        videoWidgetResult = QVideoWidget()
        videoWidget.setFixedHeight(250)
        videoWidgetResult.setFixedHeight(250)
        testbtn = QPushButton("Display status as text") # change it to -> show results as text
        testbtn.clicked.connect(self.test)

        showresultbtn = QPushButton("Show Result")
        showresultbtn.clicked.connect(self.showresult)

        # to add button vertically create a QPush button instance here

        self.playButtonResult = QPushButton()
        self.playButtonResult.setEnabled(True)
        self.playButtonResult.setFixedHeight(24)
        self.playButtonResult.setIconSize(btnSize)
        self.playButtonResult.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.playButtonResult.clicked.connect(self.playResult)

        self.positionSliderResult = QSlider(Qt.Orientation.Horizontal)
        self.positionSliderResult.setRange(0, 0)
        self.positionSliderResult.sliderMoved.connect(self.setPositionResult)

        vodbelow = QHBoxLayout()
        vodbelow.setContentsMargins(0, 0, 0, 0)
        vodbelow.addWidget(self.playButtonResult)
        vodbelow.addWidget(self.positionSliderResult)
        
        # another status bar for showing the file name of the analyzed video

        self.statusBar2 = QStatusBar()
        self.statusBar2.setFont(QFont("Noto Sans", 10))
        self.statusBar2.setFixedHeight(14)

        layoutResult = QVBoxLayout()
        layoutResult.addWidget(videoWidgetResult)
        layoutResult.addLayout(vodbelow)
        layoutResult.addWidget(self.statusBar2)
        layoutResult.addWidget(showresultbtn)
        layoutResult.addWidget(testbtn)

        # add camera button on the top right corner

        self.openButton = QPushButton("Upload Video")   
        self.openButton.setToolTip("Open Video File")
        self.openButton.setStatusTip("Open Video File")
        self.openButton.setFixedHeight(24)
        self.openButton.setIconSize(btnSize)
        self.openButton.setFont(QFont("Noto Sans", 8))
        self.openButton.setIcon(QIcon.fromTheme("document-open", QIcon("upload-icon.png")))
        self.openButton.clicked.connect(self.open_video)

        self.select_yolov5 = QPushButton('YOLOv5')
        self.select_yolov5.setWindowTitle("Analyze Video")
        self.select_yolov5.setCheckable(True)
        self.select_yolov5.setStyleSheet("QPushButton:checked {color: white; background-color: green;}")
        self.select_yolov5.clicked.connect(self.select_model)

        self.select_yolov7 = QPushButton('YOLOv7')
        self.select_yolov7.setWindowTitle("Analyze Video")
        self.select_yolov7.setCheckable(True)
        self.select_yolov7.setStyleSheet("QPushButton:checked {color: white; background-color: green;}")
        self.select_yolov7.clicked.connect(self.select_model)
        
        self.select_yoloR = QPushButton('YOLO-R')
        self.select_yoloR.setWindowTitle("Analyze Video")
        self.select_yoloR.setCheckable(True)
        self.select_yoloR.setStyleSheet("QPushButton:checked {color: white; background-color: green;}")
        self.select_yoloR.clicked.connect(self.select_model)
        
        self.select_dino = QPushButton('DINO')
        self.select_dino.setWindowTitle("Analyze Video")
        self.select_dino.setCheckable(True)
        self.select_dino.setStyleSheet("QPushButton:checked {color: white; background-color: green;}")
        self.select_dino.clicked.connect(self.select_model)


        self.analyze_button = VideoAnalyzerButton('Analyze ML model')
        self.analyze_button.setWindowTitle('Analyze video')
        self.analyze_button.setCheckable(True)
        self.analyze_button.setEnabled(False)

        
        models = QHBoxLayout()
        models.setContentsMargins(0, 0, 0, 0)
        models.addWidget(self.select_yolov5)
        models.addWidget(self.select_yolov7)
        models.addWidget(self.select_yoloR)
        models.addWidget(self.select_dino)

        self.playButton = QPushButton()
        self.playButton.setEnabled(True)
        self.playButton.setCheckable(True)
        self.playButton.setFixedHeight(24)
        self.playButton.setIconSize(btnSize)
        self.playButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.positionSlider = QSlider(Qt.Orientation.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.statusBar = QStatusBar()
        self.statusBar.setFont(QFont("Noto Sans", 10))
        self.statusBar.setFixedHeight(14)

        # camerabutton = QPushButton('Camera')
        # camerabutton.setPosition(0, 0)
        # camerabutton.setCheckable(True)
        # camerabutton.setEnabled(True)
        # camerabutton.setFixedHeight(30)
        # camerabutton.setIconSize(btnSize)
        # camerabutton.setIcon(QIcon('camera.png'))
        # camerabutton.clicked.connect(self.real_time)

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.openButton)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)

        store_results_button = QPushButton('Download results')
        store_results_button.setEnabled(True)
        store_results_button.setFixedHeight(25)
        store_results_button.setIconSize(btnSize)
        # store_results_button.setIcon(QIcon('download.png'))
        
        layoutUpload = QVBoxLayout()
        # layoutUpload.addWidget(camerabutton)
        layoutUpload.addWidget(videoWidget)
        layoutUpload.addLayout(controlLayout)
        layoutUpload.addWidget(self.statusBar)
        layoutUpload.addLayout(models)
        layoutUpload.addWidget(self.analyze_button)
        layoutUpload.addWidget(store_results_button)


        layout = QHBoxLayout()
        layout.addLayout(layoutUpload)
        layout.addLayout(layoutResult)

        self.setLayout(layout)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.playbackStateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.errorOccurred.connect(self.handleError)
        self.statusBar.showMessage("Ready")


        self.mediaPlayerResult.setVideoOutput(videoWidgetResult)
        self.mediaPlayerResult.playbackStateChanged.connect(self.mediaStateChangedResult)
        self.mediaPlayerResult.positionChanged.connect(self.positionChangedResult)
        self.mediaPlayerResult.durationChanged.connect(self.durationChangedResult)
        self.mediaPlayerResult.errorOccurred.connect(self.handleError)

    # def real_time(self):
    #     global source
    #     source = 0 # set the source 0

    def select_model(self):
        """Long running task - analyzing"""        
        global wgths
        wgths = str(ROOT) + f'/checkpoints/yolov5s6.pt' # default selection -> yolov5
        print(ROOT)
        print(self.select_yolov5.isChecked())
        # if self.select_yolov5.isChecked():
            # self.select_yolov5.setEnabled(False)
        if self.select_yolov7.isChecked():
            wgths = str(ROOT) + f'/checkpoints/yolov7s6.pt'
            # self.select_yolov7.setEnabled(False)
        elif self.select_yoloR.isChecked():
            wgths = str(ROOT) + f'/checkpoints/yolors6.pt'
            # self.select_yolov7.setEnabled(False)
        elif self.select_dino.isChecked():
            wgths = str(ROOT) + f'/checkpoints/dinos6.pt'
            # self.select_dino.setEnabled(False)
        print('selected weight:', wgths.split('/')[-1])
        self.analyze_button.setEnabled(True)
        return wgths

    def open_video(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Upload the desired video",
                ".", "Video Files (*.mp4 *.flv *.ts *.mts *.avi)")

        if fileName != '':
            self.mediaPlayer.setSource(QUrl.fromLocalFile(fileName))
            self.playButton.setEnabled(True)
            self.statusBar.showMessage(fileName.split('/')[-1]) # instead of showing the whole directory, I made it to show only the name of the video
            self.play()
            global filename 
            filename = fileName
            self.openButton.setEnabled(False)

    def showresult(self):
        fileName = str(saved_dir_retrieve()) + '/ny5s_test_pyqt.mp4'
        # fileName = str(saved_dir_retrieve())
        print('#######')
        print(fileName)
        print('#######')
        self.mediaPlayerResult.setSource(QUrl.fromLocalFile(fileName))
        self.playButton.setEnabled(True)
        # self.playButtonResult.setEnabled(True)
        # self.statusBar2.showMessage(fileName.split('/')[-1] + ' with bboxes') # add trained
        self.playResult()

    def name_of_file(self):
        print("Name of file")
        print(self.statusBar.currentMessage())
        return self.statusBar.currentMessage()

    def play(self):
        if self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def playResult(self):
        if self.mediaPlayerResult.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.mediaPlayerResult.pause()
        else:
            self.mediaPlayerResult.play()
    
    def mediaStateChanged(self, state):
        if self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    def mediaStateChangedResult(self, state):
        if self.mediaPlayerResult.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.playButtonResult.setIcon(
                    self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        else:
            self.playButtonResult.setIcon(
                    self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def positionChangedResult(self, position):
        self.positionSliderResult.setValue(position)
    
    def test(self):
        print(filename_retrieve())
    

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)
    
    def durationChangedResult(self, duration):
        self.positionSliderResult.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def setPositionResult(self, position):
        self.mediaPlayerResult.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.statusBar.showMessage("Error: " + self.mediaPlayer.errorString())

class MyTableWidget(QWidget):
    
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.tab_number = 1
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.add_tab_icon = QPushButton('Add Camera')
        self.add_tab_icon.setStyleSheet("background-color: blue")
        self.add_tab_icon.clicked.connect(self.add_tab)
        self.tabs.setCornerWidget(self.add_tab_icon, Qt.Corner.TopLeftCorner)
        self.tab1 = VideoPlayer()
        self.tabs.addTab(self.tab1,f"CAM {self.tab_number}")
        self.tabs.resize(300,200)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
    
        # how can we allow users to add more tabs
        
    def add_tab(self):
        self.tab_number += 1
        self.new_tab = VideoPlayer()
        self.tabs.addTab(self.new_tab, f"CAM {self.tab_number}")
        
        
class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'PyQt6 - User interface to run object detection models'
        self.left = 600
        self.top = 300
        self.width = 300
        self.height = 200
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)
        
        self.show()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec())