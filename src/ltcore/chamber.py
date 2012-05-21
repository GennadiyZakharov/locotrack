'''
Created on 18.03.2011
@author: Gena
'''
from __future__ import division

from numpy import meshgrid,arange
from PyQt4 import QtCore
from ltcore.ltobject import LtObject
from ltcore.lttrajectory import LtTrajectory

class Chamber(QtCore.QObject):
    '''
    This is class for one chamber
    It holds all chamber attributes: position, size, etc
    also it holds property ltObject -- all data for 
    detected object on current step
    '''
    chamberDataUpdated = QtCore.pyqtSignal()
    
    def __init__(self, rect, parent=None):
        '''
        Constructor
        '''
        super(Chamber, self).__init__(parent)
        self.rect = QtCore.QRect(rect.normalized())
        self.left = self.rect.left
        self.top = self.rect.top
        self.width = self.rect.width
        self.height = self.rect.height
        self.topLeft = self.rect.topLeft
        self.getRect = self.rect.getRect
        self.ltObject = LtObject()
        
        self.frameNumber = -1
        self.trajectoryFile = None
        self.resetTrajectory()
        self.threshold = 60
        self.fileCaption = "LocoTrack 1.0\n"
        self.initMatrix()
        
    def initMatrix(self):
        # This matrices is used to calculate mass center of object
        x,y = arange(0,self.width(),1),arange(0,self.height(),1)
        self.X,self.Y = meshgrid(x,y)
    
    def leftTopPos(self) :
        return self.rect.left(), self.rect.top()
    
    def bottomRightPos(self):
        return self.rect.right(), self.rect.bottom()
    '''
    def initTrajectory(self, firstFrame, lastFrame):
        self.ltTrajectory = LtTrajectory(firstFrame, lastFrame)
    ''' 
   
    def initTrajectory(self, fileName, scale, frameRate, sampleName):
        self.trajectoryFile = open(fileName, 'w')
        self.trajectoryFile.write(self.fileCaption)
        self.trajectoryFile.write("{0} {1}\n".format(self.left(), self.top()))
        self.trajectoryFile.write("{0} {1}\n".format(self.width(), self.height()) )
        self.trajectoryFile.write("{0}\n".format(scale/15))
        # TODO: implement mm
        self.trajectoryFile.write("{0}\n".format(frameRate))
        self.trajectoryFile.write(sampleName+"\n")
        self.trajectoryFile.write("=============\n")
        self.trajectoryFile.write("     Frame                  X                  Y\n")
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
    
    def setThreshold(self, value):
        self.threshold = value
        self.chamberDataUpdated.emit()
        
    def move(self, dirX, dirY):
        self.rect.moveTo(self.rect.left()+dirX, self.rect.top()+dirY)

    def resize(self, dirX, dirY):
        self.rect.setWidth(self.rect.width()+dirX) 
        self.rect.setHeight(self.rect.height()+dirY)
        self.initMatrix()
        
    def setPosition(self, rect):
        self.rect.setTopLeft(rect.topLeft())
        self.rect.setBottomRight(rect.bottomRight())
        self.initMatrix()