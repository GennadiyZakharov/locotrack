'''
Created on 18.03.2011
@author: Gena
'''

from PyQt4 import QtCore
from ltcore.ltobject import LtObject

class Chamber(QtCore.QRect):
    '''
    This is class for one chamber
    It holds all chamber attributes: leftTopPos, size, etc
    also it holds property ltObject -- all data for 
    detected object on current step
    '''
    
    def __init__(self, rect):
        '''
        Constructor
        '''
        super(Chamber, self).__init__(rect.normalized())
        self.ltObject = LtObject()
        self.resetTrajectory()
      
    def leftTopPos(self) :
        return self.left(), self.top()
    
    def bottomRightPos(self):
        return self.right(), self.bottom()
    
    def size(self):
        return self.size()
        
    def resetTrajectory(self):
        self.ltTrajectory = None
    
    def saveTrajectory(self, fileName):
        pass
    
    def loadTrajectory(self, fileName):
        pass
