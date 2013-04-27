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
     playing : self.playTimer is not None
     run     : self.runTimer is not None
     stop    : none of this
     
    '''
    # == Constants
    objectCaption = '[cvPlayer]\n'
    
    # == Player signals
    # Controls
    playing = QtCore.pyqtSignal(bool) # Emits when player starts
    running = QtCore.pyqtSignal(bool) # Emits when running at max speed
    # Video
    videoSourceOpened = QtCore.pyqtSignal(int, float, QtCore.QString) # video length (in frames) and frame rate
    videoSourceClosed = QtCore.pyqtSignal() # Video closed
    videoSourceEnded  = QtCore.pyqtSignal()  # End of file reached
    # Frame process
    nextFrame = QtCore.pyqtSignal(object, int) # Signal carry frame and frame number
    
    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(CvPlayer, self).__init__(parent)
        self.playSpeed = 1.0 #
        self.playTimer = None # Timer to extract frames
        self.runTimer = None # Timer to extract frames at max speed
        self.frameRate = -1           # frameRate, -1 for none 
        self.frameNumber = -1         # corent frame Nomber, -1 for none
        self.videoFileName = QtCore.QString()        # No File opened
        self.captureDevice = None      # No device for capturing
        self.videoFileLength = -1      # Length of video file, -1 for none
        self.seekInterval = 10         # Default seek interval
        self.leftBorder = 0           # Borders of playing interval 
        self.rightBorder = 0
        
    @classmethod
    def loadFromFile(cls, inputFile):
        '''
        Load all player settings from file, opened for reading
        '''
        #TODO: implement
        player = cls()
        return player
    
    def saveToFile(self, outputFile):
        '''
        Save all player settings to file, opened for writing
        '''
        #TODO:  implement
        if self.videoFileName is None :
            return
        outputFile.write(self.objectCaption)
        outputFile.write(self.videoFileName + '\n')    
        outputFile.write(str(self.playSpeed) + '\n')
        outputFile.write(str(self.frameNumber) + '\n')
    
    def isPlaying(self):
        return self.playTimer is not None
    
    def isRunning(self):
        return self.runTimer is not None
    
    def startPlayTimer(self):
        '''
        Start playing playTimer at current speed
        '''
        self.stopPlayTimer() # Killing active playTimer, if it exists
        self.playTimer = self.startTimer(1000 / (self.frameRate * self.playSpeed))
        
    def stopPlayTimer(self):
        '''
        Killing playTimer, if it was active
        '''
        if self.isPlaying() :    # We have active playTimer
            self.killTimer(self.playTimer) # Stop playTimer
            self.playTimer = None          # And now we have no playTimer
            
    def startRunTimer(self):
        '''
        Start runTimer at maximum speed
        '''
        self.stopRunTimer() # Killing active playTimer, if it exists
        self.runTimer = self.startTimer(0)
        
    def stopRunTimer(self):
        '''
        Killing playTimer, if it was active
        '''
        if self.isRunning() :    # We have active playTimer
            self.killTimer(self.runTimer) # Stop playTimer
            self.runTimer = None          # And now we have no playTimer
    
    @QtCore.pyqtSlot(QtCore.QString)
    def captureFromFile(self, fileName):
        '''
        Open video file for capturing
        '''
        self.captureClose()    
        self.captureDevice = cv.CaptureFromFile(unicode(fileName)) # Try to open file
        if self.captureDevice is None : # Error opening file
            #TODO: error report 
            print "Error opening vide file {}".format(fileName)
            return 
        self.videoFileName = fileName # Store file name
        # Get video parameters
        self.videoFileLength = int(cv.GetCaptureProperty(self.captureDevice,
                                                     cv.CV_CAP_PROP_FRAME_COUNT))
        self.frameRate = cv.GetCaptureProperty(self.captureDevice,
                                               cv.CV_CAP_PROP_FPS)
        self.seekInterval = self.videoFileLength // 50
        self.setLeftBorder(0)           # Borders of playing interval 
        self.setRightBorder(self.videoFileLength)
        #TODO: do as message
        print 'Opened file: ' + self.videoFileName
        print 'File length {} frames, {:5.2f} fps'.format(self.videoFileLength, self.frameRate) 
        self.timerEvent() # Process first frame
        self.videoSourceOpened.emit(self.videoFileLength, self.frameRate, self.videoFileName)       
          
    @QtCore.pyqtSlot(int)
    def captureFromCam(self, camNumber):
        '''
        Start capturing from video camera
        '''
        self.captureClose()
        self.captureDevice = cv.CaptureFromCAM(camNumber)
        #TODO: implement
        if self.captureDevice is None :
            #TODO: error report
            print "Error opening video cam number {}".format(camNumber)
            return
        self.frameRate = cv.GetCaptureProperty(self.captureDevice,
                                               cv.CV_CAP_PROP_FPS)
        self.timerEvent()
        self.videoSourceOpened.emit(-1, self.frameRate, 'Cam'+str(camNumber))
     
    @QtCore.pyqtSlot()
    def captureClose(self):
        '''
        Close video source
        '''
        if self.captureDevice is None :
            return # Nothing to do               
        self.stopPlayTimer()
        self.stopRunTimer()
        self.videoFileName = QtCore.QString() # No File opened
        self.captureDevice = None   # No device for capturing
        self.videoFileLength = -1   # Length of video file
        self.frameRate = -1         # 
        self.frameNumber = -1       # No number for current frame
        self.setLeftBorder(0)           # Borders of playing interval 
        self.setRightBorder(0)
        self.seekInterval = 0
        self.videoSourceClosed.emit()
         
    @QtCore.pyqtSlot(bool)   
    def play(self, checked):
        '''
        Start playing with fixed speed by playTimer
        '''
        if self.isPlaying() == checked : 
            return # Nothing to do
        if self.captureDevice is None : # No device to play from
            self.playing.emit(False)    
            return
        self.runTrough(False)
        if checked : # Start playback
            # Creating playTimer
            self.startPlayTimer()
        else : # Stop playback
            self.stopPlayTimer()
        self.playing.emit(self.isPlaying()) # Report about playing state
         
    @QtCore.pyqtSlot(bool)      
    def runTrough(self, checked):
        '''
        Play video at maximum speed
        '''
        if self.isRunning() == checked :
            return # Nothing to do
        if self.captureDevice is None : # No device to play from
            self.running.emit(False) 
            return
        if self.videoFileLength == -1 : # Running not allowed on webcam
            self.running.emit(False)
            return
        self.play(False) # Stop playing playTimer, if it was active
        if checked :
            self.startRunTimer()
        else :
            self.stopRunTimer()
        self.running.emit(self.isRunning())

    @QtCore.pyqtSlot()       
    def seekRew(self):
        '''
        Rewind. Sometimes video rewinds by 100-200 frames due to
        video encoding algorithm
        '''
        self.seek(self.frameNumber - self.seekInterval) 
    
    @QtCore.pyqtSlot()
    def seekFwd(self):
        '''
        seek forward
        '''
        self.seek(self.frameNumber + self.seekInterval)
    
    @QtCore.pyqtSlot(int)
    def seek(self, desiredPosition):
        '''
        Seek to frame desiredPosition
        '''
        if desiredPosition == self.frameNumber :
            return
        if self.captureDevice is None : # No device
            # TODO: exception
            return
        if desiredPosition < self.leftBorder :
            position = self.leftBorder
        elif desiredPosition > self.rightBorder :
            position = self.leftBorder
        else :
            position = desiredPosition
        cv.SetCaptureProperty(self.captureDevice, cv.CV_CAP_PROP_POS_FRAMES, position)
        self.timerEvent()
    
    @QtCore.pyqtSlot(float)
    def setSpeed(self, speed):
        '''
        Set playing speed multiplier
        The 1.0 corresponds to normal speed
        '''
        self.playSpeed = speed
        if self.playTimer is not None : # Speed changed during playing
            self.startPlayTimer() # restarting play to set playTimer to different speed
    
    @QtCore.pyqtSlot(int)
    def setLeftBorder(self, leftBorder):
        '''
        set left border of playing interval
        '''
        self.leftBorder = leftBorder
        if self.rightBorder < self.leftBorder:
            self.setRightBorder(self.leftBorder)
       
    @QtCore.pyqtSlot(int)
    def setRightBorder(self, rightBorder):
        '''
        set left border of playing interval
        '''
        self.rightBorder = rightBorder
        if self.leftBorder > self.rightBorder :
            self.setLeftBorder(self.rightBorder)
       
    def timerEvent(self, event=None) :
        '''
        Capture next frame from video device
        '''    
        frame = cv.QueryFrame(self.captureDevice)
        if frame is not None : 
            self.frameNumber = int(cv.GetCaptureProperty(self.captureDevice, cv.CV_CAP_PROP_POS_FRAMES))
            self.nextFrame.emit(frame, self.frameNumber)
        else: # Input file ended
            self.play(False)
            self.runTrough(False)
            self.videoSourceEnded.emit()
    
