'''
Created on 27.04.2011
@author: Gena
'''
from __future__ import division

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

    def __init__(self, startEndFrames):
        '''
        Constructor
        Creates array to store ltObjects
        in frame range, given by tuple startEndFrames
        or empty trajectory if startEndFrames in None
        '''
        # Last recorded frame number
        self.lastNumber = None
        self.saved  = True
        self.initArray(startEndFrames)    
    
    def initArray(self, startEndFrames):
        '''
        Cteate array to store objects in frame range, given by tuple startEndFrames
        '''
        self.startFrame, self.endFrame = startEndFrames
        # Creating arrays for X and Y Coordinates
        arrayLength = self.len()
        self.cpX = np.linspace(-1.0, -1.0, arrayLength)
        self.cpY = np.linspace(-1.0, -1.0, arrayLength)
    
    def len(self):
        return self.endFrame-self.startFrame+1
      
    def expand(self, startFrame, endFrame):
        start = min(startFrame, self.startFrame)
        end = max(endFrame, self.endFrame)
        newX, newY = self.initArray(start, end)
        internalS = self.frameNumberToInternal(self.startFrame)
        internalE = self.frameNumberToInternal(self.endFrame)
        newX[:] = self.cpX[:]
        newY[:] = self.cpY[:]
        
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
    
    def getXY(self, frameNumber):
        internalNumber = self.frameNumberToInternal(frameNumber)
        return self.cpX[internalNumber], self.cpY[internalNumber]
    
    def getObject(self, frameNumber):
        '''
        Store ltObject on frame number
        '''
        x,y = self.getXY(frameNumber) 
        if x < 0 :
            return None
        return LtObject((x,y))
    
    def setObject(self, frameNumber, ltObject):
        '''
        Store ltObject on frame number
        '''
        internalNumber = self.frameNumberToInternal(frameNumber)
        self.lastNumber = internalNumber
        self.cpX[internalNumber], self.cpY[internalNumber] = ltObject.massCenter
        
    def lastObject(self):
        '''
        Return last stored ltObject 
        '''
        return LtObject(self.CenterPointX[self.lastNumber], self.cpY[self.lastNumber])
    
    def rstrip(self):
        '''
        Strip all useless points from end of trajectory 
        '''
        for i in xrange(len(self.cpX)-1,-1,-1) :
            if self.cpX[i] >=0 :
                self.cpX = self.cpX[:i+1]
                self.cpY = self.cpY[:i+1]
                self.endFrame = self.internalToFrameNumber(i)
                return
    
    @classmethod
    def loadFromFile(cls, trajectoryFile):
        '''
        Load trajectory from text file
        ''' 
        startFrame, endFrame = [int(value) for value in trajectoryFile.readline().split()]
        trajectory = cls((startFrame,endFrame))
        trajectoryFile.readline()
        for line in trajectoryFile :
            values = line.split()
            frameNumber = int(values[0])
            x = float(values[1])
            y = float(values[2])
            internalNumber = trajectory.frameNumberToInternal(frameNumber)
            trajectory.cpX[internalNumber], trajectory.cpY[internalNumber] = x,y
        trajectory.lastNumber = frameNumber
        return trajectory         
    
    def saveToFile(self, trajectoryFile):
        '''
        Save trajectory to text file
        '''
        trajectoryFile.write("{} {}\n".format(self.startFrame, self.endFrame))
        trajectoryFile.write("     Frame                  X                  Y\n")
        
        for i in xrange(self.startFrame, self.endFrame+1) :
            fileString = self.formatString.format(i,
                                     self.cpX[self.frameNumberToInternal(i)], 
                                     self.cpY[self.frameNumberToInternal(i)])
            trajectoryFile.write(fileString)
            
    def getStartEndFrame(self):
        return (self.startFrame,self.endFrame)
    
    def smooth(self):
        '''
        '''
        length = self.len()
        X = np.zeros(length)
        Y = np.zeros(length)
        for n in xrange(1,length-1) :
            X[n]= 1/4 * self.cpX[n-1] + 1/2 * self.cpX[n] + 1/4 * self.cpX[n+1]
            Y[n]= 1/4 * self.cpY[n-1] + 1/2 * self.cpY[n] + 1/4 * self.cpY[n+1]
        X[0],Y[0] = self.cpX[0],self.cpY[0]
        X[length-1],Y[length-1] = self.cpX[length-1],self.cpY[length-1]
        self.cpX = X
        self.cpY = Y
        
if __name__ == '__main__':
    '''
    Self testing
    '''
    trajFile = open('/home/gena/eclipse37-workspace/locotrack/video/2012-02-22_agn-F-Ad7-N-02_c.avi.traj')
    trajectory = LtTrajectory.loadFromFile(trajFile)
    print trajectory.getStartEndFrame()
