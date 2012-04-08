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
        self.trajectoryFile = None
        self.resetTrajectory()
        self.fileCaption = "LocoTrack 1.0\n"
      
    def leftTopPos(self) :
        return self.left(), self.top()
    
    def bottomRightPos(self):
        return self.right(), self.bottom()
    '''
    def initTrajectory(self, firstFrame, lastFrame):
        self.ltTrajectory = LtTrajectory(firstFrame, lastFrame)
    ''' 
    def initTrajectory(self, fileName, scale, frameRate):
        self.trajectoryFile = open(fileName, 'w')
        self.trajectoryFile.write(self.fileCaption)
        self.trajectoryFile.write("{0} {1}\n".format(self.left(), self.top()))
        self.trajectoryFile.write("{0} {1}\n".format(self.width(), self.height()) )
        self.trajectoryFile.write("{0}\n".format(scale/15))
        # TODO: implement mm
        self.trajectoryFile.write("{0}\n".format(frameRate))
        self.trajectoryFile.write("=============\n")
        print "file {0} created".format(fileName)
        self.saveToTrajectory()
        #self.ltTrajectory = LtTrajectory(firstFrame, lastFrame)
    
    def resetTrajectory(self):
        #self.ltTrajectory = None
        if self.trajectoryFile is not None :
            self.trajectoryFile.close()
            print "File closed"
        self.trajectoryFile = None
        self.errors = 0
        
    def saveToTrajectory(self):
        if (self.trajectoryFile is not None) and (self.frameNumber >= 0):
            # save point to file
            fileString = "{0:10} {1:18.6f} {2:18.6f}\n".format(self.frameNumber,
                                     self.ltObject.massCenter[0], self.ltObject.massCenter[1])
            self.trajectoryFile.write(fileString)
            
        '''
        if (self.ltTrajectory is not None) and (self.frameNumber >= 0):
            self.ltTrajectory.setObject(self.frameNumber, self.ltObject)
        '''      
    def saveTrajectory(self, fileName):
        pass
    
    def loadTrajectory(self, fileName):
        pass
