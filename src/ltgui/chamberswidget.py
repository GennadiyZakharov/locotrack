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
        self.chambers = {}
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
        self.setChamberButton.toggled.connect(self.selectChamber)
        # Clear chamber button
        self.clearChamberButton = QtGui.QPushButton('Clear chamber')
        layout.addWidget(self.clearChamberButton, 2, 1)
        self.clearChamberButton.clicked.connect(self.chamberClear)
        # Set scale button
        self.scaleButton = QtGui.QPushButton('Set Scale')
        self.scaleButton.setCheckable(True)
        layout.addWidget(self.scaleButton)      
        self.scaleButton.toggled.connect(self.setScaleOrChamber)
        self.scaleButton.toggled.connect(self.selectScale)
        # Analysis Method 
        self.analysisMethod = QtGui.QCheckBox('MaxBright')
        layout.addWidget(self.analysisMethod)
        # Set Layout
        self.setLayout(layout)
        
    def chamberSelectionChanged(self) :
        '''
        Select different chamber, or unselect current
        '''
        currentRow = self.chambersList.currentRow()
        
        #self.chambersList.clearFocus()
        if self.selectedChamber == currentRow :
            self.chambersList.clearSelection()
            self.selectedChamber = -1
        else :
            self.selectedChamber = currentRow
            #self.chambersList.setCurrentCell(currentRow, 0)
        print self.selectedChamber
        # Emit signal with new chamber number       
        self.emit(signalChangeSelection, self.selectedChamber)
  
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

    def selectScale(self, checked):
        self.signalScaleSelect.emit(checked)
    
    def selectChamber(self, checked):
        self.signalChamberSelect.emit(checked)

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
        reply = QtGui.QMessageBox.question(self, "Chamber manager",
                                         "Clear selected chamber with all recorded data?",
                                         QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.emit(signalClearChamber)
        
    def chamberListUpdated(self, chambersList, selected):
        '''
        chamber list was modified
        Rebuilding table according to the chambersList
        '''
        self.chambers = {}
        self.chambersList.clear()
        self.chambersList.setRowCount(len(chambersList))
        for i in range(len(chambersList)) :
            chamber = chambersList[i]
            chamberWidget = ChamberWidget(chamber)
            self.chambers[chamber] = chamberWidget
            self.chambersList.setCellWidget(i, 0, chamberWidget)
        # Selecting chamber
        self.selectedChamber = selected
        self.chambersList.setCurrentCell(self.selectedChamber, 0)
        
        
