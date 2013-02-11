'''
Created on 13.12.2010

@author: gena
'''

from __future__ import division
from PyQt4 import QtCore, QtGui
from ltgui.labeledwidgets import LabelledSlider

class VideoWidget(QtGui.QWidget):
    '''
    This class holds GUI for cvPlayer
    '''
    speedChanged = QtCore.pyqtSignal(float)
    videoSeeked = QtCore.pyqtSignal(int)
    
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
        self.playButt.toggled.connect(player.play)
        player.playing.connect(self.playButt.setChecked)
        layout2.addWidget(self.playButt)
        self.fwdButt = QtGui.QPushButton(">>")
        self.fwdButt.clicked.connect(player.seekFwd)
        layout2.addWidget(self.fwdButt)
        self.runTroughButton = QtGui.QPushButton('Run')
        self.runTroughButton.setCheckable(True)
        self.runTroughButton.toggled.connect(player.runTrough)
        player.running.connect(self.runTroughButton.setChecked)
        layout2.addWidget(self.runTroughButton)
        # Speed
        layout3 = QtGui.QVBoxLayout()
        self.speedLabel = QtGui.QLabel()
        layout3.addWidget(self.speedLabel)
        self.speedSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        layout3.addWidget(self.speedSlider)
        self.speedLabel.setBuddy(self.speedSlider)
        self.speedSlider.valueChanged.connect(self.speedSliderMove)
        layout2.addLayout(layout3) 
        self.speedSlider.setMinimum(2)
        self.speedSlider.setMaximum(20)
        self.speedSlider.setValue(10)   
        # Main Layout
        layout = QtGui.QVBoxLayout()
        layout.addLayout(layout1)
        layout.addLayout(layout2)
        self.setLayout(layout)
        # Creating sets to enable/disable GUI elements
        self.playSet = set([self.videoSlider, self.playButt,
                           self.rewButt, self.fwdButt, self.runTroughButton])
        self.setGuiEnabled(False)
    
    
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
        startFrame = self.startFrameSlider.value()
        if value < startFrame :
            self.videoSlider.setValue(startFrame)
        else :
            endFrame = self.endFrameSlider.value()
            if value > endFrame :
                self.stopButt.click()
                self.videoSlider.setValue(endFrame)
            else :
                self.timeLabel.setText(str(value))
                self.videoSeeked.emit(value)
        
    @QtCore.pyqtSlot(int)
    def speedSliderMove(self, value):
        speed = value/10
        self.speedLabel.setText('Speed: {:2.1f}'.format(speed))
        self.speedChanged.emit(speed)
        
        
        
