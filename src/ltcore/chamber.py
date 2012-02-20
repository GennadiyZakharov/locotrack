'''
Created on 18.03.2011
@author: Gena
'''

from PyQt4 import QtCore
from ltcore.ltobject import LtObject
from ltcore.lttrajectory import LtTrajectory

class Chamber(QtCore.QRect):
    '''
    This is class for one chamber
    It holds all chamber attributes: position, size, etc
    also it holds property ltObject -- all data for 
    detected object on current step
    '''
    
    def __init__(self, rect):
        '''
        Constructor
        '''
        super(Chamber, self).__init__(rect.normalized())
        self.ltObject = LtObject()
        self.frameNumber = -1
        self.resetTrajectory()
      
    def leftTopPos(self) :
        return self.left(), self.top()
    
    def bottomRightPos(self):
        return self.right(), self.bottom()
    
    def size(self):
        return self.size()
    
    def initTrajectory(self, firstFrame, lastFrame):
        self.ltTrajectory = LtTrajectory(firstFrame, lastFrame)
        
    def resetTrajectory(self):
        self.ltTrajectory = None
        
    def saveToTrajectory(self):
        if (self.ltTrajectory is not None) and (self.frameNumber >= 0):
            self.ltTrajectory.setObject(self.ltObject, self.frameNumber)
            
    
    def saveTrajectory(self, fileName):
        pass
    
    def loadTrajectory(self, fileName):
        pass
