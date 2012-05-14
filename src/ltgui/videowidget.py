'''
Created on 13.12.2010

@author: gena
'''

from __future__ import division
from PyQt4 import QtCore, QtGui
#from ltcore.actions import LtActions
#from ltcore.signals import *
from ltgui.labeledwidgets import *

class VideoWidget(QtGui.QWidget):
    '''
    This class holds GUI for cvPlayer
    '''
    speedChanged = QtCore.pyqtSignal(float)
    
    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(VideoWidget, self).__init__(parent)
        # Video slider and position label
        layout1 = QtGui.QHBoxLayout()
        self.videoSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        layout1.addWidget(self.videoSlider)
        self.timeLabel = QtGui.QLabel('0')
        layout1.addWidget(self.timeLabel)
        self.videoSlider.valueChanged.connect(self.videoSliderMove)
        # Play/pause buttons
        layout2 = QtGui.QHBoxLayout()
        self.rewButt = QtGui.QPushButton("<<")
        layout2.addWidget(self.rewButt)
        self.playButt = QtGui.QPushButton("Play")
        layout2.addWidget(self.playButt)
        self.stopButt = QtGui.QPushButton("Stop")
        layout2.addWidget(self.stopButt)
        self.fwdButt = QtGui.QPushButton(">>")
        layout2.addWidget(self.fwdButt)
        self.runTroughButton = QtGui.QPushButton('Run')
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
        self.playSet = set([self.videoSlider, self.playButt, self.stopButt,
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
            self.videoSlider.setMaximum(videoLength)
            self.videoSlider.setValue(0)
        self.setGuiEnabled(videoLength > 0)
            
    
    @QtCore.pyqtSlot(object, int)
    def nextFrame(self, frame, frameNumber):
        self.videoSlider.setValue(frameNumber)
    
    @QtCore.pyqtSlot(int)
    def videoSliderMove(self, value):
        self.timeLabel.setText(str(value))
        
    @QtCore.pyqtSlot(int)
    def speedSliderMove(self, value):
        speed = value/10
        self.speedLabel.setText('Speed: {:2.1f}'.format(speed))
        self.speedChanged.emit(speed)
        
        
        
