from turtle import left
from unittest import result
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import QDir, Qt, QUrl, QSize, QObject, pyqtSignal, QThread
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel, QMainWindow,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar, QTabWidget)
import socket
from ML_model.detect import ROOT # ROOT is ML_model in our case
import json
# from server import analyze_button
# from ML_model.frames import *
#changed by Kaleb
filename = ''


global_result = {}
class GlobalResultPerCamera():
    
    def __init__(self, camera_number):
        self.result_is_done = False
        self.result_is_loaded = False
        self.result = None
        self.camera_number = camera_number
    
    def __str__(self):
        return f"Camera {self.camera_number} -> result: {self.result}"
        
        
def filename_retrieve():
    if filename ==  '':
        return 'No file selected'
    return filename

saved_dir = ''
def saved_dir_retrieve():
    if saved_dir ==  '':
        return 'No directory selected'
    return saved_dir

# multithreading -> create a worker code
class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    
    def __init__(self, tab_number):
        super().__init__()
        self.tab_number = tab_number

    def run_analyze(self):
        """Long running task - analyzing"""
        # we should perform this operation in the server side
        
        print (str(ROOT))        
        filenm = filename_retrieve()
        # sources = 0 if camerabutton.isChecked() else str(filenm)
        # weights has made global
        datayml = str(ROOT) + '/data/railway_components.yaml'
        # print(filenm)
        # print(wgths)
        # print(datayml)
        # let's send weights, data, and sources to the server
        host = '0.0.0.0'
        port = 999
        server = (host, port) # replace with server IP_addr
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # we should convert the message to string so that we can easily convert it to bytes
        message = "".join([word + "," for word in [wgths, filenm, datayml]])
        s.sendto(message.encode('utf-8'), server)
        save_dir, _ = s.recvfrom(1024)
        save_dir = save_dir.decode('utf-8')
        # save_dir = save_dir
        
        print("Received results from server: " + save_dir)
        s.close()
        # save_dir = run(**vars(opt))
        global saved_dir
        saved_dir = save_dir
        # we should read from result.json file
        # to do that let's run the command below
        curr_camera_number = f'Camera-{self.tab_number}'
        global_result[curr_camera_number].result_is_done = True
        with open(save_dir + '/result.json', 'r') as f:
            result = f.read()  # type: ignore
            # print(eval(result))
            # print(type(eval(result)))
            global_result[curr_camera_number].result = eval(result)

        json_output = {camera_num: camera_values.result for camera_num, camera_values in global_result.items()}
        # then write this result to global_result.json file
        with open('global_result.json', 'w') as f:
            json.dump(json_output, f)
        
        # statusBar = QStatusBar()
        # statusBar.setFont(QFont("Noto Sans", 10))
        # statusBar.setFixedHeight(14)
        # statusBar.showMessage('Analysis done. Click on the play button to view the result')

        


