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
    This class implements video player using openCV interface
    It can extract frames from file or video capturing device
    '''
    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(CvPlayer, self).__init__(parent)
        self.timer = None
        self.frameRate = 10
        self.captureClose()     

    def captureClose(self):
        '''
        Close video source
        '''
        self.stop()
        self.fileName = None
        self.captureDevice = None
        self.videoLength = None
        self.frameNumber = None       
        #self.emit(signalCvPlayerCapturing, None)
        
    def captureFromFile(self, fileName):
        '''
        Open file for capturing
        '''
        if self.captureDevice is not None :
            self.captureClose()    
        self.captureDevice = cv.CaptureFromFile(fileName)
        if self.captureDevice is None :
            #self.emit(signalCvPlayerCapturing, -1)
            return # Error opening file
        self.fileName = fileName
        self.videoLength = cv.GetCaptureProperty(self.captureDevice,
                                                cv.CV_CAP_PROP_FRAME_COUNT)
        self.frameRate = cv.GetCaptureProperty(self.captureDevice,
                                                cv.CV_CAP_PROP_FPS)
        print 'Opened file:', self.fileName
        print 'File length:', int(self.videoLength), 'frames', self.frameRate, 'fps' 
        
        self.emit(signalCvPlayerCapturing, self.videoLength, self.frameRate)
        self.timerEvent() # Process first frame
    
    def captureFromCam(self, camNumber):
        '''
        Open video capturing device
        '''
        if self.captureDevice is not None :
            self.captureClose()
        #TODO: implement capture from cam
    
        
    def play(self):
        '''
        Start extracting frames by timer
        '''
        if (self.captureDevice is not None) and (self.timer is None) :
            self.timer = self.startTimer(1000 / self.frameRate)
        
    def stop(self):
        '''
        Stop playing by timer
        '''
        if self.timer is not None :
            self.killTimer(self.timer)
            self.timer = None
        
    def seekRew(self):
        #TODO: implement
        pass
    
    def seekFwd(self):
        #TODO: implement
        pass
    
    def onSeek(self, frameNumber):
        '''
        Seek to frame number
        '''
        #TODO: fix
        if self.captureDevice is None :
            return
        if frameNumber == self.frameNumber :
            return
        cv.SetCaptureProperty(self.captureDevice, cv.CV_CAP_PROP_POS_FRAMES, frameNumber)
        self.timerEvent()
    
    def setBrightness(self, value):
        if self.captureDevice is not None :
            cv.SetCaptureProperty(self.captureDevice, cv.CV_CAP_PROP_BRIGHTNESS, value)
            
    def setContrast(self, value):
        if self.captureDevice is not None :
            cv.SetCaptureProperty(self.captureDevice, cv.CV_CAP_PROP_CONTRAST, value)
    #
    def timerEvent(self, event=None) :
        '''
        Event from timer
        It is called to capture next frame from video device
        '''
        self.frameNumber = int(cv.GetCaptureProperty(self.captureDevice, cv.CV_CAP_PROP_POS_FRAMES))
        frame = cv.QueryFrame(self.captureDevice)
        if frame is None :
            self.stop()
        else :
            self.emit(signalNextFrame, frame, self.frameNumber)
