from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import QDir, Qt, QUrl, QSize
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel, 
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar)


import argparse
from ML_model.detect import run, ROOT
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

class VideoAnalyzerButton(QPushButton):
    def __init__(self, parent=None):
        super(VideoAnalyzerButton, self).__init__(parent)
        self.setAccessibleName("analyze_button")
        self.setToolTip("Apply ML Model")
        self.setStatusTip("Apply ML Model")
        self.setFixedHeight(24)
        self.setIconSize(QSize(16, 16))
        self.setFont(QFont("Noto Sans", 8))
        self.setIcon(QIcon("main/analyze.png"))
        self.clicked.connect(self.analyze)

    def analyze(self):
        print (str(ROOT))
        
        filenm = filename_retrieve()
        wgths = str(ROOT) + '/checkpoints/yolov5s6.pt'
        datayml = str(ROOT) + '/coco128.yaml'
        print(filenm)
        print(wgths)
        print(datayml)
        def parse_opt():
            parser = argparse.ArgumentParser()
            parser.add_argument('--weights', nargs='+', type=str, default=[str(wgths)], help='model path(s)')
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
        saved_dir = save_dir

class VideoPlayer(QWidget):

    def __init__(self, parent=None):
        super(VideoPlayer, self).__init__(parent)

        self.mediaPlayer = QMediaPlayer()
        self.mediaPlayerResult = QMediaPlayer()

        btnSize = QSize(16, 16)
        videoWidget = QVideoWidget()
        # start
        videoWidgetResult = QVideoWidget()

        testbtn = QPushButton("Test")
        testbtn.clicked.connect(self.test)

        showresultbtn = QPushButton("Show Result")
        showresultbtn.clicked.connect(self.showresult)

        self.playButtonResult = QPushButton()
        self.playButtonResult.setEnabled(False)
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

        layoutResult = QVBoxLayout()
        layoutResult.addWidget(videoWidgetResult)
        layoutResult.addLayout(vodbelow)
        layoutResult.addWidget(showresultbtn)
        layoutResult.addWidget(testbtn)

        # end

        openButton = QPushButton("Upload Video")   
        openButton.setToolTip("Open Video File")
        openButton.setStatusTip("Open Video File")
        openButton.setFixedHeight(24)
        openButton.setIconSize(btnSize)
        openButton.setFont(QFont("Noto Sans", 8))
        openButton.setIcon(QIcon.fromTheme("document-open", QIcon("upload-icon.png")))
        openButton.clicked.connect(self.open_video)


        analyze_button = VideoAnalyzerButton()
        analyze_button.setWindowTitle("Analyze Video")

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        # self.playButton.setCheckable(True)
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

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(openButton)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)

        
        layoutUpload = QVBoxLayout()
        layoutUpload.addWidget(videoWidget)
        layoutUpload.addLayout(controlLayout)
        layoutUpload.addWidget(self.statusBar)
        layoutUpload.addWidget(analyze_button)


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

    

    def open_video(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Upload the desired video",
                ".", "Video Files (*.mp4 *.flv *.ts *.mts *.avi)")

        if fileName != '':
            self.mediaPlayer.setSource(QUrl.fromLocalFile(fileName))
            self.playButton.setEnabled(True)
            self.statusBar.showMessage(fileName)
            self.play()
            global filename 
            filename = fileName

    def showresult(self):
        fileName = str(saved_dir_retrieve()) + '/ny5s_test_pyqt.mp4'
        print('#######')
        print(fileName)
        print('#######')
        self.mediaPlayerResult.setSource(QUrl.fromLocalFile(fileName))
        #self.playButton.setEnabled(True)
        #self.statusBar.showMessage(fileName)
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

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.setWindowTitle("Player")
    player.resize(600, 400)
    player.show()
    sys.exit(app.exec())