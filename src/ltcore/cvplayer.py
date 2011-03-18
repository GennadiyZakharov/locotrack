'''
Created on 18.03.2011

@author: Gena
'''

import cv
from PyQt4 import QtCore
from ltcore.signals import *

class CvPlayer(QtCore.QObject):
    '''
    Video Player using opencv interface
    can play,stop and seek video
    '''


    def __init__(self,parent=None):
        '''
        Constructor
        '''
        super(CvPlayer, self).__init__(parent)
        
        self.on_captureClose()
        self.frameRate = 5
        
    def on_captureFromFile(self,filename):
        if self.captureDevice is not None :
            self.on_captureClose()
        self.captureDevice = cv.CaptureFromFile(filename)
        if self.captureDevice is None :
            return # Error opening file
        self.fileName = filename
        self.videoLength = cv.GetCaptureProperty(self.captureDevice, 
                                                cv.CV_CAP_PROP_FRAME_COUNT)
        print 'Opened file:',self.fileName
        print 'File length:',int(self.videoLength),'frames'
        self.emit(signalCvPlayerCapturing,self.videoLength)
        self.timerEvent(None)
    
    def on_captureFromCam(self,camNumber):
        if self.captureDevice is not None :
            self.on_captureClose()
        
    
    def on_captureClose(self):
        self.fileName=None
        self.captureDevice=None
        self.videoLength=None
        
    def on_Play(self):
        if self.captureDevice is not None :
            self.timer=self.startTimer(1000/self.frameRate)
        
    def on_Stop(self):
        if self.timer is not None :
            self.killTimer(self.timer)
        
    def on_Rew(self):
        pass
    
    def on_Fwd(self):
        pass
    
    def on_Seek(self,value):
        if self.captureDevice is not None :
            cv.SetCaptureProperty(self.captureDevice, cv.CV_CAP_PROP_POS_FRAMES, value)
    
    def on_BrightnessChanged(self,value):
        if self.captureDevice is not None :
            cv.SetCaptureProperty(self.captureDevice, cv.CV_CAP_PROP_BRIGHTNESS, value)
            
    def on_ContrastChanged(self,value):
        if self.captureDevice is not None :
            cv.SetCaptureProperty(self.captureDevice, cv.CV_CAP_PROP_CONTRAST, value)
    #
    def timerEvent(self,event) :
        frame=cv.QueryFrame(self.captureDevice)
        if frame is None :
            self.on_Stop()
        else :
            self.emit(signalNextFrame,frame)
            
            