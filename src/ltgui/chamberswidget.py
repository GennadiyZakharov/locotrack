'''
Created on 18.12.2010

@author: gena
'''

from PyQt4 import QtCore, QtGui
#from ltcore.actions import LtActions
from ltcore.signals import *

class ChambersWidget(QtGui.QWidget):
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(ChambersWidget, self).__init__(parent)
        
        layout = QtGui.QGridLayout()
        
        chambersLabel = QtGui.QLabel('Chambers')
        self.chambersList = QtGui.QListWidget()
        chambersLabel.setBuddy(self.chambersList)
        layout.addWidget(chambersLabel, 0, 0, 1, 2)
        layout.addWidget(self.chambersList, 1, 0, 1, 2)
        self.chambersList.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.chambersList.itemClicked.connect(self.on_SelectionChanged)
        self.selectedChamber = -1
        #self.connect(self.chambersList, QtCore.SIGNAL("itemClicked(QListWidgetItem)"), self.on_deselect)
                      
        self.setChamberButton = QtGui.QPushButton('Set chamber')
        self.setChamberButton.setCheckable(True)
        layout.addWidget(self.setChamberButton,2,0)
        self.connect(self.setChamberButton, signalToggled, self.on_ScaleOrChamberSet)
        
        self.clearChamberButton = QtGui.QPushButton('Clear chamber')
        layout.addWidget(self.clearChamberButton,2,1)
        self.connect(self.clearChamberButton, signalClicked, self.on_ChamberCleared)
        
        self.batchButton = QtGui.QPushButton('Batch')
        layout.addWidget(self.batchButton)
        
        self.scaleButton = QtGui.QPushButton('Set Scale')
        self.scaleButton.setCheckable(True)
        layout.addWidget(self.scaleButton)      
        self.connect(self.scaleButton, signalToggled, self.on_ScaleOrChamberSet)
        
        
        self.setLayout(layout)
        
    def on_SelectionChanged(self, item) :
        if self.selectedChamber == self.chambersList.currentRow() :
            self.selectedChamber = -1
            self.chambersList.clearSelection()
        else :
            self.selectedChamber = self.chambersList.row(item)         
        self.emit(signalChangeSelection,self.selectedChamber)
  
    def on_RegionSelected(self, rect):
        if self.scaleButton.isChecked() :
            self.scaleButton.setChecked(False)
            self.emit(signalSetScale, rect)
        elif self.setChamberButton.isChecked() :
            self.emit(signalSetChamber, rect)

    def on_ScaleOrChamberSet(self, checked):
        self.emit(signalEnableDnD, checked)
        
    def on_ChamberCleared(self):
        reply = QtGui.QMessageBox.question(self, "Chamber manager",
                                         "Clear selected chamber with all recorded data?",
                                         QtGui.QMessageBox.Yes | QtGui.QMessageBox.No )
        if reply == QtGui.QMessageBox.Yes:
            self.emit(signalClearChamber)
        
    def on_chamberListUpdated(self,list, selected):
        self.chambersList.clear()
        for i in range(len(list)) :
            text = 'Chamber '+str(i)+' '+list[i].__str__()
            self.chambersList.addItem(text)
        self.selectedChamber = selected
        self.chambersList.setCurrentRow(self.selectedChamber)
        
        
