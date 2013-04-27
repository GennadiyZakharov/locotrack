'''
Created on 13.12.2010

@author: gena
'''

from __future__ import division
from PyQt4 import QtCore, QtGui
from ltcore.consts import videoFormats
from ltcore.ltactions import createAction 
from ltgui.actionbutton import ActionButton
import imagercc

class VideoWidget(QtGui.QWidget):
    '''
    This class holds GUI for cvPlayer 
    
    Open vieo file, play, stop run, e.t.c.
    '''
    signalCaptureFromFile = QtCore.pyqtSignal(QtCore.QString)
    signalCaptureFromCam  = QtCore.pyqtSignal(int)
    
    def __init__(self, player, parent=None):
        '''
        Constructor
        player is an cvPlayer object to construct all signals
        '''
        super(VideoWidget, self).__init__(parent)
        self.player = player
        player.videoSourceOpened.connect(self.videoSourceOpen)
        player.videoSourceClosed.connect(self.videoSourceClose)
        player.nextFrame.connect(self.nextFrame)
        self.signalCaptureFromFile.connect(player.captureFromFile)
        self.signalCaptureFromCam.connect(player.captureFromCam)
        # Actions
        self.actionOpenVideo = createAction(self,"&Open...", "",
                                       "document-open", "Open video file")
        self.actionOpenVideo.triggered.connect(self.openVideoFile)
        self.actionCaptureVideo = createAction(self,"&Capture...", "",
                                          "camera-web", "")
        self.actionCaptureVideo.triggered.connect(self.captureVideo)
        self.actionCaptureClose = createAction(self,"Close video", "",
                                          "dialog-close", "")
        self.actionCaptureClose.triggered.connect(player.captureClose)
        self.actionPlay = createAction(self,"&Play", "", 
                                  "media-playback-start", "", True)
        self.actionPlay.toggled.connect(player.play)
        player.playing.connect(self.actionPlay.setChecked)
        self.actionRun =  createAction(self,"&Run", "", 
                                  "fork", "", True)
        self.actionRun.toggled.connect(player.runTrough)
        player.running.connect(self.actionRun.setChecked)
        self.actionRew = createAction(self,"&Rewind", "", 
                                 "media-seek-backward", "")
        self.actionRew.triggered.connect(player.seekRew)
        self.actionFwd = createAction(self,"&Forward", "", 
                                 "media-seek-forward", "")
        self.actionFwd.triggered.connect(player.seekFwd)
        self.actions = (self.actionOpenVideo,self.actionCaptureVideo,self.actionCaptureClose,None,
                             self.actionPlay,self.actionRun,None,
                             self.actionRew, self.actionFwd)
        
        # Video slider and position label
        layout1 = QtGui.QHBoxLayout()
        self.startFrameSpinBox = QtGui.QSpinBox()
        layout1.addWidget(self.startFrameSpinBox)
        self.videoSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        layout1.addWidget(self.videoSlider)
        self.timeLabel = QtGui.QLabel('0')
        layout1.addWidget(self.timeLabel)
        self.endFrameSpinBox = QtGui.QSpinBox()
        layout1.addWidget(self.endFrameSpinBox)
        self.videoSlider.valueChanged.connect(self.videoSliderMove)  
        self.videoSlider.sliderMoved.connect(player.seek)
        #     
        layout2 = QtGui.QHBoxLayout()
        rewButton = ActionButton(self.actionRew)
        layout2.addWidget(rewButton)
        playButton = ActionButton(self.actionPlay)
        layout2.addWidget(playButton)
        fwdButton = ActionButton(self.actionFwd)
        layout2.addWidget(fwdButton)
        runTroughButton = ActionButton(self.actionRun)
        layout2.addWidget(runTroughButton)
        # Speed
        self.speedLabel = QtGui.QLabel('Speed:')
        layout2.addWidget(self.speedLabel)
        self.speedSpinBox = QtGui.QDoubleSpinBox()
        layout2.addWidget(self.speedSpinBox)
        self.speedLabel.setBuddy(self.speedSpinBox)
        self.speedSpinBox.valueChanged.connect(player.setSpeed)
        self.speedSpinBox.setMinimum(0.2)
        self.speedSpinBox.setMaximum(2.0)
        self.speedSpinBox.setValue(1.0) 
        layout2.addStretch()
        # Open and capture video buttons
        videoOpenButton = ActionButton(self.actionOpenVideo)
        layout2.addWidget(videoOpenButton)
        videoCaptureButton = ActionButton(self.actionCaptureVideo)
        layout2.addWidget(videoCaptureButton)
        # Main Layout
        layout = QtGui.QVBoxLayout()
        layout.addLayout(layout1)
        layout.addLayout(layout2)
        self.setLayout(layout)
        # Creating sets to enable/disable GUI elements
        self.playSet = set([self.videoSlider, self.actionPlay,
                           self.actionRew, self.actionFwd, self.actionRun])
        self.setGuiEnabled(False)
    
    @QtCore.pyqtSlot()
    def openVideoFile(self):
        '''
        Open video file
        '''
        # Setting last user directory
        directory = QtCore.QFileInfo(self.player.videoFileName).path() 
        # Creating formats list
        formats = ["*.{}".format(unicode(videoFormat)) \
                   for videoFormat in videoFormats]
        # Executing standard open dialog
        fname = QtGui.QFileDialog.getOpenFileName(self,
                        "Choose video file",
                        directory, "Video files ({})".format(" ".join(formats)))
        if not fname.isEmpty() :
            self.signalCaptureFromFile.emit(fname)
    
    @QtCore.pyqtSlot()
    def captureVideo(self):
        self.signalCaptureFromCam.emit(0)
    
    def setGuiEnabled(self, flag):
        for elem in self.playSet :
            elem.setEnabled(flag)
            
    @QtCore.pyqtSlot(int, float)  
    def videoSourceOpen(self, videoLength, frameRate):
        '''
        Calling this method when video opened
        '''
        if videoLength > 0 :
            self.startFrameSpinBox.setValue(0)
            self.startFrameSpinBox.setMaximum(videoLength-1)
            self.endFrameSpinBox.setMaximum(videoLength)
            self.endFrameSpinBox.setValue(videoLength)
            self.videoSlider.setMaximum(videoLength)
            self.videoSlider.setValue(0)
        self.setGuiEnabled(videoLength > 0)
    
    @QtCore.pyqtSlot()
    def videoSourceClose(self):
        self.setGuiEnabled(False)
    
    @QtCore.pyqtSlot(object, int)
    def nextFrame(self, frame, frameNumber):
        self.videoSlider.setValue(frameNumber)
    
    @QtCore.pyqtSlot(int)
    def videoSliderMove(self, value):
        self.timeLabel.setText(str(value))
