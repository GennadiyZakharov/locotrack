'''
Created on 27.04.2011

@author: Gena
'''

import numpy

class LtTrajectory(object):
    '''
    This class holds object trajectory
    It can be representated as array of LtObject, but in python
    this desigion is really slow and memory-hungry
    
    So, i used numpy array and hold only central point of object
    '''


    def __init__(self,startFrame, endFrame):
        '''
        Constructor
        '''
        self.startFrame=startFrame
        self.endFrame = endFrame
        self.x = numpy.array()
        
    def setObject(self, frameNumber, ltObject):
        pass
        
    def getLast(self, count=20):
        return 
    
    def setItem(self, pos, item):
        return
   