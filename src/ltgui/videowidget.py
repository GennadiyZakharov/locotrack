'''
Created on 13.12.2010

@author: gena
'''

from __future__ import division
from PyQt4 import QtCore, QtGui
from ltcore.ltactions import createAction 
import os
import imagercc

class VideoWidget(QtGui.QWidget):
    '''
    This class holds GUI for cvPlayer
    '''
    speedChanged = QtCore.pyqtSignal(float)
    videoSeeked = QtCore.pyqtSignal(int)
    signalCaptureFromFile = QtCore.pyqtSignal(QtCore.QString)
    signalCaptureFromCam  = QtCore.pyqtSignal(int)
    
    def __init__(self, player, parent=None):
        '''
        Constructor
        player is an cvPlayer object to construct all signals
        '''
        super(VideoWidget, self).__init__(parent)
        self.player = player
        player.videoSourceOpened.connect(self.videoCapturing)
        player.videoSourceClosed.connect(self.videoClosed)
        player.nextFrame.connect(self.nextFrame)
        self.videoSeeked.connect(player.seek)
        self.speedChanged.connect(player.setSpeed)
        self.signalCaptureFromFile.connect(player.captureFromFile)
        self.signalCaptureFromCam.connect(player.captureFromCam)
        # Actions
        actionOpenVideo = createAction(self,"&Open...", "",
                                       "document-open", "Open video file")
        actionOpenVideo.triggered.connect(self.openVideoFile)
        actionCaptureVideo = createAction(self,"&Capture...", "",
                                          "camera-web", "")
        actionCaptureVideo.triggered.connect(self.captureVideo)
        actionCaptureClose = createAction(self,"Close video", "",
                                          "dialog-close", "")
        actionCaptureClose.triggered.connect(player.captureClose)
        actionPlay = createAction(self,"&Play", "", 
                                  "media-playback-start", "", True)
        actionPlay.toggled.connect(player.play)
        player.playing.connect(actionPlay.setChecked)
        actionRun =  createAction(self,"&Run", "", 
                                  "fork", "", True)
        actionRun.toggled.connect(player.runTrough)
        player.running.connect(actionRun.setChecked)
        actionRew = createAction(self,"&Rewind", "", 
                                 "media-seek-backward", "")
        actionRew.triggered.connect(player.seekRew)
        actionFwd = createAction(self,"&Forward", "", 
                                 "media-seek-forward", "")
        actionFwd.triggered.connect(player.seekFwd)
        self.actions = (actionOpenVideo,actionCaptureVideo,actionCaptureClose,None,
                             actionPlay, actionRun,None,
                             actionRew, actionFwd)
        # Video slider and position label
        layout1 = QtGui.QHBoxLayout()
        self.startFrameSlider = QtGui.QSpinBox()
        layout1.addWidget(self.startFrameSlider)
        self.endFrameSlider = QtGui.QSpinBox()
        self.videoSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        layout1.addWidget(self.videoSlider)
        self.timeLabel = QtGui.QLabel('0')
        layout1.addWidget(self.timeLabel)
        layout1.addWidget(self.endFrameSlider)
        self.videoSlider.valueChanged.connect(self.videoSliderMove)       
        layout2 = QtGui.QHBoxLayout()
        self.rewButt = QtGui.QPushButton("<<")
        self.rewButt.clicked.connect(player.seekRew)
        layout2.addWidget(self.rewButt)
        self.playButt = QtGui.QPushButton("Play")
        self.playButt.setCheckable(True)
        self.playButt.toggled.connect(actionPlay.setChecked)
        actionPlay.toggled.connect(self.playButt.setChecked)
        layout2.addWidget(self.playButt)
        self.fwdButt = QtGui.QPushButton(">>")
        self.fwdButt.clicked.connect(player.seekFwd)
        layout2.addWidget(self.fwdButt)
        self.runTroughButton = QtGui.QPushButton('Run')
        self.runTroughButton.setCheckable(True)
        self.runTroughButton.toggled.connect(player.runTrough)
        player.running.connect(self.runTroughButton.setChecked)
        layout2.addWidget(self.runTroughButton)
        self.videoOpenButton = QtGui.QPushButton('Open video')
        layout2.addWidget(self.videoOpenButton)
        self.videoOpenButton.clicked.connect(self.openVideoFile)
        self.videoCaptureButton = QtGui.QPushButton('Capture video')
        layout2.addWidget(self.videoCaptureButton)
        self.videoOpenButton.clicked.connect(self.captureVideo)
        # Speed
        layout3 = QtGui.QVBoxLayout()
        self.speedLabel = QtGui.QLabel()
        layout3.addWidget(self.speedLabel)
        self.speedSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        layout3.addWidget(self.speedSlider)
        self.speedLabel.setBuddy(self.speedSlider)
        self.speedSlider.valueChanged.connect(self.speedSliderMove)
        self.speedSlider.setMinimum(2)
        self.speedSlider.setMaximum(20)
        self.speedSlider.setValue(10)
        layout2.addLayout(layout3) 
        layout2.addStretch()
   
        # Main Layout
        layout = QtGui.QVBoxLayout()
        layout.addLayout(layout1)
        layout.addLayout(layout2)
        self.setLayout(layout)
        # Creating sets to enable/disable GUI elements
        self.playSet = set([self.videoSlider, self.playButt,
                           self.rewButt, self.fwdButt, self.runTroughButton])
        self.setGuiEnabled(False)
    
    @QtCore.pyqtSlot()
    def openVideoFile(self):
        '''
        Open video file
        '''
        # Setting last user dir
        directory = os.path.dirname(self.player.videoFileName) \
            if self.player.videoFileName is not None else "."
        # Creating formats list
        formats = ["*.{}".format(unicode(videoFormat)) \
                   for videoFormat in ('avi', 'mpg', 'ogg', 'mkv')]
        # Executing standard open dialog
        fname = QtGui.QFileDialog.getOpenFileName(self,
                        "Choose video file",
                        directory, "Video files (%s)" % " ".join(formats))
        
        if fname is not None :
            self.signalCaptureFromFile.emit(fname)
    
    def captureVideo(self):
        self.signalCaptureFromFile.emit(0)
    
    def setGuiEnabled(self, flag):
        for elem in self.playSet :
            elem.setEnabled(flag)
            
    @QtCore.pyqtSlot(int, float)  
    def videoCapturing(self, videoLength, frameRate):
        '''
        Calling this method when video opened
        '''
        if videoLength > 0 :
            self.startFrameSlider.setValue(0)
            self.startFrameSlider.setMaximum(videoLength-1)
            self.endFrameSlider.setMaximum(videoLength)
            self.endFrameSlider.setValue(videoLength)
            self.videoSlider.setMaximum(videoLength)
            self.videoSlider.setValue(0)
        self.setGuiEnabled(videoLength > 0)
            
    def videoClosed(self):
        self.setGuiEnabled(False)
    
    @QtCore.pyqtSlot(object, int)
    def nextFrame(self, frame, frameNumber):
        self.videoSlider.setValue(frameNumber)
    
    @QtCore.pyqtSlot(int)
    def videoSliderMove(self, value):
        self.timeLabel.setText(str(value))
        self.videoSeeked.emit(value)
        
    @QtCore.pyqtSlot(int)
    def speedSliderMove(self, value):
        speed = value/10
        self.speedLabel.setText('Speed: {:2.1f}'.format(speed))
        self.speedChanged.emit(speed)
