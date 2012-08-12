'''
Created on 27.04.2011
@author: Gena
'''

import numpy as np
from ltcore.ltobject import LtObject

class LtTrajectory(object):
    '''
    This class holds object trajectory
    
    It can be represented as array of LtObject, but in python
    this design is really slow and memory-hungry
    
    So, LtTrajectory uses numpy arrays and constructs LtObject when needed
    '''
    
    # String to format data when save to file
    formatString = "{0:10} {1:18.6f} {2:18.6f}\n"

    def __init__(self, startEndFrames=None):
        '''
        Constructor
        Creates array to store ltObjects
        in frame range, given by tuple startEndFrames
        or empty trajectory if startEndFrames in None
        '''
        self.startFrame = -1
        self.endFrame = -1
        # Last recorded frame number
        self.lastNumber = None
        self.saved  = True
        if startEndFrames is not None :
            self.initArray(startEndFrames)    
    
    def initArray(self, startEndFrames):
        '''
        Cteate array to store objects in frame range, given by tuple startEndFrames
        '''
        self.startFrame, self.endFrame = startEndFrames
        # Creating arrays for X and Y Coordinates
        arrayLength = self.endFrame-self.startFrame+1
        self.centralPointX = np.linspace(-1.0, -1.0, arrayLength)
        self.centralPointY = np.linspace(-1.0, -1.0, arrayLength)
        
    
    def frameNumberToInternal(self, frameNumber):
        '''
        Convert frame number to internal number (numpy array)
        '''
        if (frameNumber < self.startFrame) or \
            (frameNumber > self.endFrame)  :
                # TODO: paste exception
                return
        return frameNumber - self.startFrame
    
    def internalToFrameNumber(self, internal):
        '''
        Convert internal number to frame number
        '''
        return internal + self.startFrame
    
    def setObject(self, frameNumber, ltObject):
        '''
        Store ltObject on frame number
        '''
        internalNumber = self.frameNumberToInternal(frameNumber)
        self.lastNumber = internalNumber
        self.centralPointX[internalNumber], self.centralPointY[internalNumber] = ltObject.massCenter
        
    def lastObject(self):
        '''
        Return last stored ltObject 
        '''
        return LtObject(self.CenterPointX[self.lastNumber], self.centralPointY[self.lastNumber])
    
    def rstrip(self):
        '''
        Strip all useless points from end of trajectory 
        '''
        for i in xrange(len(self.centralPointX)-1,-1,-1) :
            if self.centralPointX[i] >=0 :
                self.centralPointX = self.centralPointX[:i+1]
                self.centralPointY = self.centralPointY[:i+1]
                self.endFrame = self.internalToFrameNumber(i)
                return
    
    def loadFromFile(self, trajectoryFile):
        '''
        Load trajectory from text file
        '''
        line = trajectoryFile.readLine()
        startFrame, endFrame = [float(value) for value in line.split()]
        self.initArray((startFrame, endFrame))
        for line in trajectoryFile :
            values = line.split()
            frameNumber = int(values[0])
            x = float(values[1])
            y = float(values[2])
            internalNumber = self.frameNumberToInternal(frameNumber)
            self.centralPointX[internalNumber], self.centralPointY[internalNumber] = x,y
        self.lastNumber = frameNumber         
    
    def saveToFile(self, trajectoryFile):
        '''
        Save trajectory to text file
        '''
        trajectoryFile.write("{} {}\n".format(self.startFrame, self.endFrame))
        trajectoryFile.write("     Frame                  X                  Y\n")
        
        for i in xrange(self.startFrame, self.endFrame+1) :
            fileString = self.formatString.format(i,
                                     self.centralPointX[self.frameNumberToInternal(i)], 
                                     self.centralPointY[self.frameNumberToInternal(i)])
            trajectoryFile.write(fileString)
        
if __name__ == '__main__':
    '''
    Selt testing
    '''
    pass
