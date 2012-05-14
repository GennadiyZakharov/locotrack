'''
Created on 18.12.2010

@author: gena
'''

from PyQt4 import QtCore, QtGui
#from ltcore.actions import LtActions

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
        # self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        # Creating GUI elements
        layout = QtGui.QGridLayout()
        chambersLabel = QtGui.QLabel('Chambers')
        # list of chambers
        
        self.chambersList = QtGui.QTableWidget()
        chambersLabel.setBuddy(self.chambersList)
        self.chambersList.setColumnCount(2)
        layout.addWidget(chambersLabel, 0, 0, 1, 2)
        layout.addWidget(self.chambersList, 1, 0, 1, 2)
        self.selectedChamber = -1
        self.chambersList.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.chambersList.cellPressed.connect(self.chamberSelectionChanged)
        # Add chamber button    
        self.setChamberButton = QtGui.QPushButton('Set chamber')
        self.setChamberButton.setCheckable(True)
        layout.addWidget(self.setChamberButton,2,0)
        self.setChamberButton.toggled.connect(self.setScaleOrChamber)
        # Clear chamber button
        self.clearChamberButton = QtGui.QPushButton('Clear chamber')
        layout.addWidget(self.clearChamberButton,2,1)
        self.clearChamberButton.clicked.connect(self.chamberClear)
        # Set scale button
        self.scaleButton = QtGui.QPushButton('Set Scale')
        self.scaleButton.setCheckable(True)
        layout.addWidget(self.scaleButton)      
        self.scaleButton.toggled.connect(self.setScaleOrChamber) 
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
                                         QtGui.QMessageBox.Yes | QtGui.QMessageBox.No )
        if reply == QtGui.QMessageBox.Yes:
            self.emit(signalClearChamber)
        
    def chamberListUpdated(self, chambersList, selected):
        '''
        chamber list was modified
        Rebuilding table according to the chambersList
        '''
        self.chambersList.clear()
        self.chambersList.setRowCount(len(chambersList))
        for i in range(len(chambersList)) :
            text = 'Chamber '+str(i+1)
            self.chambersList.setCellWidget(i,0,QtGui.QLabel(text))
            slider = QtGui.QSlider(QtCore.Qt.Horizontal)
            slider.setMaximum(99)
            slider.setValue(chambersList[i].threshold)
            slider.valueChanged.connect(chambersList[i].setThreshold)
            self.chambersList.setCellWidget(i,1,slider)
        # Selecting chamber
        self.selectedChamber = selected
        self.chambersList.setCurrentCell(self.selectedChamber, 0)
        
        