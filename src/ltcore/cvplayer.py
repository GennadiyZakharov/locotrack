'''
Created on 18.03.2011

@author: Gena
'''
from __future__ import division

import cv
from PyQt4 import QtCore
from ltcore.signals import *


class CvPlayer(QtCore.QObject):
    '''
    Video Player using opencv interface
    can play,stop and seek video
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(CvPlayer, self).__init__(parent)
        
        self.timer = None
        self.batchProcess = None
        self.frameRate = 10
        
        self.on_captureClose()
        
        
    def on_captureFromFile(self, filename):
        if self.captureDevice is not None :
            self.on_captureClose()
        self.captureDevice = cv.CaptureFromFile(filename)
        if self.captureDevice is None :
            return # Error opening file
        self.fileName = filename
        self.videoLength = cv.GetCaptureProperty(self.captureDevice,
                                                cv.CV_CAP_PROP_FRAME_COUNT)
        self.frameRate = cv.GetCaptureProperty(self.captureDevice,
                                                cv.CV_CAP_PROP_FPS)
        self.videoDuration = self.videoLength / self.frameRate
        print 'Opened file:', self.fileName
        print 'File length:', int(self.videoLength), 'frames', self.frameRate, 'fps', 'Duration:', self.videoDuration, ' s' 
        
        self.emit(signalCvPlayerCapturing, self.videoDuration)
        self.timerEvent(None)
    
    def on_captureFromCam(self, camNumber):
        if self.captureDevice is not None :
            self.on_captureClose()
        
    
    def on_captureClose(self):
        self.on_Stop()
        self.fileName = None
        self.captureDevice = None
        self.videoLength = None
        
        #self.emit(signalCvPlayerCapturing,None)
        
    def on_Play(self):
        if (self.captureDevice is not None) and (self.timer is None) :
            self.timer = self.startTimer(1000 / self.frameRate)
        
    def on_Stop(self):
        if self.timer is not None :
            self.killTimer(self.timer)
            self.timer = None
        if self.batchProcess is not None :
            self.batchProcess = None
        
    def on_Rew(self):
        pass
    
    def on_Fwd(self):
        pass
    
    def on_Seek(self, value):
        if self.captureDevice is not None :
            frame = int(value * self.frameRate)
            cv.SetCaptureProperty(self.captureDevice, cv.CV_CAP_PROP_POS_FRAMES, frame)
            self.timerEvent()
    
    def on_BrightnessChanged(self, value):
        if self.captureDevice is not None :
            cv.SetCaptureProperty(self.captureDevice, cv.CV_CAP_PROP_BRIGHTNESS, value)
            
    def on_ContrastChanged(self, value):
        if self.captureDevice is not None :
            cv.SetCaptureProperty(self.captureDevice, cv.CV_CAP_PROP_CONTRAST, value)
    #
    def timerEvent(self, event=None) :
        frame = cv.QueryFrame(self.captureDevice)
        if frame is None :
            self.on_Stop()
        else :
            time = cv.GetCaptureProperty(self.captureDevice,
                                                cv.CV_CAP_PROP_POS_MSEC) / 1000
            self.emit(signalNextFrame, frame, time)
             
    def on_StartBatchProcess(self):
        print 'Batch started'
        self.batchProcess = True
        while self.batchProcess is not None :
            self.timerEvent()
        
            
