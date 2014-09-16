'''
Created on 09.10.2013

@author: gena
'''
from __future__ import division
from __future__ import print_function
from math import sqrt
from PyQt4 import QtCore, QtGui

class ErrorDetector(QtCore.QObject):
    '''
    This class implements error detector
    
    Error frame is detected by several critheria:
     1 -- no object detected
     2 -- moving distance is bigger, than lenthThreshold (usuallu hals of animal size)
          AND speed between two frames is bigger, then spedThreshold
          
    Error frame is marked as "No object"     
    If object lost for period bigger, than maxMissedIntervalDuration, 
    record is errous 
    
    '''
    errorNoErrors = 0
    errorTooLongMissedInterval = -1
    errorTooMuchMissedIntervals = -2
    
    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(ErrorDetector, self).__init__(parent)
        self.maxMissedIntervalDuration = 2.0 # Seconds
        self.maxMissedIntervalCount = 5
        self.objectLengthThreshold = 1.0 # mm
        self.errorSpeedThreshold = 50.0 # mm/s

    @QtCore.pyqtSlot(float)
    def setMaxMissedIntervalDuration(self, value):
        self.maxMissedIntervalDuration = value
    
    @QtCore.pyqtSlot(int)
    def setMaxMissedIntervalCount(self, value):
        self.maxMissedIntervalCount = value
    
    @QtCore.pyqtSlot(float)
    def setObjectLengthThreshold(self, value):
        self.objectLengthThreshold = value
        
    @QtCore.pyqtSlot(float)
    def setErrorSpeedThreshold(self, value):
        self.errorSpeedThreshold = value
        
    def checkForErrors(self, trajectory, scale, frameRate):
        '''
        Check trajectory for errors 
        and return 0 if trajectory suitable for analysis
        '''
        self.missedFramesCount = 0  # Number of bad frames 
        self.missedIntervalsCount = 0  
        
        def incErrorFrame():
            # Check, if we start new missed interval
            if self.missedFramesCount == 0:
                self.missedIntervalsCount += 1
                if self.missedIntervalsCount > self.maxMissedIntervalCount :
                    return self.errorTooMuchMissedIntervals
            self.missedFramesCount += 1
            if self.missedFramesCount / frameRate >= self.maxMissedIntervalDuration :
                return self.errorTooLongMissedInterval
            return self.errorNoErrors
                
        startFrame, endFrame = trajectory.bounds()
        print('bounds', startFrame, endFrame)
        # Start frame always not none (trajectory stripped)
        
        while True :
            ltObject1 = trajectory[startFrame]
            if ltObject1 is not None:
                break
            startFrame +=1
        frame1=startFrame
        # Cycle by all frames
        for frame2 in xrange(startFrame + 1, endFrame):
            ltObject2 = trajectory[frame2]
            if ltObject2 is None :
                print("*** Object not found at frame {}".format(frame2))
                error = incErrorFrame()
                if error != self.errorNoErrors :
                    return error
                continue
                
            x1, y1 = ltObject1.center
            x2, y2 = ltObject2.center
            length = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) / scale
            time = (frame2 - frame1) / frameRate 
            # Check is frame2 buggy
            if (length > self.objectLengthThreshold) and ((length / time) > self.errorSpeedThreshold):  
                # An error -- print error message
                print("*** Speed too much at frame {}".format(frame2))
                trajectory[frame2]=None
                error = incErrorFrame()
                if error != self.errorNoErrors :
                    return error
                # Continue to next frame
                continue
            
            # If we are here -- we found good frame -- missed intervals ended
            if self.missedFramesCount > 0 :
                self.missedFramesCount = 0
            #
            frame1 = frame2
            ltObject1 = ltObject2
            QtGui.QApplication.processEvents()
        # If we here -- trajectory ended, all OK
        return self.errorNoErrors
        