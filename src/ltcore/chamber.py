'''
Created on 18.03.2011
@author: Gena
'''
from __future__ import division

from hashlib import sha512
from time import time
from random import randint

from numpy import meshgrid, arange
from PyQt4 import QtCore, QtGui
from ltcore.lttrajectory import LtTrajectory

class Chamber(QtCore.QObject):
    '''
    This is class for one chamber
    It holds all chamber attributes: position, size, etc
    also it holds property ltObject -- all data for 
    detected object on current step,
    and recorded trajectory
    '''
    signalGuiDataUpdated = QtCore.pyqtSignal() # Updated data, showing on GUI
    signalPositionUpdated = QtCore.pyqtSignal() # Update chamber position and size
    signalRecalculateChamber = QtCore.pyqtSignal() # Need to redraw chamber and recalculate object position 
    fileCaption = "LocoTrack 1.0\n"
    
    def __init__(self, rect, sampleName='UnknownSample', number=0, parent=None):
        '''
        Constructor
        '''
        super(Chamber, self).__init__(parent)
        # Create hash number
        self.hashValue = int(sha512(str(time() + randint(0, 100))).hexdigest(), 16)
        # Creating QRect to store chamber position
        self.rect = QtCore.QRect(rect.normalized())
        # Creating links to QRect Methods
        self.left = self.rect.left
        self.top = self.rect.top
        self.width = self.rect.width
        self.height = self.rect.height
        self.topLeft = self.rect.topLeft
        self.bottomRight = self.rect.bottomRight
        self.getRect = self.rect.getRect
        self.size = self.rect.size
        # Information about object
        # Sample Name
        self.sampleName = sampleName
        self.number = number
        self.ltObject = None
        # No trajectory is recorded
        self.trajectory = None
        self.smoothedTrajectory = None
        self.trajectoryImage = None 
        self.saveObjectToTrajectory = False
        # Individual threshold
        self.threshold = 60
        # Do not show trajectory
        self.showTrajectory = False
        # Creating matrix for center location
        self.initMatrices()
        
    def __hash__(self):
        '''
        Return hash value to store chambers in dictionary or set
        '''
        return self.hashValue
        
    def initMatrices(self):
        '''
        Calculate matrices, which is used to calculate mass center of object using numPy
        matrices recalculated when chamber resizes, so it is stored here
        '''
        x, y = arange(0, self.width(), 1), arange(0, self.height(), 1)
        self.Xmatrix, self.Ymatrix = meshgrid(x, y)
    
    def matrices(self):
        '''
        Return matrices for massCenterDetector
        '''
        return (self.Xmatrix, self.Ymatrix)
    
    def setNumber(self, number):
        '''
        set number of chamber
        '''
        self.number = number
        self.signalGuiDataUpdated.emit()
    
    def setThreshold(self, value):
        '''    
        Set threshold value   
        '''
        if value != self.threshold :
            self.threshold = value
            self.signalGuiDataUpdated.emit()
            self.signalRecalculateChamber.emit()
            
    def setSampleName(self, sampleName):
        '''    
        Set set sample name  
        '''
        if self.sampleName != sampleName :
            self.sampleName = sampleName
            self.signalGuiDataUpdated.emit()
    
    def setRecordTrajectory(self, checked):
        '''
        Set, if we showing trajectory or not
        '''  
        if self.saveObjectToTrajectory == checked:
            return
        self.saveObjectToTrajectory = checked
        self.signalGuiDataUpdated.emit() 
            
    def setTrajectoryShow(self, checked):
        '''
        Set, if we showing trajectory or not
        '''
        if self.showTrajectory == checked:
            return
        self.showTrajectory = checked
        if self.showTrajectory:
            self.createTrajectoryImage()
        self.signalGuiDataUpdated.emit()
    
    def setLtObject(self, ltObject, frameNumber):
        '''
        Set object for chamber and save it to trajectory, if saveObjectToTrajectory enabled
        '''
        self.ltObject = ltObject
        if (self.trajectory is not None) and self.saveObjectToTrajectory :
            self.trajectory[frameNumber] = ltObject
    
    '''
    Methods handling chamber moving and resizing
    '''   
    def moveTo(self, point):
        '''
        Move top left corner of chamber to point
        '''
        self.rect.moveTo(point)
        self.signalPositionUpdated.emit()
        self.signalRecalculateChamber.emit()
            
    def move(self, dirX, dirY):
        '''
        Move chamber for dirX, dirY
        '''
        self.rect.moveTo(self.rect.left() + dirX, self.rect.top() + dirY)
        self.signalPositionUpdated.emit()
        self.signalRecalculateChamber.emit()

    def resize(self, dirX, dirY):
        '''
        Resize chamber by dirX, dirY
        '''
        self.rect.setWidth(self.rect.width() + dirX) 
        self.rect.setHeight(self.rect.height() + dirY)
        self.initMatrices() # Init matrix for new size
        self.signalPositionUpdated.emit()
        self.signalRecalculateChamber.emit()
        
    def setPosition(self, rect):
        '''
        Move chamber to rect
        '''
        self.rect.setTopLeft(rect.topLeft())
        self.rect.setBottomRight(rect.bottomRight())
        self.initMatrices()
        self.signalPositionUpdated.emit()
        self.signalRecalculateChamber.emit()

    '''
    Methods to trajectory manipulation
    '''
    def initTrajectory(self, startFrame, endFrame):
        '''
        Init array to store trajectory from startFrame to EndFrame
        '''
        if self.trajectory is not None : # Delete old trajectory
            self.resetTrajectory()
        # Init trajectory to save frames from current to end of file
        self.trajectory = LtTrajectory(startFrame, endFrame)
        self.trajectory[startFrame] = self.ltObject
        self.signalGuiDataUpdated.emit()
    
    def resetTrajectory(self):
        '''
        Remove stored trajectory
        '''
        self.trajectory = None
        self.smoothedTrajectory = None
        self.trajectoryImage = None
        self.signalGuiDataUpdated.emit()
    
    def createTrajectoryImage(self):
        '''
        Create track image from stored trajectory
        '''
        if self.trajectory is None : # No trajectory to create image
            return 
        
        black = QtGui.QColor(0, 0, 0)
        if self.trajectoryImage is None: # Create new white image with black pen
            self.trajectoryImage = QtGui.QImage(self.rect.size(), QtGui.QImage.Format_ARGB32_Premultiplied)
            self.trajectoryPainter = QtGui.QPainter(self.trajectoryImage)
            self.trajectoryPainter.setPen(black)
        # Delete old image
        self.trajectoryImage.fill(QtCore.Qt.transparent)
        point1 = None
        point2 = None
        for ltObject in self.trajectory :
            if ltObject is None :
                continue
            x, y = ltObject.center
            point2 = QtCore.QPointF(x, y) # Reading first point
            if point1 is None :
                point1 = point2
                continue
            self.trajectoryPainter.drawLine(point2, point1)
            point1 = point2
        self.trajectoryPainter.end()
    
    @classmethod
    def loadFromFile(cls, fileName):
        '''
        Load chamber from file
        '''
        print 'Load  chamber from file {}'.format(fileName)
        trajectoryFile = open(fileName, 'r')
        if trajectoryFile.readline() != cls.fileCaption :
            #TODO: excepting
            return None
        x, y = [int(value) for value in trajectoryFile.readline().split()]
        width, height = [int(value) for value in trajectoryFile.readline().split()]
        rect = QtCore.QRect(x, y, width, height)
        chamber = cls(rect)
        # TODO: implement mm
        scale = float(trajectoryFile.readline())
        frameRate = float(trajectoryFile.readline())
        chamber.sampleName = trajectoryFile.readline().strip()
        chamber.threshold = float(trajectoryFile.readline())
        if trajectoryFile.readline().strip() == 'Trajectory:' :
            print 'Load  trajectory from file {}'.format(fileName)
            chamber.trajectory = LtTrajectory.loadFromFile(trajectoryFile)
            chamber.createTrajectoryImage()
        else :
            chamber.trajectory = None
        trajectoryFile.close()
        return chamber, scale, frameRate
    
    def saveToFile(self, fileNameTemplate, scale, frameRate):
        '''
        Save trajectory to file
        scale and Frame Rate must be written in file
        It is used to analyse chambers individually
        '''
        fileName = fileNameTemplate.format(self.number)
        print 'Save chamber for sample {} to file {}'.format(self.sampleName, fileName)
        trajectoryFile = open(fileName, 'w')
        trajectoryFile.write(self.fileCaption)
        trajectoryFile.write("{0} {1}\n".format(self.left(), self.top()))
        trajectoryFile.write("{0} {1}\n".format(self.width(), self.height()))
        trajectoryFile.write("{0}\n".format(scale)) 
        trajectoryFile.write("{0}\n".format(frameRate))
        trajectoryFile.write(self.sampleName + "\n")
        trajectoryFile.write('{}\n'.format(self.threshold))
        print "file {0} created".format(fileName)
        if self.trajectory is not None :
            trajectoryFile.write('Trajectory:' + "\n")
            self.trajectory.rstrip()
            self.trajectory.saveToFile(trajectoryFile)
            if self.trajectoryImage is None :
                self.createTrajectoryImage()
            self.trajectoryImage.save(fileName + '.png')
            # Calculate fractal dimersion
            #self.calculateFractalDimersion()
            
        else :
            trajectoryFile.write('No trajectory recorded' + "\n")
        trajectoryFile.close()
        '''
        # Calculate speed
        speedFile = open(fileName + '.spd', 'w')
        if self.trajectory is not None :
            x2, y2 = self.trajectory[self.trajectory.startFrame].center
            for i in xrange(self.trajectory.startFrame + 1, self.trajectory.endFrame) :
                point2 = self.trajectory[i]
                if point2 is None :
                    continue
                x1, y1 = x2, y2
                x2, y2 = point2.center
                runlen = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) / self.scale
                speedFile.write('{:5} {:18.6f}\n'.format(i, runlen * self.frameRate))
        '''
'''
Small test
'''          
if __name__ == '__main__':
    '''
    Self testing
    '''
    trajName = '/home/gena/eclipse37-workspace/locotrack/video/2012-02-22_agn-F-Ad7-N-02_c.avi.lt1'
    chamber = Chamber.loadFromFile(trajName)
    print chamber.getRect()
    print chamber.trajectory.bounds()
