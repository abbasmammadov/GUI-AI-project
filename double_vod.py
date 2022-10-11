from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import QDir, Qt, QUrl, QSize, QObject, pyqtSignal, QThread
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel, QMainWindow,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar, QTabWidget)
from multiprocessing import Process, Pool
from threading import Thread
from queue import Queue
import os
import argparse
from ML_model.detect import run, ROOT # ROOT is ML_model in our case
from ML_model.frames import frame_to_video
import client2
import socket
# from server import analyze_button
# from ML_model.frames import *
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

# multithreading -> create a worker code
import socket


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def run_analyze(self):
        """Long running task - analyzing"""
        # we should perform this operation in the server side
        
        print (str(ROOT))        
        filenm = filename_retrieve()
        # sources = 0 if camerabutton.isChecked() else str(filenm)
        # weights has made global
        datayml = str(ROOT) + '/data/coco128.yaml'
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
        print("Received from server: " + save_dir)
        s.close()
        # save_dir = run(**vars(opt))
        global saved_dir
        saved_dir = save_dir
        


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
        # print('Loading weights from ')
        # print(ROOT)
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

    def showresult(self):
        fileName = str(saved_dir_retrieve()) + '/' + vid_name
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