from ipaddress import ip_address
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt, QUrl, QSize, QObject, pyqtSignal, QThread
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel, QMainWindow, QLineEdit,
        QPushButton,QProgressBar, QDialog, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar, QTabWidget, QDialogButtonBox)
from ML_model.detect import run, ROOT # ROOT is ML_model in our case
import json
import argparse

filename = ''
buffer_size = 1024
vid_name = ''
global_result = {}

class GlobalResultPerCamera():
    
    def __init__(self, camera_number):
        self.result_is_done = False
        self.result_is_loaded = False
        self.result = None
        self.camera_number = camera_number
    
    def __str__(self):
        return f"Camera {self.camera_number} -> result: {self.result}"
        
frame_skip_second = 1
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
    
    def __init__(self, tab_number):#progress_bar_object):
        super().__init__()
        self.tab_number = tab_number
        # self.progress_bar_object = progress_bar_object

    def run_analyze(self):
        """Long running task - analyzing"""
        # we should perform this operation in the server side
        print (str(ROOT))        
        filenm = filename_retrieve()
        # sources = 0 if camerabutton.isChecked() else str(filenm)
        # weights has made global
        datayml = str(ROOT) + '/data/railway_components.yaml'
        print(filenm)
        print(wgths)
        # print(datayml)
        # let's send weights, data, and sources to the server  
        filenm = filename_retrieve()
        # wgths = str(ROOT) + '/checkpoints/yolov5s6.pt'
        # datayml = str(ROOT) + '/coco128.yaml'
        datayml = str(ROOT) + '/railway_components.yaml'
        
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
        save_dir = str(run(**vars(opt)))
        global saved_dir
        saved_dir = save_dir
        
        # we should read from result.json file
        # to do that let's run the command below
        curr_camera_number = f'Camera-{self.tab_number}'
        global_result[curr_camera_number].result_is_done = True
        with open(save_dir + '/result.json', 'r') as f:
            result = f.read()  # type: ignore
            # print(eval(result))
            print(type(eval(result)))
            global_result[curr_camera_number].result = eval(result)
        
        # write the paths of result video, raw video, and result json file in the project file
        

        json_output = {camera_num: camera_values.result for camera_num, camera_values in global_result.items()}
        # then write this result to global_result.json file
        with open('global_result.json', 'w') as f:
            json.dump(json_output, f)

