'''
Created on 18.03.2011
@author: Gena
'''
from __future__ import division

from hashlib import sha512
from time import time
from random import randint

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
    fileCaption = "LocoTrack 1.0\n"
    
    def __init__(self, rect, parent=None, sampleName='UnknownSample'):
        '''
        Constructor
        '''
        super(Chamber, self).__init__(parent)
        self.hashValue = int(sha512(str(time() + randint(0, 100))).hexdigest(), 16)
        # Creating QRect to store chamber position
        self.rect = QtCore.QRect(rect.normalized())
        # Sample Name
        self.sampleName = sampleName
        # Creating links to QRect Methods
        self.left = self.rect.left
        self.top = self.rect.top
        self.width = self.rect.width
        self.height = self.rect.height
        self.topLeft = self.rect.topLeft
        self.bottomRight = self.rect.bottomRight
        self.getRect = self.rect.getRect
        # Frame number is unknown
        self.frameNumber = -1
        # Information about object
        self.ltObject = LtObject()
        # No trajectory is recorded
        self.resetTrajectory()
        # Individual threshold
        self.threshold = 60
        
        self.trajectoryFile = None
        # Creating matrix for center location
        self.initMatrix()
        
    def __hash__(self):
        return self.hashValue
        
    def initMatrix(self):
        '''
        Calculate matrices, is used to calculate mass center of object using numPy
        '''
        x,y = arange(0,self.width(),1),arange(0,self.height(),1)
        self.X,self.Y = meshgrid(x,y)
    
    # For OpenCV tuple are better, the QPoint
    def topLeftTuple(self) :
        '''
        Return topLeft position as a tuple
        '''
        return self.rect.left(), self.rect.top()
    
    def bottomRightTuple(self):
        '''
        Return bottomRight position as a tuple
        '''
        return self.rect.right(), self.rect.bottom()
    
    def setThreshold(self, value):
        '''    
        Set threshold value for this chamber    
        '''
        if value != self.threshold :
            self.threshold = value
            self.chamberDataUpdated.emit()
        
    def move(self, dirX, dirY):
        '''
        Move chamber for dirX, dirY
        '''
        self.rect.moveTo(self.rect.left()+dirX, self.rect.top()+dirY)

    def resize(self, dirX, dirY):
        '''
        Resize chamber by dirX, dirY
        '''
        self.rect.setWidth(self.rect.width()+dirX) 
        self.rect.setHeight(self.rect.height()+dirY)
        # Init matrix for new size
        self.initMatrix()
        
    def setPosition(self, rect):
        '''
        Move chamber to rect
        '''
        self.rect.setTopLeft(rect.topLeft())
        self.rect.setBottomRight(rect.bottomRight())
        self.initMatrix()
        
    def initTrajectory(self, videoLength):
        '''
        Init array to store trajectory starting from curent frame and to videoLength
        '''
        if self.ltTrajectory is not None :
            self.resetTrajectory()
        # init array to save frames from current 
        self.ltTrajectory = LtTrajectory((self.frameNumber, videoLength))
        self.saveLtObjectToTrajectory()
        self.chamberDataUpdated.emit()
    
    def resetTrajectory(self):
        '''
        Remove stored in array trajectory
        '''
        self.ltTrajectory = None
        self.errors = 0
        self.chamberDataUpdated.emit()
        
    def loadTrajectory(self, fileName):
        '''
        load trajectory from file
        '''
        pass
    
    def saveTrajectory(self, fileName, scale, frameRate, sampleName):
        '''
        save trajectory to file
        '''
        print 'Save trajectory for sample {}'.format(self.sampleName)
        trajectoryFile = open(fileName, 'w')
        trajectoryFile.write(self.fileCaption)
        trajectoryFile.write("{0} {1}\n".format(self.left(), self.top()))
        trajectoryFile.write("{0} {1}\n".format(self.width(), self.height()) )
        # TODO: implement mm
        trajectoryFile.write("{0}\n".format(scale/15))
        trajectoryFile.write("{0}\n".format(frameRate))
        trajectoryFile.write(sampleName+"\n")
        print "file {0} created".format(fileName)
        self.ltTrajectory.rstrip()
        self.ltTrajectory.saveToFile(trajectoryFile)
        trajectoryFile.close()
        self.chamberDataUpdated.emit()
        
    def saveLtObjectToTrajectory(self):
        if (self.ltTrajectory is not None) and (self.frameNumber >= 0):
            self.ltTrajectory.setObject(self.frameNumber, self.ltObject) 
              
    
    
