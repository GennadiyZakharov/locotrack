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
    
    So, I used numpy array and hold only central point of object
    '''


    def __init__(self,startFrame, endFrame):
        '''
        Constructor
        '''
        self.startFrame=startFrame
        self.endFrame = endFrame
        self.lastNumber = None
        self.x = numpy.array()
    
    def frameNumberToInternal(self, frameNumber):
        if frameNumber > self.endFrame :
            return
        return frameNumber - self.startFrame
        
    def setObject(self, frameNumber, ltObject):
        internalNumber = self.frameNumberToInternal(frameNumber)
        self.lastNumber = internalNumber
        self.x[internalNumber],self.y[internalNumber] = ltObject.centralPoint()
        
    def lastObject(self):
        return LtObject(self.x[self.lastNumber],self.y[self.lastNumber])
        