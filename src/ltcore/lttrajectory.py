'''
Created on 27.04.2011
@author: Gena
'''

import numpy as np
from ltcore.ltobject import LtObject

class LtTrajectory(object):
    '''
    This class holds object trajectory
    
    It can be representated as array of LtObject, but in python
    this desigion is really slow and memory-hungry
    
    So, LtTrajectory uses numpy arrays and constructs LtObject when needed
    '''


    def __init__(self, startFrame, endFrame):
        '''
        Constructor
        Creates array to store object properties
        for frame count from startFrame to endFrame
        '''
        self.startFrame = startFrame
        self.endFrame = endFrame
        self.lastNumber = None
        self.centralPointX = np.linspace(-1.0, -1.0, endFrame-startFrame+1)
        self.centralPointY = np.linspace(-1.0, -1.0, endFrame-startFrame+1)
    
    def frameNumberToInternal(self, frameNumber):
        '''
        Convert frame number to internal number (numpy array)
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
        self.centralPointX[internalNumber], self.centralPointY[internalNumber] = ltObject.centralPoint()
        print 'saved trajectory frame', frameNumber
        
    def lastObject(self):
        '''
        Return last stored ltObject 
        '''
        return LtObject(self.CenterPointX[self.lastNumber], self.centralPointY[self.lastNumber])
        
