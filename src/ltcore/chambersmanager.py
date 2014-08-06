'''
Created on 02.11.2012
@author: gena
'''
from __future__ import print_function
from __future__ import division
from PyQt4 import QtCore
from ltcore.chamber import Chamber

class ChambersManager(QtCore.QObject):
    '''
    This class holds all chambers, 
    and all default settings for chambers
    It also has methods to set data to all chambers
    '''
    signalChamberAdded = QtCore.pyqtSignal(Chamber)   # New chamber added to list
    signalChamberDeleted = QtCore.pyqtSignal(Chamber) # Chamber removed from list
    signalRecalculateChambers = QtCore.pyqtSignal()   # Need to recalculate object position
    signalThresholdChanged = QtCore.pyqtSignal(int)   #  
    signalTrajectoryWriting = QtCore.pyqtSignal(bool)  

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(ChambersManager, self).__init__(parent)
        self.chambers = set() # Set to store chambersGui
        self.numbers = set()  # Set to store used numbers
        self.threshold = 60 # Default threshold 
        self.sampleName = QtCore.QString('UnknownSample') # Default sample name
        self.recordTrajectory=False
        self.videoLength = -1
        self.scale = -1
    
    # Standard methods to use ChambersManager as iterator
    def next(self):
        return self.chambers.next()
    
    def __len__(self):
        return self.chambers.__len__()
    
    def __iter__(self) :
        return self.chambers.__iter__()
    
    @QtCore.pyqtSlot(QtCore.QRect)
    def createChamber(self, rect):
        '''
        Create chamber from rect and add it to chamber set
        '''
        chamber = Chamber(rect, self.sampleName)
        chamber.setThreshold(self.threshold)
        self.addChamber(chamber)
    
    @QtCore.pyqtSlot(Chamber)
    def addChamber(self, chamber):
        '''
        Add new chamber to the chamberlist
        '''
        self.chambers.add(chamber)
        # send signal from chamber
        chamber.signalRecalculateChamber.connect(self.signalRecalculateChambers)
        # Finding first unused number
        i = 1
        while i in self.numbers :
            i += 1
        chamber.setNumber(i)
        self.numbers.add(i)
        if self.videoLength >0 :
            chamber.initTrajectory(self.videoLength)
        print('Chamber opened')
        self.signalChamberAdded.emit(chamber)
        self.signalRecalculateChambers.emit()
    
    @QtCore.pyqtSlot(Chamber)
    def removeChamber(self, chamber):
        '''
        Removes chamber from chambers list
        '''
        self.signalChamberDeleted.emit(chamber) # Remove all Gui first
        self.chambers.remove(chamber)
        self.numbers.remove(chamber.number)
        self.signalRecalculateChambers.emit()
    
    @QtCore.pyqtSlot()
    def clear(self):
        '''
        Clear all chambers
        '''
        for chamber in self.chambers :
            self.signalChamberDeleted.emit(chamber)
        self.chambers = set()
        self.numbers = set()
    
    @QtCore.pyqtSlot(float)         
    def setThreshold(self, threshold):
        '''
        Set threshold name for all chambers
        '''
        if self.threshold == threshold:
            return
        self.threshold = threshold
        for chamber in self.chambers :
            chamber.setThreshold(threshold)
    
    @QtCore.pyqtSlot(QtCore.QString)
    def setSampleName(self, sampleName):
        '''
        Set sample sampleName for all chambersGui
        '''
        if self.sampleName == sampleName:
            return
        self.sampleName = sampleName
        for chamber in self.chambers :
            chamber.setSampleName(sampleName)
    
    @QtCore.pyqtSlot(int,int)
    def initTrajectories(self, length):
        for chamber in self.chambers :
            chamber.initTrajectory(length)
    
    @QtCore.pyqtSlot()
    def removeTrajectory(self):
        for chamber in self.chambers :
            chamber.removeTrajectory()
    
    @QtCore.pyqtSlot(bool)
    def setRecordTrajectories(self, checked):
        for chamber in self.chambers :
            chamber.setRecordTrajectory(checked)
    
    @QtCore.pyqtSlot(bool) 
    def setShowTrajectories(self, checked):
        for chamber in self.chambers :
            chamber.setShowTrajectory(checked)
         
    @QtCore.pyqtSlot(float)   
    def setScale(self, scale):
        self.scale = scale
        self.signalRecalculateChambers.emit()
        
    def setVideoLength(self, length):
        self.videoLength = length
        
    @QtCore.pyqtSlot(bool)
    def setRecordTrajectory(self, checked):
        '''
        Enable/Disable trajectory saving
        '''
        if self.recordTrajectory == checked :
            return
        self.recordTrajectory = checked
        if self.recordTrajectory :
            self.setRecordTrajectories(True)
        self.signalTrajectoryWriting.emit(self.recordTrajectory)
