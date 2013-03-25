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
    It can be represented as array of LtObjects, but in Python
    this design is really slow and memory-hungry
    So, LtTrajectory uses numpy arrays and constructs LtObject when needed
    None object is represented by (-1, -1) in arrays
    '''
    captionString = "     Frame                  X                  Y\n"
    formatString = "{:10} {:18.6f} {:18.6f}\n"     # String to format data when save to file

    def __init__(self, startFrame, endFrame):
        '''
        Create arrays to store ltObjects
        valid numbers from startFrame to EndFrame-1 
        (to be consistent with range() function syntax)
        '''   
        self.startFrame, self.endFrame = startFrame, endFrame
        self.arrayLength = self.endFrame - self.startFrame
        # Arrays to store central point
        self.cpX = np.linspace(-1.0, -1.0, self.arrayLength)
        self.cpY = np.linspace(-1.0, -1.0, self.arrayLength)
    
    def bounds(self):
        '''
        Return start and end frames
        '''
        return self.startFrame, self.endFrame
    
    def __len__(self):
        return self.arrayLength
     
    def __iter__(self) :
        self.currentIndex = 0
        return self    
    
    def next(self):
        if self.currentIndex >= self.arrayLength :
            raise StopIteration
        else:
            x, y = self.cpX[self.currentIndex], self.cpY[self.currentIndex]
            self.currentIndex += 1
            return self.xyToLtObject(x,y)
    
    def xyToLtObject(self,x,y):
        return LtObject((x, y)) if x >= 0 else None
    
    def ltObjectToXY(self, ltObject):
        return ltObject.center if ltObject is not None else (-1, -1)
    
    def __getitem__(self, index):
        '''
        Get ltObject stored on frame number
        '''
        internalNumber = self.frameToInternal(index)
        x, y = self.cpX[internalNumber], self.cpY[internalNumber] 
        return self.xyToLtObject(x,y)
    
    def __setitem__(self, index, ltObject):
        '''
        Store ltObject on frame number
        '''
        internalNumber = self.frameToInternal(index)
        self.cpX[internalNumber], self.cpY[internalNumber] = self.ltObjectToXY(ltObject)
    
    def minMax(self):
        maxX, maxY=0,0
        minX, minY = 1000,1000
        for i in xrange(len(self)) :
            x = self.cpX[i]
            y = self.cpY[i]
            if x == -1 or y==-1 :
                continue
            if x> maxX: maxX=x
            if x< minX: minX=x
            if y> maxY: maxY=y
            if y< minY: minY=y
        return (minX,minY,maxX,maxY)
       
    def frameToInternal(self, frameNumber):
        '''
        Convert frame number to internal number (numpy array)
        '''
        return frameNumber - self.startFrame
    
    def internalToFrame(self, internal):
        '''
        Convert internal number to frame number
        '''
        return internal + self.startFrame
    
    def rstrip(self):
        '''
        Strip all none points from end of trajectory 
        '''
        for i in xrange(len(self.cpX) - 1, -1, -1) :
            if self.cpX[i] >= 0 : # Trim array
                self.endFrame = self.internalToFrame(i + 1)
                self.cpX = self.cpX[:i + 1]
                self.cpY = self.cpY[:i + 1]
                self.arrayLength = len(self.cpX)
                return
            
    def lstrip(self):
        '''
        Strip all none points from beginning of trajectory 
        '''
        for i in xrange(len(self.cpX)) :
            if self.cpX[i] >= 0 :
                self.cpX = self.cpX[i:]
                self.cpY = self.cpY[i:]
                self.startFrame = self.internalToFrame(i)
                self.arrayLength = len(self.cpX)
                return
    
    def strip(self):
        '''
        Strip all none points from both ends of trajectory 
        '''
        self.lstrip()
        self.rstrip()
    
    @classmethod
    def loadFromFile(cls, trajectoryFile):
        '''
        Load trajectory from text file, opened for reading
        ''' 
        # Reading start and end frame numbers
        startFrame, endFrame = [int(value) for value in trajectoryFile.readline().split()]
        trajectory = cls(startFrame, endFrame)
        # Reading trajectory
        trajectoryFile.readline()
        for i in xrange(startFrame, endFrame) :
            line = trajectoryFile.readline()
            values = line.split()
            frameNumber = int(values[0])
            if frameNumber != i :
                raise Exception('Inconsistent numbers during trajectory loading.' + 
                                'Frame {}, at line {}'.format(i, frameNumber))
            # Save data in trajectory
            x = float(values[1])
            y = float(values[2])
            index = trajectory.frameToInternal(frameNumber)
            trajectory.cpX[index], trajectory.cpY[index] = x, y
        return trajectory         
    
    def saveToFile(self, trajectoryFile):
        '''
        Save trajectory to text file, opened for writing
        '''
        # Writing caption
        trajectoryFile.write("{} {}\n".format(self.startFrame, self.endFrame))
        trajectoryFile.write(self.captionString)
        
        for i in xrange(self.startFrame, self.endFrame) :
            fileString = self.formatString.format(i,
                                     self.cpX[self.frameToInternal(i)],
                                     self.cpY[self.frameToInternal(i)])
            trajectoryFile.write(fileString)
    
    def clone(self):
        '''
        Creates deep copy of trajectory
        '''
        trajectory = LtTrajectory(*self.bounds())
        trajectory.cpX = self.cpX[:]
        trajectory.cpY = self.cpY[:]
        return trajectory
    
    def smoothLinear(self):
        '''
        Make the linear smooth for trajectory
        '''
        self.strip() # Ensure, that first and last frame is not none
        length = len(self)
        # Creating new arrays
        X = np.zeros(length)
        Y = np.zeros(length)
        # Filling arrays according to linear smooth formula
        X[0], Y[0] = self.cpX[0], self.cpY[0]
        for n in xrange(1, length - 1) :
            X[n] = 1 / 4 * self.cpX[n - 1] + 1 / 2 * self.cpX[n] + 1 / 4 * self.cpX[n + 1]
            Y[n] = 1 / 4 * self.cpY[n - 1] + 1 / 2 * self.cpY[n] + 1 / 4 * self.cpY[n + 1]
        X[length - 1], Y[length - 1] = self.cpX[length - 1], self.cpY[length - 1]
        # Storing new arrays
        self.cpX = X
        self.cpY = Y
        
if __name__ == '__main__': # Small unit tests
    '''
    Self testing
    '''
    from math import sin
    
    def printTrajectory(trajectory):
        startFrame, endFrame = trajectory.bounds()
        print 'Bounds: ', startFrame, endFrame 
        for i in xrange(startFrame, endFrame) :
            ltObject = trajectory[i]
            obj = (ltObject.center if ltObject is not None else 'None')
            print '{} - '.format(i), obj
        
    trajectory = LtTrajectory(50, 100)
    for i in xrange(58, 95) :
        ltObject = LtObject((i / 2, sin(i / 4)))
        trajectory[i] = ltObject
    
    printTrajectory(trajectory)      
    trajectory.strip()
    printTrajectory(trajectory)
    
    tr1 = trajectory.clone()
    tr1.smoothLinear()
    printTrajectory(tr1)
