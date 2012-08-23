'''
Created on 18.03.2011
@author: Gena
'''

from __future__ import division
import cv
from PyQt4 import QtCore

class CvPlayer(QtCore.QObject):
    '''
    This class implements video player using openCV interface
    '''
    # Player signals
    nextFrame         = QtCore.pyqtSignal(object, int)
    ''' Signal carry frame and frame number  '''
    videoSourceOpened = QtCore.pyqtSignal(int, float)
    ''' Signal carry video length and frame rate when video opened,
        or -1, -1 when video closed '''
    videoEnd = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(CvPlayer, self).__init__(parent)
        self.playSpeed = 1.0 
        self.timer = None   # Timer to extract frames from 
        self.frameRate = 5.0  
        self.captureClose() # Reset capture values
    
    @QtCore.pyqtSlot()
    def captureClose(self):
        '''
        Close video source
        '''
        self.stop()                   # Reset timer and runTroughFlag
        self.fileName = None          # No File opened
        self.captureDevice = None     # No device for capturing
        self.videoFileLength = None   # Length of video file
        self.frameNumber = None       # No number for current frame
        self.videoSourceOpened.emit(-1,-1)
    
    @QtCore.pyqtSlot()    
    def stop(self):
        '''
        Stop playing
        '''
        self.runTroughFlag = False     # This flag is used to process frames at maximum speed
        if self.timer is not None :    # We have active timer
            self.killTimer(self.timer) # Stop timer
            self.timer = None          # And now we have no timer
        
    @QtCore.pyqtSlot(str)
    def captureFromFile(self, fileName):
        '''
        Open video file for capturing
        '''
        if self.captureDevice is not None : # Now we have active capture device
            self.captureClose()    
        self.captureDevice = cv.CaptureFromFile(fileName) # Try to open file
        if self.captureDevice is None : # Error opening file
            #TODO: error report 
            return 
        self.fileName = fileName # Store file name
        # Get video parameters
        self.videoFileLength = cv.GetCaptureProperty(self.captureDevice,
                                                     cv.CV_CAP_PROP_FRAME_COUNT)
        self.frameRate = cv.GetCaptureProperty(self.captureDevice,
                                               cv.CV_CAP_PROP_FPS)
        print 'Opened file: '+self.fileName
        print 'File length {} frames, {:5.2f} fps'.format(self.videoFileLength, self.frameRate) 
        self.videoSourceOpened.emit(self.videoFileLength, self.frameRate)
        self.seekInterval = self.videoFileLength // 50
        self.timerEvent() # Process first frame
    
    @QtCore.pyqtSlot(int)
    def captureFromCam(self, camNumber):
        '''
        Open video camera
        '''
        if self.captureDevice is not None :
            self.captureClose()
        #TODO: implement capture from cam
    
    @QtCore.pyqtSlot()   
    def play(self):
        '''
        Start playing with fixed speed by timer
        '''
        if self.captureDevice is None : 
            return
        # Stop runTrough, if it was active
        self.runTroughFlag = False
        if self.timer is None :
            # Creating timer
            self.timer = self.startTimer(1000 / (self.frameRate* self.playSpeed))
         
    @QtCore.pyqtSlot()       
    def runTrough(self):
        '''
        Play file at maximum speed
        '''
        if self.captureDevice is None : 
            return
        self.stop() # Stop playing timer, if it was active
        self.runTroughFlag = True
        while self.runTroughFlag :
            self.timerEvent() # Capture next frame
            QtCore.QCoreApplication.processEvents() # Allow system to process signals
    
    @QtCore.pyqtSlot()       
    def seekRew(self):
        '''
        Revind. Sometimes video rewinds by 100-200 frames due to
        video encoding algoritm
        '''
        position = self.frameNumber-self.seekInterval
        if position >=0 : 
            self.seek(position)
    
    @QtCore.pyqtSlot()
    def seekFwd(self):
        '''
        seek forward
        '''
        position = self.frameNumber+self.seekInterval
        if position < self.videoFileLength : 
            self.seek(position)
    
    @QtCore.pyqtSlot(int)
    def seek(self, frameNumber):
        '''
        Seek to frame frameNumber
        '''
        if self.captureDevice is None :
            return
        if frameNumber == self.frameNumber :
            return
        cv.SetCaptureProperty(self.captureDevice, cv.CV_CAP_PROP_POS_FRAMES, frameNumber)
        self.timerEvent()
    
    @QtCore.pyqtSlot(float)
    def setSpeed(self, speed):
        self.playSpeed = speed
        if self.timer is not None :
            self.stop()
            self.play()
            
    def timerEvent(self, event=None) :
        '''
        Event from timer
        It is called to capture next frame from video device
        '''    
        frame = cv.QueryFrame(self.captureDevice)
        if frame is None : # Input file ended
            self.stop()
            self.videoEnd.emit()
        else :
            self.frameNumber = int(cv.GetCaptureProperty(self.captureDevice, cv.CV_CAP_PROP_POS_FRAMES))
            self.nextFrame.emit(frame, self.frameNumber)
    