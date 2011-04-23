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
    
    def __init__(self,rect):
        super(Chamber, self).__init__(rect.normalized())
        self.objectPos = None
        self.maxBrightPos = None
        self.contours = None
        self.trajectory = []
      
    def getPos(self) :
        return self.left(),self.top()
    
    def getPos2(self):
        return self.right(),self.bottom()
    
    def getSize(self):
        return self.size()
    
    def setObjectPos(self,x=None,y=None):
        if x is None :
            self.objectPos = None
        else :
            self.objectPos = QtCore.QPointF(x,y)
            self.trajectory.append(self.objectPos)
    