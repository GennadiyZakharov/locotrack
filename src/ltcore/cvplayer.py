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
    with play, stop, and seek functions
    
    player can be in three states
     playing : self.timer is not None
     run   : runTroughFlag == True
     stop  : none of this
     
    '''
    # == Constants
    objectCaption = '[cvPlayer]\n'
    # == Player signals
    # Controls
    playing = QtCore.pyqtSignal(bool)
    running = QtCore.pyqtSignal(bool)
    # Video
    ''' Signal carry video length and frame rate'''
    videoSourceOpened = QtCore.pyqtSignal(int, float)
    videoSourceClosed = QtCore.pyqtSignal()
    videoSourceEnded = QtCore.pyqtSignal()
    # Frame process
    nextFrame         = QtCore.pyqtSignal(object, int)
    ''' Signal carry frame and frame number  '''
    
    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(CvPlayer, self).__init__(parent)
        self.playSpeed = 1.0 
        self.timer = None   # Timer to extract frames from 
        self.frameRate = 5.0  
        self.captureClose() # Reset capture values
    
    @classmethod
    def loadFromFile(cls, inputFile):
        #TODO:
        player = cls()
        return player
    
    def saveToFile(self, outputFile):
        #TODO:
        if self.videoFileName is None :
            return
        outputFile.write(self.objectCaption)
        outputFile.write(self.videoFileName+'\n')    
        outputFile.write(str(self.playSpeed)+'\n')
        outputFile.write(str(self.frameNumber)+'\n')
        
    @QtCore.pyqtSlot()
    def captureClose(self):
        '''
        Close video source
        '''               
        # Reset timer and runTroughFlag
        self.runTroughFlag = False     # This flag is used to process frames at maximum speed
        if self.timer is not None :    # We have active timer
            self.killTimer(self.timer) # Stop timer
            self.timer = None          # And now we have no timer
        self.videoFileName = ''          # No File opened
        self.captureDevice = None     # No device for capturing
        self.videoFileLength = -1   # Length of video file
        self.frameNumber = -1       # No number for current frame
        #self.videoSourceClosed.emit()
        
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
        self.videoFileName = fileName # Store file name
        # Get video parameters
        self.videoFileLength = cv.GetCaptureProperty(self.captureDevice,
                                                     cv.CV_CAP_PROP_FRAME_COUNT)
        self.frameRate = cv.GetCaptureProperty(self.captureDevice,
                                               cv.CV_CAP_PROP_FPS)
        print 'Opened file: '+self.videoFileName
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
    
    @QtCore.pyqtSlot(bool)   
    def play(self, checked):
        '''
        Start playing with fixed speed by timer
        '''
        if (self.timer is not None) == checked :
            return # Nothing to do
        if self.captureDevice is None : 
            self.playing.emit(False)
            return
        if checked :
            # Stop runTrough, if it was active
            if self.runTroughFlag :
                self.runTrough(False)
            # Creating timer
            self.startPlayTimer()
        else :
            self.killTimer(self.timer)
            self.timer = None
        self.playing.emit(self.timer is not None)
         
    @QtCore.pyqtSlot(bool)      
    def runTrough(self, checked=True):
        '''
        Play video at maximum speed
        '''
        if self.runTroughFlag == checked :
            return # Nothing to do
        if self.captureDevice is None :
            self.running.emit(False) # Reset button
            return
        self.runTroughFlag = checked
        if self.runTroughFlag and (self.timer is not None) :
            self.play(False) # Stop playing timer, if it was active
        self.running.emit(self.runTroughFlag)
        
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
        if position < 0 :
            position = 0 
        self.seek(position) 
    
    @QtCore.pyqtSlot()
    def seekFwd(self):
        '''
        seek forward
        '''
        position = self.frameNumber+self.seekInterval
        if position >= self.videoFileLength :
            position = self.videoFileLength -1
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
            # restarting play to set timer to different speed
            self.startPlayTimer()
    
    def startPlayTimer(self):
        if self.timer is not None :
            self.killTimer()
        self.timer = self.startTimer(1000 / (self.frameRate* self.playSpeed))
         
    def timerEvent(self, event=None) :
        '''
        This procedure is called to capture next frame from video device
        '''    
        frame = cv.QueryFrame(self.captureDevice)
        if frame is not None : 
            self.frameNumber = int(cv.GetCaptureProperty(self.captureDevice, cv.CV_CAP_PROP_POS_FRAMES))
            self.nextFrame.emit(frame, self.frameNumber)
        else: # Input file ended
            self.play(False)
            self.runTrough(False)
            self.videoSourceEnded.emit()
    