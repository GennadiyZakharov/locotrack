'''
Created on 02.11.2012

@author: gena
'''

from __future__ import division
from PyQt4 import QtCore
from ltcore.chamber import Chamber

class ChambersManager(QtCore.QObject):
    '''
    This class holds all chambersGui, 
    default settings for chambersGui
    '''
    signalChamberAdded = QtCore.pyqtSignal(object)
    signalChamberDeleted = QtCore.pyqtSignal(object)
    signalRecalculateChambers = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(ChambersManager, self).__init__(parent)
        self.chambers = set() # Set to store chambersGui
        self.numbers = set()  # Set to store used numbers
        self.threshold = 60 # Default threshold 
        self.sampleName = 'UnknownSample' # Default sample name
    
    # Standard methods to use ChambersManager as iterator
    def next(self):
        return self.chambers.next()
    
    def __len__(self):
        return self.chambers.__len__()
    
    def __iter__(self) :
        return self.chambers.__iter__()
    
    def recalculateChambers(self):
        self.signalRecalculateChambers.emit()
    
    def createChamber(self, rect):
        '''
        Create chamber from rect and add it to chamberlist
        '''
        chamber = Chamber(rect)
        chamber.setThreshold(self.threshold)
        chamber.setSampleName(self.sampleName)
        self.addChamber(chamber)
    
    def addChamber(self, chamber):
        '''
        Add new chamber to the chamberlist
        '''
        self.chambers.add(chamber)
        chamber.signalRecalculateChamber.connect(self.recalculateChambers)
        i=1
        while i in self.numbers :
            i+=1
        chamber.setNumber(i)
        self.numbers.add(i)
        self.signalChamberAdded.emit(chamber)
        self.signalRecalculateChambers.emit()
    
    def removeChamber(self, chamber):
        '''
        Removes chamber from chambersGui list
        '''
        self.signalChamberDeleted.emit(chamber) # Remove all Gui first
        self.chambers.remove(chamber)
        self.numbers.remove(chamber.number)
        self.signalRecalculateChambers.emit()
    
    def clear(self):
        '''
        Clear all chambersGui
        '''
        for chamber in self.chambers :
            self.signalChamberDeleted.emit(chamber)
        self.chambersGui = set()
        self.numbers = set()
                
    def setThreshold(self, threshold):
        '''
        Set threshold name for all chambersGui
        '''
        self.threshold = threshold
        for chamber in self.chambers :
            chamber.setThreshold(threshold)
    
    def setSampleName(self, sampleName):
        '''
        Set sample sampleName for all chambersGui
        '''
        self.sampleName = sampleName
        for chamber in self.chambers :
            chamber.setSampleName(sampleName)
        
        