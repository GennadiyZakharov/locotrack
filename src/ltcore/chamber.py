'''
Created on 18.03.2011

@author: Gena
'''
from PyQt4 import QtCore

class Chamber(QtCore.QRect):
    '''
    This is class for one chamber
    It holds all chamber attributes
    '''
    
    def __init__(self, rect):
        super(Chamber, self).__init__(rect.normalized())
        self.objectPos = None
        self.maxBrightPos = None
        self.contours = None
        self.resetTrajectory()
      
    def getPos(self) :
        return self.left(), self.top()
    
    def getPos2(self):
        return self.right(), self.bottom()
    
    def getSize(self):
        return self.size()
    
    def setObjectPos(self, frame, pos=None):
        self.objectPos = pos
        self.trajectory.append((frame,) + pos)
        
    def trajEnd(self, count):
        trajend = [(int(x),int(y)) for (frame, x, y) in self.trajectory[-count:]]
        return trajend
        
    def setMaxBrightPos(self, pos=None):
        self.MaxBrightPos = pos
            
    def resetTrajectory(self):
        self.trajectory = []
    
    def saveTrajectory(self, fileName):
        for frame,x,y in self.trajectory :
            print frame, x, y
    
    def loadTrajectory(self, fileName):
        pass