class VideoAnalyzerButton(QPushButton, QMainWindow):
    def __init__(self, tab_number, parent=None):
        super(VideoAnalyzerButton, self).__init__(parent)
        self.setAccessibleName("analyze_button")
        self.setToolTip("Apply ML Model")
        self.setStatusTip("Apply ML Model")
        self.setFixedHeight(24)
        self.setIconSize(QSize(16, 16))
        self.setFont(QFont("Noto Sans", 8))
        self.setIcon(QIcon("analyze.png"))
        self.clicked.connect(self.analyze)
        self.tab_number = tab_number
    def analyze(self):
        # Create a QThread object
        self.thread = QThread()
        # Create a worker object
        self.worker = Worker(self.tab_number)
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

    def __init__(self, tab_number, parent=None):
        super(VideoPlayer, self).__init__(parent)
        self.tab_number = tab_number
        self.curr_camera_number = f'Camera-{self.tab_number}'

        global_result[self.curr_camera_number] = GlobalResultPerCamera(self.curr_camera_number)
        # global result_is_done, result_is_loaded
        # result_is_done = False
        # result_is_loaded = False
        
        self.mediaPlayer = QMediaPlayer()
        self.mediaPlayerResult = QMediaPlayer()
        btnSize = QSize(16, 16)
        videoWidget = QVideoWidget()
        # start
        videoWidgetResult = QVideoWidget()
        # videoWidget.setFixedHeight(250)
        # videoWidgetResult.setFixedHeight(250)
        # testbtn = QPushButton("Display status as text") # change it to -> show results as text
        # testbtn.clicked.connect(self.test)

        # showresultbtn = QPushButton("Show Result")
        # showresultbtn.clicked.connect(self.showresult)

        # to add button vertically create a QPush button instance here

        # self.playButtonResult = QPushButton()
        # self.playButtonResult.setEnabled(True)
        # self.playButtonResult.setFixedHeight(24)
        # self.playButtonResult.setIconSize(btnSize)
        # self.playButtonResult.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        # self.playButtonResult.clicked.connect(self.playResult)

        # self.positionSliderResult = QSlider(Qt.Orientation.Horizontal)
        # self.positionSliderResult.setRange(0, 0)
        # self.positionSliderResult.sliderMoved.connect(self.setPositionResult)

        # vodbelow = QHBoxLayout()
        # vodbelow.setContentsMargins(0, 0, 0, 0)
        # vodbelow.addWidget(self.playButtonResult)
        # vodbelow.addWidget(self.positionSliderResult)
        
        # another status bar for showing the file name of the analyzed video

        # add camera button on the top right corner
        
        self.openButton = QPushButton("Upload Video")   
        self.openButton.setToolTip("Open Video File")
        self.openButton.setStatusTip("Open Video File")
        self.openButton.setFixedHeight(24)
        self.openButton.setIconSize(btnSize)
        # self.openButton.setFont(QFont("Noto Sans", 8))
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
        self.select_yolov7.setEnabled(False)
        self.select_yolov7.setStyleSheet("QPushButton:checked {color: white; background-color: green;}")
        self.select_yolov7.clicked.connect(self.select_model)
        
        self.select_yoloR = QPushButton('YOLO-R')
        self.select_yoloR.setWindowTitle("Analyze Video")
        self.select_yoloR.setCheckable(True)
        self.select_yoloR.setEnabled(False)
        self.select_yoloR.setStyleSheet("QPushButton:checked {color: white; background-color: green;}")
        self.select_yoloR.clicked.connect(self.select_model)
        
        self.select_dino = QPushButton('DINO')
        self.select_dino.setWindowTitle("Analyze Video")
        self.select_dino.setCheckable(True)
        self.select_dino.setEnabled(False)
        self.select_dino.setStyleSheet("QPushButton:checked {color: white; background-color: green;}")
        self.select_dino.clicked.connect(self.select_model)

        self.analyze_button = VideoAnalyzerButton(self.tab_number, 'Analyze ML model')
        self.analyze_button.setWindowTitle('Analyze video')
        self.analyze_button.setCheckable(True)
        self.analyze_button.setEnabled(False)

        
        models = QHBoxLayout()
        models.setContentsMargins(0, 0, 0, 0)
        models.addWidget(self.select_yolov5)
        models.addWidget(self.select_yolov7)
        models.addWidget(self.select_yoloR)
        models.addWidget(self.select_dino)

        self.playbuttons = QHBoxLayout()
        self.playButton = QPushButton('Play')
        self.playButton.setEnabled(True)
        self.playButton.setCheckable(True)
        self.playButton.setFixedHeight(24)
        self.playButton.setIconSize(btnSize)
        self.playButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.fastforward = QPushButton('+10s')
        self.fastforward.setEnabled(True)
        # self.fastforward.setCheckable(True)
        self.fastforward.setFixedHeight(24)
        self.fastforward.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekForward))

        self.skipbackward = QPushButton('-10s')
        self.skipbackward.setEnabled(True)
        # self.skipbackward.setCheckable(True)
        self.skipbackward.setFixedHeight(24)
        self.skipbackward.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekBackward))
        
        self.playbuttons.addWidget(self.skipbackward)
        self.playbuttons.addWidget(self.playButton)
        self.playbuttons.addWidget(self.fastforward)

        self.positionSlider = QSlider(Qt.Orientation.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.statusBar = QStatusBar()
        self.statusBar.setFont(QFont("Noto Sans", 10))
        self.statusBar.setFixedHeight(14)
        self.statusBar.showMessage('Ready')

        # camerabutton = QPushButton('Camera')
        # camerabutton.setPosition(0, 0)
        # camerabutton.setCheckable(True)
        # camerabutton.setEnabled(True)
        # camerabutton.setFixedHeight(30)
        # camerabutton.setIconSize(btnSize)
        # camerabutton.setIcon(QIcon('camera.png'))
        # camerabutton.clicked.connect(self.real_time)

        # controlLayout = QHBoxLayout()
        # controlLayout.setContentsMargins(0, 0, 0, 0)
        # layoutUpload.addWidget(self.openButton)
        # layoutUpload.addWidget(self.playButton)
        # layoutUpload.addWidget(self.positionSlider)

        store_results_button = QPushButton('Download results')
        store_results_button.setEnabled(True)
        store_results_button.setFixedHeight(25)
        store_results_button.setIconSize(btnSize)
        store_results_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown))        
        # store_results_button.clicked.connect(self.download_results)
        videolayout = QHBoxLayout()
        videolayout.addWidget(videoWidget)
        videolayout.addWidget(videoWidgetResult)
        layoutUpload = QVBoxLayout()
        # layoutUpload.addWidget(camerabutton)
        # layoutUpload.addWidget(videoWidget)
        layoutUpload.addLayout(videolayout)
        layoutUpload.addWidget(self.openButton)
        # layoutUpload.addWidget(self.playButton)
        layoutUpload.addLayout(self.playbuttons)
        layoutUpload.addWidget(self.positionSlider)
        leftbuttons = QVBoxLayout()
        # controls = QVBoxLayout()
        analyze_and_get_results = QHBoxLayout()
        # analyze_and_get_results.addWidget(self.analyze_button)
        # layoutUpload.addLayout(controlLayout)
        leftbuttons.addWidget(self.statusBar)
        leftbuttons.addLayout(models)
        leftbuttons.addWidget(self.analyze_button)
        # leftbuttons.addWidget(store_results_button)
        # controls.addLayout(analyze_and_get_results)
        # controls.addWidget(store_results_button)
        self.statusBar2 = QStatusBar()
        self.statusBar2.setFont(QFont("Noto Sans", 10))
        self.statusBar2.setFixedHeight(60)

        layoutResult = QVBoxLayout()
        # layoutResult.addWidget(videoWidgetResult)
        # layoutResult.addLayout(vodbelow)
        layoutResult.addWidget(self.statusBar2)
        # layoutResult.addWidget(showresultbtn)
        # layoutResult.addWidget(testbtn)
        layoutResult.addWidget(store_results_button)
        analyze_and_get_results.addLayout(leftbuttons)
        analyze_and_get_results.addLayout(layoutResult)
        layoutUpload.addLayout(analyze_and_get_results)


        # layout = QHBoxLayout()
        # layout.addLayout(layoutUpload)
        # # layout.addLayout(layoutResult)

        self.setLayout(layoutUpload)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.playbackStateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.errorOccurred.connect(self.handleError)
        self.statusBar.showMessage("Ready")


        self.mediaPlayerResult.setVideoOutput(videoWidgetResult)
        self.mediaPlayerResult.playbackStateChanged.connect(self.mediaStateChangedResult)
        self.mediaPlayerResult.positionChanged.connect(self.positionChanged)
        self.mediaPlayerResult.durationChanged.connect(self.durationChanged)
        self.mediaPlayerResult.errorOccurred.connect(self.handleError)

    # def real_time(self):
    #     global source
    #     source = 0 # set the source 0

    def download_results(self):
        pass
    
    def select_model(self):
        """Long running task - analyzing"""        
        global wgths
        wgths = str(ROOT) + f'/checkpoints/yolov5_best.pt' # default selection -> yolov5
        # print('Loading weights from ')
        # print(ROOT)
        # print(self.select_yolov5.isChecked())
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
        global vid_name
        vid_name = fileName.split('/')[-1]

        if fileName != '':
            self.mediaPlayer.setSource(QUrl.fromLocalFile(fileName))
            self.playButton.setEnabled(True)
            self.statusBar.showMessage(vid_name) # instead of showing the whole directory, I made it to show only the name of the video
            self.play()
            global filename 
            filename = fileName
            self.openButton.setEnabled(False)

    def load_result(self):
        fileName = str(saved_dir_retrieve()) + '/' + vid_name
        # fileName = str(saved_dir_retrieve())
        print('#######')
        print(fileName)
        print('#######')
        self.mediaPlayerResult.setSource(QUrl.fromLocalFile(fileName))
        self.playButton.setEnabled(True)
        # global result_is_loaded
        # result_is_loaded = True
        # self.playButtonResult.setEnabled(True)
        # self.playResult()

    def name_of_file(self):
        print("Name of file")
        print(self.statusBar.currentMessage())
        return self.statusBar.currentMessage()

    def play(self):
        # print('result is done:', result_is_done)
        # if not result_is_done:
        #     print('Analysis is running. Please wait for a moment')
        
        if global_result[self.curr_camera_number].result_is_done and not global_result[self.curr_camera_number].result_is_loaded:
            self.load_result()
            global_result[self.curr_camera_number].result_is_loaded = True
            
        if self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            if global_result[self.curr_camera_number].result_is_done:
                self.mediaPlayerResult.pause()
            self.mediaPlayer.pause()
        else:
            if global_result[self.curr_camera_number].result_is_done:
                self.mediaPlayerResult.play()
            self.mediaPlayer.play()

    def playResult(self):
        if self.mediaPlayer.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
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
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)
        # if global_result[self.curr_camera_number].result_is_done:
        #     self.positionChangedResult(position)

    # def positionChangedResult(self, position):
    #     self.positionSliderResult.setValue(position)
    
    def test(self):
        print(filename_retrieve())
    

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)
    #     if global_result[self.curr_camera_number].result_is_done:
    #         self.durationChangedResult(duration)
    
    # def durationChangedResult(self, duration):
    #     self.positionSliderResult.setRange(0, duration)

    def setPosition(self, position):
        if global_result[self.curr_camera_number].result_is_done:
            self.setPositionResult(position)
        self.mediaPlayer.setPosition(position)

    def setPositionResult(self, position):
        self.mediaPlayerResult.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.statusBar.showMessage("Error: " + self.mediaPlayer.errorString())

class MyTableWidget(QWidget):
    
    def __init__(self, parent=None):
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
        self.tab1 = VideoPlayer(self.tab_number)
        self.tabs.addTab(self.tab1,f"CAM {self.tab_number}")
        self.tabs.resize(300,200)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
    
        # how can we allow users to add more tabs
        
    def add_tab(self):
        self.tab_number += 1
        self.new_tab = VideoPlayer(self.tab_number)
        self.tabs.addTab(self.new_tab, f"CAM {self.tab_number}")
        
        
class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'PyQt6 - User interface to run object detection models'
        self.left = 600
        self.top = 300
        self.width = 800
        self.height = 600
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