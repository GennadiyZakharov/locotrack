'''
Created on 27.04.2011

@author: Gena
'''

import numpy
from ltcore.ltobject import LtObject

class LtTrajectory(object):
    '''
    This class holds object trajectory
    
    It can be representated as array of LtObject, but in python
    this desigion is really slow and memory-hungry
    
    So, I use numpy array and hold only central point of object
    '''


    def __init__(self,startFrame, endFrame):
        '''
        Constructor
        Creates array to store object properties
        for frame count from startFrame to endFrame
        '''
        self.startFrame=startFrame
        self.endFrame = endFrame
        self.lastNumber = None
        # TODO: fix array init
        self.x = numpy.array(int)
        self.y = numpy.array(int)
    
    def frameNumberToInternal(self, frameNumber):
        '''
        Covers frame number to internal number (numpy array)
        '''
        if (frameNumber < self.startFrame) or \
            (frameNumber > self.endFrame)  :
                # TODO: paste exception
                return
        return frameNumber - self.startFrame
        
    def setObject(self, frameNumber, ltObject):
        '''
        Store ltObject on frame number
        '''
        internalNumber = self.frameNumberToInternal(frameNumber)
        self.lastNumber = internalNumber
        self.x[internalNumber],self.y[internalNumber] = ltObject.centralPoint()
        print 'saved trajectory frame',frameNumber
        
    def lastObject(self):
        '''
        Return last stored ltObject 
        '''
        return LtObject(self.x[self.lastNumber],self.y[self.lastNumber])
        