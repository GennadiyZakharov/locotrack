'''
Created on 13.12.2010

@author: gena
'''
from PyQt4 import QtCore, QtGui
#from ltcore.actions import LtActions
from ltcore.signals import *
from ltgui.labeledwidgets import *

class VideoWidget(QtGui.QWidget):
    '''
    This class holds GUI for cvPlayer
    '''
    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(VideoWidget, self).__init__(parent)
        # Slider and label
        layout1 = QtGui.QHBoxLayout()
        self.videoSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        layout1.addWidget(self.videoSlider)
        self.timeLabel = QtGui.QLabel('0')
        layout1.addWidget(self.timeLabel)
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
        '''
        # Brightness/Contrast
        layout3 = QtGui.QHBoxLayout()
                
        self.brighnessSlider = LabelledSlider("&Brightness:", QtCore.Qt.Horizontal)
        layout3.addWidget(self.brighnessSlider)      
        self.contrastSlider = LabelledSlider("&Contrast:", QtCore.Qt.Horizontal)
        layout3.addWidget(self.contrastSlider)
        '''
        # Main Layout
        layout = QtGui.QVBoxLayout()
        layout.addLayout(layout1)
        layout.addLayout(layout2)
        #layout.addLayout(layout3)
        self.setLayout(layout)
        #Creating video player actions
        self.connect(self.videoSlider, signalValueChanged, self.videoSliderMove)
             
    def videoCapturing(self, videoLength=None):
        '''
        Calling this method when video opened
        '''
        if videoLength is not None :
            self.videoSlider.setMaximum(int(videoLength))
            self.videoSlider.setValue(0)            
    
    def nextFrame(self, image, time):
        self.videoSlider.setValue(time)
    
    #video source closed
    def videoClosed(self):
        pass
    
    def videoSliderMove(self, value):
        self.timeLabel.setText(str(value))
        
        
        