class VideoAnalyzerButton(QPushButton, QMainWindow):
    def __init__(self, tab_number, parent=None):#progress_bar_object, parent=None):
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
        # self.progress_bar_object = progress_bar_object
    def analyze(self):
        # Create a QThread object
        self.thread = QThread()
        # Create a worker object
        self.worker = Worker(self.tab_number)#, self.progress_bar_object)
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
        
        
        self.mediaPlayer = QMediaPlayer()
        self.mediaPlayerResult = QMediaPlayer()
        btnSize = QSize(16, 16)
        videoWidget = QVideoWidget()
        # start
        videoWidgetResult = QVideoWidget()

        self.playButtonResult = QPushButton('Result Video')
        self.playButtonResult.setEnabled(True)
        self.playButtonResult.setFixedHeight(24)
        self.playButtonResult.setIconSize(btnSize)
        self.playButtonResult.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.playButtonResult.clicked.connect(self.playResult)

        self.positionSliderResult = QSlider(Qt.Orientation.Horizontal)
        self.positionSliderResult.setRange(0, 0)
        self.positionSliderResult.sliderMoved.connect(self.setPositionResult)
        
        self.positionSlider = QSlider(Qt.Orientation.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)
      
        self.openButton = QPushButton("Upload Video")   
        self.openButton.setToolTip("Open Video File")
        self.openButton.setStatusTip("Open Video File")
        self.openButton.setFixedHeight(25)
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

        

        self.progress_bar = QProgressBar(self)
        # global progress_bar_scale
        # progress_bar_scale = int(1e5)
        # self.progress_bar.setValue(0)
        # self.progress_bar.setRange(0, 100)

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
        self.playButton = QPushButton('Original Video')
        self.playButton.setEnabled(True)
        self.playButton.setCheckable(True)
        self.playButton.setFixedHeight(24)
        self.playButton.setIconSize(btnSize)
        self.playButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.fastforward = QPushButton(f'+{frame_skip_second}s')
        self.fastforward.setEnabled(True)
        # self.fastforward.setCheckable(True)
        self.fastforward.setFixedHeight(24)
        self.fastforward.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekForward))
        self.fastforward.clicked.connect(self.forward10)


        self.skipbackward = QPushButton(f'-{frame_skip_second}s')
        self.skipbackward.setEnabled(True)
        # self.skipbackward.setCheckable(True)
        self.skipbackward.setFixedHeight(24)
        self.skipbackward.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekBackward))
        self.skipbackward.clicked.connect(self.back10)


        self.playbuttons.addWidget(self.skipbackward)
        self.playbuttons.addWidget(self.playButton)
        self.playbuttons.addWidget(self.fastforward)

        self.playresultbuttons = QHBoxLayout()
        self.fastforwardResult = QPushButton(f'+{frame_skip_second}s')
        self.fastforwardResult.setEnabled(True)
        self.fastforwardResult.setFixedHeight(24)
        self.fastforwardResult.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekForward))
        self.fastforwardResult.clicked.connect(self.forward10_result)


        self.skipbackwardResult = QPushButton(f'-{frame_skip_second}s')
        self.skipbackwardResult.setEnabled(True)
        # self.skipbackwaResultskipbackwardResultrd.setCheckable(True)
        self.skipbackwardResult.setFixedHeight(24)
        self.skipbackwardResult.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaSeekBackward))
        self.skipbackwardResult.clicked.connect(self.back10_result)


        self.playbuttons.addWidget(self.skipbackward)
        self.playbuttons.addWidget(self.playButton)
        self.playbuttons.addWidget(self.fastforward)

        self.playresultbuttons.addWidget(self.skipbackwardResult)
        self.playresultbuttons.addWidget(self.playButtonResult)
        self.playresultbuttons.addWidget(self.fastforwardResult)

        self.statusBar = QStatusBar()
        self.statusBar.setFont(QFont("Noto Sans", 10))
        self.statusBar.setFixedHeight(14)
        self.statusBar.showMessage('Ready')

        store_results_button = QPushButton('Download results')
        store_results_button.setEnabled(True)
        store_results_button.setFixedHeight(25)
        store_results_button.setIconSize(btnSize)
        store_results_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown))        
        # store_results_button.clicked.connect(self.download_results)
        videolayout = QHBoxLayout()

        videoWidgetsupplements = QVBoxLayout()
        open_and_playbuttons = QVBoxLayout()
        open_and_playbuttons.addLayout(self.playbuttons)
        videoWidgetsupplements.addWidget(videoWidget)
        videoWidgetsupplements.addWidget(self.openButton)
        videoWidgetsupplements.addLayout(open_and_playbuttons)
        videoWidgetsupplements.addWidget(self.positionSlider)

        videoWidgetResultsupplements = QVBoxLayout()
        playresult_and_resultseekbar = QVBoxLayout()
        playresult_and_resultseekbar.addLayout(self.playresultbuttons)
        playresult_and_resultseekbar.addWidget(self.positionSliderResult)
        map_vid_to_server = QPushButton('Map video to server')
        map_vid_to_server.setEnabled(True)
        map_vid_to_server.setFixedHeight(25)
        map_vid_to_server.setIconSize(btnSize)
        map_vid_to_server.clicked.connect(self.map_video_to_server)
        videoWidgetResultsupplements.addWidget(videoWidgetResult)
        videoWidgetResultsupplements.addWidget(map_vid_to_server)
        videoWidgetResultsupplements.addLayout(playresult_and_resultseekbar)
        videolayout.addLayout(videoWidgetsupplements)
        videolayout.addLayout(videoWidgetResultsupplements)
        layoutUpload = QVBoxLayout()
        layoutUpload.addLayout(videolayout)
   

        leftbuttons = QVBoxLayout()
        analyze_and_get_results = QHBoxLayout()
        leftbuttons.addWidget(self.statusBar)
        leftbuttons.addLayout(models)
        leftbuttons.addWidget(self.analyze_button)
        self.statusBar2 = QStatusBar()
        self.statusBar2.setFont(QFont("Noto Sans", 10))
        self.statusBar2.setFixedHeight(60)
        self.statusBar2.showMessage('Result')
        
        layoutResult = QVBoxLayout()
        layoutResult.addWidget(self.statusBar2)
        layoutResult.addWidget(self.progress_bar)
        layoutResult.addWidget(store_results_button)
        analyze_and_get_results.addLayout(leftbuttons)
        analyze_and_get_results.addLayout(layoutResult)

        entire_layout = QVBoxLayout()
        entire_layout.addLayout(layoutUpload)
        entire_layout.addLayout(analyze_and_get_results)

        self.setLayout(entire_layout)

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

    def forward10(self):
        self.mediaPlayer.setPosition(self.mediaPlayer.position() + 1000 * frame_skip_second) # 1 second forward
    
    def back10(self):
        self.mediaPlayer.setPosition(self.mediaPlayer.position() - 1000 * frame_skip_second) # 1 second backward
    
    def forward10_result(self):
        self.mediaPlayer.setPosition(self.mediaPlayer.position() + 1000 * frame_skip_second) # 1 second forward

    def back10_result(self):
        self.mediaPlayerResult.setPosition(self.mediaPlayer.position() - 1000 * frame_skip_second) # 1 second backward
        
    def select_model(self):
            
        global wgths
        wgths = str(ROOT) + f'/checkpoints/yolov5_best.pt' # default selection -> yolov5
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
        print(fileName)
        global vid_name#, income_video_size, mounted_drive
        # mounted_drive = fileName[0]
        vid_name = fileName.split('/')[-1]
        # income_video_size = os.path.getsize(fileName)
        if fileName != '':
            self.mediaPlayer.setSource(QUrl.fromLocalFile(fileName))
            self.playButton.setEnabled(True)
            self.statusBar.showMessage(vid_name) # instead of showing the whole directory, I made it to show only the name of the video
            self.play()
            global filename 
            filename = fileName
            self.openButton.setEnabled(False)

    def load_result(self):
        fileName = str(saved_dir_retrieve()) + '\\' + vid_name
        print('#######')
        print('result file name is ', fileName)
        print('#######')
        self.mediaPlayerResult.setSource(QUrl.fromLocalFile(fileName))
        self.playButton.setEnabled(True)
        # global result_is_loaded
        # result_is_loaded = True
        self.playButtonResult.setEnabled(True)
        # self.playResult()

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
        if global_result[self.curr_camera_number].result_is_done and not global_result[self.curr_camera_number].result_is_loaded:
            self.load_result()
            # self.progress_bar.setValue(66)
            global_result[self.curr_camera_number].result_is_loaded = True
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
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)
        # if global_result[self.curr_camera_number].result_is_done:
        #     self.positionChangedResult(position)

    def positionChangedResult(self, position):
        self.positionSliderResult.setValue(position)
    
    def test(self):
        print(filename_retrieve())
    

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)
    #     if global_result[self.curr_camera_number].result_is_done:
    #         self.durationChangedResult(duration)
    
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
    
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.tab_number = 1
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.add_tab_icon = QPushButton('Add Camera')
        self.add_tab_icon.setStyleSheet("background-color: blue; color: white;")
        self.add_tab_icon.clicked.connect(self.add_tab)
        self.tabs.setCornerWidget(self.add_tab_icon, Qt.Corner.TopLeftCorner)
        self.tab1 = VideoPlayer(self.tab_number)
        self.tabs.addTab(self.tab1,f"CAM {self.tab_number}")
        self.tabs.resize(300,200)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        
    def add_tab(self):
        self.tab_number += 1
        self.new_tab = VideoPlayer(self.tab_number)
        self.tabs.addTab(self.new_tab, f"CAM {self.tab_number}")
        
        
