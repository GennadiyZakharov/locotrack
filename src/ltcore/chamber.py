'''
Created on 18.03.2011

@author: Gena
'''
class Chamber(object):
    '''
    This is class for one chamber
    It holds all chamber attributes
    '''
    
    def __init__(self,x1,y1,x2,y2):
        self.pos = (min(x1,x2),min(y1,y2))
        self.size = (abs(x2-x1),abs(y2-y1))
        
    def getPos(self) :
        return self.pos
    
    def getPos2(self):
        return (self.pos[0] + self.size[0],self.pos[1] + self.size[1])
    
    def getSize(self):
        return self.size
    
    def getRect(self):
        return self.pos+self.size