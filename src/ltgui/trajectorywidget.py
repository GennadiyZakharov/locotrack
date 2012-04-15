'''
Created on 04.02.2012

@author: gena
'''

from PyQt4 import QtCore, QtGui
#from ltcore.actions import LtActions
from ltcore.signals import *
from ltgui.labeledwidgets import *

class TrajectoryWidget(QtGui.QWidget):
    '''
    This widget hols GUI elements for trajectory analysing
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(TrajectoryWidget, self).__init__(parent)
        #
        layout=QtGui.QVBoxLayout()
        #
        self.speciesEdit = LabelledLineEdit('Line')
        layout.addWidget(self.speciesEdit)
        self.speciesEdit.lineEdit.textChanged.connect(self.descriptionChanged)
        self.genderEdit = LabelledLineEdit('Gender')
        layout.addWidget(self.genderEdit)
        self.genderEdit.lineEdit.textChanged.connect(self.descriptionChanged)
        self.conditionEdit = LabelledLineEdit('Condition')
        layout.addWidget(self.conditionEdit)
        self.conditionEdit.lineEdit.textChanged.connect(self.descriptionChanged)
        #
        self.recordTrajectoryButton = QtGui.QPushButton('Record trajectory')
        self.recordTrajectoryButton.setCheckable(True)
        self.recordTrajectoryButton.setEnabled(False)
        self.connect(self.recordTrajectoryButton, signalToggled, self.setTrajectoryRecord)
        layout.addWidget(self.recordTrajectoryButton)
        #
        self.analyseTrajectoryButton = QtGui.QPushButton('Analyse trajectory')
        self.connect(self.analyseTrajectoryButton, signalClicked, self.analyseTrajectory)
        layout.addWidget(self.analyseTrajectoryButton)
        #
        self.setLayout(layout)
        
        
    def setTrajectoryRecord(self, checked):
        self.emit(signalWriteTrajectory, checked,self.speciesEdit.text(),
                  self.genderEdit.text(), self.conditionEdit.text())
        
    def analyseTrajectory(self):
        self.emit(signalAnalyseTrajectory)
        
    def descriptionChanged(self):
        flag = (self.speciesEdit.text() != '' and 
                self.genderEdit.text() != '' and
                self.conditionEdit.text() != '')
        self.recordTrajectoryButton.setEnabled(flag)
        if flag :
            self.emit(signalSampleNameChanged, self.speciesEdit.text(),
                      self.genderEdit.text(), self.conditionEdit.text())
        
    