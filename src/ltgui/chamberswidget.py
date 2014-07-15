'''
Created on 18.12.2010

@author: gena
'''
from __future__ import print_function
from __future__ import division

from PyQt4 import QtCore, QtGui
from ltcore.ltactions import createAction
from ltgui.actionbutton import ActionButton
import imagercc

class ChambersWidget(QtGui.QWidget):
    '''
    This widget is responsible for chamber list
    It displays list of chambers, 
    holds buttons to create, delete chambers and scale label
    '''
    signalScaleSelect = QtCore.pyqtSignal(bool)
    signalChamberSelect = QtCore.pyqtSignal(bool)
    
    signalChamberSelected = QtCore.pyqtSignal(object)
    
    signalSetScale = QtCore.pyqtSignal(float)
    signalSetChamber = QtCore.pyqtSignal(QtCore.QRect)
    signalClearChamber = QtCore.pyqtSignal(object) 

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(ChambersWidget, self).__init__(parent)
        self.chambersManager = None
        # self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        # Creating GUI elements
        layout = QtGui.QGridLayout()
        #chambersLabel = QtGui.QLabel('Chambers')
        #chambersLabel.setBuddy(self.chambersList)
        #layout.addWidget(chambersLabel, 0, 0, 1, 2)
        # list of chambers
        self.chamberWidgets = {} #
        self.selectedChamber = None 
        self.chambersList = QtGui.QTableWidget()
        self.chambersList.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents);
        self.chambersList.setColumnCount(2)
        self.chambersList.setHorizontalHeaderLabels(['Sample name', 'Threshold'])
        self.chambersList.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        header = self.chambersList.verticalHeader()
        header.setClickable(True)
        header.sectionClicked.connect(self.chamberSelectionChanged)
        layout.addWidget(self.chambersList, 1, 0, 1, 2)
        
        # Actions
        self.actionSetChamber = createAction(self, "Set chamber", "",
                                       "distribute-horizontal-center", "", True)
        self.actionSetChamber.toggled.connect(self.setChamber)
        self.actionClearChamber = createAction(self, "Clear chamber", "",
                                  "process-stop", "")
        self.actionSetScale = createAction(self, "Set scale", "",
                                  "measure", "", True)
        self.actionSetScale.toggled.connect(self.setScale)
        self.actionRecordTrajectory = createAction(self, "&Record trajectory", "",
                                 "media-record", "", True)
        self.actionSaveTrajectory = createAction(self, "Save trajectory", "",
                                 "document-save", "")
        self.actions = (self.actionSetChamber, self.actionClearChamber, None,
                        self.actionSetScale, None,
                        self.actionRecordTrajectory, self.actionSaveTrajectory)
        # Sample name label and edit
        sampleNameLabel = QtGui.QLabel('Sample name:')
        self.sampleNameEdit = QtGui.QLineEdit()
        sampleNameLabel.setBuddy(self.sampleNameEdit)
        
        layout.addWidget(sampleNameLabel, 2, 0)
        layout.addWidget(self.sampleNameEdit, 2, 1)
        # Add chamber button    
        self.setChamberButton = ActionButton(self.actionSetChamber)
        layout.addWidget(self.setChamberButton, 3, 0)
        # Clear chamber button
        self.clearChamberButton = ActionButton(self.actionClearChamber)
        layout.addWidget(self.clearChamberButton, 3, 1)
        self.clearChamberButton.clicked.connect(self.chamberClear)
        # Set scale button
        self.scaleButton = ActionButton(self.actionSetScale)
        layout.addWidget(self.scaleButton, 4, 0)      

        self.recordTrajectoryButton = ActionButton(self.actionRecordTrajectory)
        layout.addWidget(self.recordTrajectoryButton, 5, 0)
        self.saveTrajectoryButton = ActionButton(self.actionSaveTrajectory)
        layout.addWidget(self.saveTrajectoryButton, 5, 1)
        self.setLayout(layout)
        self.setEnabledActions()
    
    def setChambersManager(self, chambersManager):
        if self.chambersManager is not None :
            self.signalSetChamber.disconnect(self.chambersManager.createChamber)
            self.signalClearChamber.disconnect(self.chambersManager.removeChamber)
            self.sampleNameEdit.textChanged.disconnect(self.chambersManager.setSampleName)
            self.chamberWidgets = {} #
            self.selectedChamber = None 
            self.chambersList.clear()
            self.chambersList.setHorizontalHeaderLabels(['Sample name', 'Threshold'])
            
        self.chambersManager = chambersManager
        if self.chambersManager is not None :
            
            self.signalSetChamber.connect(self.chambersManager.createChamber)
            self.signalClearChamber.connect(self.chambersManager.removeChamber)
            self.sampleNameEdit.textChanged.connect(self.chambersManager.setSampleName)
            for chamber in self.chambersManager:
                self.addChamber(chamber)
        self.setEnabledActions()
        
        
        
    def setEnabledActions(self):
        flag = self.chambersManager is not None
        for action in self.actions :
            if action is not None :
                action.setEnabled(flag)
    
    def getChamberByNumber(self, number):
        for chamber in self.chamberWidgets.keys():
            if chamber.number == number:
                return chamber
        return None 
        
        
    def chamberSelectionChanged(self, index) :
        '''
        Select different chamber, or unselect current
        '''
        chamber = self.getChamberByNumber(index + 1)
        if chamber is self.selectedChamber :
            self.selectChamber(None)
        else :
            self.selectChamber(chamber)
        
    def selectChamber(self, chamber):
        '''
        Move selection to chamber
        if chamber is None, clear selection
        '''
        if chamber is self.selectedChamber :
            return
        self.selectedChamber = chamber
        self.signalChamberSelected.emit(self.selectedChamber)     
    
    @QtCore.pyqtSlot(QtCore.QRect)
    def chamberSetted(self, rect):
        self.signalSetChamber.emit(rect)
    
    @QtCore.pyqtSlot(float)
    def scaleSetted(self, scaleFactor):
        self.actionSetScale.setChecked(False)
        self.signalSetScale.emit(scaleFactor)
    
    @QtCore.pyqtSlot(bool)
    def setScale(self, checked):
        self.actionSetChamber.setChecked(False)
        self.signalScaleSelect.emit(checked)
    
    @QtCore.pyqtSlot(bool)
    def setChamber(self, checked):
        self.actionSetScale.setChecked(False)
        self.signalChamberSelect.emit(checked)
        
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
       
    def updateChamberGui(self):
        chamber = self.sender()
        sampleName, thresholdSpibBox = self.chamberWidgets[chamber]
        sampleName.setText(chamber.sampleName)
        thresholdSpibBox.setValue(chamber.threshold)
        
    def addChamber(self, chamber):
        '''
        Add new created chamber to list adn create GUI widget for it
        '''
        number = chamber.number - 1
        if self.chambersList.rowCount() <= number :
            self.chambersList.setRowCount(chamber.number)
        '''
        chamberWidget = ChamberWidget(chamber)
        self.chamberWidgets[chamber] = chamberWidget
        self.chambersList.setCellWidget(chamber.number-1, 0, chamberWidget)
        self.chambersList.resizeColumnsToContents()
        #self.chambersList.verticalHeader().setDefaultSectionSize(rowheight)
        '''
        
        sampleName = QtGui.QLineEdit()
        sampleName.setText(chamber.sampleName)
        sampleName.textChanged.connect(chamber.setSampleName)
        self.chambersList.setCellWidget(number, 0, sampleName)
        thresholdSpinBox = QtGui.QSpinBox()
        thresholdSpinBox.setMaximum(100)
        thresholdSpinBox.setValue(chamber.threshold)
        thresholdSpinBox.valueChanged.connect(chamber.setThreshold)
        self.chambersList.setCellWidget(number, 1, thresholdSpinBox)
        self.chamberWidgets[chamber] = (sampleName, thresholdSpinBox)
        chamber.signalGuiDataUpdated.connect(self.updateChamberGui)  
    
    
    def removeChamber(self, chamber):
        '''
        Remove GUI for chamber 
        '''
        self.selectedChamber = None
        self.chambersList.removeCellWidget(chamber.number - 1, 0)
        self.chambersList.removeCellWidget(chamber.number - 1, 1)
        del self.chamberWidgets[chamber]
        if self.chambersList.rowCount() == chamber.number :
            i = 1 # 
            for chamber in self.chamberWidgets.keys() :
                if i < chamber.number :
                    i = chamber.number
            self.chambersList.setRowCount(i)
                    
        
