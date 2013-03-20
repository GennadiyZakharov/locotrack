'''
Created on 13.12.2010

@author: gena
'''

from __future__ import division
from PyQt4 import QtCore, QtGui
from ltcore.ltactions import createAction 
from ltgui.actionbutton import ActionButton
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
        rewButton = ActionButton(self.actionRew)
        layout2.addWidget(rewButton)
        playButton = ActionButton(self.actionPlay)
        layout2.addWidget(playButton)
        fwdButton = ActionButton(self.actionFwd)
        layout2.addWidget(fwdButton)
        runTroughButton = ActionButton(self.actionRun)
        layout2.addWidget(runTroughButton)
        # Speed
        
        #layout3 = QtGui.QVBoxLayout()
        self.speedLabel = QtGui.QLabel('Speed:')
        layout2.addWidget(self.speedLabel)
        self.speedSlider = QtGui.QDoubleSpinBox()
        layout2.addWidget(self.speedSlider)
        self.speedLabel.setBuddy(self.speedSlider)
        self.speedSlider.valueChanged.connect(player.setSpeed)
        self.speedSlider.setMinimum(0.2)
        self.speedSlider.setMaximum(2.0)
        self.speedSlider.setValue(1.0)
        #layout2.addLayout(layout3) 
        layout2.addStretch()
        #
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
