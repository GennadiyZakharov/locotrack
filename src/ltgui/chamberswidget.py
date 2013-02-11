'''
Created on 18.12.2010

@author: gena
'''

from PyQt4 import QtCore, QtGui
from ltcore.signals import *

#from ltgui.labeledwidgets import LabelledSlider
from chamberwidget import ChamberWidget

class ChambersWidget(QtGui.QWidget):
    '''
    This widget is responsible for chamber list
    It displays list of chambers, 
    holds buttons to create, delete chambers and scale label
    '''
    signalScaleSelect = QtCore.pyqtSignal(bool)
    signalChamberSelect = QtCore.pyqtSignal(bool)
    
    signalChamberSelected = QtCore.pyqtSignal(object)
    signalClearChamber = QtCore.pyqtSignal(object) 

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(ChambersWidget, self).__init__(parent)
        # self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        # Creating GUI elements
        layout = QtGui.QGridLayout()
        chambersLabel = QtGui.QLabel('Chambers')
        # list of chambers
        self.chamberWidgets = {} # 
        self.chambersList = QtGui.QTableWidget()
        chambersLabel.setBuddy(self.chambersList)
        self.chambersList.setColumnCount(1)
        self.chambersList.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding))
        layout.addWidget(chambersLabel, 0, 0, 1, 2)
        layout.addWidget(self.chambersList, 1, 0, 1, 2)
        self.selectedChamber = -1
        self.chambersList.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.chambersList.cellPressed.connect(self.chamberSelectionChanged)
        # Add chamber button    
        self.setChamberButton = QtGui.QPushButton('Set chamber')
        self.setChamberButton.setCheckable(True)
        layout.addWidget(self.setChamberButton, 2, 0)
        self.setChamberButton.toggled.connect(self.setScaleOrChamber)
        #self.setChamberButton.toggled.connect(self.setChamber)
        # Clear chamber button
        self.clearChamberButton = QtGui.QPushButton('Clear chamber')
        layout.addWidget(self.clearChamberButton, 2, 1)
        self.clearChamberButton.clicked.connect(self.chamberClear)
        # Set scale button
        self.scaleButton = QtGui.QPushButton('Set Scale')
        self.scaleButton.setCheckable(True)
        layout.addWidget(self.scaleButton)      
        self.scaleButton.toggled.connect(self.setScaleOrChamber)
        #self.scaleButton.toggled.connect(self.setScale)
        self.setLayout(layout)
    
    def getChamberByNumber(self, number):
        for chamber in self.chamberWidgets.keys():
            if chamber.number == number:
                return chamber
        return None 
        
        
    def chamberSelectionChanged(self) :
        '''
        Select different chamber, or unselect current
        '''
        currentRow = self.chambersList.currentRow()
        chamber = self.getChamberByNumber(currentRow+1)
        if chamber is self.selectedChamber :
            self.selectChamber(None)
        else :
            self.selectChamber(chamber)
        
    def selectChamber(self, chamber):
        if chamber is self.selectedChamber :
            return
        self.selectedChamber = chamber
        if  self.selectedChamber is not None:
            self.chambersList.setCurrentCell(chamber.number-1, 0)
        else :
            self.chambersList.clearSelection()
        self.signalChamberSelected.emit(self.selectedChamber)
  
    def regionSelected(self, rect):
        '''
        This procedure is called, when some region
        was selected on cvLabel
        '''
        if self.scaleButton.isChecked() :
            # This rect was scale label
            self.scaleButton.setChecked(False)
            self.emit(signalSetScale, rect)
        elif self.setChamberButton.isChecked() :
            # This rect was chamber selection
            self.emit(signalSetChamber, rect)
    '''
    def setScale(self, checked):
        self.signalScaleSelect.emit(checked)
    
    def setChamber(self, checked):
        self.signalChamberSelect.emit(checked)
    '''
    def setScaleOrChamber(self, checked):
        '''
        This procedure is called, when setScale or setChamber button
        is pressed
        '''
        if self.scaleButton.isChecked() :
            self.setChamberButton.setChecked(False)
        # We sent signal to enable drag on cvLabel
        self.emit(signalEnableDnD, checked)
        # Now we only can wait for signal from cvLabel to receive 
        # selected Rectangle
        
    def chamberClear(self):
        '''
        Delete selected chamber
        '''
        if self.selectedChamber is None:
            return
        reply = QtGui.QMessageBox.question(self, "Chamber manager",
                                         "Clear selected chamber with all recorded data?",
                                         QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.signalClearChamber.emit(self.selectedChamber)
        
    def addChamber(self, chamber):
        chamberWidget = ChamberWidget(chamber)
        
        if self.chambersList.rowCount() < chamber.number :
            self.chambersList.setRowCount(chamber.number)
        self.chamberWidgets[chamber] = chamberWidget
        self.chambersList.setCellWidget(chamber.number-1, 0, chamberWidget) 
    
    def removeChamber(self, chamber):
        self.selectedChamber = None
        self.chambersList.removeCellWidget(chamber.number-1,0)
        del self.chamberWidgets[chamber]
        if self.chambersList.rowCount() == chamber.number :
            i = 1
            for chamber in self.chamberWidgets.keys() :
                if i < chamber.number :
                    i = chamber.number
            self.chambersList.setRowCount(i)
                    
        
