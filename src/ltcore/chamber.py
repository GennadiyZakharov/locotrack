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
        self.resetTrajectory()
        self.recordTrajectory = False
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
    
    @QtCore.pyqtSlot(int)
    def setNumber(self, number):
        '''
        set number of chamber
        '''
        if self.number != number :
            self.number = number
            self.signalGuiDataUpdated.emit()
    
    @QtCore.pyqtSlot(int)
    def setThreshold(self, value):
        '''    
        Set threshold value   
        '''
        if value != self.threshold :
            self.threshold = value
            self.signalGuiDataUpdated.emit()
            self.signalRecalculateChamber.emit()
    
    @QtCore.pyqtSlot(QtCore.QString)
    def setSampleName(self, sampleName):
        '''    
        Set set sample name  
        '''
        if self.sampleName != sampleName :
            self.sampleName = sampleName
            self.signalGuiDataUpdated.emit()
    
    @QtCore.pyqtSlot(bool)
    def setRecordTrajectory(self, checked):
        '''
        Set, if we saving ltObjects to trajectory
        '''  
        if self.recordTrajectory == checked:
            return
        self.recordTrajectory = checked
        self.signalGuiDataUpdated.emit() 
            
    @QtCore.pyqtSlot(bool)
    def setShowTrajectory(self, checked):
        '''
        Set, if we showing trajectory or not
        '''
        if self.showTrajectory == checked:
            return
        self.showTrajectory = checked
        # TODO: implement show trajectory
        self.signalGuiDataUpdated.emit()
    
    def setLtObject(self, ltObject, frameNumber):
        '''
        Set object for chamber and save it to trajectory, if setRecordTrajectory enabled
        '''
        self.ltObject = ltObject
        if (self.trajectory is not None) and self.recordTrajectory :
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
        Move chamber by dirX, dirY
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
        
    @QtCore.pyqtSlot(QtCore.QRect)
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
        # Init trajectory to save frames
        self.trajectory = LtTrajectory(startFrame, endFrame)
        #self.signalGuiDataUpdated.emit()
    
    def resetTrajectory(self):
        '''
        Remove stored trajectory
        '''
        self.trajectory = None
        self.signalGuiDataUpdated.emit()
    
    @classmethod
    def loadFromFile(cls, fileName):
        '''
        Load chamber and trajectory from file
        '''
        def stripeq(string):
            '''
            strip `=` if presented (new chamber format)
            '''
            pos = string.find('=')
            if pos >= 0 : # New file format
                return string[pos+1:]
            else :
                return string   
        print 'Load  chamber from file {}'.format(fileName)
        trajectoryFile = open(fileName, 'r')
        if trajectoryFile.readline().strip() != cls.fileCaption.strip() :
            print 'This is not Trajectory'
            return None
        # Chamber position and size
        x, y = [int(value) for value in stripeq(trajectoryFile.readline()).split()]
        width, height = [int(value) for value in stripeq(trajectoryFile.readline()).split()]
        # Creating chamber
        chamber = cls(QtCore.QRect(x, y, width, height))
        # TODO: Reading scale label and frame rate
        scale = float(stripeq(trajectoryFile.readline()))
        frameRate = float(stripeq(trajectoryFile.readline()))
        chamber.sampleName = stripeq(trajectoryFile.readline()).strip()
        chamber.threshold = float(stripeq(trajectoryFile.readline()))
        if trajectoryFile.readline().strip() == 'Trajectory:' :
            chamber.trajectory = LtTrajectory.loadFromFile(trajectoryFile)
        else :
            chamber.trajectory = None
        trajectoryFile.close()
        return chamber, scale, frameRate
    
    def saveToFile(self, fileNameTemplate, scale, frameRate):
        '''
        Save trajectory to file
        
        Scale and Frame Rate must be written in file
        It is used to analyse chambers
        '''
        fileName = fileNameTemplate.format(self.number)
        print 'Save chamber for sample {} to file {}'.format(self.sampleName, fileName)
        trajectoryFile = open(fileName, 'w')
        trajectoryFile.write(self.fileCaption)
        trajectoryFile.write('Position = {0} {1}\n'.format(self.left(), self.top()))
        trajectoryFile.write('Size = {0} {1}\n'.format(self.width(), self.height()))
        trajectoryFile.write('Scale (px/mm) = {0}\n'.format(scale)) 
        trajectoryFile.write('FrameRate = {0}\n'.format(frameRate))
        trajectoryFile.write('Sample name = {}\n'.format(self.sampleName))
        trajectoryFile.write('Threshold level = {}\n'.format(self.threshold))
        if self.trajectory is not None :
            trajectoryFile.write('Trajectory:' + "\n")
            self.trajectory.strip()
            self.trajectory.saveToFile(trajectoryFile)
        else :
            trajectoryFile.write('No trajectory recorded' + "\n")
        trajectoryFile.close()
        
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
