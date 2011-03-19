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
        
    def getPos(self) :
        return self.left(),self.top()
    
    def getPos2(self):
        return self.right(),self.bottom()
    
    def getSize(self):
        return self.size()
    