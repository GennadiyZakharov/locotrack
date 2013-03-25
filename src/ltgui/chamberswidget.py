'''
Created on 18.12.2010

@author: gena
'''

from PyQt4 import QtCore, QtGui
from ltcore.ltactions import createAction
from ltcore.signals import *
from ltgui.actionbutton import ActionButton
import imagercc

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
    
    signalSetScale     = QtCore.pyqtSignal(QtCore.QRect)
    signalSetChamber   = QtCore.pyqtSignal(QtCore.QRect)
    signalClearChamber = QtCore.pyqtSignal(object) 

    def __init__(self, chambersManager, parent=None):
        '''
        Constructor
        '''
        super(ChambersWidget, self).__init__(parent)
        self.chambersManager = chambersManager
        
        self.signalSetChamber.connect(chambersManager.createChamber)
        self.signalClearChamber.connect(chambersManager.removeChamber)
        # self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        # Creating GUI elements
        layout = QtGui.QGridLayout()
        #chambersLabel = QtGui.QLabel('Chambers')
        #chambersLabel.setBuddy(self.chambersList)
        #layout.addWidget(chambersLabel, 0, 0, 1, 2)
        # list of chambers
        self.chamberWidgets = {} # 
        self.chambersList = QtGui.QTableWidget()
        self.chambersList.setColumnCount(1)
        self.chambersList.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Preferred)
        
        layout.addWidget(self.chambersList, 1, 0, 1, 2)
        self.selectedChamber = -1
        self.chambersList.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.chambersList.cellPressed.connect(self.chamberSelectionChanged)
        # Actions
        self.actionSetChamber = createAction(self,"Set chamber", "",
                                       "distribute-horizontal-center", "", True)
        self.actionSetChamber.toggled.connect(self.setScaleOrChamber)
        self.actionClearChamber = createAction(self,"Clear chamber", "", 
                                  "process-stop", "")
        self.actionSetScale =  createAction(self,"Set scale", "", 
                                  "measure", "", True)
        self.actionSetScale.toggled.connect(self.setScaleOrChamber)
        self.actionRecordTrajectory = createAction(self,"&Record trajectory", "", 
                                 "media-record", "", True)
        self.actionSaveTrajectory = createAction(self,"Save trajectory", "", 
                                 "document-save", "")
        self.actions = (self.actionSetChamber,self.actionClearChamber,None,
                        self.actionSetScale,None,
                        self.actionRecordTrajectory,self.actionSaveTrajectory)
        # Saple name label and edit
        sampleNameLabel = QtGui.QLabel('Sample name:')
        sampleNameEdit = QtGui.QLineEdit()
        sampleNameLabel.setBuddy(sampleNameEdit)
        sampleNameEdit.textChanged.connect(self.chambersManager.setSampleName)
        layout.addWidget(sampleNameLabel,2,0)
        layout.addWidget(sampleNameEdit,2,1)
        # Add chamber button    
        self.setChamberButton = ActionButton(self.actionSetChamber)
        layout.addWidget(self.setChamberButton, 3, 0)
        # Clear chamber button
        self.clearChamberButton = ActionButton(self.actionClearChamber)
        layout.addWidget(self.clearChamberButton, 3, 1)
        self.clearChamberButton.clicked.connect(self.chamberClear)
        # Set scale button
        self.scaleButton = ActionButton(self.actionSetScale)
        layout.addWidget(self.scaleButton,4,0)      

        self.recordTrajectoryButton = ActionButton(self.actionRecordTrajectory)
        layout.addWidget(self.recordTrajectoryButton,5,0)
        self.saveTrajectoryButton = ActionButton(self.actionSaveTrajectory)
        layout.addWidget(self.saveTrajectoryButton,5,1)
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
            self.signalSetScale.emit(rect)
        elif self.setChamberButton.isChecked() :
            # This rect was chamber selection
            '''
            for chamber in self.chamberWidgets.keys() :
                if rect.intersects(chamber.rect) :
                    QtGui.QMessageBox.warning(self,'Chambers manager', 'New chamber can`t intersect with existing one')
                    return
            '''
            self.signalSetChamber.emit(rect)
    '''
    def setScale(self, checked):
        self.setChamberButton.setChecked(False)
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
        '''
        Add new created chamber to list adn create GUI widget for it
        '''
        chamberWidget = ChamberWidget(chamber)
        if self.chambersList.rowCount() < chamber.number :
            self.chambersList.setRowCount(chamber.number)
        self.chamberWidgets[chamber] = chamberWidget
        self.chambersList.setCellWidget(chamber.number-1, 0, chamberWidget)
        #self.chambersList.verticalHeader().setDefaultSectionSize(rowheight)
        
    
    def removeChamber(self, chamber):
        '''
        Remove GUI for chamber 
        '''
        self.selectedChamber = None
        self.chambersList.removeCellWidget(chamber.number-1,0)
        del self.chamberWidgets[chamber]
        if self.chambersList.rowCount() == chamber.number :
            i = 1 # 
            for chamber in self.chamberWidgets.keys() :
                if i < chamber.number :
                    i = chamber.number
            self.chambersList.setRowCount(i)
                    
        
