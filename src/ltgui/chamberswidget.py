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
               
        self.scaleButton = QtGui.QPushButton('Set Scale')
        self.scaleButton.setCheckable(True)
        layout.addWidget(self.scaleButton)      
        self.connect(self.scaleButton, signalToggled, self.on_ScaleOrChamberSet)
        
        self.chamberButton = QtGui.QPushButton('Set Chamber')
        self.chamberButton.setCheckable(True)
        layout.addWidget(self.chamberButton)
        self.connect(self.chamberButton, signalToggled, self.on_ScaleOrChamberSet)
        
        self.batchButton = QtGui.QPushButton('Batch')
        layout.addWidget(self.batchButton)
        
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
        elif self.chamberButton.isChecked() :
            #self.chamberButton.setChecked(False)
            self.emit(signalSetChamber, rect)

    def on_ScaleOrChamberSet(self, checked):
        self.emit(signalEnableDnD, checked)
        
    def on_chamberListUpdated(self,list):
        self.chambersList.clear()
        for i in range(len(list)) :
            text = 'Chamber '+str(i)+' '+list[i].__str__()
            self.chambersList.addItem(text)
        
        
