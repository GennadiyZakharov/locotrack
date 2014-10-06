'''
Created on 27.04.2011
@author: Gena
'''
from __future__ import print_function
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
    formatString = "{:10} {:18.6f} {:18.6f}\n"  # String to format data when save to file

    def __init__(self, length):
        '''
        Create arrays to store ltObjects
        valid numbers from startFrame to EndFrame-1 
        (to be consistent with range() function syntax)
        '''   
        self.length = length
        # Arrays to store central point
        self.cpX = np.empty(length)
        self.cpX.fill(-1.0)
        self.cpY = np.empty(length)
        self.cpY.fill(-1.0)
        self.leftBorder = 0
        self.rightBorder = length
    
    def setBounds(self, leftBorder, rightBorder):
        if rightBorder > self.length :
            print('Unable to set borders longer than trajectory')
            return
        self.leftBorder,self.rightBorder = leftBorder,rightBorder
    
    def bounds(self):
        '''
        Return start and end frames
        '''
        return self.leftBorder, self.rightBorder
    
    def __len__(self):
        return self.length
     
    def __iter__(self) :
        self.currentIndex = 0
        return self    
    
    def next(self):
        if self.currentIndex >= self.length :
            raise StopIteration
        else:
            x, y = self.cpX[self.currentIndex], self.cpY[self.currentIndex]
            self.currentIndex += 1
            return self.xyToLtObject(x, y)
    
    def xyToLtObject(self, x, y):
        return LtObject((x, y)) if x >= 0 else None
    
    def ltObjectToXY(self, ltObject):
        return ltObject.center if ltObject is not None else (-1, -1)
    
    def __getitem__(self, index):
        '''
        Get ltObject stored on frame number
        '''
        x, y = self.cpX[index], self.cpY[index] 
        return self.xyToLtObject(x, y)
    
    def __setitem__(self, index, ltObject):
        '''
        Store ltObject on frame number
        '''
        self.cpX[index], self.cpY[index] = self.ltObjectToXY(ltObject)
    
    def minMax(self):
        maxX, maxY = 0, 0
        minX, minY = 10000, 10000
        for i in xrange(len(self)) :
            x = self.cpX[i]
            y = self.cpY[i]
            if x == -1 or y == -1 :
                continue
            if x > maxX: maxX = x
            if x < minX: minX = x
            if y > maxY: maxY = y
            if y < minY: minY = y
        return (minX, minY, maxX, maxY)
    
    """   
    def resize(self, length):
        '''
        Resize trajectory to new length
        strip old trajectory if nessesary, then expand to new bounds
        '''
        # Arrays to store central point
        newcpX = np.linspace(-1.0, -1.0, length)
        newcpY = np.linspace(-1.0, -1.0, length)
        if length > self.length :
            newcpX[0:self.length]=self.cpX
            newcpY[0:self.length]=self.cpY
        else:
            newcpX=self.cpX[0:length]
            newcpY=self.cpX[0:length]
        self.cpX=newcpX
        self.cpY=newcpY
        self.length = length
    """ 
    @classmethod
    def loadFromFile(cls, trajectoryFile):
        '''
        Load trajectory from text file, opened for reading
        ''' 
        # Reading start and end frame numbers
        length = int(trajectoryFile.readline())
        trajectory = cls(length)
        leftBound,rightBound = (int(value) for value in trajectoryFile.readline().split())
        trajectory.setBounds(leftBound,rightBound)
        # Reading trajectory
        trajectoryFile.readline()
        for i in xrange(leftBound,rightBound) :
            line = trajectoryFile.readline()
            values = line.split()
            frameNumber = int(values[0])
            if frameNumber != i :
                raise Exception('Inconsistent numbers during trajectory loading.' + 
                                'Frame {}, at line {}'.format(i, frameNumber))
            # Save data in trajectory
            x = float(values[1])
            y = float(values[2])
            trajectory.cpX[frameNumber], trajectory.cpY[frameNumber] = x, y  
        return trajectory     
    
    def saveToFile(self, trajectoryFile):
        '''
        Save trajectory to text file, opened for writing
        '''
        # Writing caption
        trajectoryFile.write("{}\n".format(self.length))
        trajectoryFile.write("{} {}\n".format(self.leftBorder, self.rightBorder))
        trajectoryFile.write(self.captionString)
        for i in xrange(self.leftBorder,self.rightBorder) :
            fileString = self.formatString.format(i,self.cpX[i],self.cpY[i])
            trajectoryFile.write(fileString)
    
    def findBorders(self):
        startFrame=0
        while self.cpX[startFrame] < 0 :
            startFrame +=1
        endFrame = self.length
        while self.cpY[endFrame-1] < 0 :
            endFrame -=1
        if endFrame > startFrame :
            self.setBounds(startFrame, endFrame)
            print('Borders',startFrame, endFrame)
            return True
        else:
            return False
        
    
    def clone(self):
        '''
        Creates deep copy of trajectory
        '''
        trajectory = LtTrajectory(self.length)
        trajectory.setBounds(self.leftBorder, self.rightBorder)
        trajectory.cpX = self.cpX[:]
        trajectory.cpY = self.cpY[:]
        return trajectory
    
    """
    def smoothLinear(self):
        '''
        Make the linear smooth for trajectory
        '''
        self.strip()  # Ensure, that first and last frame is not none
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
    """ 
if __name__ == '__main__':  # Small unit tests
    '''
    Self testing
    '''
    from math import sin
