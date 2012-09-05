'''
Created on 18.03.2011
@author: Gena
'''
from __future__ import division

from hashlib import sha512
from time import time
from random import randint
from math import sqrt

from numpy import meshgrid,arange
from PyQt4 import QtCore,QtGui
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
    chamberPositionUpdated = QtCore.pyqtSignal()
    fileCaption = "LocoTrack 1.0\n"
    
    def __init__(self, rect, parent=None, sampleName='Unknown'):
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
        self.size = self.rect.size
        # Frame number is unknown
        self.frameNumber = -1
        self.scale = -1 # Pixels in 1 mm
        self.trajectoryImage = None
        self.frameRate = -1
        # Information about object
        self.ltObject = LtObject()
        # No trajectory is recorded
        self.resetTrajectory()
        # Individual threshold
        self.threshold = 60
        #
        self.showTrajectory = False
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
            
    def setSampleName(self, name):
        if self.sampleName != name :
            self.sampleName = name
            self.chamberDataUpdated.emit()
            
    def setTrajectoryShow(self, checked):
        if self.showTrajectory == checked:
            return
        self.showTrajectory = checked
        if self.showTrajectory:
            self.createTrajectoryImage()
        self.chamberDataUpdated.emit()
     
    def move(self, dirX, dirY):
        '''
        Move chamber for dirX, dirY
        '''
        self.rect.moveTo(self.rect.left()+dirX, self.rect.top()+dirY)
        self.chamberDataUpdated.emit()
        self.chamberPositionUpdated.emit(self.getRect())

    def resize(self, dirX, dirY):
        '''
        Resize chamber by dirX, dirY
        '''
        self.rect.setWidth(self.rect.width()+dirX) 
        self.rect.setHeight(self.rect.height()+dirY)
        # Init matrix for new size
        self.initMatrix()
        self.chamberDataUpdated.emit()
        self.chamberPositionUpdated.emit()
        
    def setPosition(self, rect):
        '''
        Move chamber to rect
        '''
        self.rect.setTopLeft(rect.topLeft())
        self.rect.setBottomRight(rect.bottomRight())
        self.initMatrix()
        self.chamberPositionUpdated.emit()
    
    def moveTo(self, point):
        self.rect.moveTo(point)
        self.chamberDataUpdated.emit()
        self.chamberPositionUpdated.emit()
    
    def initTrajectory(self, videoLength):
        '''
        Init array to store trajectory starting from curent frame and to videoLength
        '''
        if self.ltTrajectory is not None :
            self.resetTrajectory()
        # init array to save frames from current 
        self.ltTrajectory = LtTrajectory(self.frameNumber, videoLength)
        self.saveLtObjectToTrajectory()
        self.chamberDataUpdated.emit()
    
    def resetTrajectory(self):
        '''
        Remove stored in array trajectory
        '''
        self.ltTrajectory = None
        self.smoothedTrajectory = None
        self.errors = 0
        self.chamberDataUpdated.emit()
        
    @classmethod
    def loadFromFile(cls, fileName):
        '''
        load chamber from file
        '''
        print 'Load  chamber from file {}'.format(fileName)
        trajectoryFile = open(fileName, 'r')
        if trajectoryFile.readline() != cls.fileCaption :
            #TODO: excepting
            return
        x, y = [int(value) for value in trajectoryFile.readline().split()]
        width, height = [int(value) for value in trajectoryFile.readline().split()]
        rect = QtCore.QRect(x,y,width, height)
        chamber = cls(rect)
        chamber.initMatrix()
        # TODO: implement mm
        chamber.scale = float(trajectoryFile.readline())
        chamber.frameRate = float(trajectoryFile.readline())
        chamber.sampleName = trajectoryFile.readline().strip()
        chamber.threshold = float(trajectoryFile.readline())
        if trajectoryFile.readline().strip() == 'Trajectory:' :
            print 'Load  trajectory from file {}'.format(fileName)
            chamber.ltTrajectory = LtTrajectory.loadFromFile(trajectoryFile)
            chamber.createTrajectoryImage()
        else :
            chamber.ltTrajectory = None
        trajectoryFile.close()
        return chamber
    
    def saveToFile(self, fileName, frameRate):
        '''
        save trajectory to file
        '''
        print 'Save chamber for sample {}'.format(self.sampleName)
        trajectoryFile = open(fileName, 'w')
        trajectoryFile.write(self.fileCaption)
        trajectoryFile.write("{0} {1}\n".format(self.left(), self.top()))
        trajectoryFile.write("{0} {1}\n".format(self.width(), self.height()) )
        trajectoryFile.write("{0}\n".format(self.scale)) 
        trajectoryFile.write("{0}\n".format(frameRate))
        trajectoryFile.write(self.sampleName+"\n")
        trajectoryFile.write('{}\n'.format(self.threshold))
        print "file {0} created".format(fileName)
        if self.ltTrajectory is not None :
            trajectoryFile.write('Trajectory:'+"\n")
            self.ltTrajectory.rstrip()
            self.ltTrajectory.saveToFile(trajectoryFile)
        else :
            trajectoryFile.write('No trajectory recorded'+"\n")
        trajectoryFile.close()
        if self.trajectoryImage is not None :
            self.trajectoryImage.save(fileName+'.png')
        # Calculate speed
        speedFile = open(fileName+'.spd', 'w')
        if self.ltTrajectory is not None :
            x2,y2 = self.ltTrajectory[self.ltTrajectory.startFrame].massCenter
            for i in xrange(self.ltTrajectory.startFrame+1,self.ltTrajectory.endFrame) :
                point2 = self.ltTrajectory[i]
                if point2 is None :
                    continue
                x1,y1 = x2,y2
                x2,y2 = point2.massCenter
                runlen = sqrt((x2-x1)**2+(y2-y1)**2)/self.scale
                if runlen < 0 :
                    print i,point2,runlen
                speedFile.write('{:5} {:18.6f}\n'.format(i,runlen*self.frameRate))
        
        self.chamberDataUpdated.emit()
        
    def saveLtObjectToTrajectory(self):
        if (self.ltTrajectory is not None) and (self.frameNumber >= 0):
            self.ltTrajectory[self.frameNumber] = self.ltObject
            if self.trajectoryImage is not None:
                point1 = self.ltTrajectory[self.frameNumber-1]
                if point1 is not None and self.ltObject is not None :
                    x1,y1 = point1.massCenter
                    x2,y2 = self.ltObject.massCenter
                    self.trajectoryPainter.drawLine(x1,y1,x2,y2)
              
    def createTrajectoryImage(self):
        if self.ltTrajectory is None :
            return
        black = QtGui.QColor(0,0,0)
        if self.trajectoryImage is None:
            self.trajectoryImage = QtGui.QImage(self.rect.size(),QtGui.QImage.Format_ARGB32_Premultiplied)
            self.trajectoryPainter = QtGui.QPainter(self.trajectoryImage)
            self.trajectoryPainter.setPen(black)
        self.trajectoryImage.fill(QtCore.Qt.transparent)
        x,y = self.ltTrajectory[self.ltTrajectory.startFrame].massCenter
        point2 = QtCore.QPoint(x,y)
        for ltObject in self.ltTrajectory :
            if ltObject is None:
                continue
            point1 = point2
            x,y = ltObject.massCenter
            point2 = QtCore.QPoint(x,y)
            self.trajectoryPainter.drawLine(point1,point2)
            QtGui.QApplication.processEvents()  
        
    
if __name__ == '__main__':
    '''
    Self testing
    '''
    trajName = '/home/gena/eclipse37-workspace/locotrack/video/2012-02-22_agn-F-Ad7-N-02_c.avi.lt1'
    chamber = Chamber.loadFromFile(trajName)
    print chamber.getRect()
    print chamber.ltTrajectory.getStartEndFrame()