class App(QMainWindow):

    def __init__(self):
        super().__init__()
        # self.setWindowTitle("HELLO!")
        # self.win = QMainWindow()
        self.title = 'PyQt6 - User interface to run object detection models'
        self.left = 300
        self.top = 300
        self.width = 300
        self.height = 400
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)
        self.dialogue = CustomDialog()
        self.user_name = self.dialogue.get_user_name()
        self.server_info = self.dialogue.get_server_info()
        self.drive_info = self.dialogue.get_drive_info()
        self.port_number = self.dialogue.get_port_number()
        # self.common_network = self.dialogue.get_common_network_info()
        # map the drive, and pass infos to server
        global ip_info, port_info, drive_info#, common_network_info
        port_info = self.port_number
        ip_info = f'{self.user_name}@{self.server_info}:{port_info}'
        drive_info = self.drive_info
        self.dialogue.buttonBox.accepted.connect(self.open_table_widget)
        self.setCentralWidget(self.dialogue)
        self.show()
        
    def open_table_widget(self):
        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)
        self.show()
class CustomDialog(QDialog, QMainWindow):
    def __init__(self):
        super().__init__()
        
        QBtn = QDialogButtonBox.StandardButton.Ok# | QDialogButtonBox.StandardButton.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        # self.buttonBox.accepted.connect(self.accept)
        # self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        drive_message = QLabel("Please enter the drive letter of the USB drive")
        self.drive_info = QLineEdit()
        self.drive_info.setPlaceholderText("exapmle: E")
        server_address_message = QLabel("Please enter the server address")
        self.server_info = QLineEdit()
        self.server_info.setPlaceholderText("Example: 125.138.99:152")
        user_name_message = QLabel("Please enter your user name")
        self.user_name = QLineEdit()
        self.user_name.setPlaceholderText("Example: kaleb")
        port_message = QLabel("Please enter the port number")
        self.port_number = QLineEdit()
        self.port_number.setPlaceholderText("Example: 7024")
        # common_network_message = QLabel("Please enter the common network address")
        # self.common_network_info = QLineEdit()
        # self.common_network_info.setPlaceholderText("Example:192.168.55.11")
        self.layout.addWidget(drive_message)
        self.layout.addWidget(self.drive_info)
        self.layout.addWidget(user_name_message)
        self.layout.addWidget(self.user_name)
        self.layout.addWidget(server_address_message)
        self.layout.addWidget(self.server_info)
        self.layout.addWidget(port_message)
        self.layout.addWidget(self.port_number)
        self.layout.addWidget(self.buttonBox)
        
        self.setLayout(self.layout)
    
    def get_user_name(self):
        return self.user_name.text()
    
    def get_server_info(self):
        return self.server_info.text()

    def get_drive_info(self):
        return self.drive_info.text()
    
    def get_port_number(self):
        return self.port_number.text()
    def get_common_network_info(self):
        return self.common_network_info.text()
    
    
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    
    ex = App()
    sys.exit(app.exec())