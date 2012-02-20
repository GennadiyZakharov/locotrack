'''
Created on 18.12.2010

@author: gena
'''

from PyQt4 import QtCore, QtGui
#from ltcore.actions import LtActions
from ltcore.signals import *

class ChambersWidget(QtGui.QWidget):
    '''
    This widget is responsible for chamber list
    It displays list of chambers, 
    holds buttons to create, delete chambers and scale label
    '''

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(ChambersWidget, self).__init__(parent)
        # Creating GUI elements
        layout = QtGui.QGridLayout()
        chambersLabel = QtGui.QLabel('Chambers')
        # list of chambers
        self.chambersList = QtGui.QListWidget()
        chambersLabel.setBuddy(self.chambersList)
        layout.addWidget(chambersLabel, 0, 0, 1, 2)
        layout.addWidget(self.chambersList, 1, 0, 1, 2)
        self.chambersList.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.chambersList.itemClicked.connect(self.chamberSelectionChanged)
        self.selectedChamber = -1
        # Add chamber button    
        self.setChamberButton = QtGui.QPushButton('Set chamber')
        self.setChamberButton.setCheckable(True)
        layout.addWidget(self.setChamberButton,2,0)
        self.connect(self.setChamberButton, signalToggled, self.setScaleOrChamber)
        # Clear chamber button
        self.clearChamberButton = QtGui.QPushButton('Clear chamber')
        layout.addWidget(self.clearChamberButton,2,1)
        self.connect(self.clearChamberButton, signalClicked, self.chamberClear)
        # Set scale button
        self.scaleButton = QtGui.QPushButton('Set Scale')
        self.scaleButton.setCheckable(True)
        layout.addWidget(self.scaleButton)      
        self.connect(self.scaleButton, signalToggled, self.setScaleOrChamber)
        # Set Layout
        self.setLayout(layout)
        
    def chamberSelectionChanged(self, item) :
        '''
        Select different chamber, or unselect current
        '''
        if self.selectedChamber == self.chambersList.currentRow() :
            self.selectedChamber = -1
            self.chambersList.clearSelection()
        else :
            self.selectedChamber = self.chambersList.row(item)  
        # Emit signal with new chamber number       
        self.emit(signalChangeSelection,self.selectedChamber)
  
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

    def setScaleOrChamber(self, checked):
        '''
        This procedure is called, when setScale or setChamber button
        is pressed
        '''
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
                                         QtGui.QMessageBox.Yes | QtGui.QMessageBox.No )
        if reply == QtGui.QMessageBox.Yes:
            self.emit(signalClearChamber)
        
    def chamberListUpdated(self, chambersList, selected):
        '''
        chamber list was modified
        Rebuilding table according to the chambersList
        '''
        self.chambersList.clear()
        for i in range(len(chambersList)) :
            text = 'Chamber '+str(i)
            self.chambersList.addItem(text)
        # Selecting chamber
        self.selectedChamber = selected
        self.chambersList.setCurrentRow(self.selectedChamber)
        
        