'''
Created on 27.04.2011
@author: Gena
'''
from __future__ import division

import numpy as np
from ltcore.ltobject import LtObject
from PyQt4 import QtCore

class LtTrajectory(object):
    '''
    This class holds object trajectory
    
    It can be represented as array of LtObject, but in python
    this design is really slow and memory-hungry
    
    So, LtTrajectory uses numpy arrays and constructs LtObject when needed
    '''
    
    # String to format data when save to file
    formatString = "{:10} {:18.6f} {:18.6f}\n"

    def __init__(self, startFrame, endFrame, cpX=None,cpY=None):
        '''
        Constructor
        Creates array to store ltObjects
        in frame range, given by startFrame and EndFrame
        
        Trajectory cannot be empty
        '''
        self.saved  = True
        self.startFrame, self.endFrame = startFrame, endFrame
        # Creating arrays for X and Y Coordinates
        arrayLength = self.endFrame-self.startFrame+1
        if cpX is None :
            self.cpX = np.linspace(-1.0, -1.0, arrayLength)
            self.cpY = np.linspace(-1.0, -1.0, arrayLength)
        else:
            if len(cpX)!=arrayLength :
                #TODO: raise exception
                return
            self.cpX = cpX[:]
            self.cpY = cpY[:] 
    
    def __len__(self):
        return len(self.cpX)
     
    def __iter__(self) :
        self.current = 0
        return self    
    
    def next(self):
        if self.current >= len(self.cpX) :
            raise StopIteration
        else:
            x,y = self.cpX[self.current], self.cpY[self.current]
            self.current += 1
            return LtObject((x,y)) if x>=0 else None
    
    def length(self):
        return self.__len__()
    
    def __setitem__(self, index, value):
        '''
        Store ltObject on frame number
        '''
        internalNumber = self.frameToInternal(index)
        x,y = value.massCenter if value is not None else (-1,-1)
        self.cpX[internalNumber], self.cpY[internalNumber] = x,y
        
    
    def __getitem__(self, index):
        '''
        Get ltObject stored on frame number
        '''
        if index < self.startFrame :
            return None
        elif index > self.endFrame:
            return None
        x,y = self.getXY(index) 
        return LtObject((x,y)) if x >= 0 else None
         
    def frameToInternal(self, frameNumber):
        '''
        Convert frame number to internal number (numpy array)
        '''
        if (frameNumber < self.startFrame) or \
            (frameNumber > self.endFrame)  :
                # TODO: paste exception
                return
        return frameNumber - self.startFrame
    
    def internalToFrame(self, internal):
        '''
        Convert internal number to frame number
        '''
        return internal + self.startFrame
    
    def lastLine(self):
        pass
    
    def getXY(self, frameNumber):
        internalNumber = self.frameToInternal(frameNumber)
        return (self.cpX[internalNumber], self.cpY[internalNumber])
    
    def rstrip(self):
        '''
        Strip all useless points from end of trajectory 
        '''
        for i in xrange(len(self.cpX)-1,-1,-1) :
            if self.cpX[i] >=0 :
                self.cpX = self.cpX[:i+1]
                self.cpY = self.cpY[:i+1]
                self.endFrame = self.internalToFrame(i)
                return
            
    def lstrip(self):
        '''
        Strip all useless points from beginning of trajectory 
        '''
        for i in xrange(len(self.cpX)) :
            if self.cpX[i] >=0 :
                self.cpX = self.cpX[i:]
                self.cpY = self.cpY[i:]
                self.startFrame = self.internalToFrame(i)
                return
    def strip(self):
        self.lstrip()
        self.rstrip()
    
    @classmethod
    def loadFromFile(cls, trajectoryFile):
        '''
        Load trajectory from text file, opened for reading
        ''' 
        startFrame, endFrame = [int(value) for value in trajectoryFile.readline().split()]
        trajectory = cls(startFrame,endFrame)
        trajectoryFile.readline()
        for line in trajectoryFile :
            values = line.split()
            frameNumber = int(values[0])
            x = float(values[1])
            y = float(values[2])
            internalNumber = trajectory.frameToInternal(frameNumber)
            trajectory.cpX[internalNumber], trajectory.cpY[internalNumber] = x,y
        return trajectory         
    
    def smoothed(self):
        trajectory = LtTrajectory(self.startFrame,self.endFrame,self.cpX,self.cpY)
        trajectory.smoothLinear()
        return trajectory
    
    def saveToFile(self, trajectoryFile):
        '''
        Save trajectory to text file
        '''
        trajectoryFile.write("{} {}\n".format(self.startFrame, self.endFrame))
        trajectoryFile.write("     Frame                  X                  Y\n")
        
        for i in xrange(self.startFrame, self.endFrame+1) :
            fileString = self.formatString.format(i,
                                     self.cpX[self.frameToInternal(i)], 
                                     self.cpY[self.frameToInternal(i)])
            trajectoryFile.write(fileString)
            
    def getStartEndFrame(self):
        return (self.startFrame, self.endFrame)
    
    def smoothLinear(self):
        '''
        '''
        length = self.length()
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
